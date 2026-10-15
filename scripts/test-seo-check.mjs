import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { basename, dirname, join, resolve } from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const tempRoot = resolve(tmpdir());
const fixture = mkdtempSync(join(tempRoot, 'ian030590-seo-'));
const checker = fileURLToPath(new URL('./seo-check.mjs', import.meta.url));
const site = 'https://example.com';
const description = 'A static website used to check that only published pages are audited and temporary browser profiles and article backups are excluded.';

function write(relativePath, content) {
  const target = join(fixture, relativePath);
  mkdirSync(dirname(target), { recursive: true });
  writeFileSync(target, content);
}

function audit() {
  const result = spawnSync(process.execPath, [checker, '--dir', fixture, '--site', site, '--json', '--fail-on', 'error'], { encoding: 'utf8' });
  assert.ifError(result.error);
  assert.ok(result.status === 0 || result.status === 1, result.stderr);
  return { status: result.status, ...JSON.parse(result.stdout) };
}

try {
  write('index.html', `<!doctype html><html lang="en"><head><title>Published website for SEO regression checks</title><meta name="description" content="${description}"></head><body><h1>Published website</h1><a href="/">Home</a></body></html>`);
  write('robots.txt', 'User-agent: *\nAllow: /\n');
  write('sitemap.xml', `<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>${site}/</loc></url></urlset>`);
  const baseline = audit();
  assert.equal(baseline.status, 0);
  assert.equal(baseline.scanned, 1);
  assert.equal(baseline.counts.error, 0);

  for (const directory of ['scratch', '.git', 'node_modules', '__pycache__']) {
    write(`${directory}/browser/Default/popup.html`, '<html><head><title>Temporary page</title></head><body></body></html>');
  }
  write('scratch/backups/index.html', '<html><head><title>Published website for SEO regression checks</title></head><body></body></html>');
  assert.deepEqual(audit(), baseline, 'Temporary files must not change the audit results');

  write('content/broken.html', '<!doctype html><html lang="en"><head><title>Published website for SEO regression checks</title></head><body><h1>Published article</h1><a href="/">Home</a></body></html>');
  const broken = audit();
  assert.equal(broken.status, 1, 'Published errors must still block a push');
  assert.equal(broken.scanned, 2, 'Published article folders must still be scanned');
  assert.ok(broken.findings.some(f => f.code === 'L1-DESC-MISSING' && f.page === 'content/broken.html'));
  assert.ok(broken.findings.some(f => f.code === 'SITE-TITLE-DUP'));
  console.log('SEO checks passed: temporary files excluded; published errors still fail the audit.');
} finally {
  assert.equal(dirname(fixture), tempRoot);
  assert.ok(basename(fixture).startsWith('ian030590-seo-'));
  rmSync(fixture, { recursive: true, force: true });
}
