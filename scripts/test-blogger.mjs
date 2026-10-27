import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';
import worker from '../worker/index.js';

const endpoint = 'https://ian030590.trainerhub.cc/api/articles';
const environment = { BLOGGER_API_KEY: 'test-private-key' };
let calls = [];
globalThis.fetch = async (input, init) => {
  const url = new URL(input);
  calls.push(url);
  assert.notEqual(url.searchParams.get('pageToken'), '', 'Google rejects an empty pageToken parameter');
  assert.equal(init.headers['X-Goog-Api-Key'], environment.BLOGGER_API_KEY);
  assert.equal(url.searchParams.get('view'), 'READER');
  assert.ok(!url.searchParams.has('key'), 'Credentials stay out of request URLs');
  return Response.json(url.searchParams.get('pageToken')
    ? { items: [{ id: '2', labels: ['原生標籤'] }] }
    : { items: [{ id: '1' }], nextPageToken: 'next' });
};

let response = await worker.fetch(new Request(endpoint + '?labels=ignored'), environment);
assert.equal(response.status, 200);
assert.equal(calls.length, 2);
assert.deepEqual((await response.json()).items.map((p) => p.id), ['1', '2']);
assert.match(response.headers.get('Cache-Control'), /max-age=300/);

response = await worker.fetch(new Request(endpoint), {});
assert.equal(response.status, 503);
response = await worker.fetch(new Request(endpoint, { method: 'POST' }), environment);
assert.equal(response.status, 405);
for (const status of [403, 429, 500]) {
  calls = [];
  globalThis.fetch = async () => { calls.push(1); return Response.json({}, { status }); };
  response = await worker.fetch(new Request(endpoint), environment);
  assert.equal(response.status, 502);
  assert.equal(calls.length, 1, 'Failed Blogger reads are not hammered with retries');
  assert.ok(!(await response.text()).includes(environment.BLOGGER_API_KEY));
}
globalThis.fetch = async () => Response.json({ items: [], nextPageToken: 'same' });
response = await worker.fetch(new Request(endpoint), environment);
assert.equal(response.status, 502, 'Repeated tokens stop pagination');
globalThis.fetch = async () => Response.json({});
response = await worker.fetch(new Request(endpoint), environment);
assert.deepEqual(await response.json(), { items: [] });

let cachedResponse;
globalThis.caches = { default: {
  match: async () => cachedResponse?.clone(),
  put: async (_, value) => { cachedResponse = value; },
} };
let pending;
await worker.fetch(new Request(endpoint), environment, { waitUntil: (promise) => { pending = promise; } });
await pending;
globalThis.fetch = () => { throw new Error('Cache hit must not call Google'); };
assert.equal((await worker.fetch(new Request(endpoint), environment)).status, 200);
delete globalThis.caches;

const main = readFileSync(new URL('../js/main.js', import.meta.url), 'utf8');
async function loadArticles(items, { offline = false, tag = '' } = {}) {
  const content = { innerHTML: '', setAttribute(key, value) { this[key] = value; },
    querySelectorAll: () => [], querySelector: () => ({ addEventListener() {} }) };
  const status = { textContent: '' };
  const tags = { innerHTML: '', querySelectorAll: () => [] };
  const context = vm.createContext({
    window: { __STATIC_ARTICLES__: [{ title: '本機文章', tags: ['本機標籤'], link: '/content/local.html' }],
      location: { search: tag ? '?tag=' + encodeURIComponent(tag) : '' } },
    URL, URLSearchParams,
    DOMParser: class { parseFromString() { return { querySelectorAll: () => [], querySelector: () => null }; } },
    localStorage: { getItem: () => null },
    document: { documentElement: { setAttribute() {} }, querySelectorAll: () => [], querySelector: () => null,
      getElementById: (id) => ({ 'article-content': content, 'articles-status': status, 'tags-filter-list': tags })[id] || null },
    fetch: async () => { if (offline) throw new Error('Offline'); return { ok: true, json: async () => ({ items }) }; },
  });
  vm.runInContext(main, context);
  await new Promise((resolve) => setImmediate(resolve));
  return { content, status, tags };
}

let page = await loadArticles([{ title: '<img onerror=alert(1)>', url: 'https://blog.example/one',
  published: '2026-10-27T08:00:00+08:00', labels: ['__proto__', 'ALL', '原生標籤'], images: [{ url: 'javascript:alert(1)' }] }]);
assert.match(page.content.innerHTML, /https:\/\/blog.example\/one/);
assert.match(page.content.innerHTML, /&lt;img onerror=alert\(1\)&gt;/);
assert.doesNotMatch(page.content.innerHTML, /javascript:/);
assert.doesNotMatch(page.content.innerHTML, /本機文章/);
assert.match(page.tags.innerHTML, /data-tag="__proto__"/);
assert.equal(page.content['aria-busy'], 'false');
page = await loadArticles([{ title: '原生 ALL 標籤', url: 'https://blog.example/one', labels: ['ALL'] }], { tag: 'ALL' });
assert.match(page.content.innerHTML, /原生 ALL 標籤/);
page = await loadArticles([]);
assert.match(page.content.innerHTML, /目前還沒有公開文章/);
assert.doesNotMatch(page.content.innerHTML, /本機文章/);
page = await loadArticles(null, { offline: true });
assert.match(page.content.innerHTML, /本機文章/);
assert.match(page.status.textContent, /本站保存/);
page = await loadArticles([{ url: 'javascript:alert(1)', title: '危險網址' }]);
assert.match(page.content.innerHTML, /本機文章/);
assert.doesNotMatch(page.content.innerHTML, /javascript:/);
console.log('Blogger checks passed: pagination, cache, failure handling, native labels, empty/offline states and safe card rendering.');
