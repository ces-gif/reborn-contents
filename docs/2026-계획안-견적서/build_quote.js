// 견 적 서 (1쪽) — 공급자 정보 중 사업자등록번호·주소·연락처는 확인되지 않아 빈칸으로 둔다.
const fs = require('fs');
const {
  Document, Packer, Paragraph, TextRun, AlignmentType,
  Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle,
  VerticalAlign, convertMillimetersToTwip,
} = require('docx');

const F = { ascii: '맑은 고딕', hAnsi: '맑은 고딕', eastAsia: '맑은 고딕', cs: '맑은 고딕', hint: 'eastAsia' };
const NAVY = '17365D', RULE = 'BFC9D4', ZEBRA = 'F4F7FB', GRAYF = 'F2F2F2', GRAY = '767676';
const MARGIN = convertMillimetersToTwip(18);
const W = convertMillimetersToTwip(210) - MARGIN * 2;

const run = (t, o = {}) => new TextRun({ text: t, bold: o.bold, color: o.color, size: o.size ?? 19, font: F, characterSpacing: o.spacing });
const P = (t, o = {}) => new Paragraph({
  alignment: o.align, spacing: { before: o.before ?? 0, after: o.after ?? 100, line: o.line ?? 300 },
  children: [run(t, o)],
});

const cell = (o) => new TableCell({
  width: { size: o.w, type: WidthType.DXA },
  columnSpan: o.span, rowSpan: o.rowSpan, verticalAlign: VerticalAlign.CENTER,
  shading: o.fill ? { type: ShadingType.CLEAR, fill: o.fill, color: 'auto' } : undefined,
  margins: { top: 52, bottom: 52, left: 100, right: 100 },
  children: [new Paragraph({
    alignment: o.align ?? AlignmentType.LEFT, spacing: { after: 0, line: 280 },
    children: [run(o.t ?? '', { bold: o.bold, size: o.size ?? 18, color: o.color })],
  })],
});
const BORDERS = {
  top: { style: BorderStyle.SINGLE, size: 12, color: NAVY },
  bottom: { style: BorderStyle.SINGLE, size: 12, color: NAVY },
  left: { style: BorderStyle.SINGLE, size: 4, color: RULE },
  right: { style: BorderStyle.SINGLE, size: 4, color: RULE },
  insideHorizontal: { style: BorderStyle.SINGLE, size: 4, color: RULE },
  insideVertical: { style: BorderStyle.SINGLE, size: 4, color: RULE },
};
const table = (widths, rows) => new Table({
  columnWidths: widths,
  width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA },
  borders: BORDERS,
  rows: rows.map((cells) => new TableRow({
    children: cells.map((c, i) => {
      const o = typeof c === 'string' ? { t: c } : { ...c };
      o.w = o.span ? widths.slice(i, i + o.span).reduce((a, b) => a + b, 0) : widths[i];
      return cell(o);
    }),
  })),
});
const R = (...c) => c;
const ctr = (t, o = {}) => ({ t, align: AlignmentType.CENTER, ...o });
const won = (t, o = {}) => ({ t, align: AlignmentType.RIGHT, ...o });
const HEAD = (t) => ({ t, bold: true, color: 'FFFFFF', fill: NAVY, align: AlignmentType.CENTER });
const LBL = (t) => ({ t, bold: true, fill: GRAYF, align: AlignmentType.CENTER });

// 공급받는자 / 공급자
const 당사자 = table([1500, 3100, 1500, 3100], [
  R(LBL('상  호'), '고양산업진흥원 K-하이테크 플랫폼 지원단', LBL('상  호'), '(주)리본마켓'),
  R(LBL('구  분'), ctr('공급받는자 (발주처)'), LBL('대표자'), '최 은 성'),
  R(LBL('사 업 명'), { t: '2026 대학생과 고양시민의 AI 기술 창업을 위한 바이브 코딩 특강 및 창업 경진대회 운영', span: 3 }),
  R(LBL('사업자등록번호'), '', LBL('연 락 처'), ''),
  R(LBL('주    소'), { t: '', span: 3 }),
]);

const 명세 = table([600, 3300, 1000, 700, 1800, 1774], [
  R(HEAD('No'), HEAD('품            목'), HEAD('단가(원)'), HEAD('수량'), HEAD('금액(원)'), HEAD('비  고')),
  R(ctr('1'), { t: '인건비 — 전문가 수당', bold: true }, ctr('-'), ctr('-'), won('3,250,000', { bold: true }), '강사·멘토·심사위원'),
  R(ctr(''), '  창업 특강 강사료', won('250,000'), ctr('1명'), won('250,000'), '지급기준 나급 · 2시간'),
  R(ctr(''), '  1:1 창업 멘토링비', won('150,000'), ctr('10팀'), won('1,500,000'), '10.8 멘토링'),
  R(ctr(''), '  예선 서류 평가료', won('150,000'), ctr('2명'), won('300,000'), '10.15 서류평가'),
  R(ctr(''), '  결승 심사수당', won('400,000'), ctr('3명'), won('1,200,000'), '10.22 현직 VC'),
  R(ctr('2'), { t: '일반경비 — 시상·실습·홍보·운영', bold: true }, ctr('-'), ctr('-'), won('5,300,000', { bold: true }), ''),
  R(ctr(''), '  시상금 및 부상', ctr('-'), ctr('10팀'), won('2,500,000'), '대상~장려상'),
  R(ctr(''), '  AI 코딩 도구 이용료', won('50,000'), ctr('30명'), won('1,500,000'), '10개 팀·팀당 3인'),
  R(ctr(''), '  홍보 및 인쇄비', ctr('-'), ctr('1식'), won('700,000'), '포스터·현수막·자료집·상장'),
  R(ctr(''), '  행사 운영비', ctr('-'), ctr('1식'), won('600,000'), '다과·식대·소모품'),
  R(ctr('3'), '일반관리비', ctr('3.0%'), ctr('1식'), won('256,500'), '법정 한도 8% 이내'),
  R(ctr('4'), '이윤', ctr('3.23%'), ctr('1식'), won('284,409'), '법정 한도 10% 이내'),
  R({ t: '소   계 (총원가)', span: 4, bold: true, fill: GRAYF, align: AlignmentType.CENTER }, won('9,090,909', { bold: true, fill: GRAYF }), { t: '', fill: GRAYF }),
  R({ t: '부 가 가 치 세 (10%)', span: 4, bold: true, fill: GRAYF, align: AlignmentType.CENTER }, won('909,091', { bold: true, fill: GRAYF }), { t: '', fill: GRAYF }),
  R({ t: '합 계 금 액', span: 4, bold: true, fill: NAVY, color: 'FFFFFF', align: AlignmentType.CENTER, size: 20 },
    won('10,000,000', { bold: true, fill: NAVY, color: 'FFFFFF', size: 20 }), { t: '', fill: NAVY }),
]);

const doc = new Document({
  styles: { default: { document: { run: { font: F, size: 19 }, paragraph: { spacing: { line: 300 } } } } },
  sections: [{
    properties: { page: { margin: { top: convertMillimetersToTwip(15), bottom: convertMillimetersToTwip(12), left: MARGIN, right: MARGIN } } },
    children: [
      P('견     적     서', { align: AlignmentType.CENTER, bold: true, size: 44, color: NAVY, spacing: 100, after: 100 }),
      new Paragraph({ spacing: { after: 150 }, border: { bottom: { style: BorderStyle.SINGLE, size: 14, color: NAVY, space: 0 } }, children: [] }),
      P('견적일자 : 2026. 09. 01.          유효기간 : 견적일로부터 30일', { align: AlignmentType.RIGHT, size: 18, after: 160 }),
      당사자,
      P('아래와 같이 견적합니다.', { before: 180, after: 130 }),
      P('일금  일천만원정  (₩10,000,000)  ※ 부가가치세 포함', { bold: true, size: 24, color: NAVY, after: 150 }),
      명세,
      P('※ 산출 근거는 별첨 「원가계산서」(총괄표·인건비·일반경비·강사수당 지급기준)를 따른다.', { before: 140, size: 17, color: GRAY, after: 40 }),
      P('※ 창업 특강 강사료는 발주처 「강사수당 지급기준」 나급(최초 1시간 170,000원 + 초과 매시간 80,000원, 2시간 250,000원)을 적용하였다.', { size: 17, color: GRAY, after: 40 }),
      P('※ 시상금(2,500,000원)과 AI 코딩 도구 이용료(1,500,000원) 등 실비성 지출의 비중이 커, 일반관리비(3.0%)와 이윤(3.23%)은 지방계약법 시행규칙상 한도(각 8%, 10%)를 밑도는 수준으로 계상하였다.', { size: 17, color: GRAY, after: 40 }),
      P('※ 본 견적은 협의용이며, 과업 내용 변경 시 금액이 조정될 수 있다.', { size: 17, color: GRAY, after: 150 }),
      P('2026. 09. 01.', { align: AlignmentType.CENTER, size: 20, after: 110 }),
      P('(주) 리 본 마 켓      대표이사   최 은 성    (인)', { align: AlignmentType.CENTER, bold: true, size: 24, spacing: 30 }),
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
