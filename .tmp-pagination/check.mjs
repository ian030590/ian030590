import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { readFileSync, existsSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';

const articles = JSON.parse(readFileSync('.generated/articles.json', 'utf8'))
  .sort((a, b) => b.dateString.localeCompare(a.dateString));
const html = readFileSync('dist/blog.html', 'utf8');
assert.equal((html.match(/class="article-card(?: |")/g) || []).length, 15);
const browser = spawn('C:/Users/ian/AppData/Local/ms-playwright/chromium-1243/chrome-win64/chrome.exe', [
  '--headless=new', '--disable-gpu', '--no-sandbox', '--in-process-gpu', '--disable-features=NetworkServiceSandbox', '--no-first-run', '--disable-background-networking',
  '--remote-debugging-port=9225', `--user-data-dir=${resolve('.tmp-pagination/profile')}`, 'about:blank',
], { stdio: 'ignore', windowsHide: true });
const delay = (ms) => new Promise((done) => setTimeout(done, ms));
let socket;
try {
  let targets;
  for (let attempt = 0; attempt < 100; attempt++) {
    try { targets = await (await fetch('http://127.0.0.1:9225/json')).json(); break; }
    catch { await delay(100); }
  }
  assert.ok(targets, 'Chromium starts');
  socket = new WebSocket(targets.find((target) => target.type === 'page').webSocketDebuggerUrl);
  await new Promise((done, reject) => { socket.onopen = done; socket.onerror = reject; });
  let sequence = 0;
  const pending = new Map();
  const errors = [];
  socket.onclose = event => { for (const task of pending.values()) task.reject(new Error(`Socket closed: ${event.code} ${event.reason}`)); };
  socket.onmessage = ({ data }) => {
    const message = JSON.parse(data);
    if (message.method === 'Runtime.exceptionThrown') errors.push(message.params.exceptionDetails);
    if (!message.id) return;
    const task = pending.get(message.id);
    pending.delete(message.id);
    if (message.error) task.reject(new Error(JSON.stringify(message.error)));
    else task.done(message.result);
  };
  const send = (method, params = {}) => new Promise((done, reject) => {
    const id = ++sequence;
    pending.set(id, { done, reject });
    socket.send(JSON.stringify({ id, method, params }));
  });
  const evaluate = async (expression) => {
    const result = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
    if (result.exceptionDetails) throw new Error(JSON.stringify(result.exceptionDetails));
    return result.result.value;
  };
  await send('Page.enable');
  await send('Runtime.enable');
  await send('Network.enable');
  await send('Network.setBlockedURLs', { urls: ['https://images.unsplash.com/*'] });
  const load = async (query = '') => {
    await send('Page.navigate', { url: `http://127.0.0.1:8765/blog.html${query}` });
    for (let attempt = 0; attempt < 100; attempt++) {
      if (await evaluate('!!document.querySelector(".article-pagination, .reset-filter-btn")')) return;
      await delay(50);
    }
    throw new Error('Article list did not initialize');
  };
  const snapshot = () => evaluate(`({
    titles: [...document.querySelectorAll('.article-title')].map(node => node.textContent),
    links: [...document.querySelectorAll('.article-card .card-link')].map(node => node.getAttribute('href')),
    status: document.querySelector('.article-page-status')?.textContent,
    current: document.querySelector('.pagination-button[aria-current="page"]')?.textContent,
    featured: document.querySelectorAll('.article-card--featured').length,
    previousDisabled: document.querySelector('.pagination-button')?.disabled,
    nextDisabled: document.querySelector('.pagination-button:last-child')?.disabled,
    overflow: document.documentElement.scrollWidth > innerWidth,
    focus: document.activeElement.id
  })`);
  const click = (selector) => evaluate(`document.querySelector(${JSON.stringify(selector)}).click()`);
  const search = (value) => evaluate(`(() => { const input = document.querySelector('#blog-search'); input.value = ${JSON.stringify(value)}; input.dispatchEvent(new Event('input', { bubbles: true })); })()`);
  const checkPage = async (expected, page = 1) => {
    const state = await snapshot();
    const start = (page - 1) * 15;
    assert.deepEqual(state.titles, expected.slice(start, start + 15).map(article => article.title));
    assert.equal(state.status, `第 ${start + 1} 至 ${Math.min(start + 15, expected.length)} 篇，共 ${expected.length} 篇`);
    assert.ok(state.titles.length <= 15);
    if (expected.length > 15) assert.equal(state.current, String(page));
    for (const link of state.links) assert.ok(existsSync(resolve('dist', decodeURIComponent(link).replace(/^\//, ''))));
    return state;
  };

  await load();
  assert.equal((await checkPage(articles)).featured, 1);
  assert.equal((await snapshot()).previousDisabled, true);
  const seen = [...(await snapshot()).titles];
  await click('[aria-label="第 2 頁"]');
  assert.equal((await checkPage(articles, 2)).featured, 0);
  assert.equal((await snapshot()).focus, 'article-content');
  seen.push(...(await snapshot()).titles);
  await click('.pagination-button:last-child');
  assert.equal((await checkPage(articles, 3)).nextDisabled, true);
  seen.push(...(await snapshot()).titles);
  assert.equal(new Set(seen).size, articles.length);
  await click('.pagination-button');
  await checkPage(articles, 2);

  const matches = articles.filter(article => [article.title, article.lead, ...article.tags].some(text => text.toLowerCase().includes('復健')));
  await search('復健');
  await checkPage(matches);
  await click('[aria-label="第 2 頁"]');
  await checkPage(matches, 2);
  await click('#clear-search-btn');
  await checkPage(articles);
  await click('[aria-label="第 2 頁"]');
  await click('[data-quick-tag="中風復健"]');
  const stroke = articles.filter(article => article.tags.includes('中風復健'));
  await checkPage(stroke);
  await click('#clear-filter-btn');
  await checkPage(articles);
  await click('[aria-label="第 2 頁"]');
  await click('.tag-filter-btn[data-tag="視覺復健"]');
  await checkPage(articles.filter(article => article.tags.includes('視覺復健')));
  await search('no-matching-article-123456');
  assert.equal((await snapshot()).titles.length, 0);
  assert.equal(await evaluate('document.querySelector(".article-pagination")'), null);
  await click('.reset-filter-btn');
  await checkPage(articles);
  await click('[aria-label="第 2 頁"]');
  const cardTag = await evaluate('document.querySelector("[data-card-tag]").dataset.cardTag');
  await click('[data-card-tag]');
  await checkPage(articles.filter(article => article.tags.includes(cardTag)));
  await load('?tag=' + encodeURIComponent('AI應用'));
  await checkPage(articles.filter(article => article.tags.includes('AI應用')));

  await load();
  await evaluate('document.fonts.ready.then(() => true)');
  for (const theme of ['light', 'dark']) {
    await evaluate(`document.documentElement.dataset.theme = '${theme}'`);
    for (const width of [320, 375, 768, 1024, 1440]) {
      await send('Emulation.setDeviceMetricsOverride', { width, height: 900, deviceScaleFactor: 1, mobile: false });
      assert.equal(await evaluate(`(() => { const nav = document.querySelector('.article-pagination'); return nav.scrollWidth <= nav.clientWidth && [...nav.querySelectorAll('button')].every(button => { const box = button.getBoundingClientRect(); return box.left >= 0 && box.right <= innerWidth; }); })()`), true, `${theme} ${width}px pagination has no horizontal overflow`);
      assert.equal(await evaluate(`[...document.querySelectorAll('.pagination-button')].every(button => {const rect = button.getBoundingClientRect(); return rect.width >= 44 && rect.height >= 44;})`), true);
      if (width === 375 || width === 1024) {
        await evaluate('document.querySelector(".article-pagination").scrollIntoView({ block: "center", behavior: "instant" })');
        await delay(100);
        const shot = await send('Page.captureScreenshot', { format: 'png' });
        writeFileSync(`.tmp-pagination/${theme}-${width}.png`, Buffer.from(shot.data, 'base64'));
      }
    }
  }
  await send('Page.bringToFront');
  await evaluate('document.querySelector(\'[aria-label="第 1 頁"]\').focus()');
  await send('Input.dispatchKeyEvent', { type: 'keyDown', key: 'Tab', code: 'Tab', windowsVirtualKeyCode: 9 });
  await send('Input.dispatchKeyEvent', { type: 'keyUp', key: 'Tab', code: 'Tab', windowsVirtualKeyCode: 9 });
  assert.equal(await evaluate('document.activeElement.getAttribute("aria-label")'), '第 2 頁');
  assert.equal(await evaluate('getComputedStyle(document.activeElement).outlineStyle'), 'solid');
  await send('Input.dispatchKeyEvent', { type: 'keyDown', key: 'Enter', code: 'Enter', windowsVirtualKeyCode: 13, nativeVirtualKeyCode: 13, text: '\r', unmodifiedText: '\r' });
  await send('Input.dispatchKeyEvent', { type: 'keyUp', key: 'Enter', code: 'Enter', windowsVirtualKeyCode: 13 });
  await delay(100);
  await checkPage(articles, 2);
  const main = readFileSync('js/main.js', 'utf8');
  for (const count of [1, 15, 16, 30, 31]) {
    const subset = articles.slice(0, count);
    await evaluate(`document.body.innerHTML = '<div id="article-content" role="region" aria-label="文章列表" tabindex="-1"></div>'; window.__STATIC_ARTICLES__ = ${JSON.stringify(subset)}; (0, eval)(${JSON.stringify(main)});`);
    await checkPage(subset);
    const pages = Math.ceil(count / 15);
    if (pages === 1) assert.equal(await evaluate('document.querySelectorAll(".pagination-button").length'), 0);
    else {
      await click(`[aria-label="第 ${pages} 頁"]`);
      assert.equal((await checkPage(subset, pages)).nextDisabled, true);
    }
  }
  assert.deepEqual(errors, []);
  console.log('PASS: static HTML 15 cards; pages 15/15/11; no missing or duplicate articles; 1/15/16/30/31 article boundaries; previous/next/page buttons; search/tag/reset transitions; initial tag; keyboard activation/focus; pagination at 320–1440px in light/dark themes; 44px targets; no runtime errors.');
} finally {
  if (socket) socket.close();
  browser.kill();
}
