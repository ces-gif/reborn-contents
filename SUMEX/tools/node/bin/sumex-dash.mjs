#!/usr/bin/env node
/**
 * SUMEX 대시보드 — 의존성 없는 로컬 웹 서버.
 *
 *   node tools/node/bin/sumex-dash.mjs            # http://localhost:5173
 *   node tools/node/bin/sumex-dash.mjs --port 8080 --no-refresh
 *
 * 왜 노드인가:
 *   차 안에서 휴대폰으로 열어 볼 체크리스트가 필요하고, 브라우저 인쇄로
 *   바로 뽑을 수 있어야 한다. 파이썬 CLI 는 서류를 만들고, 이쪽은 그걸
 *   눈으로 보고 인쇄한다.
 *
 * 데이터는 파이썬이 만든 out/export.json 을 읽는다. 서버 시작 시
 * `python3 -m sumex.cli export` 를 한 번 돌려 최신화한다(--no-refresh 로 끔).
 */
import { createServer } from 'node:http';
import { spawnSync } from 'node:child_process';
import { readFileSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { renderPage } from '../lib/render.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, '..', '..', '..');          // .../SUMEX
const EXPORT = join(ROOT, 'out', 'export.json');

function parseArgs(argv) {
  const opts = { port: 5173, refresh: true, host: '127.0.0.1' };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === '--port') opts.port = Number(argv[++i]);
    else if (arg === '--host') opts.host = argv[++i];
    else if (arg === '--no-refresh') opts.refresh = false;
    else if (arg === '--help' || arg === '-h') opts.help = true;
  }
  return opts;
}

function refresh() {
  const python = process.env.PYTHON || 'python3';
  const res = spawnSync(python, ['-m', 'sumex.cli', 'export'], {
    cwd: ROOT,
    env: { ...process.env, PYTHONPATH: join(ROOT, 'src') },
    encoding: 'utf-8',
  });
  if (res.status !== 0) {
    const detail = (res.stderr || res.error?.message || '').trim().split('\n').slice(-3).join('\n');
    console.error('데이터 갱신 실패 — 기존 export.json 으로 계속합니다.');
    if (detail) console.error(detail);
    return false;
  }
  return true;
}

function loadData() {
  if (!existsSync(EXPORT)) {
    throw new Error(
      `데이터가 없습니다: ${EXPORT}\n먼저 실행하세요:  PYTHONPATH=src python3 -m sumex.cli export`
    );
  }
  return JSON.parse(readFileSync(EXPORT, 'utf-8'));
}

function main() {
  const opts = parseArgs(process.argv.slice(2));
  if (opts.help) {
    console.log('사용법: node tools/node/bin/sumex-dash.mjs [--port 5173] [--host 127.0.0.1] [--no-refresh]');
    return;
  }

  if (opts.refresh) refresh();
  let data = loadData();

  const server = createServer((req, res) => {
    const url = new URL(req.url, `http://${req.headers.host}`);

    if (url.pathname === '/api/data') {
      res.writeHead(200, { 'content-type': 'application/json; charset=utf-8' });
      res.end(JSON.stringify(data));
      return;
    }

    if (url.pathname === '/refresh') {
      if (refresh()) data = loadData();
      res.writeHead(302, { location: url.searchParams.get('back') || '/' });
      res.end();
      return;
    }

    let html;
    try {
      html = renderPage(url, data);
    } catch (err) {
      res.writeHead(404, { 'content-type': 'text/html; charset=utf-8' });
      res.end(`<meta charset="utf-8"><h1>404</h1><p>${escapeHtml(err.message)}</p><p><a href="/">처음으로</a></p>`);
      return;
    }
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
    res.end(html);
  });

  server.listen(opts.port, opts.host, () => {
    console.log(`SUMEX 대시보드  →  http://${opts.host}:${opts.port}`);
    console.log('  /              오늘 브리핑');
    console.log('  /hospitals     거래처 · 서류 규칙');
    console.log('  /h/<id>        납품 체크리스트 (인쇄용)');
    console.log('  /month         이달 일정');
    console.log('  /audit         확인이 필요한 것');
    console.log('종료: Ctrl+C');
  });

  server.on('error', (err) => {
    if (err.code === 'EADDRINUSE') {
      console.error(`포트 ${opts.port} 가 이미 사용 중입니다. --port 로 다른 번호를 주세요.`);
      process.exit(1);
    }
    throw err;
  });
}

function escapeHtml(text) {
  return String(text).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
}

main();
