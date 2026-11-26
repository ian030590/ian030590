import { icon } from '../src/lib/icons.js';
import { fontLinks } from '../src/lib/fonts.js';
import { Parser } from 'htmlparser2';
import sanitizeHtml from 'sanitize-html';
import config from '../blogger.config.json' with { type: 'json' };
import { handleBlogger } from './blogger.js';

export const SITE = 'https://ian.trainerhub.cc';
export const LEGACY_HOST = 'ian030590.trainerhub.cc';
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
      const skip = ['style', 'script', 'header'].includes(name) || attrs.class?.split(/\s+/).includes('material-symbols-outlined');
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

function replaceIcons(html) {
  let start, name, depth = 0, offset = 0, result = '';
  const parser = new Parser({
    onopentag(tag, attrs) {
      if (depth) depth++;
      else if (tag === 'span' && attrs.class?.split(/\s+/).includes('material-symbols-outlined')) {
        start = parser.startIndex;
        name = '';
        depth = 1;
      }
    },
    ontext(text) { if (depth) name += text; },
    onclosetag() {
      if (depth && --depth === 0) {
        result += html.slice(offset, start) + icon(name.trim());
        offset = parser.endIndex + 1;
      }
    },
  });
  parser.end(html);
  return result + html.slice(offset);
}

export function articleBody(post, posts) {
  const prefix = 'blogger-';
  let hasFeaturedImage = false;
  return sanitizeHtml(replaceIcons(post.content || ''), {
    allowedTags: sanitizeHtml.defaults.allowedTags.concat(['img', 'details', 'summary', 'svg', 'path']),
    allowedAttributes: {
      '*': ['class', 'id', 'role', 'aria-label', 'aria-hidden'],
      svg: ['viewBox', 'width', 'height', 'fill', 'focusable'], path: ['d'],
      a: ['href', 'target', 'rel'],
      img: ['src', 'alt', 'title', 'width', 'height', 'loading', 'fetchpriority'],
      th: ['colspan', 'rowspan', 'scope'], td: ['colspan', 'rowspan'],
      col: ['span'], time: ['datetime'],
    },
    allowedSchemes: ['https', 'http', 'mailto'],
    allowedSchemesByTag: { img: ['https', 'http'] },
    allowProtocolRelative: false,
    transformTags: {
      '*': (tagName, attributes) => {
        if (tagName === 'svg' || tagName === 'path') {
          const allowed = tagName === 'path' ? ['d'] : ['class', 'viewbox', 'width', 'height', 'fill', 'aria-hidden', 'focusable'];
          const attrs = Object.fromEntries(Object.entries(attributes).filter(([key]) => allowed.includes(key))
            .map(([key, value]) => [key === 'viewbox' ? 'viewBox' : key, value]));
          if (attrs.fill !== 'currentColor') delete attrs.fill;
          return { tagName, attribs: attrs };
        }
        const attrs = { ...attributes };
        if (attrs.id) attrs.id = prefix + attrs.id;
        if (attrs.class) attrs.class = attrs.class.split(/\s+/).filter((c) => c !== 'article-container').join(' ');
        if (tagName === 'img') {
          attrs.src = httpURL(attrs.src, post.url || SITE);
          if (!hasFeaturedImage && attrs.class?.split(' ').includes('article-featured-img')) {
            hasFeaturedImage = true;
            attrs.loading = 'eager';
            attrs.fetchpriority = 'high';
          } else {
            attrs.loading = 'lazy';
            delete attrs.fetchpriority;
          }
        }
        if (tagName === 'a' && attrs.href) {
          if (attrs.href.startsWith('#')) attrs.href = '#' + prefix + attrs.href.slice(1);
          else {
            try {
              const url = new URL(attrs.href, post.url || SITE);
              if ([new URL(SITE).host, LEGACY_HOST].includes(url.host)) {
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

async function staticCatalog(request, env) {
  try {
    const asset = await env.ASSETS.fetch(new Request(new URL('/js/articles-data.js', request.url)));
    if (!asset.ok) return null;
    const match = (await asset.text()).match(/window\.__STATIC_ARTICLES__\s*=\s*(\[[\s\S]*\])\s*;?\s*$/);
    if (!match) return null;
    return JSON.parse(match[1]).map((post) => ({
      ...post, link: pathKey(post.link), published: post.dateString,
    })).sort((a, b) => b.dateString.localeCompare(a.dateString));
  } catch { return null; }
}

export async function articleAPI(request, env, ctx) {
  if (request.method !== 'GET') return new Response(null, { status: 405, headers: { Allow: 'GET' } });
  try {
    const { posts } = await load(request, env, ctx);
    return Response.json({ items: posts }, { headers: { 'Cache-Control': 'no-store' } });
  } catch {
    const posts = await staticCatalog(request, env);
    if (posts) return responseHeaders(Response.json({ items: posts }), 'static');
    return Response.json({ error: '文章暫時無法取得，請稍後再試。' }, {
      status: env.BLOGGER_API_KEY ? 502 : 503, headers: { 'Cache-Control': 'no-store' },
    });
  }
}

const tagPath = (tag) => '/blog?tag=' + encodeURIComponent(tag);

function breadcrumbs(tag, title) {
  const trail = [['首頁', SITE + '/'], ['專業文章', SITE + '/blog']];
  if (tag) trail.push([tag, SITE + tagPath(tag)]);
  if (title !== undefined) trail.push([title]);
  return {
    '@type': 'BreadcrumbList',
    itemListElement: trail.map(([name, item], index) => ({
      '@type': 'ListItem', position: index + 1, name, ...(item && { item }),
    })),
  };
}

export function articleSchema(post) {
  const url = new URL(post.link, SITE).href;
  const type = post.tags.some((tag) => /復健/.test(tag)) ? 'MedicalScholarlyArticle'
    : post.tags.some((tag) => ['數位學習', 'AI應用'].includes(tag)) ? 'TechArticle' : 'Article';
  const article = {
    '@type': type === 'Article' ? 'Article' : ['Article', type],
    headline: post.title, description: post.lead, url, mainEntityOfPage: url,
    inLanguage: 'zh-TW', datePublished: post.published, dateModified: post.updated || post.published,
    keywords: post.tags,
    ...(post.imageUrl ? { image: post.imageUrl } : {}),
    author: { '@id': SITE + '/#person', name: '蔡泓恩', jobTitle: '職能治療師' },
    publisher: { '@id': SITE + '/#person' },
    isPartOf: { '@id': SITE + '/#website' },
  };
  return { '@context': 'https://schema.org', '@graph': [article, breadcrumbs(post.tags[0], post.title)] };
}

export function cards(posts) {
  return '<div class="articles-grid">' + posts.map((post, index) => `
    <article class="article-card ${index === 0 && posts.length > 1 ? 'article-card--featured' : ''}">
      <a class="card-link" href="${escape(post.link)}">
        <div class="article-visual ${post.imageUrl ? '' : 'no-image'}">${post.imageUrl ? `<img src="${escape(post.imageUrl)}" alt="" ${index === 0 ? 'loading="eager" fetchpriority="high"' : 'loading="lazy"'}>` : ''}${index === 0 ? '<span class="featured-badge">最新專題</span>' : ''}</div>
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
  const urls = new Map(['/', '/blog', '/projects', '/contact', '/sponsor', '/privacy', '/terms', ...Object.values(routes)]
    .map((path) => [new URL(path, SITE).href, '']));
  for (const post of posts) {
    urls.set(new URL(post.link, SITE).href, post.updated || post.published || '');
    for (const tag of post.tags) {
      if (tag) urls.set(SITE + tagPath(tag), '');
    }
  }
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

function pageMetadata(rewrite, canonical, values) {
  rewrite.on('link[rel="canonical"]', { element: (element) => element.setAttribute('href', canonical) });
  rewrite.on('meta', { element(element) {
    const name = element.getAttribute('property') || element.getAttribute('name');
    if (Object.hasOwn(values, name)) element.setAttribute('content', escape(values[name]));
  } });
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
    const separator = '<span class="breadcrumb-separator" aria-hidden="true">/</span>';
    const firstTag = post.tags[0];
    const tagCrumb = firstTag ? `${separator}<a href="${escape(tagPath(firstTag))}">${escape(firstTag)}</a>` : '';
    rewrite.on('.breadcrumb-trail', { element: (element) => element.append(
      `${tagCrumb}${separator}<span aria-current="page">${escape(title)}</span>`, { html: true }) });
    rewrite.on('#reader-body', { element: (element) => element.after(`
      <section class="article-support" aria-labelledby="article-support-title">
        <h2 id="article-support-title">這篇文章對你有幫助嗎？</h2>
        <a href="https://trainerhub.cc" target="_blank" rel="noopener">TrainerHub 居家練習工具</a>
        <a href="/rss.xml">用 RSS 訂閱新文章</a>
        <a href="https://buymeacoffee.com/ian030590?utm_source=article&amp;utm_medium=inline" target="_blank" rel="noopener">在 Buy Me a Coffee 贊助</a>
      </section>`, { html: true }) });
    rewrite.on('meta[name="robots"]', { element: (element) => element.remove() });
    pageMetadata(rewrite, canonical, { description, 'og:title': title, 'twitter:title': title,
      'og:description': description, 'twitter:description': description, 'og:url': canonical, 'og:type': 'article',
      'og:image': post.imageUrl || SITE + '/assets/ian-tsai.jpg', 'twitter:image': post.imageUrl || SITE + '/assets/ian-tsai.jpg' });
    rewrite = content(rewrite, 'script[type="application/ld+json"]', json(articleSchema(post)), true);
    rewrite.on('head', { element: (element) => element.append(
      `<meta property="article:published_time" content="${escape(post.published)}"><meta property="article:modified_time" content="${escape(post.updated || post.published)}">`, { html: true }) });
    rewrite = content(rewrite, '#reader-tags', post.tags.map((tag) => `<a class="article-badge" href="${escape(tagPath(tag))}">${escape(tag)}</a>`).join(''), true);
    rewrite = content(rewrite, '#reader-date', post.dateString);
    rewrite.on('#reader-date', { element: (element) => element.setAttribute('datetime', post.published || '') });
  }
  return responseHeaders(rewrite.transform(new Response(template.body, { status, headers: template.headers })), post ? 'blogger' : 'unavailable');
}

async function staticArticle(asset, path, source) {
  const canonical = new URL(path, SITE).href;
  const rewrite = new HTMLRewriter()
    .on('style', { element: (element) => element.remove() })
    .on('head', { element: (element) => element.append(fontLinks, { html: true }) })
    .on('link[rel="canonical"]', { element: (element) => element.setAttribute('href', canonical) })
    .on('meta[property="og:url"]', { element: (element) => element.setAttribute('content', canonical) });
  const html = new Response(replaceIcons(await asset.text()), { headers: asset.headers });
  return responseHeaders(rewrite.transform(html), source);
}

export async function articlePage(request, env, ctx) {
  const url = new URL(request.url);
  if (!['GET', 'HEAD'].includes(request.method)) return new Response(null, { status: 405, headers: { Allow: 'GET, HEAD' } });
  const path = pathKey(url.pathname);
  if (['/blog.html', '/article.html'].includes(url.pathname) || (path.startsWith('/content/') && url.pathname.endsWith('.html'))) {
    return Response.redirect(new URL(path + url.search, SITE), 301);
  }
  let data, source = 'blogger';
  try { data = await load(request, env, ctx); } catch {
    source = 'static';
    if (path === '/blog' || path === '/article') {
      const posts = await staticCatalog(request, env);
      if (posts) data = { posts };
      if (path === '/article') {
        if (!url.searchParams.get('id') && posts) return Response.redirect(new URL('/blog', SITE), 302);
        const post = posts?.find((item) => item.id === url.searchParams.get('id'));
        if (post) return Response.redirect(new URL(post.link, SITE), 302);
        return reader(request, env, null, [], 503);
      }
    }
    if (path.startsWith('/content/') || ['/sitemap.xml', '/rss.xml'].includes(path)) {
      const asset = await env.ASSETS.fetch(new Request(request.url)).catch(() => null);
      if (asset?.ok) {
        if (path.startsWith('/content/')) return staticArticle(asset, path, source);
        const headers = new Headers(asset.headers);
        headers.set('Content-Type', path === '/rss.xml' ? 'application/rss+xml; charset=utf-8' : 'application/xml; charset=utf-8');
        return responseHeaders(new Response(asset.body, { headers }), source);
      }
    }
    if (path.startsWith('/content/')) {
      const posts = await staticCatalog(request, env);
      return reader(request, env, null, [], posts ? 404 : 503);
    }
    if (['/sitemap.xml', '/rss.xml'].includes(url.pathname)) return new Response('Blogger unavailable', {
      status: 503, headers: { 'Cache-Control': 'no-store', 'Retry-After': '300' },
    });
  }
  if (path === '/blog') {
    const template = await env.ASSETS.fetch(new Request(new URL('/blog', request.url)));
    const posts = data?.posts || [];
    const selected = url.searchParams.get('tag');
    const filtered = selected ? posts.filter((post) => post.tags.includes(selected)) : posts.slice(0, 15);
    let rewrite = content(new HTMLRewriter(), '#article-content', filtered.length ? cards(filtered)
      : `<p class="empty-state">${data ? '目前沒有符合條件的公開文章。' : '文章暫時無法取得，請稍後重新整理。'}</p>`, true);
    rewrite = content(rewrite, '#articles-status', '');
    rewrite = content(rewrite, '#blogger-catalog', json(data ? posts.map(({ content, ...post }) => post) : null), true);
    if (selected && filtered.length) {
      const canonical = SITE + tagPath(selected);
      const title = selected + ' 文章 | 蔡泓恩 職能治療師';
      const description = `蔡泓恩職能治療師整理的${selected}相關文章，每篇附原始文獻連結。`;
      pageMetadata(rewrite, canonical, { description, 'og:url': canonical, 'og:title': title, 'twitter:title': title,
        'og:description': description, 'twitter:description': description });
      rewrite = content(rewrite, 'title', title);
      rewrite = content(rewrite, '.blog-header .page-title', selected);
      rewrite = content(rewrite, '.blog-header .page-intro', description);
      const collection = { '@type': 'CollectionPage', '@id': canonical + '#collection', url: canonical,
        name: selected, description, inLanguage: 'zh-TW', author: { '@id': SITE + '/#person' }, isPartOf: { '@id': SITE + '/#website' } };
      rewrite = content(rewrite, 'script[type="application/ld+json"]', json({
        '@context': 'https://schema.org', '@graph': [collection, breadcrumbs(selected)],
      }), true);
    } else if (selected !== null && data) {
      rewrite.on('head', { element: (element) => element.append('<meta name="robots" content="noindex,follow">', { html: true }) });
    }
    rewrite.on('#article-content', { element: (element) => element.setAttribute('aria-busy', 'false') });
    return responseHeaders(rewrite.transform(new Response(template.body, { status: data ? 200 : 503, headers: template.headers })), data ? source : 'unavailable');
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
    return staticArticle(asset, path, 'legacy-pending-import');
  }
  return reader(request, env, null, [], 404);
}
