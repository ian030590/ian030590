import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";
import { DomUtils, parseDocument } from "htmlparser2";

const main = readFileSync(new URL("../js/main.js", import.meta.url), "utf8");
const snapshot = readFileSync(new URL("../js/projects-data.js", import.meta.url), "utf8");

function loadProjects(response, { offline = false, withSnapshot = true } = {}) {
  const grid = { innerHTML: "" };
  const status = { textContent: "" };
  const context = vm.createContext({
    window: {},
    localStorage: { getItem: () => null },
    document: {
      documentElement: { setAttribute() {} },
      querySelectorAll: () => [],
      querySelector: () => null,
      getElementById: (id) => ({ "projects-grid": grid, "projects-status": status })[id] || null,
    },
    fetch: (url) => {
      assert.match(url, /type=owner/);
      return offline ? Promise.reject(new Error("Offline")) : Promise.resolve(response);
    },
  });
  if (withSnapshot) vm.runInContext(snapshot, context);
  vm.runInContext(main, context);
  return { grid, status };
}

const settle = () => new Promise((resolve) => setImmediate(resolve));
const children = (node) => node.children.filter((child) => child.type === "tag");

function projectIndex(html) {
  assert.doesNotMatch(html, /opengraph\.githubassets\.com|<img\b|\bonerror=|class="tags"/i);
  const headingIds = new Set();
  return children(parseDocument(html)).map((section) => {
    assert.equal(section.name, "section");
    const [heading, list] = children(section);
    assert.equal(heading.name, "h2");
    assert.ok(heading.attribs.id);
    assert.equal(section.attribs["aria-labelledby"], heading.attribs.id);
    assert.ok(!headingIds.has(heading.attribs.id));
    headingIds.add(heading.attribs.id);
    assert.equal(list.name, "ul");
    const items = children(list);
    assert.ok(items.length, "Empty groups are omitted");
    const names = items.map((item) => {
      assert.equal(item.name, "li");
      const links = DomUtils.getElementsByTagName("a", item);
      assert.equal(links.length, 1);
      const [link] = links;
      assert.deepEqual(children(item), [link]);
      assert.match(link.attribs.href, /^https:\/\/github\.com\//);
      assert.equal(link.attribs.target, "_blank");
      assert.equal(link.attribs.rel, "noopener noreferrer");
      const [name] = children(link);
      assert.equal(name.name, "h3");
      const [updated] = DomUtils.getElementsByTagName("time", link);
      assert.ok(updated.attribs.datetime);
      assert.match(DomUtils.textContent(updated), /^更新於 \d/);
      assert.match(DomUtils.textContent(link), /在 GitHub 查看/);
      return DomUtils.textContent(name);
    });
    return [DomUtils.textContent(heading), names];
  });
}

const snapshotIndex = [
  ["視覺與復健練習", ["RehabTrainerHub", "OcuTrain", "OcuDrive", "FlyingMoo"]],
  ["臨床與研究流程", ["EzEMR", "NTUHNotifier", "NTUHNotifier2"]],
  ["文件與日常工具", ["FormatConverter", "PDFCombiner", "PDFSeparater", "PDFDecrypter", "EzReceipt", "ZhBible"]],
  ["開發工具與其他", ["ClaudeBrainCodexHands"]],
  ["已封存作品", ["StrokeTrainer", "VisionTrainer"]],
];

for (const options of [{ offline: true }, {}]) {
  const page = loadProjects({ ok: false }, options);
  assert.deepEqual(projectIndex(page.grid.innerHTML), snapshotIndex, "Snapshot renders in clinical order before the request finishes");
  assert.equal((page.grid.innerHTML.match(/>已封存</g) || []).length, 2);
  assert.match(page.status.textContent, /2026-11-09/);
  const saved = page.grid.innerHTML;
  await settle();
  assert.equal(page.grid.innerHTML, saved, "Offline/rate-limited requests preserve saved projects");
  assert.match(page.status.textContent, /2026-11-09/);
}

const repo = (name, fields = {}) => ({
  name,
  html_url: `https://github.com/ian030590/${encodeURIComponent(name)}`,
  updated_at: "2026-11-09T05:40:11Z",
  stargazers_count: 0,
  topics: ["unused-topic"],
  ...fields,
});
const hostileName = '<b>New & "Unsafe"</b>';
const excludedRepos = [
  repo("IAN030590"),
  repo("MyPortfolio"),
  repo("Fork", { fork: true, archived: true }),
  repo("Private", { private: true }),
];
const records = [
  repo(hostileName, { description: '<script>alert("x")</script>', stargazers_count: 3 }),
  repo("FlyingMoo", { description: "中文保留 / " }),
  repo("NTUHNotifier2"),
  repo("OcuTrain", { archived: true }),
  repo("OcuDrive", { description: "English first / 中文在後" }),
  repo("EzStorage", { description: null }),
  repo("NewerProject", { updated_at: "2026-11-10T05:40:11Z" }),
  repo("ClaudeBrainCodexHands", { updated_at: "2026-11-01T05:40:11Z" }),
  repo("EzEMR", { description: "臨床工具 /  / English detail" }),
  repo("rEHABtRAINERhUB", { description: "中文說明 / English summary" }),
  repo("NTUHNotifier"),
  ...excludedRepos,
];
const live = loadProjects({ ok: true, json: async () => records });
await settle();
assert.deepEqual(projectIndex(live.grid.innerHTML), [
  ["視覺與復健練習", ["rEHABtRAINERhUB", "OcuDrive", "FlyingMoo"]],
  ["臨床與研究流程", ["EzEMR", "EzStorage", "NTUHNotifier", "NTUHNotifier2"]],
  ["開發工具與其他", ["ClaudeBrainCodexHands", "NewerProject", hostileName]],
  ["已封存作品", ["OcuTrain"]],
]);
assert.match(live.grid.innerHTML, /<p>中文說明<\/p>/);
assert.match(live.grid.innerHTML, /<p>臨床工具<\/p>/);
assert.match(live.grid.innerHTML, /<p>English first \/ 中文在後<\/p>/);
assert.match(live.grid.innerHTML, /<p>中文保留 \/ <\/p>/);
assert.match(live.grid.innerHTML, /<h3>EzStorage<\/h3>\s*<div class="project-meta">/);
assert.match(live.grid.innerHTML, /&lt;b&gt;New &amp; &quot;Unsafe&quot;&lt;\/b&gt;/);
assert.match(live.grid.innerHTML, /&lt;script&gt;alert\(&quot;x&quot;\)&lt;\/script&gt;/);
assert.doesNotMatch(live.grid.innerHTML, /<script>|<b>|English summary|unused-topic/);
assert.deepEqual(live.grid.innerHTML.match(/\d+ 顆星/g), ["3 顆星"]);
assert.equal((live.grid.innerHTML.match(/>已封存</g) || []).length, 1);
assert.match(live.status.textContent, /已同步/);

const excluded = loadProjects({ ok: true, json: async () => excludedRepos });
await settle();
assert.doesNotMatch(excluded.grid.innerHTML, /<section\b|<h3>/);
assert.match(excluded.grid.innerHTML, /尚無/);

const malformed = loadProjects({ ok: true, json: async () => ({ message: "Unexpected response" }) });
await settle();
assert.deepEqual(projectIndex(malformed.grid.innerHTML), snapshotIndex);

const noSnapshot = loadProjects(null, { offline: true, withSnapshot: false });
await settle();
assert.match(noSnapshot.grid.innerHTML, /github.com\/ian030590\?tab=repositories/);
assert.match(noSnapshot.status.textContent, /無法更新/);

console.log("Project checks passed: snapshot and live group order, archived override, new repositories, description parsing, escaping, filtering, and network/API failures.");
