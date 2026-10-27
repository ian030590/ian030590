import { Parser } from 'htmlparser2';
import sanitizeHtml from 'sanitize-html';
import config from '../blogger.config.json' with { type: 'json' };
import { handleBlogger } from './blogger.js';

export const SITE = 'https://ian030590.trainerhub.cc';
const taiwanDate = new Intl.DateTimeFormat('en-CA', {
  timeZone: 'Asia/Taipei', year: 'numeric', month: '2-digit', day: '2-digit',
});
const escape = (value) => String(value ?? '').replace(/[&<>"']/g,
  (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]);
const json = (value) => JSON.stringify(value).replace(/</g, '\\u003c');
export const pathKey = (path) => {
  try { return decodeURI(path).replace(/\.html$/, ''); }
  catch { return path; }
};

function httpURL(value, base = SITE) {
  if (!value) return '';
  try {
    const url = new URL(value, base);
    return ['http:', 'https:'].includes(url.protocol) ? url.href : '';
  } catch { return ''; }
}

function inspectContent(content) {
  let marker, image = '', lead = '', paragraph = false, skipped = 0;
  const stack = [];
  const parser = new Parser({
    onopentag(name, attrs) {
      const skip = ['style', 'script', 'header'].includes(name);
      stack.push(skip);
      if (skip) skipped++;
      if (attrs['data-ian-blogger-sync']) {
        try { marker = JSON.parse(attrs['data-ian-blogger-sync']); } catch { /* Unmanaged post. */ }
      }
      if (name === 'img' && !image) image = attrs.src || '';
      if (name === 'p' && !skipped && !lead) paragraph = true;
    },
    ontext(text) { if (paragraph && !skipped) lead += text; },
    onclosetag(name) {
      if (name === 'p' && paragraph) { paragraph = false; parser.pause(); }
      if (stack.pop()) skipped--;
    },
  });
  parser.end(content || '');
  return { marker, image, lead: lead.replace(/\s+/g, ' ').trim().slice(0, 160) };
}

export function catalog(posts, routes) {
  const used = new Set();
  return posts.map((post) => {
    if (!/^\d+$/.test(String(post.id))) throw new Error('Invalid Blogger post ID');
    const { marker, image, lead } = inspectContent(post.content);
    const source = marker?.repository === config.repository ? marker.source : '';
    if (source && !Object.hasOwn(routes, source)) return null;
    const link = Object.hasOwn(routes, source) ? routes[source] : `/article?id=${post.id}`;
    if (used.has(link)) throw new Error('Duplicate Blogger article route');
    used.add(link);
    return {
      ...post, link, title: String(post.title || ''), lead,
      imageUrl: httpURL(post.images?.[0]?.url || image, post.url || SITE),
      tags: [...new Set((post.labels || []).filter((label) => typeof label === 'string'))],
      dateString: Number.isFinite(Date.parse(post.published)) ? taiwanDate.format(new Date(post.published)) : '',
      readTime: '', category: '',
    };
  }).filter(Boolean).sort((a, b) => String(b.published || '').localeCompare(String(a.published || '')));
}

export function articleBody(post, posts) {
  const prefix = 'blogger-';
  return sanitizeHtml(post.content || '', {
    allowedTags: sanitizeHtml.defaults.allowedTags.concat(['img', 'details', 'summary']),
    allowedAttributes: {
      '*': ['class', 'id', 'role', 'aria-label', 'aria-hidden'],
      a: ['href', 'target', 'rel'],
      img: ['src', 'alt', 'title', 'width', 'height', 'loading'],
      th: ['colspan', 'rowspan', 'scope'], td: ['colspan', 'rowspan'],
      col: ['span'], time: ['datetime'],
    },
    allowedSchemes: ['https', 'http', 'mailto'],
    allowedSchemesByTag: { img: ['https', 'http'] },
    allowProtocolRelative: false,
    transformTags: {
      '*': (tagName, attributes) => {
        const attrs = { ...attributes };
        if (attrs.id) attrs.id = prefix + attrs.id;
        if (attrs.class) attrs.class = attrs.class.split(/\s+/).filter((c) => c !== 'article-container').join(' ');
        if (tagName === 'img') {
          attrs.src = httpURL(attrs.src, post.url || SITE);
          attrs.loading = 'lazy';
        }
        if (tagName === 'a' && attrs.href) {
          if (attrs.href.startsWith('#')) attrs.href = '#' + prefix + attrs.href.slice(1);
          else {
            try {
              const url = new URL(attrs.href, post.url || SITE);
              if ([new URL(SITE).host, 'ian.trainerhub.cc'].includes(url.host)) {
                url.hostname = new URL(SITE).hostname;
                url.protocol = 'https:';
                const linked = posts.find((item) => pathKey(new URL(item.link, SITE).pathname) === pathKey(url.pathname)
                  && new URL(item.link, SITE).search === url.search);
                if (linked) {
                  url.pathname = new URL(linked.link, SITE).pathname;
                  if (url.hash) url.hash = '#' + prefix + url.hash.slice(1);
                }
              }
              attrs.href = url.href;
            } catch { delete attrs.href; }
          }
          attrs.rel = 'noopener noreferrer';
        }
        return { tagName: tagName === 'h1' ? 'h2' : tagName, attribs: attrs };
      },
    },
    exclusiveFilter: (frame) => (frame.attribs.class || '').split(/\s+/)
      .some((c) => ['article-detail-header', 'article-top-nav', 'material-symbols-outlined'].includes(c)),
  });
}

async function load(request, env, ctx) {
  const response = await handleBlogger(new Request(new URL('/api/articles', request.url)), env, ctx);
  if (!response.ok) throw new Error('Blogger unavailable');
  const routesResponse = await env.ASSETS.fetch(new Request(new URL('/article-routes.json', request.url)));
  if (!routesResponse.ok) throw new Error('Article routes unavailable');
  const routes = await routesResponse.json();
  return { posts: catalog((await response.json()).items, routes), routes };
}

export async function articleAPI(request, env, ctx) {
  if (request.method !== 'GET') return new Response(null, { status: 405, headers: { Allow: 'GET' } });
  try {
    const { posts } = await load(request, env, ctx);
    return Response.json({ items: posts }, { headers: { 'Cache-Control': 'no-store' } });
  } catch {
    return Response.json({ error: '文章暫時無法取得，請稍後再試。' }, {
      status: env.BLOGGER_API_KEY ? 502 : 503, headers: { 'Cache-Control': 'no-store' },
    });
  }
}

export function articleSchema(post) {
  const url = new URL(post.link, SITE).href;
  const type = post.tags.some((tag) => /復健/.test(tag)) ? 'MedicalScholarlyArticle'
    : post.tags.some((tag) => ['數位學習', 'AI應用'].includes(tag)) ? 'TechArticle' : 'Article';
  return {
    '@context': 'https://schema.org', '@type': type === 'Article' ? 'Article' : ['Article', type],
    headline: post.title, description: post.lead, url, mainEntityOfPage: url,
    inLanguage: 'zh-TW', datePublished: post.published, dateModified: post.updated || post.published,
    keywords: post.tags,
    ...(post.imageUrl ? { image: post.imageUrl } : {}),
    author: { '@type': 'Person', '@id': SITE + '/#person', name: '蔡泓恩', jobTitle: '職能治療師', url: SITE + '/' },
  };
}

export function cards(posts) {
  return '<div class="articles-grid">' + posts.slice(0, 15).map((post, index) => `
    <article class="article-card ${index === 0 && posts.length > 1 ? 'article-card--featured' : ''}">
      <a class="card-link" href="${escape(post.link)}">
        <div class="article-visual ${post.imageUrl ? '' : 'no-image'}">${post.imageUrl ? `<img src="${escape(post.imageUrl)}" alt="" loading="lazy">` : ''}${index === 0 ? '<span class="featured-badge">最新專題</span>' : ''}</div>
        <div class="article-content">
          <div class="card-tags-row">${post.tags.map((tag) => `<span class="card-tag-pill">${escape(tag)}</span>`).join('')}</div>
          <h2 class="article-title">${escape(post.title)}</h2>
          <div class="article-meta"><time datetime="${escape(post.published)}">${escape(post.dateString)}</time></div>
          <p class="article-excerpt">${escape(post.lead)}</p>
          <div class="article-footer"><span class="read-more-link">閱讀全文</span></div>
        </div>
      </a>
    </article>`).join('') + '</div>';
}

export function sitemap(posts, routes) {
  const urls = new Map(['/', '/blog', '/projects', '/contact', '/sponsor', ...Object.values(routes)]
    .map((path) => [new URL(path, SITE).href, '']));
  for (const post of posts) urls.set(new URL(post.link, SITE).href, post.updated || post.published || '');
  return '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    + [...urls].map(([url, date]) => `<url><loc>${escape(url)}</loc>${date ? `<lastmod>${escape(date)}</lastmod>` : ''}</url>`).join('') + '</urlset>';
}

export function rss(posts) {
  return '<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>蔡泓恩 職能治療師</title>'
    + `<link>${SITE}/blog</link><description>復健與數位學習文章</description><language>zh-TW</language>`
    + posts.map((post) => `<item><title>${escape(post.title)}</title><link>${escape(new URL(post.link, SITE).href)}</link>`
      + `<guid isPermaLink="true">${escape(new URL(post.link, SITE).href)}</guid><description>${escape(post.lead)}</description>`
      + (Number.isFinite(Date.parse(post.published)) ? `<pubDate>${new Date(post.published).toUTCString()}</pubDate>` : '')
      + post.tags.map((tag) => `<category>${escape(tag)}</category>`).join('') + '</item>').join('') + '</channel></rss>';
}

function content(rewriter, selector, value, html = false) {
  return rewriter.on(selector, { element: (element) => element.setInnerContent(value, { html }) });
}

function responseHeaders(response, source) {
  const headers = new Headers(response.headers);
  headers.delete('Content-Length');
  headers.delete('ETag');
  headers.set('X-Article-Source', source);
  headers.set('Cache-Control', response.ok ? 'public, max-age=60' : 'no-store');
  return new Response(response.body, { status: response.status, headers });
}

async function reader(request, env, post, posts, status = 200) {
  const template = await env.ASSETS.fetch(new Request(new URL('/article', request.url)));
  let rewrite = new HTMLRewriter();
  const title = post?.title || (status === 404 ? '找不到這篇文章' : '文章暫時無法取得');
  const description = post?.lead || (status === 404 ? '這篇文章不存在或已移除。' : '請稍後重新整理頁面。');
  rewrite = content(rewrite, 'title', title + ' | 蔡泓恩 職能治療師');
  rewrite = content(rewrite, '#reader-title', title);
  rewrite = content(rewrite, '#reader-body', post ? articleBody(post, posts) : description, Boolean(post));
  rewrite.on('#reader-status', { element: (element) => element.remove() });
  rewrite.on('#blogger-reader', { element: (element) => element.setAttribute('aria-busy', 'false') });
  if (post) {
    const canonical = new URL(post.link, SITE).href;
    rewrite.on('meta[name="robots"]', { element: (element) => element.remove() });
    rewrite.on('link[rel="canonical"]', { element: (element) => element.setAttribute('href', canonical) });
    rewrite.on('meta', { element(element) {
      const name = element.getAttribute('property') || element.getAttribute('name');
      const values = { description, 'og:title': title, 'twitter:title': title,
        'og:description': description, 'twitter:description': description, 'og:url': canonical, 'og:type': 'article',
        'og:image': post.imageUrl || SITE + '/assets/ian-tsai.jpg', 'twitter:image': post.imageUrl || SITE + '/assets/ian-tsai.jpg' };
      if (Object.hasOwn(values, name)) element.setAttribute('content', values[name]);
    } });
    rewrite = content(rewrite, 'script[type="application/ld+json"]', json(articleSchema(post)), true);
    rewrite.on('head', { element: (element) => element.append(
      `<meta property="article:published_time" content="${escape(post.published)}"><meta property="article:modified_time" content="${escape(post.updated || post.published)}">`, { html: true }) });
    rewrite = content(rewrite, '#reader-tags', post.tags.map((tag) => `<a class="article-badge" href="/blog?tag=${encodeURIComponent(tag)}">${escape(tag)}</a>`).join(''), true);
    rewrite = content(rewrite, '#reader-date', post.dateString);
    rewrite.on('#reader-date', { element: (element) => element.setAttribute('datetime', post.published || '') });
  }
  return responseHeaders(rewrite.transform(new Response(template.body, { status, headers: template.headers })), post ? 'blogger' : 'unavailable');
}

export async function articlePage(request, env, ctx) {
  const url = new URL(request.url);
  if (!['GET', 'HEAD'].includes(request.method)) return new Response(null, { status: 405, headers: { Allow: 'GET, HEAD' } });
  const path = pathKey(url.pathname);
  if (['/blog.html', '/article.html'].includes(url.pathname) || (path.startsWith('/content/') && url.pathname.endsWith('.html'))) {
    return Response.redirect(new URL(path + url.search, SITE), 301);
  }
  let data;
  try { data = await load(request, env, ctx); } catch {
    if (path === '/article' || path.startsWith('/content/')) return reader(request, env, null, [], 503);
    if (['/sitemap.xml', '/rss.xml'].includes(url.pathname)) return new Response('Blogger unavailable', {
      status: 503, headers: { 'Cache-Control': 'no-store', 'Retry-After': '300' },
    });
  }
  if (path === '/blog') {
    const template = await env.ASSETS.fetch(new Request(new URL('/blog', request.url)));
    const posts = data?.posts || [];
    const selected = url.searchParams.get('tag');
    const filtered = selected ? posts.filter((post) => post.tags.includes(selected)) : posts;
    let rewrite = content(new HTMLRewriter(), '#article-content', filtered.length ? cards(filtered)
      : `<p class="empty-state">${data ? '目前沒有符合條件的公開文章。' : '文章暫時無法取得，請稍後重新整理。'}</p>`, true);
    rewrite = content(rewrite, '#articles-status', '');
    rewrite = content(rewrite, '#blogger-catalog', json(data ? posts.map(({ content, ...post }) => post) : null), true);
    rewrite.on('#article-content', { element: (element) => element.setAttribute('aria-busy', 'false') });
    return responseHeaders(rewrite.transform(new Response(template.body, { status: data ? 200 : 503, headers: template.headers })), data ? 'blogger' : 'unavailable');
  }
  if (url.pathname === '/sitemap.xml' || url.pathname === '/rss.xml') {
    return new Response(url.pathname === '/sitemap.xml' ? sitemap(data.posts, data.routes) : rss(data.posts), {
      headers: { 'Content-Type': url.pathname === '/sitemap.xml' ? 'application/xml; charset=utf-8' : 'application/rss+xml; charset=utf-8', 'Cache-Control': 'public, max-age=60' },
    });
  }
  const post = data.posts.find((item) => path === '/article' ? item.id === url.searchParams.get('id')
    : pathKey(new URL(item.link, SITE).pathname) === path);
  if (post) {
    const canonical = new URL(post.link, SITE);
    if (url.pathname !== canonical.pathname || url.search !== canonical.search) return Response.redirect(canonical, 301);
    return reader(request, env, post, data.posts);
  }
  // Keep existing URLs working while the throttled initial import is still in progress.
  if (path.startsWith('/content/')) {
    const asset = await env.ASSETS.fetch(request);
    if (!asset.ok) return asset;
    const canonical = new URL(path, SITE).href;
    const rewrite = new HTMLRewriter()
      .on('link[rel="canonical"]', { element: (element) => element.setAttribute('href', canonical) })
      .on('meta[property="og:url"]', { element: (element) => element.setAttribute('content', canonical) });
    return responseHeaders(rewrite.transform(asset), 'legacy-pending-import');
  }
  return reader(request, env, null, [], 404);
}
