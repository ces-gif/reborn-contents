// 프로그램(운영) 견적서 — 발주처가 보내온 세 양식 중 3안(고양산업진흥원 수신 프로그램 운영 견적서)을 따른다.
const fs = require('fs');
const {
  Document, Packer, Paragraph, TextRun, AlignmentType, PageBreak, ImageRun,
  Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle,
  VerticalAlign, VerticalMergeType, HeightRule, LineRuleType, convertMillimetersToTwip,
} = require('docx');

const F = { ascii: '맑은 고딕', hAnsi: '맑은 고딕', eastAsia: '맑은 고딕', cs: '맑은 고딕', hint: 'eastAsia' };
const GRAY = 'D9D9D9', TITLE_BG = 'BFBFBF', BLUE = 'DCE6F1', LINE = '808080', DIM = '767676';
const MARGIN = convertMillimetersToTwip(16);
const W = convertMillimetersToTwip(210) - MARGIN * 2;   // 178mm ≈ 10091 twip

const run = (t, o = {}) => new TextRun({
  text: t, bold: o.bold, color: o.color, size: o.size ?? 18, font: F, characterSpacing: o.spacing,
});
const P = (t, o = {}) => new Paragraph({
  alignment: o.align, spacing: { before: o.before ?? 0, after: o.after ?? 90, line: o.line ?? 280 },
  children: [run(t, o)],
});

const B = (sz = 4, color = LINE) => ({ style: BorderStyle.SINGLE, size: sz, color });
const NONE = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };

const cell = (o) => new TableCell({
  width: { size: o.w, type: WidthType.DXA },
  columnSpan: o.span, rowSpan: o.rowSpan, verticalMerge: o.vmerge,
  verticalAlign: VerticalAlign.CENTER,
  shading: o.fill ? { type: ShadingType.CLEAR, fill: o.fill, color: 'auto' } : undefined,
  borders: o.borders,
  margins: { top: 46, bottom: 46, left: 70, right: 70 },
  children: o.children ?? [new Paragraph({
    alignment: o.align ?? AlignmentType.LEFT,
    spacing: { after: 0, line: 260 },
    children: [run(o.t ?? '', { bold: o.bold, size: o.size ?? 17, color: o.color })],
  })],
});

const grid = (widths, rows, o = {}) => new Table({
  columnWidths: widths,
  width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA },
  borders: o.borders ?? {
    top: B(6), bottom: B(6), left: B(6), right: B(6),
    insideHorizontal: B(4), insideVertical: B(4),
  },
  rows: rows.map((cells, ri) => new TableRow({
    height: o.heights && o.heights[ri]
      ? { value: o.heights[ri], rule: HeightRule.ATLEAST } : undefined,
    children: cells.map((c, i) => {
      const x = typeof c === 'string' ? { t: c } : { ...c };
      x.w = x.span ? widths.slice(i, i + x.span).reduce((a, b) => a + b, 0) : widths[i];
      return cell(x);
    }),
  })),
});
const R = (...c) => c;
const ctr = (t, o = {}) => ({ t, align: AlignmentType.CENTER, ...o });
const rgt = (t, o = {}) => ({ t, align: AlignmentType.RIGHT, ...o });
const LBL = (t) => ({ t, bold: true, fill: GRAY, align: AlignmentType.CENTER });
const HD  = (t) => ({ t, bold: true, fill: GRAY, align: AlignmentType.CENTER });
const CONT = { t: '', vmerge: VerticalMergeType.CONTINUE };

// ── 제목 ──────────────────────────────────────────────────────────────────
const titleBar = grid([W], [[{
  t: '', fill: TITLE_BG,
  children: [new Paragraph({
    alignment: AlignmentType.CENTER, spacing: { before: 40, after: 40, line: 300 },
    children: [run('프로그램(운영) 견 적 서', { bold: true, size: 34, spacing: 60 })],
  })],
}]]);

// ── 수신 / 공급자 ─────────────────────────────────────────────────────────
// 왼쪽은 밑줄만 있는 기입란, 오른쪽은 공급자 표. 한 격자 안에서 테두리를 나눠 쓴다.
const L = (label, value) => ({
  t: '', borders: { top: NONE, left: NONE, right: NONE, bottom: B(4) },
  children: [new Paragraph({
    spacing: { after: 0, line: 260 },
    children: [run(label, { bold: true, size: 17 }), run(' : ' + value, { size: 17 })],
  })],
});

const 도장 = fs.readFileSync(process.argv[3]);
const header = grid([4700, 1900, 3491], [
  R(L('수    신', '(재)고양산업진흥원'), LBL('견적일자'), ctr('2026. 09. 01.')),
  R(L('참    조', 'K-하이테크 플랫폼 지원단'), { t: '공  급  자', span: 2, bold: true, fill: GRAY, align: AlignmentType.CENTER, size: 19 }),
  R(L('과    업', '2026년 한국항공대학교 바이브 코딩 기반 학생창업 경진대회 및 창업 특강 운영'),
    LBL('사업자 등록번호'), ctr('')),
  R(L('유효기간', '발행일로부터 30일'), LBL('상        호'), ctr('주식회사 리본마켓', { bold: true })),
  R(L('과업기간', '계약일 ~ 2026. 11. 6.'), LBL('대  표  자'), {
    t: '', align: AlignmentType.CENTER,
    children: [new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 0, line: 240, lineRule: LineRuleType.AUTO },
      children: [
        run('김  기  훈    ', { bold: true, size: 18 }),
        new ImageRun({ data: 도장, type: 'png', transformation: { width: 54, height: 54 } }),
      ],
    })],
  }),
  R(L('지급방법', '계산서 발행'), LBL('주        소'), ctr('')),
  R(L('행사장소', '한국항공대학교 대강당 및 스타트업 라운지'), LBL('담  당  자'), ctr('')),
]);

// ── 견적합계 ──────────────────────────────────────────────────────────────
const totalBar = grid([4700, 5391], [
  R({ t: '견적합계 (VAT)포함', bold: true, fill: GRAY, align: AlignmentType.CENTER, size: 24 },
    rgt('10,000,000', { bold: true, size: 26 })),
]);

// ── 예산 명세 ─────────────────────────────────────────────────────────────
const CW = [1150, 620, 1700, 380, 380, 1180, 380, 380, 1330, 2591]; // = 10091
const won = (n) => rgt(n, { size: 17 });
const item = (no, name, unitN, unitU, price, qtyN, qtyU, sum, note) =>
  R(CONT, ctr(no, { bold: true }), name, ctr(unitN), ctr(unitU), won(price), ctr(qtyN), ctr(qtyU), won(sum), { t: note, size: 15 });

const budget = grid(CW, [
  R({ t: '구분', span: 3, bold: true, fill: GRAY, align: AlignmentType.CENTER },
    { t: '예산 (원)', span: 6, bold: true, fill: GRAY, align: AlignmentType.CENTER },
    { t: '', fill: GRAY }),
  R(HD('행사구분'), HD('연번'), HD('개별항목'), { t: '단위', span: 2, bold: true, fill: GRAY, align: AlignmentType.CENTER },
    HD('단가'), { t: '수량', span: 2, bold: true, fill: GRAY, align: AlignmentType.CENTER }, HD('합계'), HD('비고')),

  R({ t: '프로그램 예산', vmerge: VerticalMergeType.RESTART, bold: true, align: AlignmentType.CENTER },
    ctr('1-1', { bold: true }), '창업 특강 강사비', ctr('1'), ctr('식'), won('250,000'), ctr('1'), ctr('회'), won('250,000'),
    { t: '강사수당 지급기준 나급 · 2시간', size: 15 }),
  item('1-2', '1:1 창업 멘토링비', '1', '식', '150,000', '10', '팀', '1,500,000', '10.8 멘토링 · 팀당 60분'),
  item('1-3', '예선 서류 평가료', '1', '식', '150,000', '2', '인', '300,000', '10.15 내/외부 심사위원'),
  item('1-4', '결승 심사수당', '1', '식', '400,000', '3', '인', '1,200,000', '10.22 현직 VC'),
  item('1-5', '시상금 및 부상', '1', '식', '-', '10', '팀', '2,500,000', '대상 100만 / 최우수 50만 / 우수 30만 / 장려 10만×7팀'),
  item('1-6', 'AI 코딩 도구 이용료', '1', '인', '50,000', '30', '인', '1,500,000', '멘토링 10개 팀 · 팀당 3인 기준'),
  item('1-7', '홍보 및 인쇄비', '1', '식', '700,000', '1', '회', '700,000', '포스터 · 현수막 · 자료집 · 상장'),
  item('1-8', '행사 운영비', '1', '식', '600,000', '1', '회', '600,000', '특강 다과 · 결승 식대 · 소모품'),
  R(CONT, { t: 'Sub Total', span: 7, bold: true, fill: GRAY, align: AlignmentType.CENTER },
    rgt('8,550,000', { bold: true, fill: GRAY }), { t: '', fill: GRAY }),

  R({ t: '최종 제안가', vmerge: VerticalMergeType.RESTART, bold: true, fill: BLUE, align: AlignmentType.CENTER },
    { t: '프로그램 대행비 (일반관리비 3.0% + 이윤 3.23%)', span: 7, fill: GRAY, align: AlignmentType.CENTER },
    rgt('540,909', { fill: GRAY }), { t: '', fill: GRAY }),
  R(CONT, { t: '견적 합계 (VAT 제외)', span: 7, fill: GRAY, align: AlignmentType.CENTER },
    rgt('9,090,909', { fill: GRAY }), { t: '', fill: GRAY }),
  R(CONT, { t: '부가가치세', span: 7, fill: GRAY, align: AlignmentType.CENTER },
    rgt('909,091', { fill: GRAY }), { t: '', fill: GRAY }),
  R(CONT, { t: '용역합계 (VAT 포함)', span: 7, bold: true, fill: BLUE, align: AlignmentType.CENTER, size: 19 },
    rgt('10,000,000', { bold: true, fill: BLUE, size: 19 }), { t: '', fill: BLUE }),
]);

// ── 별지 : 강사수당 지급기준 ──────────────────────────────────────────────
const AW = [820, 3500, 2300, 950, 950, 1571]; // = 10091
const 별지 = grid(AW, [
  R(HD('등급'), HD('적용대상 (일반)'), HD('적용대상 (공직자 등)'), HD('최초 1시간'), HD('초과 매시간'), HD('2시간')),
  R(ctr('특1급'), { t: '전직 장관(급) 및 광역자치단체장, 전직 국회의원, 전직 한국은행장, 전직 대학의 총장(이사장), 대기업 총수(부회장 이상)', size: 14 },
    { t: '장관(급)*, 광역자치단체장*, 국회의원*, 한국은행장*, 대학의 총장(이사장)', size: 14 }, rgt('400,000'), rgt('300,000'), rgt('700,000')),
  R(ctr('특2급'), { t: '전직 차관(급) 및 기초자치단체장, 전직 공직유관단체장, 전직 전문대학 등의 총장(이사장), 대기업 임원, 중견기업 대표', size: 14 },
    { t: '차관(급), 기초자치단체장, 공직유관단체장, 전문대학 등의 총장(이사장), 대형언론사 총수', size: 14 }, rgt('300,000'), rgt('200,000'), rgt('500,000')),
  R(ctr('가급'), { t: '전직 4급 이상 공무원, 전직 지방의회의원(의장 포함), 전직 공직유관단체 임원, 전직 대학의 교수(조교수 이상), 유명 예술인·종교인, 대기업 부장(급)·중견기업 임원·중소기업 대표, 전문직 3년 이상 실무경력자, 박사학위 취득 후 해당분야 3년 이상 실무경력자, 국가대표 지도자 및 국가대표 출신 강사', size: 14 },
    { t: '4급 이상 공무원, 지방의회의원(의장 포함), 공직유관단체 임원, 대학의 교수(조교수 이상), 초·중·고교의 장(이사장), 대형언론사 임원, 기타언론사 대표', size: 14 },
    rgt('280,000'), rgt('120,000'), rgt('400,000')),
  R({ t: '나급', bold: true, fill: 'FFF2CC', align: AlignmentType.CENTER },
    { t: '전직 5급(상당) 공무원, 중견기업 부장(급)·중소기업 임원, 원어민 어학 강사(외국국적을 가진 자로서 해당 국가에서 고등교육을 이수한 자), 국가전문자격증을 가진 자로서 3년 이상 실무경력자, 기타 전문자격을 가진 자로서 5년 이상 실무경력자', size: 14, bold: true, fill: 'FFF2CC' },
    { t: '5급 이하 공무원, 공직유관단체 직원, 대학의 강사 등(교직원 포함), 초·중·고교의 교직원, 기타언론사 임원', size: 14, bold: true, fill: 'FFF2CC' },
    rgt('170,000', { bold: true, fill: 'FFF2CC' }), rgt('80,000', { bold: true, fill: 'FFF2CC' }), rgt('250,000', { bold: true, fill: 'FFF2CC' })),
  R(ctr('다급'), { t: '전직 6급 이하 공무원, 외국어·전산 등 강사, 체육·레크리에이션 등 취미·소양 강사로서 해당분야 3년 이상(공공기관·공공교육훈련기관 경력) 또는 5년 이상(외부경력 포함) 강의 경력자', size: 14 },
    '', rgt('100,000'), rgt('50,000'), rgt('150,000')),
  R(ctr('라급'), { t: '체육, 레크리에이션 등 취미·소양 강사', size: 14 }, '', rgt('80,000'), rgt('40,000'), rgt('120,000')),
  R(ctr('마급'), { t: '각종 교육운영(실기실습 등) 보조자', size: 14 }, '', rgt('60,000'), rgt('30,000'), rgt('90,000')),
]);

const doc = new Document({
  styles: { default: { document: { run: { font: F, size: 18 }, paragraph: { spacing: { line: 280 } } } } },
  sections: [{
    properties: { page: { margin: { top: convertMillimetersToTwip(14), bottom: convertMillimetersToTwip(12), left: MARGIN, right: MARGIN } } },
    children: [
      titleBar,
      new Paragraph({ spacing: { after: 60 }, children: [] }),
      header,
      new Paragraph({ spacing: { after: 140 }, children: [] }),
      totalBar,
      new Paragraph({ spacing: { after: 60 }, children: [] }),
      budget,
      P('※ 산출 근거는 별첨 「원가계산서」(총괄표·인건비·일반경비·강사수당 지급기준)를 따르며, 강사비는 발주처 「강사수당 지급기준」 나급을 적용하였다. 본 견적은 협의용이며 과업 내용 변경 시 금액이 조정될 수 있다.',
        { before: 160, size: 15, color: DIM }),

      new Paragraph({ children: [new PageBreak()] }),
      P('[ 별지 ]  강사수당 지급기준', { align: AlignmentType.CENTER, bold: true, size: 30, spacing: 50, after: 80 }),
      new Paragraph({ spacing: { after: 160 }, border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: '000000', space: 0 } }, children: [] }),
      P('발주처 「3. 강사수당 지급기준 — 가. 일반강의 강사수당」', { after: 140, size: 17 }),
      별지,
      P('1. 전문직 : 감정평가사, 건축사, 공인노무사, 공인회계사, 관세사, 기술사, 법무사, 변리사, 변호사, 보험계리사, 세무사, 약사, 의사', { before: 180, size: 15, color: DIM, after: 40 }),
      P('2. 특1급 초과 매시간은 300,000원이나, * 표시된 청탁금지법 적용 대상(공직자 등)은 200,000원을 적용한다.', { size: 15, color: DIM, after: 40 }),
      P('3. 본 견적의 창업 특강(2시간)은 나급을 적용하여 170,000원 + 80,000원 = 250,000원으로 계상하였다.', { size: 15, color: DIM, after: 40 }),
      P('4. 2025년 용역도 동일하게 나급을 적용하였다 (4시간 410,000원 / 3시간 330,000원).', { size: 15, color: DIM, after: 40 }),
      P('5. 강사가 중소기업 대표 등 가급 요건에 해당하면 2시간 400,000원까지 적용할 수 있다.', { size: 15, color: DIM }),
    ],
  }],
});

const ORDER = ['top', 'left', 'bottom', 'right', 'between', 'bar'];
const fixPBdr = (xml) => xml.replace(/<w:pBdr>([\s\S]*?)<\/w:pBdr>/g, (_, inner) => {
  const kids = inner.match(/<w:(?:top|left|bottom|right|between|bar)\b[^>]*\/>/g) || [];
  return `<w:pBdr>${kids.slice().sort((a, b) => ORDER.indexOf(a.match(/<w:(\w+)/)[1]) - ORDER.indexOf(b.match(/<w:(\w+)/)[1])).join('')}</w:pBdr>`;
});
Packer.toBuffer(doc)
  .then((b) => require('jszip').loadAsync(b))
  .then(async (zip) => {
    zip.file('word/document.xml', fixPBdr(await zip.file('word/document.xml').async('string')));
    return zip.generateAsync({ type: 'nodebuffer', compression: 'DEFLATE' });
  })
  .then((b) => { fs.writeFileSync(process.argv[2], b); console.log('wrote', process.argv[2], b.length); });
