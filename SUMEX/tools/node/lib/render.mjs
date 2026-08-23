/** 대시보드 HTML 렌더링. 의존성 없음. 인쇄를 염두에 두고 만든다. */

const PRI_RANK = { 최상: 0, 상: 1, 중: 2 };

export function esc(text) {
  return String(text ?? '').replace(/[&<>"]/g, (c) => (
    { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]
  ));
}

function layout(title, body, { back = null } = {}) {
  return `<!doctype html>
<html lang="ko"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${esc(title)} · SUMEX</title>
<style>
  :root{--fg:#16181d;--muted:#666e7a;--line:#e2e5ea;--bg:#fff;--accent:#0b5cd5;--warn:#c0392b;--card:#f7f8fa}
  @media (prefers-color-scheme:dark){:root{--fg:#e8eaee;--muted:#9aa3af;--line:#2c313a;--bg:#14161a;--accent:#6fa8ff;--warn:#ff7b6b;--card:#1b1e24}}
  *{box-sizing:border-box}
  body{margin:0;font:15px/1.65 -apple-system,BlinkMacSystemFont,"Pretendard","맑은 고딕",sans-serif;color:var(--fg);background:var(--bg)}
  header{position:sticky;top:0;background:var(--bg);border-bottom:1px solid var(--line);padding:10px 16px;display:flex;gap:14px;flex-wrap:wrap;align-items:center;z-index:5}
  header a{color:var(--fg);text-decoration:none;font-size:14px;padding:4px 8px;border-radius:6px}
  header a:hover{background:var(--card)}
  header .sp{flex:1}
  main{max-width:940px;margin:0 auto;padding:20px 16px 80px}
  h1{font-size:22px;margin:18px 0 4px}
  h2{font-size:16px;margin:26px 0 8px;padding-bottom:5px;border-bottom:1px solid var(--line)}
  .sub{color:var(--muted);font-size:13px;margin:0 0 18px}
  ul{margin:6px 0 0;padding-left:20px}
  li{margin:3px 0}
  .card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:10px 0}
  .pill{display:inline-block;font-size:11px;padding:1px 7px;border-radius:999px;border:1px solid var(--line);color:var(--muted);margin-right:6px}
  .pill.hi{color:var(--warn);border-color:var(--warn)}
  .warn{color:var(--warn)}
  table{border-collapse:collapse;width:100%;font-size:13.5px}
  th,td{border-bottom:1px solid var(--line);padding:7px 8px;text-align:left;vertical-align:top}
  th{color:var(--muted);font-weight:600;white-space:nowrap}
  .num{text-align:right;font-variant-numeric:tabular-nums}
  .scroll{overflow-x:auto}
  .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:10px}
  .kv{color:var(--muted);font-size:13px}
  .big{font-size:34px;font-weight:700;line-height:1.1}
  a.q{color:var(--accent);text-decoration:none}
  a.q:hover{text-decoration:underline}
  @media print{
    header{display:none} main{max-width:none;padding:0}
    .card{break-inside:avoid;background:none;border:1px solid #999}
    body{font-size:12pt;color:#000;background:#fff}
  }
</style></head><body>
<header>
  <a href="/">오늘</a><a href="/hospitals">거래처</a><a href="/month">이달</a>
  <a href="/tasks">할 일</a><a href="/audit">확인 필요</a><a href="/case">케이스 커버</a>
  <span class="sp"></span>
  ${back ? `<a href="${esc(back)}">← 돌아가기</a>` : ''}
  <a href="/refresh?back=${encodeURIComponent(back || '/')}">↻ 갱신</a>
</header>
<main>${body}</main></body></html>`;
}

function entryList(entries) {
  if (!entries.length) return '<p class="kv">해당 없음</p>';
  return entries.map((e) => {
    const detail = String(e.detail || '').split('\n').map((s) => s.trim()).filter(Boolean);
    return `<div class="card">
      <div>
        <span class="pill${e.pri === '최상' ? ' hi' : ''}">${esc(e.pri || '중')}</span>
        <span class="pill">${esc(e.kind)}</span>
        ${e.overdue ? '<span class="pill hi">기한 지남</span>' : ''}
        ${e.hospital ? `<span class="pill">${esc(e.hospital)}</span>` : ''}
      </div>
      <div style="margin-top:6px;font-weight:600">${esc(e.title)}</div>
      ${detail.length ? `<ul>${detail.map((d) => `<li>${esc(d.replace(/^[-·]\s*/, ''))}</li>`).join('')}</ul>` : ''}
    </div>`;
  }).join('');
}

function pageToday(data) {
  const overdue = data.today.filter((e) => e.overdue).sort((a, b) => a.when.localeCompare(b.when));
  const today = data.today.filter((e) => !e.overdue);
  const blocking = data.audit.filter((a) => ['매수 미확인', '배부처 미기재', '매수 불일치'].includes(a.kind));

  return layout('오늘', `
    <h1>오늘 할 일</h1>
    <p class="sub">기준일 ${esc(data.generated)}</p>
    <div class="grid">
      <div class="card"><div class="kv">기한 지남</div><div class="big ${overdue.length ? 'warn' : ''}">${overdue.length}</div></div>
      <div class="card"><div class="kv">오늘 예정</div><div class="big">${today.length}</div></div>
      <div class="card"><div class="kv">서류 규칙 미확정</div><div class="big">${blocking.length}</div></div>
      <div class="card"><div class="kv">거래처</div><div class="big">${data.hospitals.length}</div></div>
    </div>
    ${overdue.length ? `<h2>기한이 지난 것</h2>${entryList(overdue)}` : ''}
    <h2>오늘</h2>${entryList(today)}
    ${data.routing.length ? `<h2>동선 메모</h2><ul>${data.routing.map((r) => `<li>${esc(r)}</li>`).join('')}</ul>` : ''}
  `);
}

function pageHospitals(data) {
  const rows = [...data.hospitals].sort(
    (a, b) => (PRI_RANK[a.priority] ?? 9) - (PRI_RANK[b.priority] ?? 9) || a.short.localeCompare(b.short)
  );
  return layout('거래처', `
    <h1>거래처 · 서류 규칙</h1>
    <p class="sub">매수를 잘못 준비하면 다시 출력하러 나가야 한다. 병원 이름을 눌러 체크리스트를 열고 인쇄하세요.</p>
    <div class="scroll"><table>
      <tr><th>거래처</th><th>지역</th><th>서류</th><th class="num">매수</th><th>도장</th><th>간납사</th><th>우선</th></tr>
      ${rows.map((h) => `<tr>
        <td><a class="q" href="/h/${esc(h.id)}">${esc(h.short)}</a></td>
        <td class="kv">${esc(h.region)}</td>
        <td>${esc(h.docType)}</td>
        <td class="num ${h.copies == null ? 'warn' : ''}">${h.copies == null ? '?' : h.copies}</td>
        <td>${h.stamp === true ? '<span class="warn">필요</span>' : h.stamp === false ? '불필요' : '-'}</td>
        <td class="kv">${esc(h.consignment || '직거래')}</td>
        <td>${esc(h.priority)}</td>
      </tr>`).join('')}
    </table></div>
  `);
}

function pageHospital(data, id) {
  const h = data.hospitals.find((x) => x.id === id);
  if (!h) throw new Error(`거래처 '${id}' 를 찾을 수 없습니다.`);

  const block = (title, items, cls = '') => (items && items.length
    ? `<h2>${title}</h2><ul class="${cls}">${items.map((i) => `<li>${esc(String(i).replace(/\n/g, ' '))}</li>`).join('')}</ul>`
    : '');

  return layout(h.short, `
    <h1>${esc(h.name)}</h1>
    <p class="sub">${esc(h.region)} · ${esc(h.docType)} ${h.copies == null ? '(매수 미확인)' : `${h.copies}장`}
      · 간납사 ${esc(h.consignment || '없음')} · 우선순위 ${esc(h.priority)}</p>
    ${h.copies == null ? '<div class="card warn">이 병원의 서류 매수 규칙이 아직 확인되지 않았습니다. 기본 4장을 준비하고 현장에서 확정하세요.</div>' : ''}
    ${block('서류 준비 · 배부', h.checklist)}
    ${block('반드시 지킬 것', h.hard)}
    ${block('월 마감', h.closing)}
    ${block('주의', h.cautions)}
    ${block('진행 중인 건', h.watch)}
    ${block('확인 필요', h.open)}
    ${block('취급 품목', h.products)}
  `, { back: '/hospitals' });
}

function pageMonth(data) {
  const byDay = new Map();
  for (const e of data.month) {
    if (!byDay.has(e.when)) byDay.set(e.when, []);
    byDay.get(e.when).push(e);
  }
  const days = [...byDay.keys()].sort();
  return layout('이달 일정', `
    <h1>이달 일정</h1>
    <p class="sub">${data.month.length}건 · 마감을 넘기면 대금 지급이 밀립니다.</p>
    ${days.map((d) => `<h2>${esc(d)}</h2>${entryList(byDay.get(d))}`).join('')}
  `);
}

function pageTasks(data) {
  const order = { todo: 0, doing: 1, done: 2, dropped: 3 };
  const rows = [...data.tasks].sort(
    (a, b) => (order[a.status] ?? 9) - (order[b.status] ?? 9)
      || (PRI_RANK[a.pri] ?? 9) - (PRI_RANK[b.pri] ?? 9)
  );
  return layout('할 일', `
    <h1>인수인계 후속조치</h1>
    <p class="sub">상태 변경은 <code>sumex task done T-004</code> 또는 data/tasks.yaml 직접 편집.</p>
    <div class="scroll"><table>
      <tr><th>ID</th><th>상태</th><th>중요도</th><th>기한</th><th>거래처</th><th>할 일</th></tr>
      ${rows.map((t) => `<tr>
        <td>${esc(t.id)}</td>
        <td>${esc(t.status || 'todo')}</td>
        <td class="${t.pri === '최상' ? 'warn' : ''}">${esc(t.pri || '중')}</td>
        <td class="kv">${esc(t.due || '')}</td>
        <td class="kv">${esc(t.hospital || '')}</td>
        <td>${esc(t.title)}${t.note ? `<div class="kv">${esc(t.note)}</div>` : ''}</td>
      </tr>`).join('')}
    </table></div>
  `);
}

function pageAudit(data) {
  const byKind = new Map();
  for (const f of data.audit) {
    if (!byKind.has(f.kind)) byKind.set(f.kind, []);
    byKind.get(f.kind).push(f);
  }
  return layout('확인 필요', `
    <h1>확인이 필요한 것</h1>
    <p class="sub">인수인계 자료 두 부가 서로 다르게 말하거나, 아예 비어 있는 항목입니다. ${data.audit.length}건.</p>
    ${[...byKind.entries()].map(([kind, rows]) => `
      <h2>${esc(kind)} (${rows.length})</h2>
      <ul>${rows.map((r) => `<li><b>${esc(r.hospital)}</b> — ${esc(r.detail)}</li>`).join('')}</ul>
    `).join('')}
  `);
}

function pageCase(data) {
  return layout('케이스 커버', `
    <h1>관절경 케이스 커버 7축</h1>
    <p class="sub">하나라도 비면 수술이 멈춘다. 케이스 전에 머릿속으로 한 바퀴 돌린다.</p>
    ${data.caseCover.map((a) => `<div class="card">
      <div style="font-weight:700">${esc(a.axis)}</div>
      <ul>${(a.items || []).map((i) => `<li>☐ ${esc(i)}</li>`).join('')}</ul>
      ${a.spare ? `<div class="warn" style="margin-top:6px">★ ${esc(a.spare)}</div>` : ''}
    </div>`).join('')}
  `);
}

export function renderPage(url, data) {
  const path = url.pathname;
  if (path === '/' || path === '/today') return pageToday(data);
  if (path === '/hospitals') return pageHospitals(data);
  if (path.startsWith('/h/')) return pageHospital(data, decodeURIComponent(path.slice(3)));
  if (path === '/month') return pageMonth(data);
  if (path === '/tasks') return pageTasks(data);
  if (path === '/audit') return pageAudit(data);
  if (path === '/case') return pageCase(data);
  throw new Error(`페이지를 찾을 수 없습니다: ${path}`);
}
