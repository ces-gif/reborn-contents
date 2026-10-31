// 2027 신년 기업 AX 챌린지 제안서 (A4 10쪽)
// 서식은 docs/2026-계획안-견적서/build_plan.js 를 그대로 따른다.
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

const TITLE = '2027 신년 기업 AX 챌린지';

const run = (t, o = {}) => new TextRun({
  text: t, bold: o.bold, color: o.color, size: o.size ?? 20, font: F,
});
const P = (t, o = {}) => new Paragraph({
  alignment: o.align, indent: o.indent,
  spacing: { before: o.before ?? 0, after: o.after ?? 100, line: o.line ?? 320 },
  children: [run(t, o)],
});
const H = (t) => new Paragraph({
  heading: HeadingLevel.HEADING_1,
  spacing: { before: 280, after: 140, line: 300 },
  border: { bottom: { style: BorderStyle.SINGLE, size: 10, color: NAVY, space: 5 } },
  children: [run('□ ' + t, { bold: true, size: 23, color: NAVY })],
});
const O = (t) => new Paragraph({
  spacing: { after: 80, line: 315 },
  indent: { left: 220 },
  children: [run('○ ' + t, {})],
});
const D = (t) => new Paragraph({
  spacing: { after: 70, line: 315 },
  indent: { left: 620, hanging: 200 },
  children: [run('- ' + t, { size: 19 })],
});
const callout = (t) => new Paragraph({
  spacing: { before: 120, after: 120, line: 310 },
  indent: { left: 160, right: 160 },
  shading: { type: ShadingType.CLEAR, fill: BOX, color: 'auto' },
  border: {
    top: { style: BorderStyle.SINGLE, size: 2, color: BOX, space: 7 },
    left: { style: BorderStyle.SINGLE, size: 18, color: NAVY_L, space: 10 },
    bottom: { style: BorderStyle.SINGLE, size: 2, color: BOX, space: 7 },
    right: { style: BorderStyle.SINGLE, size: 2, color: BOX, space: 7 },
  },
  children: [run(t, { size: 18 })],
});

const cell = (o) => new TableCell({
  width: { size: o.w, type: WidthType.DXA },
  columnSpan: o.span, verticalAlign: VerticalAlign.CENTER,
  shading: o.fill ? { type: ShadingType.CLEAR, fill: o.fill, color: 'auto' } : undefined,
  margins: { top: 70, bottom: 70, left: 100, right: 100 },
  children: [new Paragraph({
    alignment: o.align ?? AlignmentType.LEFT,
    spacing: { after: 0, line: 275 },
    children: [run(o.t ?? '', { bold: o.bold, size: o.size ?? 18, color: o.color })],
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
const rgt = (t) => ({ t, align: AlignmentType.RIGHT });
const BRK = () => new Paragraph({ children: [new PageBreak()] });
const SUB = (t) => P('◇ ' + t, { bold: true, before: 230, after: 120, size: 21 });

// ═══════════════════════════════════════════════ 표지
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
      margins: { top: 230, bottom: 230, left: 200, right: 200 },
      children: [
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 100, line: 320 },
          children: [run('한국항공대학교 SW중심대학 · 기업 연계 프로젝트', { bold: true, size: 23 })] }),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 140, line: 340 },
          children: [run(TITLE, { bold: true, size: 36, color: NAVY })] }),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 0, line: 300 },
          children: [run('< 기업의 진짜 과제를, 학생이 AI로 푼다 >', { size: 21, color: NAVY_L })] }),
      ],
    })],
  })],
});

// ═══════════════════════════════════════════════ 1쪽 제안 배경
const 배경 = [
  H('제안 배경'),
  O('(산업 환경) 생성형 AI 도입이 개별 도구를 시범 사용하는 단계를 지나, 업무 프로세스 자체를 다시 설계하는 AX(AI Transformation) 단계로 넘어가고 있음. 그러나 상당수 기업은 "어느 업무부터 바꿔야 하는가"를 정의하지 못한 채 도입을 미루고 있음'),
  O('(대학 교육) SW중심대학 재학생은 기술 역량을 갖추었으나, 실제 기업의 업무 맥락과 제약(비용·보안·규제·조직)을 접할 기회가 적어 졸업 후 현업 적응에 시간이 소요됨'),
  O('(직전 사업의 성과와 한계) 2026년 10월 「고양시 바이브 코딩 창업경진대회」는 본선 10개 팀이 동작하는 프로토타입을 제작하는 성과를 거두었으나, 과제가 학생의 상상에서 출발해 실제 수요자 검증으로 이어지지 못한 한계가 있었음'),
  O('(제안 요지) 학생에게는 「진짜 과제」를, 기업에는 「외부 시각의 AX 설계안」을 주고받는 구조로 전환함. 산출물이 기업에서 실제로 검토·적용되고, 그 과정이 그대로 채용·창업 연계로 이어지도록 설계함'),
  callout('※ AX(AI Transformation)란 — 기존 업무에 AI 도구를 덧붙이는 것이 아니라, 어떤 일을 사람이 하고 어떤 일을 AI에 맡길지 업무 흐름 자체를 다시 그리는 것을 말한다. 따라서 산출물은 프로토타입 하나가 아니라 「재설계된 업무 흐름 + 그것을 증명하는 프로토타입」이다.'),
  SUB('기존 경진대회와의 구조 차이'),
  table([2250, 3550, 3739], [
    R('구 분', '일반 아이디어 경진대회', '본 제안 (기업 AX 챌린지)'),
    R(ctr('과제 출처'), '학생이 스스로 상상', '참여 기업이 직접 제출한 현업 과제'),
    R(ctr('수요 검증'), '발표 시점에 심사위원이 추정', '과제를 낸 기업 실무자가 직접 확인'),
    R(ctr('심사위원'), '외부 전문가', '참여 기업 임원 + 외부 AX 전문가'),
    R(ctr('산출물의 행방'), '대회 종료와 함께 소멸', '기업 내부 검토 → PoC 전환 가능'),
    R({ t: '학생에게 남는 것', bold: true }, '수상 실적', { t: '기업 확인서가 붙은 프로젝트 이력 + 채용 연계', bold: true }),
  ]),
];

// ═══════════════════════════════════════════════ 2쪽 제안 개요
const 개요 = [
  BRK(),
  H('제안 개요'),
  O('(행 사 명) 2027 신년 기업 AX 챌린지'),
  O('(기    간) 2027년 1월 4일(월) ~ 2월 24일(수)  ※ 착수 1월, 본선 2월'),
  D('착수 · 기업 과제 발굴 : 1. 4.(월) ~ 1. 15.(금)'),
  D('참가 모집 : 1. 11.(월) ~ 1. 22.(금)'),
  D('신년 발대식 및 AI 특강 : 1. 26.(화)'),
  D('업계 관계자 미팅 : 1. 27.(수) ~ 2. 3.(수)'),
  D('멘토링 1회차 : 2. 10.(수)  /  중간 점검·본선 진출 팀 선발 : 2. 17.(수)  /  멘토링 2회차 : 2. 19.(금)'),
  D('본선 AX 데모데이 : 2. 24.(수)'),
  O('(장    소) 한국항공대학교 대강당 및 스타트업 라운지 ※ 업계 관계자 미팅은 기업 현장 병행'),
  O('(주    최) 한국항공대학교 SW중심대학사업단'),
  O('(주    관) (주)리본마켓'),
  O('(협    력) 참여 기업 4개사 — 회계법인 · 메디컬 · 유통 · 화장품'),
  O('(대    상) 한국항공대학교 재학생 (전공 무관, 4~5인 팀)'),
  O('(규    모) 참가 10개 팀 · 50명 내외 → 중간 점검을 거쳐 본선 6개 팀 선발'),
  O('(시 상 금) 총 6,000,000원 — 1등 3,000,000 / 2등 2,000,000 / 3등 1,000,000'),
  O('(예    산) 금 30,000,000원 (부가가치세 포함)'),
  SUB('핵심 차별점 세 가지'),
  table([1100, 2500, 5939], [
    R('구 분', '내 용', '구체적 장치'),
    R(ctr('①'), { t: '가상의 문제가 아니다', bold: true },
      '운영사가 참여 기업 실무자를 사전 인터뷰하여 「과제 정의서」를 작성하고, 학생은 그 문서에서 출발한다'),
    R(ctr('②'), { t: '발표로 끝나지 않는다', bold: true },
      '우수 과제는 기업이 내부 PoC 대상으로 검토하며, 전환 시 별도 과제 용역으로 이어질 수 있다'),
    R(ctr('③'), { t: '대회가 곧 채용 과정이다', bold: true },
      '심사위원이 곧 각 사의 채용 담당 임원이며, 데모데이 당일 현장 채용 상담 부스를 함께 연다'),
  ]),
  callout('※ 연구 지원 — 참가 팀에는 AI 연구 소프트웨어 사용료를 팀당 1,000,000원씩 지원한다(5개 팀, 총 5,000,000원). 유료 AI 모델·API·분석 도구를 비용 걱정 없이 쓰게 하여, 「무료 도구로 가능한 범위」에 갇히지 않도록 하기 위함이다.'),
  SUB('기대 효과'),
  table([1500, 8039], [
    R('대 상', '기 대 효 과'),
    R({ t: '학 생', bold: true }, '실제 기업 과제를 2개월간 수행한 이력과 기업 확인서 확보 · 현업 제약을 반영한 설계 경험 · 채용 연계 기회'),
    R({ t: '기 업', bold: true }, '외부 시각의 AX 설계안 확보 · 검증된 인재 선발 기회 · 산학협력 및 사회공헌 실적'),
    R({ t: '대 학', bold: true }, 'SW중심대학 산학협력 실적 · 재학생 취업 연계 성과 · 기업 네트워크 4개사 확보'),
    R({ t: '지 역', bold: true }, '지역 중견 · 중소기업의 AI 전환 저변 확대 · 우수 인재의 지역 정착 유인'),
  ]),
];

// ═══════════════════════════════════════════════ 3쪽 참여 기업
const 기업 = [
  BRK(),
  H('참여 기업 구성(안)'),
  O('(선정 원칙) ① 반복 문서 업무의 비중이 큰 산업, ② AX 수요는 있으나 전담 조직이 없는 중견·중소 규모, ③ 학생이 2개월 안에 다룰 수 있는 범위의 과제를 낼 수 있는 기업'),
  O('(구    성) 4개 산업 각 1개사, 기업당 과제 1건, 과제당 2~3개 팀이 경쟁하여 총 10개 팀'),
  O('(기업 부담) 과제 정의 1건, 실무자 미팅 1회, 멘토링 참여 2회, 임원 심사 1회 — 담당자 1인 기준 약 10시간. 금전 부담 없음'),
  P('', { after: 50 }),
  table([1450, 1950, 3550, 2589], [
    R('산 업', '기업 성격(안)', 'AX 과제 예시', '학생 산출물'),
    R({ t: '회계법인', bold: true }, '중견 회계 · 세무 법인', '감사 증빙 1차 검토 및 조서 초안 자동화 — 반복 대조에 쓰이는 시간을 줄인다',
      '업무 흐름 재설계안 + 검토 보조 프로토타입'),
    R({ t: '메디컬', bold: true }, '의료기기 제조사 또는 병원', '인허가 · 임상 기술문서 초안 생성과 규정 적합성 사전 점검',
      '문서 템플릿 + 규정 대조 프로토타입'),
    R({ t: '유통', bold: true }, '온 · 오프라인 유통사', 'VOC · 리뷰 데이터 기반 상품기획 어시스턴트 및 CS 응대 초안 생성',
      'VOC 분석 파이프라인 + 기획 보조 도구'),
    R({ t: '화장품', bold: true }, '브랜드 또는 제조사', '성분 · 표시광고 규제 사전 검토와 채널별 마케팅 콘텐츠 자동 생성',
      '규제 체크리스트 자동화 + 콘텐츠 생성기'),
  ]),
  callout('※ 위 과제는 산업별 예시이며, 실제 과제는 착수 2주 동안 각 사 실무자 인터뷰를 거쳐 「과제 정의서」로 확정한다. 과제 정의서에는 ① 현재 업무 흐름, ② 걸리는 시간과 병목, ③ 제공 가능한 데이터의 범위와 형태, ④ 성공 기준을 적는다.'),
  SUB('기업이 얻는 것'),
  table([2400, 7139], [
    R('항 목', '내        용'),
    R({ t: 'AX 진단', bold: true }, '외부 시각으로 정리된 업무 재설계안 2~3건을 비용 부담 없이 확보'),
    R({ t: '인재 검증', bold: true }, '2개월간 실제 과제를 수행하는 과정을 지켜본 뒤 채용 여부를 판단 — 면접 한 번으로는 알 수 없는 부분'),
    R({ t: '산학 실적', bold: true }, 'SW중심대학 산학협력 참여 실적 및 사회공헌(ESG) 실적'),
    R({ t: '후속 선택권', bold: true }, '우수 산출물에 대한 내부 PoC 전환 우선 검토권'),
  ]),
  H('보안 및 지식재산 처리(안)'),
  O('(자료 제공) 기업 제공 자료는 비식별 처리된 샘플 데이터를 원칙으로 하며, 반출 범위는 업계 관계자 미팅에서 문서로 확정함'),
  O('(비밀유지) 참가자 · 멘토 · 운영 인력 전원이 비밀유지서약서를 제출하며, 과제 종료 후 제공 자료는 폐기하고 폐기 확인서를 회신함'),
  O('(지식재산) 학생 산출물의 권리는 제작 팀에 귀속함을 원칙으로 하되, 과제를 제출한 기업은 자사 과제 범위 안에서 무상 사용권을 가짐'),
  O('(후속 계약) PoC 전환 시 권리관계와 대가는 별도 계약으로 정하며, 운영사는 계약 체결을 중개하지 않고 양 당사자 협의에 맡김'),
  O('(발표 공개) 본선 발표 자료 중 기업이 비공개를 요청한 부분은 심사위원에게만 제공하고 대외 자료집에서 제외함'),
];

// ═══════════════════════════════════════════════ 4쪽 프로그램 구성
const 구성 = [
  BRK(),
  H('프로그램 구성'),
  O('(설계 원칙) 학생이 혼자 상상하는 시간을 줄이고, ① 방법을 배우고 → ② 현장을 듣고 → ③ 다듬고 → ④ 검증받는 네 개의 축으로 구성함'),
  P('', { after: 50 }),
  table([1050, 2250, 1500, 4739], [
    R('단 계', '프로그램', '일 자', '내        용'),
    R(ctr('①'), { t: 'AI 특강 (1회)', bold: true }, ctr('1. 26.(화)'), '신년 발대식과 함께 개최 — AX 방법론과 AI 도구 실습, 기업 과제 설명회, 팀·과제 매칭'),
    R(ctr('②'), { t: '업계 관계자 미팅', bold: true }, ctr('1. 27. ~ 2. 3.'), '팀별로 과제를 낸 기업의 실무자를 직접 만나 현업 맥락과 제약을 확인'),
    R(ctr('③'), { t: '멘토링 (2회차)', bold: true }, ctr('2. 10. · 2. 19.'), '1회차 설계 방향 점검(전체 10팀), 2회차 발표 준비 점검(본선 6팀)'),
    R(ctr('④'), { t: '본선 AX 데모데이', bold: true }, ctr('2. 24.(수)'), '기업 임원 심사 · 시상 · 현장 채용 상담'),
  ]),
  SUB('추진 일정(안)'),
  table([1650, 2150, 5739], [
    R('시 기', '구 분', '내        용'),
    R(ctr('1월 1~2주'), '착수 · 과제 발굴', '참여 기업 4개사 확정, 실무자 인터뷰, 「과제 정의서」 4건 작성'),
    R(ctr('1월 2~4주'), '참가 모집', '교내 공고 · 포스터 · 온라인 접수, 팀 구성 (10개 팀 · 50명 내외)'),
    R(ctr('1월 4주'), '신년 발대식 · AI 특강', '1. 26.(화) — 특강, 기업 과제 설명회, 팀·과제 매칭 확정'),
    R(ctr('1월 5주 ~ 2월 1주'), '업계 관계자 미팅', '1. 27. ~ 2. 3. — 기업별 실무자 미팅(현장 또는 화상), 요구사항 정리'),
    R(ctr('2월 1주'), { t: '설 연휴 (2. 5. ~ 2. 8.)', span: 2, align: AlignmentType.CENTER }),
    R(ctr('2월 2주'), '멘토링 1회차', '2. 10.(수) — 업무 재설계 방향 점검 (전체 10개 팀)'),
    R(ctr('2월 3주'), '중간 점검 · 본선 선발', '2. 17.(수) — 중간 산출물 심사, 본선 진출 6개 팀 선발'),
    R(ctr('2월 3주'), '멘토링 2회차', '2. 19.(금) — 본선 6개 팀 발표 준비 점검'),
    R(ctr('2월 4주'), '본선 AX 데모데이', '2. 24.(수) — 발표 · 심사 · 시상 · 채용 상담'),
  ]),
  callout('※ 2027년 설 연휴(2. 5.~2. 8.)를 피해 멘토링을 2월 2~3주에 배치했다. 한국항공대학교 겨울방학에 맞춰 설계했으므로, 학사일정이 확정되면 본선 일자는 개강 전 주로 조정할 수 있다.'),
];

// ═══════════════════════════════════════════════ 5쪽 AI 특강
const 특강 = [
  BRK(),
  H('① AI 특강 및 신년 발대식 세부 계획(안) : 대강당'),
  O('(목    적) 참가자 전원이 같은 방법론과 같은 도구에서 출발하도록 하고, 기업 과제를 직접 듣고 팀·과제 매칭을 확정함'),
  O('(일    시) 2027년 1월 26일(화) 13:00 ~ 17:00'),
  O('(운영방식) 이론 50분 + 실습 70분의 실습 병행형, 참가자 노트북 지참'),
  O('(정    원) 50명 내외 (참가 신청자 전원)'),
  P('', { after: 50 }),
  table([2300, 1400, 5839], [
    R('일  정', '구  분', '내        용'),
    R(ctr('12:30~13:00 (30분)'), ctr('등  록'), '<사전 등록> 팀 확인 및 자료 배포'),
    R(ctr('13:00~13:15 (15분)'), ctr('발 대 식'), '<개회사> SW중심대학사업단 / 참여 기업 소개'),
    R(ctr('13:15~14:05 (50분)'), ctr('특강 1부'), '<AX란 무엇인가 — 도구 도입과 업무 재설계는 어떻게 다른가>'),
    R(ctr('14:05~14:20 (15분)'), { t: '휴 식 시 간', span: 2, align: AlignmentType.CENTER }),
    R(ctr('14:20~15:30 (70분)'), ctr('특강 2부'), '<실습 : 업무 흐름 분해 → AI로 대체 가능한 구간 찾기 → 프로토타입 뼈대 만들기>'),
    R(ctr('15:30~16:30 (60분)'), ctr('과제 설명회'), '기업 4개사 각 15분 — 과제 정의서 발표 및 질의응답'),
    R(ctr('16:30~17:00 (30분)'), ctr('매  칭'), '팀별 희망 과제 접수 → 과제 배정 확정 · 연구 소프트웨어 지원 안내 · 이후 일정 공지'),
  ]),
  callout('※ 과제 배정은 팀의 1·2지망과 팀 구성(전공·역량)을 함께 보아 운영사가 조정한다. 한 기업에 2~3개 팀을 붙이는 것은 같은 과제에 서로 다른 접근이 나오게 하여, 기업이 선택지를 갖도록 하기 위함이다.'),
  SUB('특강에서 다루는 AI 도구'),
  table([2400, 7139], [
    R('구 분', '도구 및 활용 범위'),
    R('업무 분석', '생성형 AI 대화 모델 — 업무 인터뷰 내용 정리, 병목 구간 도출'),
    R('문서 · 데이터 처리', '문서 요약 · 추출 · 대조 자동화 (회계 · 메디컬 · 화장품 과제의 핵심)'),
    R('프로토타입 구현', 'AI 코딩 에이전트 — 동작하는 웹 기반 시제품 제작'),
    R('검증', '테스트 데이터로 정확도 · 소요시간 비교 측정 (성공 기준 대비)'),
  ]),
];

// ═══════════════════════════════════════════════ 6쪽 업계 관계자 미팅
const 미팅 = [
  BRK(),
  H('② 업계 관계자 미팅 세부 계획(안)'),
  O('(목    적) 과제 정의서만으로는 알 수 없는 현업의 맥락 — 왜 지금 방식으로 일하는지, 무엇을 바꾸면 곤란한지 — 을 실무자에게 직접 듣게 함'),
  O('(일    시) 2027년 1월 27일(수) ~ 2월 3일(수) 중 기업별 1회 (회차당 90분)'),
  O('(장    소) 참여 기업 현장 방문을 원칙으로 하되, 기업 사정에 따라 화상 회의로 대체'),
  O('(참 석 자) 기업 실무 담당자 1~2인, 해당 과제에 배정된 2~3개 팀, 운영사 진행자 1인'),
  P('', { after: 50 }),
  table([1750, 1300, 6489], [
    R('구 분', '시 간', '내        용'),
    R(ctr('현장 브리핑'), ctr('20분'), '실무자가 실제 업무 흐름을 설명 — 가능한 경우 사용 중인 문서 · 화면을 보여 줌'),
    R(ctr('질의응답'), ctr('40분'), '팀별 사전 질문지 기반 질의 — 처리 건수, 소요 시간, 오류가 나는 지점, 담당자가 가장 번거로워하는 작업'),
    R(ctr('데이터 협의'), ctr('20분'), '제공 가능한 데이터의 범위 · 형태 · 비식별 수준 확정, 반출 가능 여부 확인'),
    R(ctr('정  리'), ctr('10분'), '성공 기준 합의 — 무엇이 얼마나 줄면 성공인가를 숫자로 적어 둔다'),
  ]),
  callout('※ 팀은 미팅 3일 전까지 사전 질문지를 제출한다. 현장에서 처음 생각하기 시작하면 90분으로는 부족하다. 운영사가 질문지를 미리 검토해 중복되거나 추상적인 질문을 걸러 낸다.'),
  O('(산 출 물) 미팅 후 3일 이내에 팀별 「현업 요구사항 정리서」 제출 — 운영사가 기업에 회신하여 사실관계를 확인받음'),
  O('(보안 조치) 참가자 전원 비밀유지서약서 제출, 기업 제공 자료는 비식별 · 샘플 데이터를 원칙으로 함'),
  SUB('사전 질문지 항목 (예시)'),
  table([900, 8639], [
    R('번 호', '질        문'),
    R(ctr('1'), '이 업무는 하루(또는 주) 몇 건 발생하며, 1건당 몇 분이 걸립니까'),
    R(ctr('2'), '담당자가 가장 번거로워하는 구간은 어디입니까'),
    R(ctr('3'), '틀리면 가장 곤란한 항목은 무엇이며, 지금은 어떻게 걸러 냅니까'),
    R(ctr('4'), '외부로 나갈 수 없는 정보는 무엇입니까'),
    R(ctr('5'), '이 업무가 얼마나 줄면 "도입할 만하다"고 판단하시겠습니까'),
  ]),
];

// ═══════════════════════════════════════════════ 7쪽 멘토링
const 멘토링 = [
  BRK(),
  H('③ 멘토링 및 중간 점검 세부 계획(안) : 스타트업 라운지'),
  O('(목    적) 설계 단계와 구현 단계에서 각 한 번씩 점검하여, 방향이 어긋난 채로 2월을 보내는 팀이 없도록 함'),
  O('(멘토구성) 기업 실무 멘토 4인(각 사 1인) + 외부 전문 멘토 4인(AX 컨설턴트 2인, 개발 전문가 1인, 채용 담당 1인)'),
  O('(운영방식) 팀당 60분, 기업 실무 멘토와 외부 전문 멘토가 함께 들어가 현업 타당성과 기술 타당성을 같은 자리에서 본다'),
  P('', { after: 50 }),
  table([1700, 1850, 5989], [
    R('회 차', '일 자', '점 검 내 용'),
    R({ t: '1회차', bold: true }, ctr('2. 10.(수) 13:00~17:30'),
      '전체 10개 팀 — 업무 재설계안 점검. 어느 구간을 AI에 맡기는가, 사람이 남는 구간은 어디인가, 성공 기준은 측정 가능한가'),
    R({ t: '중간 점검', bold: true }, ctr('2. 17.(수) 13:00~17:00'),
      '전체 10개 팀 — 중간 산출물 심사(평가위원 3인), 본선 진출 6개 팀 선발 및 당일 통보'),
    R({ t: '2회차', bold: true }, ctr('2. 19.(금) 13:00~17:00'),
      '본선 6개 팀 — 발표 구성과 라이브 시연 점검, 기업 강평 대비'),
  ]),
  SUB('멘토링 1회차 진행 (2. 10.)'),
  table([2300, 1400, 5839], [
    R('일  정', '구  분', '내        용'),
    R(ctr('13:00~13:10 (10분)'), ctr('개  시'), '진행 안내 및 멘토 소개'),
    R(ctr('13:10~14:10 (60분)'), ctr('1 세 션'), '멘토 4개 조 병행 — 4개 팀 (팀당 60분)'),
    R(ctr('14:10~14:25 (15분)'), { t: '휴 식 시 간', span: 2, align: AlignmentType.CENTER }),
    R(ctr('14:25~15:25 (60분)'), ctr('2 세 션'), '멘토 4개 조 병행 — 4개 팀'),
    R(ctr('15:25~16:25 (60분)'), ctr('3 세 션'), '멘토 2개 조 병행 — 나머지 2개 팀'),
    R(ctr('16:25~17:10 (45분)'), ctr('공개 피드백'), '팀별 3분 요약 발표 후 전체 공유 — 다른 팀의 접근에서 배우는 시간'),
    R(ctr('17:10~17:30 (20분)'), ctr('정  리'), '팀별 개선 과제 목록 확정 및 회신'),
  ]),
  callout('※ 멘토링 결과는 「개선 과제 목록」 형태로 팀과 기업 양쪽에 회신한다. 중간 점검에서는 1회차 목록의 처리 여부를 먼저 확인하고 시작하므로, 피드백이 흘러가 버리지 않는다.'),
  O('(본선 선발 기준) 중간 점검 심사는 본선 심사 기준과 같은 항목으로 평가하되, 「구현 완성도」 대신 「남은 2주의 실행 계획」을 본다'),
];

// ═══════════════════════════════════════════════ 8쪽 본선
const 본선 = [
  BRK(),
  H('④ 본선 AX 데모데이 세부 계획(안) : 대강당'),
  O('(목    적) 과제를 낸 기업의 임원 앞에서 재설계안과 프로토타입을 함께 제시하게 하여, 기획과 구현을 동시에 검증함'),
  O('(일    시) 2027년 2월 24일(수) 13:00 ~ 17:30'),
  O('(진출 팀) 중간 점검을 통과한 6개 팀'),
  O('(심사위원) 참여 기업 임원 4인 + 외부 AX 전문가 1인 (총 5인)'),
  O('(발표방식) 팀당 10분 발표 + 5분 질의응답, 발표 중 프로토타입 라이브 시연 필수'),
  P('', { after: 50 }),
  table([2300, 1400, 5839], [
    R('일  정', '구  분', '내        용'),
    R(ctr('12:30~13:00 (30분)'), ctr('등  록'), '<사전 등록> 참여 기업 · 내빈 영접'),
    R(ctr('13:00~13:20 (20분)'), ctr('개  최'), '<개회사> SW중심대학사업단 / 참여 기업 인사 / 심사위원 소개'),
    R(ctr('13:20~13:30 (10분)'), ctr('안  내'), '심사 기준 및 발표 순서 안내'),
    R(ctr('13:30~14:15 (45분)'), ctr('발표 1부'), '1~3팀 (팀당 10분 발표 + 5분 질의응답, 라이브 시연 포함)'),
    R(ctr('14:15~14:30 (15분)'), { t: '휴 식 시 간', span: 2, align: AlignmentType.CENTER }),
    R(ctr('14:30~15:15 (45분)'), ctr('발표 2부'), '4~6팀'),
    R(ctr('15:15~15:50 (35분)'), ctr('심사 · 집계'), '심사위원 합의 / 같은 시간 참가자는 기업별 부스에서 자유 상담'),
    R(ctr('15:50~16:20 (30분)'), ctr('기업 강평'), '기업별 총평 — 어느 안을 내부 검토로 가져갈지 밝힘'),
    R(ctr('16:20~16:40 (20분)'), ctr('시 상 식'), '1등 · 2등 · 3등 시상 및 전 팀 수료증 수여'),
    R(ctr('16:40~17:30 (50분)'), ctr('채용 상담'), '기업별 채용 상담 부스 운영 (인턴십 · 채용 전형 안내, 개별 면담)'),
  ]),
  SUB('심사 기준'),
  table([2750, 1000, 5789], [
    R('심사 항목', '배점', '평가 내용'),
    R({ t: '과제 이해도', bold: true }, ctr('20'), '기업이 실제로 겪는 문제를 정확히 파악했는가 (현업 맥락 · 제약 반영)'),
    R({ t: 'AX 설계의 타당성', bold: true }, ctr('25'), '업무 흐름 재설계가 현실적인가, 사람과 AI의 역할 분담이 분명한가'),
    R({ t: '구현 완성도', bold: true }, ctr('25'), '프로토타입이 실제로 동작하며 설계안을 증명하는가'),
    R({ t: '적용 가능성', bold: true }, ctr('20'), '비용 · 보안 · 규제 · 조직 측면에서 기업이 실제로 도입할 수 있는가'),
    R({ t: '발표 및 전달력', bold: true }, ctr('10'), '제한 시간 안에 핵심을 전달했는가'),
    R({ t: '합 계', bold: true, fill: 'F2F2F2' }, { t: '100', bold: true, fill: 'F2F2F2', align: AlignmentType.CENTER }, { t: '', fill: 'F2F2F2' }),
  ]),
  callout('※ 「적용 가능성」 20점은 일반 경진대회에 없는 항목이다. 아무리 좋은 안이라도 데이터 반출이 불가능하거나 비용이 맞지 않으면 기업은 쓸 수 없다. 이 항목을 두어야 학생이 현실 제약을 설계 안으로 끌어들인다.'),
];

// ═══════════════════════════════════════════════ 9쪽 취·창업 연계
const 연계 = [
  BRK(),
  H('취 · 창업 연계 방안'),
  O('(설계 의도) 대회를 채용 과정의 일부로 설계함. 기업은 2개월간 과제를 수행하는 모습을 보고 판단하며, 학생은 대회 참가 자체가 경력이 되도록 함'),
  P('', { after: 50 }),
  table([1500, 1850, 4289, 1900], [
    R('트 랙', '대 상', '내        용', '시 점'),
    R({ t: '채용 연계', bold: true }, '본선 진출 전원',
      '참여 기업 인턴십 · 채용 전형 서류 우대, 데모데이 당일 현장 채용 상담 부스 운영', ctr('2월 말')),
    R({ t: '인턴십', bold: true }, '수상 팀 우선',
      '참여 기업 4~8주 인턴십 — SW중심대학 현장실습 학점 연계 여부 협의', ctr('3월 ~ 여름')),
    R({ t: 'PoC 전환', bold: true }, '1등 · 2등',
      '기업 내부 PoC 대상으로 검토, 전환 시 별도 과제 용역 계약으로 연결', ctr('3월 이후')),
    R({ t: '창업 연계', bold: true }, '범용 과제 보유 팀',
      '특정 기업에 종속되지 않는 과제는 예비창업패키지 등 정부지원사업 연계 및 후속 멘토링', ctr('3월 이후')),
    R({ t: '포트폴리오', bold: true }, '참가 전원',
      '기업 확인서가 포함된 프로젝트 결과보고서 발급 — 취업 서류에 바로 쓸 수 있는 형태', ctr('2월 말')),
  ]),
  callout('※ 인턴십과 PoC 전환은 기업의 채용 · 투자 계획에 달려 있으므로 「보장」이 아니라 「우선 검토」로 제안한다. 다만 데모데이 당일 채용 상담 부스 운영과 기업 확인서 발급은 기업 참여 조건에 명시하여 반드시 제공되도록 한다.'),
  SUB('시상 내역'),
  table([2200, 1300, 2500, 3539], [
    R('구 분', '팀 수', '시 상 금', '비 고'),
    R({ t: '1등 (대상)', bold: true }, ctr('1팀'), rgt('3,000,000원'), '상장 · 상패 및 상금 · PoC 우선 검토'),
    R({ t: '2등 (최우수상)', bold: true }, ctr('1팀'), rgt('2,000,000원'), '상장 · 상패 및 상금 · PoC 우선 검토'),
    R({ t: '3등 (우수상)', bold: true }, ctr('1팀'), rgt('1,000,000원'), '상장 · 상패 및 상금'),
    R('본선 진출', ctr('3팀'), ctr('—'), '수료증 및 기업 확인서'),
    R({ t: '계', bold: true, fill: 'F2F2F2' }, { t: '6팀', bold: true, fill: 'F2F2F2', align: AlignmentType.CENTER },
      { t: '6,000,000원', bold: true, fill: 'F2F2F2', align: AlignmentType.RIGHT }, { t: '', fill: 'F2F2F2' }),
  ]),
  O('(연구 지원) 참가 팀에는 AI 연구 소프트웨어 사용료를 팀당 1,000,000원씩 지원함 (5개 팀 · 총 5,000,000원). 지원 대상은 과제 수행 착수 시점에 팀 구성과 과제 계획을 보아 선정하며, 사용 내역은 정산 증빙으로 확인함'),
];

// ═══════════════════════════════════════════════ 10쪽 예산
const 예산 = [
  BRK(),
  H('예 산(안) : 30,000,000원 (부가가치세 포함)'),
  O('(전문가 활용비) 9,700,000원'),
  D('AI 특강 강사료 400,000 × 1명 = 400,000  ·  기업 과제 정의 자문료 200,000 × 4사 = 800,000'),
  D('기업 실무 멘토비 300,000 × 4사 × 2회 = 2,400,000  ·  외부 전문 멘토비 200,000 × (10팀+6팀) = 3,200,000'),
  D('중간 점검 평가료 300,000 × 3명 = 900,000  ·  본선 심사수당 400,000 × 5명 = 2,000,000'),
  O('(시상금) 6,000,000원  ·  (AI 연구 소프트웨어 사용료) 1,000,000원 × 5팀 = 5,000,000원'),
  O('(홍보 및 인쇄비) 1,200,000원  ·  (행사 운영비) 1,700,000원  ※ 세부 내역은 아래 표 비고 참조'),
  O('(일반관리비 및 이윤) 3,672,727원  ·  (부 가 세) 2,727,273원'),
  P('', { after: 80 }),
  table([2850, 1850, 1250, 3589], [
    R('구 분', '금액(원)', '구성비', '비 고'),
    R('전문가 활용비', rgt('9,700,000'), ctr('32.3%'), '강사료 · 자문료 · 멘토비 · 평가료 · 심사수당'),
    R('시상금', rgt('6,000,000'), ctr('20.0%'), '1등 300만 / 2등 200만 / 3등 100만'),
    R('AI 연구 소프트웨어 사용료', rgt('5,000,000'), ctr('16.7%'), '팀당 100만원 × 5팀'),
    R('홍보 및 인쇄비', rgt('1,200,000'), ctr('4.0%'), '포스터 · 자료집 · 상장 · 상패'),
    R('행사 운영비', rgt('1,700,000'), ctr('5.7%'), '다과 · 식대 · 교통비 · 현장 운영'),
    R({ t: '직접비 계', bold: true }, { t: '23,600,000', bold: true, align: AlignmentType.RIGHT }, { t: '78.7%', bold: true, align: AlignmentType.CENTER }, ''),
    R('일반관리비 및 이윤', rgt('3,672,727'), ctr('12.2%'), '일반관리비 5.06% · 이윤 10.0%'),
    R('부가가치세', rgt('2,727,273'), ctr('9.1%'), '총원가의 10%'),
    R({ t: '합 계', bold: true, fill: NAVY, color: 'FFFFFF', align: AlignmentType.CENTER },
      { t: '30,000,000', bold: true, fill: NAVY, color: 'FFFFFF', align: AlignmentType.RIGHT },
      { t: '100.0%', bold: true, fill: NAVY, color: 'FFFFFF', align: AlignmentType.CENTER },
      { t: '금 삼천만원정', bold: true, fill: NAVY, color: 'FFFFFF' }),
  ]),
  callout('※ 일반관리비 5.06%와 이윤 10.0%는 지방계약법 시행규칙 제8조 한도(각 8%, 10%) 이내이다. AI 연구 소프트웨어 사용료를 본선 진출 팀 수(6팀)에 맞추려면 1,000,000원이 더 필요하며, 홍보·인쇄비 또는 행사 운영비에서 조정하거나 총액을 31,000,000원으로 올려야 한다. 지원 대상 팀 수는 협의 사항이다.'),
];

// ═══════════════════════════════════════════════ 11쪽 보안·기대효과·협의
const 마무리 = [
  H('향후 협의 필요 사항'),
  O('(참여 기업) 4개 산업 각 1개사 — 섭외는 운영사가 수행하되, 대학 산학협력 네트워크를 공유해 주시면 기간을 줄일 수 있음'),
  O('(연구 지원 범위) AI 연구 소프트웨어 사용료 지원 대상 — 5개 팀인지 본선 6개 팀 전원인지 확정 필요'),
  O('(학점 연계) 현장실습 · 비교과 학점 인정 여부 및 요건 — SW중심대학사업단 확인 필요'),
  O('(참가 범위) 타 대학 연합팀 · 대학원생 참가 허용 여부  /  (일정) 2027학년도 학사일정 확정 후 본선 일자 최종 조정'),
  callout('본 제안서는 (주)리본마켓이 2026년 10월 「고양시 바이브 코딩 창업경진대회」(4단계 · 본선 10개 팀)를 기획 · 운영한 경험을 바탕으로 작성하였습니다.'),
  P('2026년 11월', { align: AlignmentType.CENTER, size: 21, before: 200, after: 100 }),
  P('(주) 리 본 마 켓', { align: AlignmentType.CENTER, bold: true, size: 26, color: NAVY, after: 110 }),
  P('담당 최은성  ·  010-5843-0627  ·  ces@rebornmarket.org', { align: AlignmentType.CENTER, size: 18, color: GRAY }),
];

const doc = new Document({
  styles: { default: { document: { run: { font: F, size: 20 }, paragraph: { spacing: { line: 320 } } } } },
  sections: [{
    properties: { page: { margin: { top: convertMillimetersToTwip(20), bottom: convertMillimetersToTwip(16), left: MARGIN, right: MARGIN } } },
    headers: {
      default: new Header({ children: [new Paragraph({
        alignment: AlignmentType.RIGHT, spacing: { after: 0, line: 240 },
        border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: RULE, space: 6 } },
        children: [run(TITLE + ' 제안서', { size: 16, color: GRAY })],
      })] }),
    },
    footers: {
      default: new Footer({ children: [new Paragraph({
        alignment: AlignmentType.CENTER, spacing: { before: 90, line: 240 },
        children: [new TextRun({ children: ['- ', PageNumber.CURRENT, ' -'], size: 18, color: GRAY, font: F })],
      })] }),
    },
    children: [titleBox, new Paragraph({ spacing: { after: 220 }, children: [] }),
               ...배경, ...개요, ...기업, ...구성, ...특강, ...미팅, ...멘토링, ...본선, ...연계, ...예산, ...마무리],
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
