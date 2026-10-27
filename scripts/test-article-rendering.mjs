import assert from 'node:assert/strict';
import { articleBody, articleSchema, catalog, cards, sitemap, rss, articlePage, SITE } from '../worker/articles.js';

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
assert.equal(schema.mainEntityOfPage, new URL(route, SITE).href);
assert.deepEqual(schema['@type'], ['Article', 'MedicalScholarlyArticle']);
assert.equal(schema.dateModified, post.updated);
assert.match(cards(posts), /復健 &amp; &lt;標題&gt;/);
for (const xml of [sitemap(posts, routes), rss(posts)]) {
  assert.doesNotMatch(xml, /blog\.example|\/article\?id=123|001_視覺復健\.html/);
  assert.ok(xml.includes(new URL(route, SITE).href));
  assert.match(xml, /\/article\?id=456/);
}
assert.equal((sitemap(posts, routes).match(/001_%E8%A6%96/g) || []).length, 1);
const alias = await articlePage(new Request(SITE + route + '.html'), {});
assert.equal(alias.status, 301);
assert.equal(alias.headers.get('Location'), new URL(route, SITE).href);
globalThis.fetch = async () => Response.json({ items: [post] });
const env = { BLOGGER_API_KEY: 'test-key', ASSETS: { fetch: async () => Response.json(routes) } };
const oldReader = await articlePage(new Request(SITE + '/article?id=123'), env);
assert.equal(oldReader.status, 301);
assert.equal(oldReader.headers.get('Location'), new URL(route, SITE).href);
console.log('Article rendering checks passed: Blogger route markers, sanitization, native labels, canonical redirects, schema and feeds.');
