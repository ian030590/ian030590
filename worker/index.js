// Cloudflare Worker for the site. Static files in dist/ are served by the
// assets binding; only /api/* reaches this script (see run_worker_first in
// wrangler.jsonc). Contact messages are emailed through Resend; the API key
// stays on the server as the RESEND_API_KEY secret so visitors cannot use it.

import { handleBlogger } from './blogger.js';

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
    if (!value) return { error: '請填寫所有欄位。' };
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
    subject: `[網站聯絡] ${fields.subject} - ${fields.name}`,
    text: [
      `姓名／組織：${fields.name}`,
      `專業背景：${fields.role}`,
      `Email：${fields.email}`,
      `主旨：${fields.subject}`,
      '',
      fields.body,
    ].join('\n'),
  };
}

async function handleContact(request, env) {
  if (request.method !== 'POST') {
    return new Response(null, { status: 405, headers: { Allow: 'POST' } });
  }

  // Browsers always send Origin on a cross-site POST; only accept our own pages.
  const origin = request.headers.get('Origin');
  if (origin && origin !== new URL(request.url).origin) {
    return json(403, { error: '不接受來自其他網站的請求。' });
  }
  if (!(request.headers.get('Content-Type') || '').includes('application/json')) {
    return json(415, { error: '表單內容格式錯誤。' });
  }

  if (env.CONTACT_RATE_LIMITER) {
    const key = request.headers.get('CF-Connecting-IP') || 'unknown';
    const { success } = await env.CONTACT_RATE_LIMITER.limit({ key });
    if (!success) return json(429, { error: '送出次數過多，請稍候一分鐘再試。' });
  }

  const raw = await request.text();
  if (new TextEncoder().encode(raw).length > MAX_BODY_BYTES) {
    return json(413, { error: '訊息內容過長。' });
  }
  let input;
  try {
    input = JSON.parse(raw);
  } catch {
    return json(400, { error: '表單內容格式錯誤。' });
  }

  // Bots fill the hidden "website" field; pretend success so they move on.
  if (text(input?.website)) return json(200, { ok: true });

  const { fields, error } = validateContact(input);
  if (error) return json(400, { error });

  if (!env.RESEND_API_KEY || !env.CONTACT_FROM_EMAIL || !env.CONTACT_TO_EMAIL) {
    console.error('RESEND_API_KEY, CONTACT_FROM_EMAIL and CONTACT_TO_EMAIL must all be set');
    return json(503, { error: UNAVAILABLE });
  }

  const response = await fetch(RESEND_ENDPOINT, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${env.RESEND_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(emailPayload(fields, env)),
  });
  if (!response.ok) {
    console.error(`Resend request failed: ${response.status} ${await response.text()}`);
    return json(502, { error: UNAVAILABLE });
  }
  return json(200, { ok: true });
}

export default {
  async fetch(request, env, ctx) {
    const { pathname } = new URL(request.url);
    if (pathname === '/api/contact') return handleContact(request, env);
    if (pathname === '/api/articles') return handleBlogger(request, env, ctx);
    if (pathname.startsWith('/api/')) return json(404, { error: 'Not found' });
    return env.ASSETS.fetch(request);
  },
};
