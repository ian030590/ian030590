import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";

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
  return { grid, status, context };
}

const settle = () => new Promise((resolve) => setImmediate(resolve));
const cardCount = (html) => (html.match(/class="project-card"/g) || []).length;

for (const options of [{ offline: true }, {}]) {
  const page = loadProjects({ ok: false }, options);
  assert.equal(cardCount(page.grid.innerHTML), 12, "Snapshot renders before the request finishes");
  assert.match(page.grid.innerHTML, /OcuTrain/);
  assert.match(page.grid.innerHTML, /RehabTrainerHub/);
  assert.equal((page.grid.innerHTML.match(/>已封存</g) || []).length, 2);
  const saved = page.grid.innerHTML;
  await settle();
  assert.equal(page.grid.innerHTML, saved, "Offline/rate-limited requests preserve saved projects");
  assert.match(page.status.textContent, /2026-10-15/);
}

const records = [];
const live = loadProjects({ ok: true, json: async () => records });
const repo = { ...live.context.window.GITHUB_PROJECTS.repositories[0], name: "NewProject", description: '<script>alert("x")</script>' };
records.push(repo, { ...repo, name: "ian030590" }, { ...repo, name: "MyPortfolio" }, { ...repo, name: "Fork", fork: true }, { ...repo, name: "Private", private: true });
await settle();
assert.equal(cardCount(live.grid.innerHTML), 1, "Latest public, owned projects replace the snapshot");
assert.match(live.grid.innerHTML, /<h2>NewProject<\/h2>/);
assert.match(live.grid.innerHTML, /&lt;script&gt;/);
assert.doesNotMatch(live.grid.innerHTML, /<script>/);
assert.match(live.status.textContent, /已同步/);

const excluded = loadProjects({ ok: true, json: async () => records.slice(1) });
await settle();
assert.equal(cardCount(excluded.grid.innerHTML), 0, "Excluded repositories never reappear as a fallback");
assert.match(excluded.grid.innerHTML, /尚無/);

const malformed = loadProjects({ ok: true, json: async () => ({ message: "Unexpected response" }) });
await settle();
assert.equal(cardCount(malformed.grid.innerHTML), 12);

const noSnapshot = loadProjects(null, { offline: true, withSnapshot: false });
await settle();
assert.match(noSnapshot.grid.innerHTML, /github.com\/ian030590\?tab=repositories/);
assert.match(noSnapshot.status.textContent, /無法更新/);

console.log("Project checks passed: immediate snapshot, live refresh, archived labels, filtering, escaping, and network/API failures.");
