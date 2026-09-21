// 고양산업진흥원 용역계약 체결 서류 — 작성 서식 일괄
// 진흥원 제공 HWP 양식(3번 파일)의 서식 6종을 리본마켓 정보로 채운 사본.
// 원본은 한글 양식에 그대로 타이핑해 제출하고, 이 파일은 기재값 대조·검토용이다.
const fs = require('fs');
const {
  Document, Packer, Paragraph, TextRun, AlignmentType, PageBreak, ImageRun,
  Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle,
  VerticalAlign, LineRuleType, convertMillimetersToTwip,
} = require('docx');

const F = { ascii: '맑은 고딕', hAnsi: '맑은 고딕', eastAsia: '맑은 고딕', cs: '맑은 고딕', hint: 'eastAsia' };
const NAVY = '17365D', RULE = '9AA5B1', GRAY = 'D9D9D9', SOFT = 'F2F2F2', DIM = '767676', WARN = '9C2A2A';
const MARGIN = convertMillimetersToTwip(20);
const W = convertMillimetersToTwip(210) - MARGIN * 2;   // 170mm ≈ 9639 twip

// ── 계약 기본값 ────────────────────────────────────────────────────────────
const V = {
  계약명: '한국항공대학교 바이브 코딩(Vibe Coding) 기반 학생창업 경진대회 및 창업 특강 운영',
  계약기간: '계약일 ~ 2026. 11. 6.',
  계약금액: '금10,000,000원(금일천만원정) / 부가세 포함',
  보증금: '금1,000,000원(금일백만원정)',
  상호: '주식회사 리본마켓',
  대표자: '김 기 훈',
  주소: '경기도 평택시 이충로 49-29, 103호',
  사업자: '209-88-03446',
  연락처: '010-5843-0627',
  날짜: '2026.   9.   21.',
};
const 귀하 = '고양산업진흥원 재무관 귀하';
const 도장 = fs.readFileSync(process.argv[3]);

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
const 법조 = (t) => new Paragraph({
  spacing: { after: 110, line: 300 }, indent: { left: 200, hanging: 200 },
  children: [run(t, { size: 18 })],
});

const cell = (o) => new TableCell({
  width: { size: o.w, type: WidthType.DXA },
  columnSpan: o.span, verticalAlign: VerticalAlign.CENTER,
  shading: o.fill ? { type: ShadingType.CLEAR, fill: o.fill, color: 'auto' } : undefined,
  margins: { top: o.tight ? 34 : 70, bottom: o.tight ? 34 : 70, left: 100, right: 100 },
  children: o.children ?? [new Paragraph({
    alignment: o.align ?? AlignmentType.LEFT, spacing: { after: 0, line: 280 },
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

// 서명란 : 주소/상호/대표자 + 직인
const 서명란 = (opts = {}) => {
  const rows = [];
  if (opts.주소 !== false) rows.push(['주    소 :  ' + V.주소, false]);
  rows.push(['상    호 :  ' + V.상호, false]);
  rows.push(['대 표 자 :  ' + V.대표자, true]);
  return [
    P(V.날짜, { align: AlignmentType.CENTER, size: 21, before: 560, after: 420 }),
    ...rows.map(([t, seal]) => new Paragraph({
      alignment: AlignmentType.RIGHT,
      spacing: { before: seal ? 260 : 0, after: 130, line: 240, lineRule: LineRuleType.AUTO },
      indent: { right: 900 },
      children: seal
        ? [run(t, { size: 21 }), run('        ', { size: 21 }),
           new ImageRun({ data: 도장, type: 'png', transformation: { width: 50, height: 50 } })]
        : [run(t, { size: 21 })],
    })),
    P(귀하, { align: AlignmentType.CENTER, bold: true, size: 22, before: 420 }),
  ];
};
const PB = () => new Paragraph({ children: [new PageBreak()] });

// ══════════════════════════════════════════════════════ 0. 체크리스트
const mark = (s) => ({ t: s, align: AlignmentType.CENTER, bold: true,
  color: s === '작성완료' ? '1F6F3F' : (s === '확인필요' ? WARN : '000000') });

const 체크 = [
  H('계약 체결 서류 준비 현황'),
  P(`계약명 : ${V.계약명}`, { size: 18 }),
  P(`계약금액 : ${V.계약금액}    ·    계약기간 : ${V.계약기간}`, { size: 18, after: 300 }),

  P('1. 작성 서류', { bold: true, size: 22, after: 140 }),
  grid([620, 3900, 1300, 3819], [
    R(LBL('구분'), LBL('서류'), LBL('상태'), LBL('비고')),
    R(ctr('1)'), '최종 견적서(산출내역서)', mark('작성완료'), '기 작성본 사용 · 법인인감 날인'),
    R(ctr('2)'), '계약특수조건', mark('기재란 없음'), '제공 양식 그대로 제출'),
    R(ctr('3)'), '청렴계약 이행 서약서', mark('작성완료'), '본 파일 2쪽'),
    R(ctr('4)'), '계약보증금 지급 각서', mark('작성완료'), '3천만원 이하 → 보증보험 불요'),
    R(ctr('5)'), '안전보건관리 준수 서약서', mark('작성완료'), '본 파일 4쪽'),
    R(ctr('6)'), '각서 · 수의계약 배제사유 자가평가표', mark('확인필요'), '업종(등록)란만 미기재'),
    R(ctr('7)'), '수의계약 체결 제한 여부 확인서', mark('작성완료'), '법인 기준 체크 완료'),
  ]),

  P('2. 발급 서류 — 리본마켓이 직접 발급받아야 하는 서류', { bold: true, size: 22, before: 320, after: 140 }),
  grid([620, 3900, 5119], [
    R(LBL('구분'), LBL('서류'), LBL('유의사항')),
    R(ctr('1)'), '법인 인감증명서', '발행 3개월 이내 · 원본 (사용인감 날인 시 사용인감계 별도)'),
    R(ctr('2)'), '법인 등기부등본', '발행 3개월 이내 · 원본'),
    R(ctr('3)'), '지방세·국세 완납증명 각 1부', '유효기간 확인 · 원본'),
    R(ctr('4)'), '정부 수입인지', { t: '계약금액이 1천만원 "초과"가 아니므로 대상이 아닌 것으로 보임 — 담당자 확인 권장', color: WARN }),
    R(ctr('5)'), '사업자등록증', '사본에 원본대조필'),
    R(ctr('6)'), '통장 사본', '기업 명의 · 원본대조필'),
    R(ctr('7)'), '증빙서류 (해당 시)', '중소기업확인서, 여성기업, 벤처기업 등 보유분'),
    R(ctr('8)'), '위임장·재직증명서·신분증', '대표자가 직접 계약하면 신분증만 지참'),
  ]),

  P('3. 표준계약서 (진흥원 제공 1번 파일)', { bold: true, size: 22, before: 320, after: 140 }),
  P('상호·사업자등록번호·주소·대표자·연락처·계약금액·계약기간이 진흥원 측에서 이미 기재되어 있어 별도 작성이 필요하지 않다. 2부 출력하여 대표란에 날인하고 계약일자는 공란으로 둔다. 간인은 발주처 계약 천공으로 갈음한다.', { size: 18 }),
];

// ══════════════════════════════════════════════════════ 1. 청렴계약 서약서
const 청렴 = [
  PB(), H('청 렴 계 약 서 약 서'),
  법조('제1조(목적) 이 청렴계약서는 계약담당자와 계약상대자가 체결하는 공사ㆍ용역ㆍ물품계약에 있어 계약일반조건 외에 청렴계약을 위한 내용을 특별히 규정함을 목적으로 한다.'),
  법조('제2조(청렴계약이행 준수의무) 공사ㆍ물품ㆍ용역 등의 입찰에서 청렴계약 이행서약서를 제출하고 계약체결하거나 계약체결 할 상대자는 계약체결 및 이행과 관련하여 어떠한 명분으로도 관계공무원에게 직ㆍ간접적으로 금품ㆍ향응 등의 부당한 이익을 제공하여서는 아니 된다.'),
  법조('제3조(부정당업자의 입찰참가자격 제한) ① 입찰에 참가하는 자가 입찰가격이나 특정인의 낙찰을 위하여 담합 등 입찰의 자유경쟁을 방해하는 행위나 불공정 행위의 금지에 관한 사항에 대하여 다음 각 호에서 정하는 바에 의하여 국가 및 지방자치단체(국가 및 지방자치단체가 출연한 기관 포함, 이하 “국가 등”이라 한다)에서 시행하는 입찰에 참가 제한을 받게 된다.'),
  법조('② 입찰담합 등 불공정행위를 한 경우에는 제1항과 병행하여 「독점규제 및 공정거래에 관한 법령」에 따라 공정거래위원회에 고발 등 조치를 하는데 일체 이의를 제기하지 않는다.'),
  법조('③ 입찰, 낙찰, 계약의 체결 및 이행, 「지방자치단체를 당사자로 하는 계약에 관한 법률」 제16조에 따른 감독, 제17조에 따른 검사와 관련하여 직접 또는 간접적인 사례(謝禮), 증여, 금품·향응을 제공하지 않으며, 이를 위반하였을 때에는 국가 등에서 시행하는 입찰에 입찰참가자격 제한 처분을 받은 날로부터 3개월에서 2년의 기간 동안 입찰참가제한을 받게 된다.'),
  법조('④ 공정한 직무수행을 방해하는 알선·청탁을 통하여 입찰 또는 계약과 관련된 특정 정보의 제공을 요구하거나 받는 행위를 한 자는 입찰참가제한 또는 민·형사상의 책임을 져야 한다.'),
  법조('⑤ 제1항 내지 제4항의 규정에 의하여 입찰참가자격을 제한하는 고양시의 처분을 받은 자는 고양시를 상대로 손해배상을 청구하거나 배제하는 입찰에 관하여 민ㆍ형사상 이의를 제기하지 않는다.'),
  법조('제4조(계약해지 등) 입찰과정에서 거짓 서류를 제출하여 부당하게 낙찰 받은 자 및 입찰, 낙찰, 계약체결 또는 계약이행 과정에서 관계 공무원 등에게 직접 또는 간접적으로 사례, 증여, 금품·향응 등을 제공한 사실이 드러날 경우에는 정해진 바에 의하여 당해 계약에 대한 조치를 받는다.'),
  법조('제5조(기타사항) 계약상대자는 임․직원(하도급업체 포함)과 대리인이 관계공무원에게 뇌물을 제공하거나 담합 등 불공정행위를 하지 않도록 하는 업체윤리강령과 내부비리 제보자에 대하여도 일체의 불이익 처분을 하지 않는 사규를 제정하도록 적극 노력한다.'),
  P(V.날짜, { align: AlignmentType.CENTER, size: 21, before: 520, after: 420 }),
  new Paragraph({ alignment: AlignmentType.RIGHT, indent: { right: 900 },
    spacing: { after: 130, line: 240, lineRule: LineRuleType.AUTO },
    children: [run('서약자     상    호 :  ' + V.상호, { size: 21 })] }),
  new Paragraph({ alignment: AlignmentType.RIGHT, indent: { right: 900 },
    spacing: { before: 260, after: 130, line: 240, lineRule: LineRuleType.AUTO },
    children: [run('대 표 자 :  ' + V.대표자, { size: 21 }), run('        ', { size: 21 }),
               new ImageRun({ data: 도장, type: 'png', transformation: { width: 50, height: 50 } })] }),
  P(귀하, { align: AlignmentType.CENTER, bold: true, size: 22, before: 420 }),
];

// ══════════════════════════════════════════════════════ 2. 계약보증금 지급 각서
const 보증 = [
  PB(), H('계약보증금 지급 각서'),
  grid([1900, 7739], [
    R(LBL('1. 계 약 명'), V.계약명),
    R(LBL('2. 계약기간'), V.계약기간),
    R(LBL('3. 계약금액'), V.계약금액),
    R(LBL('4. 계약보증금'), V.보증금 + '   (계약금액의 10%)'),
    R(LBL('5. 납부면제사유'), '지방자치단체를 당사자로 하는 계약에 관한 법률 시행령 제53조 (계약보증금 면제)'),
  ]),
  P('위와 같이 계약보증금의 납부를 지방자치단체를 당사자로 하는 계약에 관한 법률 시행령 제53조의 규정에 의하여 그 납부를 면제하고 계약보증금 귀속 사유가 발생하였을 때에는 계약보증금 해당금액을 현금으로 지급할 것을 확약하며 이 지급각서를 제출합니다.', { before: 300, size: 19 }),
  P('(※ 계약보증금 지급각서는 계약기간이 연장된 경우에 실제 계약이행 완료일까지 본 계약 보증이 유효합니다.)', { size: 17, color: DIM }),
  ...서명란(),
];

// ══════════════════════════════════════════════════════ 3. 안전보건관리 준수 서약서
const 안전 = [
  PB(), H('안전보건관리 준수 서약서'),
  P('본인은 귀 기관과 계약을 수행함에 있어 산업재해예방을 위하여 관련 법규에서 정한 필수사항을 철저히 준수할 것을 다음과 같이 서약합니다.', { after: 260 }),
  grid([6200, 3439], [
    R({ t: '「산업안전보건법」, 「중대재해처벌법」 등 안전 관련 법규를 준수하겠습니다.', bold: true },
      { t: '예 ( ○ )          아니오 (    )', align: AlignmentType.CENTER }),
    R(LBL('계 약 명'), { t: V.계약명, size: 17 }),
  ]),
  P('당사(본인)는 본 계약을 수행함에 있어 위에 언급한 내용대로 계약 및 관련 법규를 성실히 이행할 것이며, 만일 이를 이행하지 않을 경우 계약해지, 입찰참가 자격제한조치 등 불이익 처분을 받더라도 하등의 이의를 제기하지 아니할 것을 확약합니다.', { before: 300 }),
  ...서명란(),
];

// ══════════════════════════════════════════════════════ 4. 각서
const 각서 = [
  PB(), H('각           서'),
  grid([1900, 7739], [
    R(LBL('업 체 명'), V.상호),
    R(LBL('대 표 자'), V.대표자.replace(/ /g, '')),
    R(LBL('소 재 지'), V.주소),
    R(LBL('업종(등록)'), { t: '(사업자등록증상 업태·종목 기재)', color: WARN }),
  ]),
  P('상기 본인(법인)은 귀 기관과 수의계약을 체결함에 있어서 붙임 배제사유 중 어느 사유에도 해당되지 않으며 차후에 이러한 사실이 발견된 경우 계약의 해제ㆍ해지 및 부정당업자 제재 처분을 받아도 하등의 이유를 제기하지 않겠습니다.', { before: 300 }),
  P('붙임 :  <별표1> 수의계약 배제사유 1부.', { before: 180, size: 18 }),
  P('           <별표2> 수의계약 배제사유 자가평가표 1부.', { size: 18 }),
  ...서명란({ 주소: false }),
];

// ══════════════════════════════════════════════════════ 5. 자가평가표
const 평가항목 = [
  '① 견적서 제출 마감일 현재 부도 · 파산 · 해산 · 영업정지 등이 확정된 경우',
  '② 입찰참가자격 제한기간 중에 있는 자',
  '③ 견적서 제출 마감일을 기준으로 시행령 제92조 또는 다른 법령에 따라 부실이행, 담합행위, 입찰ㆍ계약 서류의 허위ㆍ위조 제출, 입찰·낙찰·계약이행 관련 뇌물 제공으로 부정당업자 제재 처분을 받고 그 종료일로부터 3개월이 지나지 아니한 자',
  '④ 공사 또는 기술용역의 경우 기술자 보유현황이 관련법령에 따른 업종등록 기준에 미달하는 자',
  '⑤ 견적서 제출 마감일 기준 최근 3개월 이내에 해당 지방자치단체의 입찰ㆍ계약 및 그 이행과 관련하여 10일 이상 지연배상금 부과, 정당한 이행명령 거부, 불법하도급, 5회 이상 하자보수 또는 물의를 일으키는 등 신용이 떨어져 계약 체결이 곤란하다고 판단되는 자',
  '⑥ 견적서 제출 마감일 기준 최근 3개월 이내에 해당 지방자치단체와의 계약 및 그 이행과 관련하여 정당한 이유 없이 계약에 응하지 아니하거나 포기서를 제출한 사실이 있는 자',
  '⑦ 수의계약 체결일 현재 법 제33조(입찰 및 계약체결 제한)에 해당하는 자',
  '⑧ 발주기관이 제한한 자격요건 등을 충족하지 아니한 자',
  '⑨ 그밖에 계약담당자가 계약이행능력이 없다고 판단되는 명백한 증거가 있는 자',
  '⑩ 「재난 및 안전관리 기본법」 제60조에 따라 특별재난지역으로 선포된 지역의 재난복구공사(용역)의 경우 배제여부 심사일 현재 계약금액 5천만 원 이상 해당 업종 관급공사 또는 계약금액 2천만 원 이상 관급용역이 3건 이상인 자',
];
const 평가 = [
  PB(), H('수의계약 배제사유 자가평가표'),
  grid([7639, 1000, 1000], [
    R(LBL('평    가    내    용'), LBL('적정'), LBL('부적정')),
    ...평가항목.map((t) => R({ t, size: 16 }, ctr('○', { bold: true, size: 22 }), ctr(''))),
  ]),
  P('※ 수의계약 배제사유 평가는 계약체결 전 또는 후에 실시하며, 평가내용 중에 배제 사유가 있는 경우 수의계약을 체결할 수 없고 계약 이후에는 계약을 해제ㆍ해지한다.', { before: 200, size: 16, color: DIM }),
  P('※ 평가내용을 확인하여 해당하지 아니하는 경우 적정란에 ○ 표시함.', { size: 16, color: DIM }),
];

// ══════════════════════════════════════════════════════ 6. 수의계약 체결 제한 여부 확인서
const 확인항목 = [
  '① 발주기관의 소속 고위임직원, 배우자, 고위임직원의 직계존속·비속 또는 생계를 같이하는 배우자의 직계존속·비속에 해당하는가?',
  '② 계약 업무를 법령상·사실상 담당하는 임직원, 배우자, 임직원의 직계존속·비속 또는 생계를 같이하는 배우자의 직계존속·비속에 해당하는가?',
  '③ 발주기관(산하기관)의 감독기관 소속 고위임직원, 배우자, 고위임직원의 직계존속·비속 또는 생계를 같이하는 배우자의 직계존속·비속에 해당하는가?',
  '④ 발주기관(자회사)의 모회사 소속 고위임직원, 배우자, 고위임직원의 직계존속·비속 또는 생계를 같이하는 배우자의 직계존속·비속에 해당하는가?',
  '⑤ 상임위원회 위원인 국회의원, 배우자, 국회의원의 직계존속·비속 또는 생계를 같이하는 배우자의 직계존속·비속에 해당하는가?',
  '⑥ 공공기관을 감사 또는 조사하는 지방의회의 의원, 배우자, 의원의 직계존속·비속 또는 생계를 같이하는 배우자의 직계존속·비속에 해당하는가?',
];
const 확인 = [
  PB(), H('수의계약 체결 제한 여부 확인서'),
  P('• 해당하는 [  ]에 √ 표시를 합니다.', { size: 17, color: DIM, after: 110 }),
  grid([1500, 3200, 1500, 3439], [
    R({ t: '발 주 자', bold: true, fill: GRAY, align: AlignmentType.CENTER, span: 4 }),
    R(LBL('발주기관'), '고양산업진흥원', LBL('발주부서'), 'ESG경영팀'),
    R(LBL('발주날짜'), '2026.   9.', LBL('발주내용'), '[  ] 공사   [√] 용역   [  ] 물품   [  ] 기타'),
    R(LBL('계약명'), { t: V.계약명, span: 3, size: 16 }),
    R(LBL('수의계약 사유'), { t: '「지방자치단체를 당사자로 하는 계약에 관한 법률 시행령」 제25조', span: 3, size: 16 }),
  ]),
  P('', { after: 60 }),
  grid([1500, 3200, 1500, 3439], [
    R({ t: '계약상대자 (확인인)', bold: true, fill: GRAY, align: AlignmentType.CENTER, span: 4 }),
    R(LBL('성    명'), V.대표자.replace(/ /g, ''), LBL('소    속'), V.상호),
    R(LBL('구    분'), '[  ] 개인   [√] 법인   [  ] 단체   [  ] 기타', LBL('연 락 처'), V.연락처),
    R(LBL('주    소'), { t: V.주소, span: 3 }),
  ]),
  P('', { after: 60 }),
  grid([7139, 2500], [
    R({ t: '수의계약 체결 제한 확인사항', bold: true, fill: GRAY, align: AlignmentType.CENTER, span: 2 }),
    ...확인항목.map((t) => R({ t, size: 15, tight: true },
      { t: '[  ] 예   [  ] 아니오   [√] 해당없음', align: AlignmentType.CENTER, size: 15, tight: true })),
    R({ t: '⑦ ①부터 ⑥까지 어느 하나에 해당하는 사람이 대표자인 법인 또는 단체에 해당하는가?', size: 15, tight: true },
      { t: '[  ] 예   [√] 아니오', align: AlignmentType.CENTER, size: 15, tight: true }),
    R({ t: '⑧ ①부터 ⑥까지 어느 하나에 해당하는 사람과 특수한 관계의 사업자(임직원, 배우자, 임직원의 직계존속·비속, 생계를 같이하는 배우자의 직계존속·비속이 단독으로 또는 합산하여 발행주식 총수의 100분의 30 이상, 출자지분 총수의 100분의 30 이상, 자본금 총액의 100분의 50 이상을 소유하고 있는 법인 또는 단체)에 해당하는가?', size: 15, tight: true },
      { t: '[  ] 예   [√] 아니오', align: AlignmentType.CENTER, size: 15, tight: true }),
  ]),
  P('「공직자의 이해충돌 방지법」 제12조에 따른 수의계약 체결 제한에 대하여 위와 같이 확인합니다. 만약 위 사항이 사실과 다른 경우에는 어떠한 처벌이나 불이익도 감수할 것을 서약합니다.', { before: 120, size: 17 }),
  P('2026년    9월    21일', { align: AlignmentType.CENTER, size: 21, before: 180, after: 170 }),
  new Paragraph({ alignment: AlignmentType.RIGHT, indent: { right: 900 },
    spacing: { after: 120, line: 240, lineRule: LineRuleType.AUTO },
    children: [run('계약상대자(확인인)   회사명 :  ' + V.상호, { size: 21 }), run('     ', { size: 21 }),
               new ImageRun({ data: 도장, type: 'png', transformation: { width: 50, height: 50 } })] }),
  P(귀하, { align: AlignmentType.CENTER, bold: true, size: 22, before: 190 }),
  P('※ 법인은 ①~⑥을 「해당없음」, ⑦·⑧을 「예/아니오」로 표기한다. (공직자의 이해충돌 방지제도 운영지침 [별지 제10호 서식])', { before: 300, size: 16, color: DIM }),
];

const doc = new Document({
  styles: { default: { document: { run: { font: F, size: 19 }, paragraph: { spacing: { line: 300 } } } } },
  sections: [{
    properties: { page: { margin: { top: convertMillimetersToTwip(22), bottom: convertMillimetersToTwip(18), left: MARGIN, right: MARGIN } } },
    children: [...체크, ...청렴, ...보증, ...안전, ...각서, ...평가, ...확인],
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
