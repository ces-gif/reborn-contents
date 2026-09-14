// 2026 바이브 코딩 특강 및 경진대회 계획(안)
// 2025년 계획(안)(hwpx)의 구성 — 개요 / 세부 계획(시간표) / 예산(안) — 을 그대로 따른다.
const fs = require('fs');
const {
  Document, Packer, Paragraph, TextRun, AlignmentType, HeadingLevel,
  Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle,
  VerticalAlign, Header, Footer, PageNumber, PageBreak,
  convertMillimetersToTwip,
} = require('docx');

const F = { ascii: '맑은 고딕', hAnsi: '맑은 고딕', eastAsia: '맑은 고딕', cs: '맑은 고딕', hint: 'eastAsia' };
const NAVY = '17365D', NAVY_L = '2E5C8A', RULE = 'BFC9D4', ZEBRA = 'F4F7FB', BOX = 'EEF3F9', GRAY = '767676';
const MARGIN = convertMillimetersToTwip(20);
const CONTENT = convertMillimetersToTwip(210) - MARGIN * 2;

const run = (t, o = {}) => new TextRun({
  text: t, bold: o.bold, color: o.color, size: o.size ?? 21, font: F, characterSpacing: o.spacing,
});
const P = (t, o = {}) => new Paragraph({
  alignment: o.align, indent: o.indent,
  spacing: { before: o.before ?? 0, after: o.after ?? 110, line: o.line ?? 330 },
  children: [run(t, o)],
});

// □ 대제목
const H = (t) => new Paragraph({
  heading: HeadingLevel.HEADING_1,
  spacing: { before: 340, after: 160, line: 300 },
  border: { bottom: { style: BorderStyle.SINGLE, size: 10, color: NAVY, space: 5 } },
  children: [run('□ ' + t, { bold: true, size: 24, color: NAVY })],
});
// ○ 항목
const O = (t) => new Paragraph({
  spacing: { after: 90, line: 330 },
  indent: { left: 220 },
  children: [run('○ ' + t, {})],
});
// - 세부
const D = (t) => new Paragraph({
  spacing: { after: 80, line: 330 },
  indent: { left: 620, hanging: 200 },
  children: [run('- ' + t, { size: 20 })],
});

const callout = (t) => new Paragraph({
  spacing: { before: 140, after: 140, line: 320 },
  indent: { left: 160, right: 160 },
  shading: { type: ShadingType.CLEAR, fill: BOX, color: 'auto' },
  border: {
    top: { style: BorderStyle.SINGLE, size: 2, color: BOX, space: 8 },
    left: { style: BorderStyle.SINGLE, size: 18, color: NAVY_L, space: 10 },
    bottom: { style: BorderStyle.SINGLE, size: 2, color: BOX, space: 8 },
    right: { style: BorderStyle.SINGLE, size: 2, color: BOX, space: 8 },
  },
  children: [run(t, { size: 19 })],
});

const cell = (o) => new TableCell({
  width: { size: o.w, type: WidthType.DXA },
  columnSpan: o.span, verticalAlign: VerticalAlign.CENTER,
  shading: o.fill ? { type: ShadingType.CLEAR, fill: o.fill, color: 'auto' } : undefined,
  margins: { top: 80, bottom: 80, left: 110, right: 110 },
  children: [new Paragraph({
    alignment: o.align ?? AlignmentType.LEFT,
    spacing: { after: 0, line: 285 },
    children: [run(o.t ?? '', { bold: o.bold, size: o.size ?? 19, color: o.color })],
  })],
});

const BORDERS = {
  top: { style: BorderStyle.SINGLE, size: 12, color: NAVY },
  bottom: { style: BorderStyle.SINGLE, size: 12, color: NAVY },
  left: { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' },
  right: { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' },
  insideHorizontal: { style: BorderStyle.SINGLE, size: 4, color: RULE },
  insideVertical: { style: BorderStyle.SINGLE, size: 4, color: RULE },
};

const table = (widths, rows) => new Table({
  columnWidths: widths,
  width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA },
  borders: BORDERS,
  rows: rows.map((cells, r) => new TableRow({
    tableHeader: r === 0,
    children: cells.map((c, i) => {
      const o = typeof c === 'string' ? { t: c } : { ...c };
      if (r === 0) Object.assign(o, { bold: true, color: 'FFFFFF', fill: NAVY, align: o.align ?? AlignmentType.CENTER });
      else if (o.fill === undefined && r % 2 === 0) o.fill = ZEBRA;
      o.w = o.span ? widths.slice(i, i + o.span).reduce((a, b) => a + b, 0) : widths[i];
      return cell(o);
    }),
  })),
});
const R = (...c) => c;
const ctr = (t) => ({ t, align: AlignmentType.CENTER });
const SPAN2 = (t) => ({ t, span: 2 });

// ══════════════════════════════════════════════════════════ 제목부
const titleBox = new Table({
  columnWidths: [CONTENT],
  width: { size: CONTENT, type: WidthType.DXA },
  borders: {
    top: { style: BorderStyle.DOUBLE, size: 10, color: NAVY },
    bottom: { style: BorderStyle.DOUBLE, size: 10, color: NAVY },
    left: { style: BorderStyle.DOUBLE, size: 10, color: NAVY },
    right: { style: BorderStyle.DOUBLE, size: 10, color: NAVY },
    insideHorizontal: { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' },
    insideVertical: { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' },
  },
  rows: [new TableRow({
    children: [new TableCell({
      width: { size: CONTENT, type: WidthType.DXA },
      margins: { top: 260, bottom: 260, left: 200, right: 200 },
      children: [
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 110, line: 320 },
          children: [run('2026 대학생과 고양시민의 AI 기술 창업을 위한', { bold: true, size: 26 })] }),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 160, line: 340 },
          children: [run('바이브 코딩 특강 및 창업 경진대회', { bold: true, size: 34, color: NAVY })] }),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 0, line: 300 },
          children: [run('< 코딩을 몰라도, 2시간 만에 내 서비스를 만든다 >', { size: 22, color: NAVY_L })] }),
      ],
    })],
  })],
});

// ══════════════════════════════════════════════════════════ 개요
const 개요 = [
  H('특강 및 경진대회 개요'),
  O('(개최목적) 급변하는 AI 시대에 창업가로서 필요한 지식과 역량을 기르되, 기획안에 머무르지 않고 AI 코딩 도구로 직접 동작하는 시제품(프로토타입)을 만들어 보게 함으로써 대학생과 고양시민의 AI 기술 창업 경쟁력을 강화함'),
  O('(일    시)'),
  D('(특    강) 2026년 9월 28일(월) 13:00 ~ 15:40'),
  D('(멘 토 링) 2026년 10월 8일(목) 13:00 ~ 16:30'),
  D('(예    선) 2026년 10월 15일(목) 14:00 ~ 17:00 ※ 서류평가, 비공개'),
  D('(결    승) 2026년 10월 22일(목) 13:00 ~ 16:05'),
  O('(장    소) 한국항공대학교 대강당 및 스타트업 라운지'),
  O('(주    최) 고용노동부, 한국산업인력공단'),
  O('(주    관) SKT, 고양산업진흥원, 한국항공대학교'),
  O('(운    영) (주)리본마켓'),
  O('(대    상) 한국항공대학교 학부·대학원 재학생 및 고양시민 (개인 또는 팀, 팀당 1~4인)'),
  O('(예    산) 금 10,000,000원 (부가가치세 포함)'),
  callout('※ 「바이브 코딩」이란 — Claude Code, Cursor, GitHub Copilot 등 AI 코딩 에이전트에게 자연어로 요구사항을 전달하여, 코드 작성 경험이 적은 참가자도 웹·앱 형태의 동작하는 프로토타입(MVP)을 직접 완성하는 개발 방식을 말한다.'),

  P('◇ 추진 체계', { bold: true, before: 260, after: 140, size: 22 }),
  table([1700, 1500, 6439], [
    R('단 계', '일 자', '내        용'),
    R(ctr('① 특 강'), ctr('9.28(월)'), '바이브 코딩 실습 특강(2시간) · 경진대회 접수 및 멘토링 신청 개시'),
    R(ctr('② 멘토링'), ctr('10.8(목)'), '신청 팀 10개 팀 대상 전문가 1:1 멘토링 (팀당 60분)'),
    R(ctr('③ 예 선'), ctr('10.15(목)'), '사업계획서 서류평가 → 결승 진출 10개 팀 선정'),
    R(ctr('④ 결 승'), ctr('10.22(목)'), '현직 VC 3인 심사 · 프로토타입 라이브 데모 발표 및 시상'),
  ]),
];

// ══════════════════════════════════════════════════════════ 특강
const 특강 = [
  new Paragraph({ children: [new PageBreak()] }),
  H('특강 세부 계획(안) : 대강당'),
  O('(개최목적) 대학생과 고양시민이 AI 코딩 도구를 활용해 자기 아이디어를 직접 프로토타입으로 구현해 보도록 하여, 비전공자도 제품을 만들 수 있다는 경험을 제공함'),
  O('(운영방식) 이론 40분 + 실습 80분의 실습 병행형으로 운영하며, 참가자는 노트북을 지참함'),
  O('(정    원) 60명 내외'),
  P('', { after: 60 }),
  table([2350, 1350, 5939], [
    R('일  정', '구  분', '내        용'),
    R(ctr('12:30~13:00 (30분)'), ctr('등  록'), '<사전등록>'),
    R(ctr('13:00~13:05 (05분)'), ctr('개  최'), '<개회사> 한국항공대학교 / <인사말씀> 고양산업진흥원'),
    R(ctr('13:05~13:45 (40분)'), ctr('세 션 1'), '<바이브 코딩이란 무엇인가 — AI 창업 트렌드와 대학생 창업 사례>'),
    R(ctr('13:45~14:00 (15분)'), { t: '휴 식 시 간', span: 2, align: AlignmentType.CENTER }),
    R(ctr('14:00~15:20 (80분)'), ctr('세 션 2'), '<실습 : 내 아이디어를 동작하는 프로토타입으로> (노트북 지참)'),
    R(ctr('15:20~15:40 (20분)'), ctr('안내·질의응답'), '경진대회 참가 접수 및 1:1 멘토링 신청 개시'),
  ]),
  callout('※ 과업수행자는 실습에 필요한 예제 프롬프트·템플릿과 실습 가이드를 사전에 준비하고, 특강 참가자 전원에게 AI 코딩 도구 무료 체험 계정을 제공한다.'),
];

// ══════════════════════════════════════════════════════════ 멘토링
const 멘토링 = [
  new Paragraph({ children: [new PageBreak()] }),
  H('1:1 멘토링 세부 계획(안) : 스타트업 라운지'),
  O('(개최목적) 전문가의 경험과 노하우로 예비창업가의 AI 기술 창업을 지원하고, 특강에서 만든 프로토타입의 개선 방향과 사업계획서 작성 방향을 제시함'),
  O('(대상선정) 특강 참가자 및 경진대회 참가 신청자 중 멘토링 신청 팀 10개 팀'),
  O('(멘토구성) AC 심사역 1인, VC 심사역 1인, 개발 전문가 1인, 벤처기업 대표 1인 (총 4인 병행)'),
  P('', { after: 60 }),
  table([2350, 1350, 5939], [
    R('일  정', '구  분', '내        용'),
    R(ctr('12:30~13:00 (30분)'), ctr('등  록'), '<사전 등록>'),
    R(ctr('13:00~13:10 (10분)'), ctr('개  최'), '<개회사> 한국항공대학교 / <인사말씀> 고양산업진흥원 / 멘토 소개'),
    R(ctr('13:10~14:10 (60분)'), ctr('세 션 1'), '멘토 4인 병행 — 4개 팀 (팀당 60분)'),
    R(ctr('14:10~15:10 (60분)'), ctr('세 션 2'), '멘토 4인 병행 — 4개 팀'),
    R(ctr('15:10~15:30 (20분)'), { t: '휴 식 시 간', span: 2, align: AlignmentType.CENTER }),
    R(ctr('15:30~16:30 (60분)'), ctr('세 션 3'), '멘토 2인 병행 — 2개 팀'),
    R(ctr('16:30'), ctr('종  료'), '팀별 멘토링 결과 요약(개선 과제 목록) 회신 안내'),
  ]),
];

// ══════════════════════════════════════════════════════════ 예선
const 예선 = [
  new Paragraph({ children: [new PageBreak()] }),
  H('예선(서류평가) 세부 계획(안)'),
  O('(개최목적) 사업계획서를 통해 아이템의 타당성과 구현 계획을 검증하고 결승 진출 10개 팀을 선정함'),
  O('(제 출 물) 「AI 창업 아이템 사업계획서」 ※ 예선 단계에서는 프로토타입을 제출받지 않음'),
  P('', { after: 60 }),
  table([2350, 1350, 5939], [
    R('일  정', '구  분', '내        용'),
    R(ctr('10.13(화) 18:00'), ctr('접수 마감'), '사업계획서 제출 마감 (온라인 접수)'),
    R(ctr('10.15(목) 14:00~17:00'), ctr('서류평가'), '내/외부 심사위원 2인, 결승 진출 10개 팀 선정'),
    R(ctr('10.16(금)'), ctr('결과 발표'), '결승 진출 팀 개별 통보 및 발표 준비 안내'),
  ]),
  P('◇ 심사 기준', { bold: true, before: 240, after: 120, size: 22 }),
  table([3100, 1100, 5439], [
    R('심사 항목', '배점', '평가 내용'),
    R({ t: '아이템 적합성', bold: true }, ctr('30%'), '바이브 코딩을 활용한 창업 아이템으로 적합하며 구현 계획이 구체적인가'),
    R('문제 정의 및 해결방안', ctr('30%'), '해결하려는 문제가 분명하고 해법이 타당한가'),
    R('시장성', ctr('20%'), '목표 고객과 시장 규모가 구체적인가'),
    R('실현 가능성', ctr('20%'), '팀 역량과 자원으로 사업화가 가능한가'),
    R({ t: '합계', bold: true, fill: 'F2F2F2' }, { t: '100%', bold: true, fill: 'F2F2F2', align: AlignmentType.CENTER }, { t: '', fill: 'F2F2F2' }),
  ]),
];

// ══════════════════════════════════════════════════════════ 결승
const 결승 = [
  new Paragraph({ children: [new PageBreak()] }),
  H('결승 경진대회 세부 계획(안) : 대강당'),
  O('(개최목적) 실제로 동작하는 프로토타입을 현직 벤처투자자 앞에서 시연하도록 하여 기획과 구현을 함께 검증하고, 우수 팀을 시상함'),
  O('(심사위원) 현직 벤처투자자(VC) 3인'),
  O('(발표방식) 팀당 5분 발표 + 5분 질의응답, 발표 시간 내 프로토타입 라이브 데모 필수'),
  O('(최종평가) 예선 서류 점수 40% + 결승 발표 점수 60%'),
  P('', { after: 60 }),
  table([2350, 1350, 5939], [
    R('일  정', '구  분', '내        용'),
    R(ctr('12:30~13:00 (30분)'), ctr('등  록'), '<사전 등록>'),
    R(ctr('13:00~13:10 (10분)'), ctr('개  최'), '<개회사> 한국항공대학교 / <인사말씀> 고양산업진흥원 / 심사위원 소개'),
    R(ctr('13:10~13:20 (10분)'), ctr('안  내'), '심사 기준 및 발표 순서 안내'),
    R(ctr('13:20~14:10 (50분)'), ctr('발표 1부'), '1~5팀 (팀당 5분 발표 + 5분 Q&A, 라이브 데모 포함)'),
    R(ctr('14:10~14:25 (15분)'), { t: '휴 식 시 간', span: 2, align: AlignmentType.CENTER }),
    R(ctr('14:25~15:15 (50분)'), ctr('발표 2부'), '6~10팀'),
    R(ctr('15:15~15:45 (30분)'), ctr('심사·집계'), '심사위원 총평'),
    R(ctr('15:45~16:05 (20분)'), ctr('시 상 식'), '대상·최우수상·우수상·장려상 시상'),
    R(ctr('16:05'), ctr('폐  회'), ''),
  ]),
  P('◇ 시상 내역', { bold: true, before: 240, after: 120, size: 22 }),
  table([2400, 1700, 2600, 2939], [
    R('구 분', '팀 수', '시상 내역', '비 고'),
    R({ t: '대상 (1등)', bold: true }, ctr('1팀'), { t: '1,000,000원', align: AlignmentType.RIGHT }, '상장 및 상금'),
    R('최우수상 (2등)', ctr('1팀'), { t: '500,000원', align: AlignmentType.RIGHT }, '상장 및 상금'),
    R('우수상 (3등)', ctr('1팀'), { t: '300,000원', align: AlignmentType.RIGHT }, '상장 및 상금'),
    R('장려상 (4~10등)', ctr('7팀'), { t: '100,000원 상당', align: AlignmentType.RIGHT }, '상장 및 부상(상품)'),
    R({ t: '계', bold: true, fill: 'F2F2F2' }, { t: '10팀', bold: true, fill: 'F2F2F2', align: AlignmentType.CENTER },
      { t: '2,500,000원', bold: true, fill: 'F2F2F2', align: AlignmentType.RIGHT }, { t: '', fill: 'F2F2F2' }),
  ]),
];

// ══════════════════════════════════════════════════════════ 예산
const 예산 = [
  new Paragraph({ children: [new PageBreak()] }),
  H('예 산(안) : 10,000,000원 (부가가치세 포함)'),
  O('(전문가 활용비) 3,250,000원'),
  D('특강 강사료 250,000원 × 1명 = 250,000원  ※ 강사수당 지급기준 나급 · 2시간(170,000 + 80,000)'),
  D('1:1 창업 멘토링비 150,000원 × 10개 팀 = 1,500,000원'),
  D('예선 서류 평가료 150,000원 × 2명 = 300,000원'),
  D('결승 심사수당 400,000원 × 3명 = 1,200,000원'),
  O('(시상금 및 부상) 대상 1,000,000 / 최우수상 500,000 / 우수상 300,000 / 장려상 100,000원 × 7팀 = 2,500,000원'),
  O('(실습 환경비) AI 코딩 도구 이용료 50,000원 × 30명 = 1,500,000원'),
  O('(홍보 및 인쇄비) 포스터, 현수막·X배너, 결승 자료집, 상장 = 700,000원'),
  O('(행사 운영비) 특강 다과, 결승 식대(도시락), 소모품 및 현장 운영 = 600,000원'),
  O('(일반관리비 및 이윤) 540,909원  ※ 일반관리비 3.0% 256,500원 + 이윤 3.23% 284,409원'),
  O('(부 가 세) 909,091원'),
  P('', { after: 100 }),
  table([2700, 1900, 1450, 3589], [
    R('구 분', '금액(원)', '구성비', '비 고'),
    R('전문가 활용비', { t: '3,250,000', align: AlignmentType.RIGHT }, ctr('32.5%'), '강사료·멘토링비·평가료·심사수당'),
    R('시상금 및 부상', { t: '2,500,000', align: AlignmentType.RIGHT }, ctr('25.0%'), '10개 팀 시상'),
    R('실습 환경비', { t: '1,500,000', align: AlignmentType.RIGHT }, ctr('15.0%'), 'AI 코딩 도구 이용료'),
    R('홍보 및 인쇄비', { t: '700,000', align: AlignmentType.RIGHT }, ctr('7.0%'), '포스터·현수막·자료집·상장'),
    R('행사 운영비', { t: '600,000', align: AlignmentType.RIGHT }, ctr('6.0%'), '다과·식대·소모품'),
    R('일반관리비 및 이윤', { t: '540,909', align: AlignmentType.RIGHT }, ctr('5.4%'), '지방계약법 시행규칙 제8조'),
    R('부가가치세', { t: '909,091', align: AlignmentType.RIGHT }, ctr('9.1%'), '총원가의 10%'),
    R({ t: '합 계', bold: true, fill: NAVY, color: 'FFFFFF', align: AlignmentType.CENTER },
      { t: '10,000,000', bold: true, fill: NAVY, color: 'FFFFFF', align: AlignmentType.RIGHT },
      { t: '100.0%', bold: true, fill: NAVY, color: 'FFFFFF', align: AlignmentType.CENTER },
      { t: '금 일천만원정', bold: true, fill: NAVY, color: 'FFFFFF' }),
  ]),

  // 표가 쪽을 걸쳐 마지막 한 줄만 넘어가지 않도록 새 쪽에서 시작한다
  new Paragraph({ children: [new PageBreak()] }),
  P('◇ 2025년 대비 주요 변경사항', { bold: true, before: 0, after: 140, size: 22 }),
  table([2400, 3400, 3839], [
    R('구 분', '2025년', '2026년'),
    R('프로그램', '특강 1회 + 멘토링 1회', '특강 → 멘토링 → 예선 → 결승 (4단계 경진대회)'),
    R('주제', 'AI 시대 창업·투자 트렌드', '바이브 코딩 (AI 코딩 도구로 프로토타입 직접 제작)'),
    R('산출물', '없음 (강의 청강)', '동작하는 프로토타입 + 사업계획서'),
    R('시상', '없음', '10개 팀 시상 (총 2,500,000원)'),
    R('기념품', '텀블러 100개 (1,300,000원)', '제외'),
    R({ t: '예산', bold: true }, { t: '13,000,000원', bold: true }, { t: '10,000,000원', bold: true }),
  ]),
  callout('※ 2025년 대비 예산은 3,000,000원 줄었으나 경진대회와 시상금 2,500,000원이 새로 포함되었다. 강사료를 발주처 「강사수당 지급기준」 나급에 맞춘 뒤에도 일반관리비(3.0%)와 이윤(3.23%)은 지방계약법 시행규칙상 한도(각 8%, 10%)를 밑돈다. 상세 산출 근거는 별첨 원가계산서를 참조한다.'),
];

const doc = new Document({
  styles: { default: { document: { run: { font: F, size: 21 }, paragraph: { spacing: { line: 330 } } } } },
  sections: [{
    properties: { page: { margin: { top: convertMillimetersToTwip(22), bottom: convertMillimetersToTwip(18), left: MARGIN, right: MARGIN } } },
    headers: {
      default: new Header({ children: [new Paragraph({
        alignment: AlignmentType.RIGHT, spacing: { after: 0, line: 240 },
        border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: RULE, space: 6 } },
        children: [run('2026 바이브 코딩 특강 및 창업 경진대회 계획(안)', { size: 16, color: GRAY })],
      })] }),
    },
    footers: {
      default: new Footer({ children: [new Paragraph({
        alignment: AlignmentType.CENTER, spacing: { before: 100, line: 240 },
        children: [new TextRun({ children: ['- ', PageNumber.CURRENT, ' -'], size: 18, color: GRAY, font: F })],
      })] }),
    },
    children: [titleBox, new Paragraph({ spacing: { after: 260 }, children: [] }),
               ...개요, ...특강, ...멘토링, ...예선, ...결승, ...예산],
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
