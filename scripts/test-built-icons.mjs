import assert from 'node:assert/strict';
import { readdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

const files = readdirSync('dist', { recursive: true }).filter(path => path.endsWith('.html'));
assert.ok(files.includes('index.html'));
for (const file of files) {
  const html = readFileSync(join('dist', file), 'utf8');
  if (file.startsWith('content/')) {
    assert.deepEqual(readFileSync(join('dist', file)), readFileSync(join('.generated/public', file)), file);
    const source = readFileSync(file, 'utf8');
    assert.equal(html, source.replaceAll('https://ian030590.trainerhub.cc/', 'https://ian.trainerhub.cc/'), file);
  } else {
    assert.doesNotMatch(html, /material-symbols-outlined|Material\+Symbols/, file);
  }
}
console.log('Built icon and static article copy checks passed.');
