import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { renderPage, esc } from '../lib/render.mjs';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const EXPORT = join(ROOT, 'out', 'export.json');

if (!existsSync(EXPORT)) {
  console.error('out/export.json 이 없습니다. 먼저: PYTHONPATH=src python3 -m sumex.cli export');
  process.exit(1);
}
const data = JSON.parse(readFileSync(EXPORT, 'utf-8'));

assert.equal(esc('<b>&"'), '&lt;b&gt;&amp;&quot;');

for (const path of ['/', '/hospitals', '/month', '/tasks', '/audit', '/case']) {
  const html = renderPage(new URL(`http://x${path}`), data);
  assert.ok(html.startsWith('<!doctype html>'), `${path} 가 HTML 이 아님`);
  assert.ok(html.includes('SUMEX'), `${path} 에 제목 없음`);
}

for (const h of data.hospitals) {
  const html = renderPage(new URL(`http://x/h/${encodeURIComponent(h.id)}`), data);
  assert.ok(html.includes(esc(h.name)), `${h.id} 페이지에 이름 없음`);
}

assert.throws(() => renderPage(new URL('http://x/nope'), data), /찾을 수 없습니다/);
assert.throws(() => renderPage(new URL('http://x/h/없는병원'), data), /찾을 수 없습니다/);

console.log(`ok — 페이지 ${6 + data.hospitals.length}개 렌더링 통과`);
