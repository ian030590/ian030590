// Cloudflare Worker for the site. Static files in dist/ are served by the
// assets binding; article routes also use Blogger (see wrangler.jsonc).
// Contact messages are emailed through Resend; the API key
// stays on the server as the RESEND_API_KEY secret so visitors cannot use it.

import { articleAPI, articlePage, LEGACY_HOST, SITE } from './articles.js';

const RESEND_ENDPOINT = 'https://api.resend.com/emails';
const MAX_BODY_BYTES = 16 * 1024;
const LIMITS = { name: 100, role: 100, email: 254, subject: 200, body: 3500 };
// Plain addresses only: no display names, lists or brackets in reply_to.
const EMAIL_PATTERN = /^[^\s@<>(),;:"[\]]+@[^\s@<>(),;:"[\]]+\.[^\s@<>(),;:"[\]]+$/;
const UNAVAILABLE = '目前無法送出訊息，請改用 Email 聯絡。';

function json(status, data) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      'Cache-Control': 'no-store',
    },
  });
}

function text(value) {
  return typeof value === 'string' ? value.trim() : '';
}

// Returns the cleaned fields, or a Chinese error message for the visitor.
export function validateContact(input) {
  if (!input || typeof input !== 'object') return { error: '表單內容格式錯誤。' };
  const fields = {};
  for (const [key, limit] of Object.entries(LIMITS)) {
    let value = text(input[key]);
    // Only the message keeps line breaks; the rest end up in one-line headers.
    if (key !== 'body') value = value.replace(/\s+/g, ' ');
    if (!value && (key === 'name' || key === 'email' || key === 'body')) {
      return { error: '請填寫姓名、電子郵件與訊息內容。' };
    }
    if (value.length > limit) return { error: `欄位內容過長（上限 ${limit} 字）。` };
    fields[key] = value;
  }
  if (!EMAIL_PATTERN.test(fields.email)) return { error: '請確認電子郵件信箱格式。' };
  return { fields };
}

export function emailPayload(fields, env) {
  return {
    from: env.CONTACT_FROM_EMAIL,
    to: env.CONTACT_TO_EMAIL,
    // Replying in the mail app answers the visitor directly.
    reply_to: fields.email,
    subject: `[網站聯絡] ${fields.subject || '一般聯絡'} - ${fields.name}`,
    text: [
      `姓名／組織：${fields.name}`,
      `專業背景：${fields.role || '未填寫'}`,
      `Email：${fields.email}`,
      `主旨：${fields.subject || '未填寫'}`,
      '',
      fields.body,
    ].join('\n'),
  };
}

async function handleContact(request, env) {
  if (request.method !== 'POST') {
    return new Response(null, { status: 405, headers: { Allow: 'POST' } });
  }

  const contentType = request.headers.get('Content-Type') || '';
  const mediaType = contentType.split(';')[0].trim().toLowerCase();
  const native = ['application/x-www-form-urlencoded', 'multipart/form-data'].includes(mediaType);
  const respond = (status, data) => native
    ? new Response(null, { status: 303, headers: {
      Location: '/contact?' + (data.ok ? 'sent=1' : 'error=' + status),
      'Cache-Control': 'no-store',
    } })
    : json(status, data);

  // Browsers always send Origin on a cross-site POST; only accept our own pages.
  const origin = request.headers.get('Origin');
  if (origin && origin !== new URL(request.url).origin) {
    return respond(403, { error: '不接受來自其他網站的請求。' });
  }
  if (!native && mediaType !== 'application/json') {
    return respond(415, { error: '表單內容格式錯誤。' });
  }

  if (env.CONTACT_RATE_LIMITER) {
    const key = request.headers.get('CF-Connecting-IP') || 'unknown';
    const { success } = await env.CONTACT_RATE_LIMITER.limit({ key });
    if (!success) return respond(429, { error: '送出次數過多，請稍候一分鐘再試。' });
  }

  const raw = await request.arrayBuffer();
  if (raw.byteLength > MAX_BODY_BYTES) {
    return respond(413, { error: '訊息內容過長。' });
  }
  let input;
  try {
    input = native
      ? Object.fromEntries(await new Response(raw, { headers: { 'Content-Type': contentType } }).formData())
      : JSON.parse(new TextDecoder().decode(raw));
  } catch {
    return respond(400, { error: '表單內容格式錯誤。' });
  }

  // Bots fill the hidden "website" field; pretend success so they move on.
  if (text(input?.website)) return respond(200, { ok: true });

  const { fields, error } = validateContact(input);
  if (error) return respond(400, { error });

  if (!env.RESEND_API_KEY || !env.CONTACT_FROM_EMAIL || !env.CONTACT_TO_EMAIL) {
    console.error('RESEND_API_KEY, CONTACT_FROM_EMAIL and CONTACT_TO_EMAIL must all be set');
    return respond(503, { error: UNAVAILABLE });
  }

  const response = await fetch(RESEND_ENDPOINT, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${env.RESEND_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(emailPayload(fields, env)),
  }).catch((error) => {
    if (!native) throw error;
    return null;
  });
  if (!response) return respond(502, { error: UNAVAILABLE });
  if (!response.ok) {
    console.error(`Resend request failed: ${response.status} ${await response.text()}`);
    return respond(502, { error: UNAVAILABLE });
  }
  return respond(200, { ok: true });
}

export default {
  async fetch(request, env, ctx) {
    const { hostname, pathname, search } = new URL(request.url);
    if (hostname === LEGACY_HOST) return Response.redirect(SITE + pathname + search, 301);
    if (pathname === '/api/contact') return handleContact(request, env);
    if (pathname === '/api/articles') return articleAPI(request, env, ctx);
    if (pathname.startsWith('/api/')) return json(404, { error: 'Not found' });
    if (['/blog', '/blog.html', '/article', '/article.html', '/sitemap.xml', '/rss.xml'].includes(pathname)
      || pathname.startsWith('/content/')) return articlePage(request, env, ctx);
    return env.ASSETS.fetch(request);
  },
};
