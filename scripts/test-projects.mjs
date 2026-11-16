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
const cardLabels = (html) => Array.from(
  html.matchAll(/<div class="tags">([\s\S]*?)<\/div>/g),
  ([, tags]) => Array.from(tags.matchAll(/<span class="tag">(.*?)<\/span>/g), ([, label]) => label),
);

for (const options of [{ offline: true }, {}]) {
  const page = loadProjects({ ok: false }, options);
  assert.equal(cardCount(page.grid.innerHTML), 16, "Snapshot renders before the request finishes");
  assert.match(page.grid.innerHTML, /OcuTrain/);
  assert.match(page.grid.innerHTML, /RehabTrainerHub/);
  assert.doesNotMatch(page.grid.innerHTML, /ResearchAssistant|<h2>ian030590<\/h2>/);
  assert.equal((page.grid.innerHTML.match(/>已封存</g) || []).length, 2);
  const repositories = Array.from(page.context.window.GITHUB_PROJECTS.repositories);
  assert.equal(repositories.length, 17);
  assert.deepEqual(
    cardLabels(page.grid.innerHTML),
    repositories.filter((repo) => repo.name !== "ian030590")
      .map((repo) => [...(repo.archived ? ["已封存"] : []), ...repo.topics]),
    "Snapshot cards show each repository's topics in order, after its archived status",
  );
  assert.match(page.status.textContent, /2026-11-09/);
  const saved = page.grid.innerHTML;
  await settle();
  assert.equal(page.grid.innerHTML, saved, "Offline/rate-limited requests preserve saved projects");
  assert.match(page.status.textContent, /2026-11-09/);
}

const records = [];
const live = loadProjects({ ok: true, json: async () => records });
const repo = {
  ...live.context.window.GITHUB_PROJECTS.repositories[0],
  name: "NewProject",
  description: '<script>alert("x")</script>',
  language: "JavaScript",
  topics: ["first", "<topic>", "third", "fourth", "fifth"],
  archived: false,
};
records.push(repo, { ...repo, name: "ian030590" }, { ...repo, name: "MyPortfolio" }, { ...repo, name: "Fork", fork: true }, { ...repo, name: "Private", private: true });
await settle();
assert.equal(cardCount(live.grid.innerHTML), 1, "Latest public, owned projects replace the snapshot");
assert.match(live.grid.innerHTML, /<h2>NewProject<\/h2>/);
assert.match(live.grid.innerHTML, /&lt;script&gt;/);
assert.doesNotMatch(live.grid.innerHTML, /<script>/);
assert.deepEqual(cardLabels(live.grid.innerHTML), [["first", "&lt;topic&gt;", "third", "fourth"]], "Only the first four topics render, with escaping");
assert.doesNotMatch(live.grid.innerHTML, />JavaScript</, "The programming language is not a label");
assert.match(live.status.textContent, /已同步/);

const archived = loadProjects({ ok: true, json: async () => [{ ...repo, archived: true }] });
await settle();
assert.deepEqual(cardLabels(archived.grid.innerHTML), [["已封存", "first", "&lt;topic&gt;", "third", "fourth"]], "Archived status precedes up to four topic labels");

const excluded = loadProjects({ ok: true, json: async () => records.slice(1) });
await settle();
assert.equal(cardCount(excluded.grid.innerHTML), 0, "Excluded repositories never reappear as a fallback");
assert.match(excluded.grid.innerHTML, /尚無/);

const malformed = loadProjects({ ok: true, json: async () => ({ message: "Unexpected response" }) });
await settle();
assert.equal(cardCount(malformed.grid.innerHTML), 16);

const noSnapshot = loadProjects(null, { offline: true, withSnapshot: false });
await settle();
assert.match(noSnapshot.grid.innerHTML, /github.com\/ian030590\?tab=repositories/);
assert.match(noSnapshot.status.textContent, /無法更新/);

console.log("Project checks passed: immediate snapshot, live refresh, topic-only labels (max 4), archived status, filtering, escaping, and network/API failures.");
