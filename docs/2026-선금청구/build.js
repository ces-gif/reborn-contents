// 고양산업진흥원 선금 청구 서류 — 작성 서식 일괄
// 진흥원 제공 한글 양식(선금·잔금 청구 시 필요한 서류)의 서식 3종을
// 리본마켓 정보로 채운 사본. 날짜와 직인은 공란으로 두고 연도만 표기한다.
const fs = require('fs');
const {
  Document, Packer, Paragraph, TextRun, AlignmentType, PageBreak,
  Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle,
  VerticalAlign, LineRuleType, VerticalMergeType, convertMillimetersToTwip,
} = require('docx');

const F = { ascii: '맑은 고딕', hAnsi: '맑은 고딕', eastAsia: '맑은 고딕', cs: '맑은 고딕', hint: 'eastAsia' };
const NAVY = '17365D', RULE = '9AA5B1', GRAY = 'D9D9D9', SOFT = 'F2F2F2', DIM = '767676', WARN = '9C2A2A', OK = '1F6F3F';
const MARGIN = convertMillimetersToTwip(20);

const V = {
  계약명: '한국항공대학교 바이브 코딩(Vibe Coding) 기반 학생창업 경진대회 및 창업 특강 운영',
  계약기간: '계약일 ~ 2026. 11. 6.',
  계약금액: '금10,000,000원(금일천만원정)',
  선금액: '금5,000,000원(금오백만원정)',
  선금비율: '50%',
  잔금액: '금5,000,000원(금오백만원정)',
  보증만기: '2027. 1. 5.',
  상호: '주식회사 리본마켓',
  대표자: '김 기 훈',
  주소: '경기도 평택시 이충로 49-29, 103호',
  사업자: '209-88-03446',
  연락처: '010-5843-0627',
  날짜: '2026.    9.    28.',
};
const 귀하 = '고양산업진흥원 귀하';

const run = (t, o = {}) => new TextRun({
  text: t, bold: o.bold, color: o.color, size: o.size ?? 19, font: F, characterSpacing: o.spacing,
});
const P = (t, o = {}) => new Paragraph({
  alignment: o.align, indent: o.indent,
  spacing: { before: o.before ?? 0, after: o.after ?? 110, line: o.line ?? 300 },
  children: [run(t, o)],
});
const H = (t) => new Paragraph({
  alignment: AlignmentType.CENTER, spacing: { before: 0, after: 320, line: 340 },
  children: [run(t, { bold: true, size: 32, spacing: 80 })],
});
const 항목 = (t) => new Paragraph({
  spacing: { after: 130, line: 300 }, indent: { left: 280, hanging: 280 },
  children: [run(t, { size: 20 })],
});
const 법조 = (t) => new Paragraph({
  spacing: { after: 110, line: 300 }, indent: { left: 200, hanging: 200 },
  children: [run(t, { size: 18 })],
});

const cell = (o) => new TableCell({
  width: { size: o.w, type: WidthType.DXA },
  columnSpan: o.span, verticalAlign: VerticalAlign.CENTER,
  verticalMerge: o.vm,
  shading: o.fill ? { type: ShadingType.CLEAR, fill: o.fill, color: 'auto' } : undefined,
  margins: { top: o.tight ? 34 : 64, bottom: o.tight ? 34 : 64, left: 90, right: 90 },
  children: o.children ?? [new Paragraph({
    alignment: o.align ?? AlignmentType.LEFT, spacing: { after: 0, line: 270 },
    children: [run(o.t ?? '', { bold: o.bold, size: o.size ?? 18, color: o.color })],
  })],
});
const B = (sz, c) => ({ style: BorderStyle.SINGLE, size: sz, color: c });
const grid = (widths, rows) => new Table({
  columnWidths: widths,
  width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA },
  borders: { top: B(8, NAVY), bottom: B(8, NAVY), left: B(4, RULE), right: B(4, RULE),
             insideHorizontal: B(4, RULE), insideVertical: B(4, RULE) },
  rows: rows.map((cs) => new TableRow({
    children: cs.map((c, i) => {
      const o = typeof c === 'string' ? { t: c } : { ...c };
      o.w = o.span ? widths.slice(i, i + o.span).reduce((a, b) => a + b, 0) : widths[i];
      return cell(o);
    }),
  })),
});
const R = (...c) => c;
const LBL = (t) => ({ t, bold: true, fill: SOFT, align: AlignmentType.CENTER });
const ctr = (t, o = {}) => ({ t, align: AlignmentType.CENTER, ...o });
const rgt = (t, o = {}) => ({ t, align: AlignmentType.RIGHT, ...o });
const MERGE = { vm: VerticalMergeType.CONTINUE };
const VM = { vm: VerticalMergeType.RESTART, bold: true, align: AlignmentType.CENTER };

// 신청자 서명란 — 날짜는 연도만, 직인은 (인)
const 서명란 = (라벨, opts = {}) => [
  P(V.날짜, { align: AlignmentType.CENTER, size: 21, before: opts.before ?? 480, after: 400 }),
  ...[['상  호 :  ' + V.상호, false],
      ['주  소 :  ' + V.주소, false],
      ['대표자 :  ' + V.대표자, true],
      ...(opts.연락처 ? [['연락처 :  ' + V.연락처, false]] : [])]
    .map(([t, seal], i) => new Paragraph({
      alignment: AlignmentType.LEFT,
      spacing: { before: seal ? 200 : 0, after: 120, line: 240, lineRule: LineRuleType.AUTO },
      indent: { left: 4200 },
      children: [run((i === 0 ? 라벨 + '  ' : '          ') + t, { size: 21 }),
                 ...(seal ? [run('          (인)', { size: 21 })] : [])],
    })),
  P(귀하, { align: AlignmentType.CENTER, bold: true, size: 22, before: 400 }),
];
const PB = () => new Paragraph({ children: [new PageBreak()] });
const mark = (s) => ({ t: s, align: AlignmentType.CENTER, bold: true,
  color: s === '작성완료' ? OK : (s === '해당없음' ? DIM : WARN) });

// ══════════════════════════════════════════════════ 0. 체크리스트
const W1 = [620, 2700, 1300, 5019];
const 체크 = [
  H('선금 청구 서류 준비 현황'),
  P(`계약명 : ${V.계약명}`, { size: 18 }),
  P(`계약금액 : ${V.계약금액} (부가세 포함)    ·    계약기간 : ${V.계약기간}`, { size: 18 }),
  P(`선금 청구액 : ${V.선금액} — 계약금액의 ${V.선금비율}  (한도 70% 이내)`,
    { size: 18, bold: true, after: 300 }),

  P('1. 선금 청구 시 제출 서류', { bold: true, size: 22, after: 140 }),
  grid(W1, [
    R(LBL('구분'), LBL('서류'), LBL('상태'), LBL('비고')),
    R(ctr('1)'), '청구 공문', mark('작성완료'), '본 파일 2쪽 — 계약건명·계약기간·계약금액·선금청구액 기재, 날인 필수'),
    R(ctr('2)'), '선금 신청서', mark('작성완료'), '본 파일 3쪽'),
    R(ctr('3)'), '선금 사용 계획서', mark('작성완료'), '본 파일 4쪽 [붙임1]'),
    R(ctr('4)'), '선금 지급에 대한 각서', mark('작성완료'), '본 파일 5쪽 [붙임2]'),
    R(ctr('5)'), '선금보증서', mark('발급필요'),
      { t: '이행(선금)보증보험증권 — 보증기간 증권발급일 ~ 2027. 1. 5. 이상(계약종료일 + 60일), 보증금액 5,000,000원 + 보증기간 이자상당액', color: WARN, size: 17 }),
    R(ctr('6)'), '지역개발채권 매입필증', mark('해당없음'),
      { t: '계약금액 2,000만원 미만(부가세 포함 2,200만원 미만)은 제외 대상 — 본 계약 10,000,000원', size: 17 }),
    R(ctr('7)'), '지방세·국세 완납증명', mark('발급필요'), '각 1부 · 유효기간 확인'),
    R(ctr('8)'), '세금계산서', mark('발급필요'), '전자세금계산서 발행'),
    R(ctr('9)'), '통장 사본', mark('발급필요'), '기업 명의 1부 · 원본대조필'),
  ]),

  PB(),
  P('2. 잔금 청구 시 제출 서류  (행사 종료 · 검수 후)', { bold: true, size: 22, after: 140 }),
  P(`잔금 예정액 : ${V.잔금액} — 계약금액에서 선금 ${V.선금액}을 제외한 금액`,
    { size: 18, after: 140 }),
  grid(W1, [
    R(LBL('구분'), LBL('서류'), LBL('상태'), LBL('비고')),
    R(ctr('1)'), '청구 공문', mark('행사 후'), '계약건명·계약기간·계약금액·잔금청구액 기재, 날인 필수'),
    R(ctr('2)'), '하자보증서', mark('해당없음'), '공사 계약이 아닌 용역이므로 하자 보증 대상 아님 — 담당자 확인 권장'),
    R(ctr('3)'), '지역개발채권 매입필증', mark('해당없음'),
      '잔금 2천만원 미만 · 선금 시 필증 미제출(제외 대상)이므로 잔금에도 해당 없음'),
    R(ctr('4)'), '정산합의서 및 정산내역서', mark('행사 후'), '정산 사항 발생 시'),
    R(ctr('5)'), '지방세·국세 완납증명', mark('행사 후'), '각 1부 · 유효기간 확인'),
    R(ctr('6)'), '4대보험 완납증명', mark('해당없음'), '공사 계약에 한해 필수 — 용역은 담당자 확인'),
    R(ctr('7)'), '세금계산서', mark('행사 후'), '전자세금계산서 발행'),
    R(ctr('8)'), '통장 사본', mark('행사 후'), '기업 명의 1부 · 원본대조필'),
  ]),
  P('※ 본 작성본의 작성일은 2026. 9. 28.로 기재되어 있다. 직인은 공란이므로 출력 후 대표자(인)란에 법인인감 또는 사용인감을 날인한다.',
    { before: 260, size: 18, color: WARN }),
];

// ══════════════════════════════════════════════════ 1. 청구 공문
const 공문 = [
  PB(), H('선 금 청 구'),
  grid([1900, 7739], [
    R(LBL('수    신'), '고양산업진흥원장'),
    R(LBL('제    목'), '「' + V.계약명 + '」 선금 청구'),
  ]),
  P('1. 귀 기관의 무궁한 발전을 기원합니다.', { before: 320, size: 20 }),
  P('2. 당사는 귀 기관과 체결한 아래 용역계약과 관련하여, 「지방회계법」 제35조 및 같은 법 시행령 제44조와 행정안전부 예규 「지방자치단체 입찰 및 계약 집행기준」에 따라 다음과 같이 선금을 청구하오니 검토 후 지급하여 주시기 바랍니다.',
    { size: 20, after: 260 }),
  grid([1900, 7739], [
    R(LBL('계 약 명'), V.계약명),
    R(LBL('계약기간'), V.계약기간),
    R(LBL('계약금액'), V.계약금액 + '  (부가가치세 포함)'),
    R(LBL('선금청구액'), { t: V.선금액 + '  /  계약금액의 ' + V.선금비율 + '  (한도 70% 이내)', bold: true }),
    R(LBL('보증방법'), '이행(선금)보증보험증권 제출'),
  ]),
  P('붙임  1. 선금 신청서 1부.', { before: 240, size: 19 }),
  P('         2. 선금 사용 계획서 1부.', { size: 19 }),
  P('         3. 선금 지급에 대한 각서 1부.', { size: 19 }),
  P('         4. 이행(선금)보증보험증권 사본 1부.', { size: 19 }),
  P('         5. 지방세·국세 완납증명 각 1부.', { size: 19 }),
  P('         6. 전자세금계산서 1부.', { size: 19 }),
  P('         7. 통장 사본 1부.  끝.', { size: 19 }),
  ...서명란('청구인', { before: 420, 연락처: true }),
];

// ══════════════════════════════════════════════════ 2. 선금 신청서
const 신청 = [
  PB(), H('선 금 신 청 서'),
  항목('○ 계 약 명 :  ' + V.계약명),
  항목('○ 계약금액 :  ' + V.계약금액),
  항목('○ 계약기간 :  ' + V.계약기간),
  항목('○ 선금신청액 :  ' + V.선금액 + '  /  ' + V.선금비율 + '  (한도 70% 이내)'),
  항목('○ 선금보증방법 :  이행(선금)보증보험증권 제출'),
  P('위와 같이 체결한 계약에 행정안전부 계약 예규 「지방자치단체 입찰 및 계약 집행기준」을 숙지하고 본 용역의 원활한 추진을 위해 선금을 신청합니다.',
    { before: 320, size: 20, indent: { firstLine: 200 } }),
  P('붙임  1. 선금사용계획서 1부.', { before: 240, size: 19 }),
  P('         2. 선금지급에 대한 각서 1부.', { size: 19 }),
  ...서명란('신청자'),
];

// ══════════════════════════════════════════════════ 3. 선금 사용 계획서
const 사용내역 = [
  ['인건비', '1:1 창업 멘토링비', '전문가 1:1 멘토링', '팀', '10', '150,000', '1,500,000', ''],
  ['인건비', '예선 서류 평가료', '내/외부 심사위원', '명', '2', '150,000', '300,000', ''],
  ['인건비', '창업 특강 강사료', '강사수당 지급기준 나급 · 2시간', '건', '1', '250,000', '250,000', ''],
  ['재료비', 'AI 코딩 도구 이용료', '멘토링 대상 10개 팀 · 1인당 50,000원', '명', '30', '50,000', '1,500,000', ''],
  ['재료비', '홍보물 · 인쇄비', '포스터, 현수막, 자료집, 상장', '식', '1', '700,000', '700,000', ''],
  ['경  비', '행사 운영비', '식대·다과, 소모품, 현장 운영 인력', '식', '1', '750,000', '750,000', '일부'],
];
const W2 = [1000, 1900, 2239, 600, 600, 1300, 1400, 600];
const 계획 = [
  PB(),
  P('[붙임1]', { size: 19, bold: true, after: 140 }),
  H('선 금 사 용 계 획 서'),
  항목('○ 계 약 명 :  ' + V.계약명),
  항목('○ 계약기간 :  ' + V.계약기간),
  항목('○ 선금신청액 :  ' + V.선금액),
  P('○ 신청내역', { before: 200, after: 140, size: 20 }),
  grid(W2, [
    R(LBL('구분'), LBL('경비별'), LBL('규  격'), LBL('단위'), LBL('수량'), LBL('단가'), LBL('금  액'), LBL('비고')),
    R({ t: '계', bold: true, fill: GRAY, align: AlignmentType.CENTER, span: 6 },
      { t: '5,000,000', bold: true, fill: GRAY, align: AlignmentType.RIGHT }, { t: '', fill: GRAY }),
    ...사용내역.map((r, i) => {
      const prev = i > 0 ? 사용내역[i - 1][0] : null;
      const first = r[0] !== prev;
      return R(first ? { t: r[0], ...VM, size: 17, tight: true } : { ...MERGE, tight: true },
        { t: r[1], size: 17, tight: true }, { t: r[2], size: 16, tight: true },
        ctr(r[3], { size: 17, tight: true }), ctr(r[4], { size: 17, tight: true }),
        rgt(r[5], { size: 17, tight: true }), rgt(r[6], { size: 17, bold: true, tight: true }),
        ctr(r[7], { size: 16, tight: true }));
    }),
  ]),
  P('※ 행사 운영비는 계약 총액 2,050,000원 중 특강·멘토링 준비에 필요한 750,000원만 선금으로 집행하며, 잔여분과 상금 및 결승 심사수당은 행사 이후 집행하므로 잔금으로 청구합니다.',
    { before: 200, size: 17, color: DIM }),
  P('※ 선금은 계약목적 달성 이외의 용도로 사용하지 않으며, 별도 계좌로 관리하여 위 계획에 따라 노임 지급과 자재 확보에 우선 집행합니다. 사용 계획을 변경할 필요가 있을 때에는 사전에 선금사용 변경계획서를 제출하겠습니다.',
    { size: 17, color: DIM }),
  P('위와 같이 선금사용계획서를 제출하며 계획서를 준수하여 계약목적 달성을 위한 용도로만 사용할 것을 확약합니다.',
    { before: 260, size: 20, indent: { firstLine: 200 } }),
  ...서명란('신청자', { before: 400 }),
];

// ══════════════════════════════════════════════════ 4. 각서
const 각서 = [
  PB(),
  P('[붙임2]', { size: 19, bold: true, after: 140 }),
  H('선 금 지 급 에  대 한  각 서'),
  항목('○ 계 약 명 :  ' + V.계약명),
  항목('○ 계약금액 :  ' + V.계약금액),
  항목('○ 계약기간 :  ' + V.계약기간),
  항목('○ 선금신청액 :  ' + V.선금액),
  P('지방회계법 제35조 및 동법 시행령 제44조의 규정에 의한 선금을 수령함에 있어, 행정안전부 예규 「지방자치단체 입찰 및 계약 집행기준」(제1장 2절 선금ㆍ대가 지급)을 준수하고, 선금을 계약목적 달성 이외의 용도로 사용하지 않겠으며 위반 시는 이행(선금)보증서에 의한 보증금액으로 상환하겠음을 확약하며 이에 각서를 제출합니다.',
    { before: 300, after: 260, size: 19, indent: { firstLine: 200 } }),
  P('[ 선금 지급 조건 ]', { align: AlignmentType.CENTER, bold: true, size: 21, after: 180 }),
  법조('제1조(총칙) 지방자치단체를 당사자로 하는 계약에 관한 법률 제18조의 규정에 의하여 선금을 지급하고자 할 때에는 이 조건에 의한다.'),
  법조('제2조(선금의 사용) ① 선금은 당해 계약목적 달성을 위한 용도 이외 다른 목적에 사용해서는 안되고 선금 사용계획서에 따라 노임 지급과 자재확보 등에 우선 사용하여야 한다.'),
  법조('② 계약상대자는 선금 수령 시 별도의 계좌에 의하여 선금을 관리하여야 한다.'),
  법조('③ 계약상대자는 선금을 사용할 때에는 사용계획에 따라 집행하여야 하며, 계약이행이 원활하지 않아 선금이 다른 목적에 사용되었는지 확인할 필요가 있다고 판단되는 경우 사용내역서를 제출하게 할 수 있다.'),
  법조('④ 계약상대자는 선금 사용계획과 다르게 선금을 사용하고자 할 경우에는 사전에 선금사용 변경계획서를 제출하여야 한다.'),
  법조('제3조(선금의 반환) 계약상대자는 지방자치단체 입찰 및 계약 집행기준 제1장 2절 선금ㆍ대가 지급(행정안전부 예규) 사항을 위반하여 선금반환 청구가 있을 경우에는 반드시 이에 응하여야 한다.'),
  법조('제5조(기타사항) 이 조건에 규정되지 않은 사항은 「지방자치단체 입찰 및 계약 집행기준」 제6장 선금ㆍ대가 지급요령(행정안전부 예규)에 따른다.'),
  ...서명란('신청자', { before: 360 }),
];

const doc = new Document({
  styles: { default: { document: { run: { font: F, size: 19 }, paragraph: { spacing: { line: 300 } } } } },
  sections: [{
    properties: { page: { margin: { top: convertMillimetersToTwip(22), bottom: convertMillimetersToTwip(18), left: MARGIN, right: MARGIN } } },
    children: [...체크, ...공문, ...신청, ...계획, ...각서],
  }],
});

const ORDER = ['top', 'left', 'bottom', 'right', 'between', 'bar'];
const fix = (x) => x.replace(/<w:pBdr>([\s\S]*?)<\/w:pBdr>/g, (_, inner) => {
  const k = inner.match(/<w:(?:top|left|bottom|right|between|bar)\b[^>]*\/>/g) || [];
  return `<w:pBdr>${k.slice().sort((a, b) => ORDER.indexOf(a.match(/<w:(\w+)/)[1]) - ORDER.indexOf(b.match(/<w:(\w+)/)[1])).join('')}</w:pBdr>`;
});
Packer.toBuffer(doc)
  .then((b) => require('jszip').loadAsync(b))
  .then(async (z) => {
    z.file('word/document.xml', fix(await z.file('word/document.xml').async('string')));
    return z.generateAsync({ type: 'nodebuffer', compression: 'DEFLATE' });
  })
  .then((b) => { fs.writeFileSync(process.argv[2], b); console.log('wrote', process.argv[2], b.length); });
