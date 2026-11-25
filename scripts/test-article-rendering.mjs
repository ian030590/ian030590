import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { Miniflare, convertV4MiniflareOptions } from 'miniflare';
import { rolldown } from 'rolldown';
import { unstable_readConfig as readWranglerConfig } from 'wrangler';
import { articleBody, articleSchema, catalog, cards, sitemap, rss, articlePage, SITE } from '../worker/articles.js';
import worker from '../worker/index.js';

const route = '/content/VisualRehab/001_視覺復健';
const routes = { VisualRehab_001: route };
const marker = JSON.stringify({ repository: 'ian030590/ian030590', source: 'VisualRehab_001' });
const post = { id: '123', title: '復健 & <標題>', published: '2026-10-27T08:00:00+08:00',
  updated: '2026-10-27T09:00:00+08:00', labels: ['視覺復健', 'Blogger 自訂標籤'],
  url: 'https://blog.example/2026/10/post.html',
  content: `<style>body {display:none}</style><div data-ian-blogger-sync='${marker}'>
    <div class="article-container"><header class="article-detail-header"><p>舊日期</p></header>
    <img src="https://images.example/one.jpg" onerror="alert(1)"><p>真正的文章摘要。</p>
    <h2 id="references">參考文獻</h2><a href="#references">查看引用</a>
    <a href="https://doi.org/10.1000/test" target="_blank">正式 DOI</a>
    <script>alert(1)</script><iframe src="https://evil.example"></iframe><form><input name="reader-title"></form>
    <a href="javascript:alert(1)">危險網址</a></div></div>` };
const posts = catalog([post, { id: '456', title: '原生文章', labels: ['ALL'], content: '<p>原生內容</p>' }], routes);
assert.equal(posts[0].link, route);
assert.equal(posts[0].lead, '真正的文章摘要。');
assert.equal(posts[0].imageUrl, 'https://images.example/one.jpg');
assert.equal(catalog([{ ...post, published: '2026-10-26T17:00:00-07:00' }], routes)[0].dateString, '2026-10-27');
assert.deepEqual(posts[0].tags, ['視覺復健', 'Blogger 自訂標籤']);
assert.equal(posts[1].link, '/article?id=456');
assert.equal(posts[1].imageUrl, '');
const doubleQuoted = post.content.replace(`'${marker}'`, '"' + marker.replaceAll('"', '&quot;') + '"');
assert.equal(catalog([{ ...post, content: doubleQuoted }], routes)[0].link, route);
assert.throws(() => catalog([post, post], routes), /Duplicate/);
assert.throws(() => catalog([{ id: 'bad' }], routes), /Invalid/);
assert.deepEqual(catalog([post], {}), [], 'Withdrawn Git sources stay hidden while the trash operation is queued');
const body = articleBody(posts[0], posts);
assert.doesNotMatch(body, /<script|<style|<iframe|<form|<input|onerror|javascript:|display:none|舊日期|class="article-container"/);
assert.match(body, /id="blogger-references"/);
assert.match(body, /href="#blogger-references"/);
assert.match(body, /href="https:\/\/doi.org\/10.1000\/test" target="_blank" rel="noopener noreferrer"/);
const schema = articleSchema(posts[0]);
const [article, trail] = schema['@graph'];
assert.equal(schema['@context'], 'https://schema.org');
assert.equal(article.mainEntityOfPage, new URL(route, SITE).href);
assert.deepEqual(article['@type'], ['Article', 'MedicalScholarlyArticle']);
assert.equal(article.dateModified, post.updated);
assert.equal(article.author['@id'], SITE + '/#person');
assert.deepEqual(article.publisher, { '@id': SITE + '/#person' });
assert.deepEqual(article.isPartOf, { '@id': SITE + '/#website' });
const tagPath = '/blog?tag=' + encodeURIComponent(post.labels[0]);
assert.equal(trail['@type'], 'BreadcrumbList');
assert.deepEqual(trail.itemListElement, [
  { '@type': 'ListItem', position: 1, name: '首頁', item: SITE + '/' },
  { '@type': 'ListItem', position: 2, name: '專業文章', item: SITE + '/blog' },
  { '@type': 'ListItem', position: 3, name: post.labels[0], item: SITE + tagPath },
  { '@type': 'ListItem', position: 4, name: post.title },
]);
assert.equal(articleSchema({ ...posts[0], tags: [] })['@graph'][1].itemListElement[2].name, post.title);
assert.match(cards(posts), /復健 &amp; &lt;標題&gt;/);
for (const xml of [sitemap(posts, routes), rss(posts)]) {
  assert.doesNotMatch(xml, /blog\.example|\/article\?id=123|001_視覺復健\.html/);
  assert.ok(xml.includes(new URL(route, SITE).href));
  assert.match(xml, /\/article\?id=456/);
}
assert.equal((sitemap(posts, routes).match(/001_%E8%A6%96/g) || []).length, 1);
for (const tag of posts.flatMap((post) => post.tags)) {
  assert.ok(sitemap(posts, routes).includes('<loc>' + SITE + '/blog?tag=' + encodeURIComponent(tag) + '</loc>'));
}
for (const path of ['/projects', '/api/contact?next=one%2Ftwo', '//path.example/to?x=1&x=2']) {
  const response = await worker.fetch(new Request('http://ian.trainerhub.cc' + path), {});
  assert.equal(response.status, 301);
  assert.equal(response.headers.get('location'), SITE + path);
}
const routing = readWranglerConfig({ config: 'wrangler.jsonc' }).assets.run_worker_first;
assert.deepEqual(new Set(routing), new Set(['/*', '!/css/*', '!/js/*', '!/icons/*', '!/assets/*', '!/_astro/*', '!/favicon.ico']));
const alias = await articlePage(new Request(SITE + route + '.html'), {});
assert.equal(alias.status, 301);
assert.equal(alias.headers.get('Location'), new URL(route, SITE).href);
const originalFetch = globalThis.fetch;
globalThis.fetch = async () => Response.json({ items: [post] });
const env = { BLOGGER_API_KEY: 'test-key', ASSETS: { fetch: async () => Response.json(routes) } };
const oldReader = await articlePage(new Request(SITE + '/article?id=123'), env);
assert.equal(oldReader.status, 301);
assert.equal(oldReader.headers.get('Location'), new URL(route, SITE).href);
globalThis.fetch = originalFetch;

// Exercise the Workers HTMLRewriter against the page bodies before Astro's build step.
function template(page) {
  const source = readFileSync(new URL('../src/pages/' + page + '.astro', import.meta.url), 'utf8');
  return new Response(`<html><head><title></title><link rel="canonical" href="${SITE}/${page}">
    <meta property="og:url" content="${SITE}/${page}"><meta name="description" content=""><script type="application/ld+json">{}</script>
    </head><body>${source.split('---').at(-1)}</body></html>`, { headers: { 'Content-Type': 'text/html' } });
}
const extraPosts = Array.from({ length: 16 }, (_, i) => ({
  id: String(1000 + i), title: '同標籤文章 ' + i, labels: [post.labels[0]], content: '<p>摘要</p>',
}));
const literalTag = '視覺 &amp; <復健> "A"';
const bundle = await rolldown({ input: 'worker/index.js', platform: 'browser', external: [/^node:/] });
const { output } = await bundle.generate({ format: 'esm' });
await bundle.close();
const runtime = new Miniflare(convertV4MiniflareOptions({
  modules: true, script: output[0].code, cf: false, compatibilityDate: '2026-10-19', compatibilityFlags: ['nodejs_compat'],
  bindings: { BLOGGER_API_KEY: 'test-key' },
  outboundService: () => Response.json({ items: [post, ...extraPosts, { id: '456', title: '其他文章' },
    { id: '457', title: '標籤測試', labels: [literalTag] }] }),
  serviceBindings: { ASSETS: (request) => {
    const path = new URL(request.url).pathname;
    if (path === '/article-routes.json') return Response.json(routes);
    assert.ok(['/blog', '/article'].includes(path));
    return template(path.slice(1));
  } },
}));
try {
  async function render(path, status = 200) {
    const response = await runtime.dispatchFetch(SITE + path, { redirect: 'manual' });
    assert.equal(response.status, status);
    return response.text();
  }
  const tagged = await render(tagPath + '&tracking=1');
  assert.ok(tagged.includes(`<link rel="canonical" href="${SITE + tagPath}">`));
  assert.ok(tagged.includes(`<meta property="og:url" content="${SITE + tagPath}">`));
  assert.ok(tagged.includes(`<title>${post.labels[0]} 文章 | 蔡泓恩 職能治療師</title>`));
  const intro = '蔡泓恩職能治療師整理的視覺復健相關文章，每篇附原始文獻連結。';
  assert.ok(tagged.includes(`<h1 class="page-title">${post.labels[0]}</h1>`));
  assert.ok(tagged.includes(`<p class="page-intro">${intro}</p>`));
  assert.ok(tagged.includes(`<meta name="description" content="${intro}">`));
  assert.equal((tagged.match(/class="card-link"/g) || []).length, 17);
  assert.ok(!tagged.includes('href="/article?id=456"'));
  const renderedGraph = (html) => JSON.parse(html.match(/<script type="application\/ld\+json">(.+?)<\/script>/s)[1])['@graph'];
  assert.equal(renderedGraph(tagged).find((node) => node['@type'] === 'CollectionPage').description, intro);
  assert.deepEqual(renderedGraph(tagged).find((node) => node['@type'] === 'BreadcrumbList').itemListElement,
    trail.itemListElement.slice(0, 3));
  const blog = await render('/blog');
  assert.equal((blog.match(/class="card-link"/g) || []).length, 15);
  assert.doesNotMatch(blog, /noindex/);
  const unknown = await render('/blog?tag=missing');
  assert.ok(unknown.includes(`<link rel="canonical" href="${SITE}/blog">`));
  assert.match(unknown, /<meta name="robots" content="noindex,follow">/);
  assert.doesNotMatch(unknown, /class="card-link"/);
  const xml = await render('/sitemap.xml');
  assert.equal(xml.split('<loc>' + SITE + tagPath + '</loc>').length, 2);
  const reader = await render(route);
  assert.deepEqual(renderedGraph(reader), schema['@graph']);
  const crumb = (html) => html.match(/<nav class="breadcrumb-trail"[^>]*>([\s\S]*?)<\/nav>/)[1];
  const separator = '<span class="breadcrumb-separator" aria-hidden="true">/</span>';
  assert.equal(crumb(reader).replace(/>\s+</g, '><').trim(), [
    '<a href="/">首頁</a>', '<a href="/blog">專業文章</a>', `<a href="${tagPath}">視覺復健</a>`,
    '<span aria-current="page">復健 &amp; &lt;標題&gt;</span>',
  ].join(separator));
  const untagged = crumb(await render('/article?id=456'));
  assert.doesNotMatch(untagged, /\?tag=/);
  assert.ok(untagged.includes('<span aria-current="page">其他文章</span>'));
  const literalPath = '/blog?tag=' + encodeURIComponent(literalTag);
  const literalHub = await render(literalPath);
  assert.ok(literalHub.includes('content="蔡泓恩職能治療師整理的視覺 &amp;amp; &lt;復健&gt; &quot;A&quot;相關文章，每篇附原始文獻連結。"'));
  assert.ok(crumb(await render('/article?id=457')).includes(`<a href="${literalPath}">視覺 &amp;amp; &lt;復健&gt; &quot;A&quot;</a>`));
  const support = reader.match(/<section class="article-support" aria-labelledby="article-support-title">([\s\S]*?)<\/section>/)[1];
  assert.ok(support.includes('<h2 id="article-support-title">這篇文章對你有幫助嗎？</h2>'));
  assert.deepEqual(support.match(/<a [^>]+>[^<]+<\/a>/g), [
    '<a href="https://trainerhub.cc" target="_blank" rel="noopener">TrainerHub 居家練習工具</a>',
    '<a href="/rss.xml">用 RSS 訂閱新文章</a>',
    '<a href="https://buymeacoffee.com/ian030590?utm_source=article&amp;utm_medium=inline" target="_blank" rel="noopener">在 Buy Me a Coffee 贊助</a>',
  ]);
  assert.match(reader, /id="reader-body"[\s\S]*?<\/div>\s*<section class="article-support"/);
  assert.match(reader, /<\/section>\s*<div class="article-bottom-actions"/);
  assert.doesNotMatch(await render('/article?id=999', 404), /class="article-support"/);
} finally {
  await runtime.dispose();
}
console.log('Article rendering checks passed: redirects, Blogger routes, sanitized content, tag hubs, schema and feeds.');
