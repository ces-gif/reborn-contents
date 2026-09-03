const fs = require('fs');
const {
  Document, Packer, Paragraph, TextRun, AlignmentType, HeadingLevel,
  Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle,
  PageBreak, LevelFormat, VerticalMergeType, VerticalAlign,
  Header, Footer, PageNumber, SectionType, PageBorderOffsetFrom,
  convertMillimetersToTwip,
} = require('docx');

// ── 서체 ───────────────────────────────────────────────────────────────────
// 한글은 맑은 고딕, 라틴/숫자도 같은 패밀리로 맞춘다. hint:'eastAsia'를 주지 않으면
// 워드가 한글에 라틴 폰트를 적용해 자간이 무너진다.
const F = { ascii: '맑은 고딕', hAnsi: '맑은 고딕', eastAsia: '맑은 고딕', cs: '맑은 고딕', hint: 'eastAsia' };

// ── 색 ─────────────────────────────────────────────────────────────────────
const NAVY = '17365D';   // 제목 바
const NAVY_L = '2E5C8A'; // 중제목
const RULE = 'BFC9D4';   // 표 괘선
const ZEBRA = 'F4F7FB';  // 표 줄무늬
const BOX = 'EEF3F9';    // 강조 박스
const GRAY = '767676';   // 머리말/각주
const DRAFT = '9C2A2A';  // 미확정 안내

const PAGE_W = convertMillimetersToTwip(210);
const MARGIN = convertMillimetersToTwip(22);
const CONTENT = PAGE_W - MARGIN * 2; // 본문 폭 = 9354 twip

// ── 문단 헬퍼 ──────────────────────────────────────────────────────────────
const run = (text, o = {}) => new TextRun({
  text, bold: o.bold, italics: o.italics, color: o.color,
  size: o.size ?? 21, font: F, characterSpacing: o.spacing,
});

const P = (text, o = {}) => new Paragraph({
  alignment: o.align,
  spacing: { before: o.before ?? 0, after: o.after ?? 120, line: o.line ?? 340 },
  indent: o.indent,
  border: o.border,
  shading: o.fill ? { type: ShadingType.CLEAR, fill: o.fill, color: 'auto' } : undefined,
  children: [run(text, o)],
});

// 대제목: 남색 바탕에 흰 글씨 — 관공서 과업지시서의 표준 형태
const H1 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_1,
  spacing: { before: 400, after: 200, line: 300 },
  shading: { type: ShadingType.CLEAR, fill: NAVY, color: 'auto' },
  indent: { left: 120, right: 120 },
  children: [run(text, { bold: true, size: 24, color: 'FFFFFF' })],
});

// 중제목: 남색 글씨 + 밑줄 괘선
const H2 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_2,
  spacing: { before: 300, after: 140, line: 300 },
  border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: RULE, space: 4 } },
  children: [run(text, { bold: true, size: 22, color: NAVY_L })],
});

const bullet = (text, level = 0) => new Paragraph({
  numbering: { reference: 'body', level },
  spacing: { after: 90, line: 340 },
  children: [run(text)],
});

// 강조 박스: 왼쪽에 남색 세로선 + 연한 바탕
const callout = (text) => new Paragraph({
  spacing: { before: 140, after: 160, line: 330 },
  indent: { left: 180, right: 180 },
  shading: { type: ShadingType.CLEAR, fill: BOX, color: 'auto' },
  // OOXML의 w:pBdr는 top → left → bottom → right 순서를 강제한다
  border: {
    top: { style: BorderStyle.SINGLE, size: 2, color: BOX, space: 8 },
    left: { style: BorderStyle.SINGLE, size: 18, color: NAVY_L, space: 10 },
    bottom: { style: BorderStyle.SINGLE, size: 2, color: BOX, space: 8 },
    right: { style: BorderStyle.SINGLE, size: 2, color: BOX, space: 8 },
  },
  children: [run(text, { size: 19 })],
});

// 미확정 안내 상자 — 확정본이 아님을 표지·본문에서 반복해 알린다
const noticeBox = (text) => new Paragraph({
  spacing: { before: 200, after: 120, line: 320 },
  indent: { left: 500, right: 500 },
  alignment: AlignmentType.CENTER,
  shading: { type: ShadingType.CLEAR, fill: 'FBF0F0', color: 'auto' },
  border: {
    top: { style: BorderStyle.SINGLE, size: 8, color: DRAFT, space: 8 },
    left: { style: BorderStyle.SINGLE, size: 8, color: DRAFT, space: 8 },
    bottom: { style: BorderStyle.SINGLE, size: 8, color: DRAFT, space: 8 },
    right: { style: BorderStyle.SINGLE, size: 8, color: DRAFT, space: 8 },
  },
  children: [run(text, { size: 18, color: DRAFT, bold: true })],
});

// 장(章)은 반드시 새 쪽에서 시작한다 — 한 쪽에 두 개의 대주제가 섞이지 않도록
const PB = () => new Paragraph({ children: [new PageBreak()] });

// ── 표 헬퍼 ────────────────────────────────────────────────────────────────
const cell = (o) => new TableCell({
  width: { size: o.w, type: WidthType.DXA },
  columnSpan: o.span,
  verticalMerge: o.vmerge,
  verticalAlign: VerticalAlign.CENTER,
  shading: o.fill ? { type: ShadingType.CLEAR, fill: o.fill, color: 'auto' } : undefined,
  margins: { top: 90, bottom: 90, left: 130, right: 130 },
  children: [new Paragraph({
    alignment: o.align ?? AlignmentType.LEFT,
    spacing: { after: 0, line: 290 },
    children: [run(o.t ?? '', { bold: o.bold, size: o.size ?? 19, color: o.color })],
  })],
});

const TBL_BORDERS = {
  top: { style: BorderStyle.SINGLE, size: 12, color: NAVY },
  bottom: { style: BorderStyle.SINGLE, size: 12, color: NAVY },
  left: { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' },
  right: { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' },
  insideHorizontal: { style: BorderStyle.SINGLE, size: 4, color: RULE },
  insideVertical: { style: BorderStyle.SINGLE, size: 4, color: RULE },
};

// rows: 첫 행은 머리행. 각 칸은 문자열이거나 {t, align, span, vmerge, bold, fill}
const table = (widths, rows, o = {}) => new Table({
  columnWidths: widths,
  width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA },
  alignment: o.align,
  borders: TBL_BORDERS,
  rows: rows.map((cells, r) => new TableRow({
    tableHeader: r === 0,
    children: cells.map((c, i) => {
      const o = typeof c === 'string' ? { t: c } : { ...c };
      // 머리행은 남색 바탕 흰 글씨, 본문행은 두 줄마다 줄무늬
      if (r === 0) Object.assign(o, { bold: true, color: 'FFFFFF', fill: NAVY, align: o.align ?? AlignmentType.CENTER });
      else if (o.fill === undefined && r % 2 === 0) o.fill = ZEBRA;
      // span이 있으면 합쳐진 칸들의 폭을 더한다
      o.w = o.span ? widths.slice(i, i + o.span).reduce((a, b) => a + b, 0) : widths[i];
      return cell(o);
    }),
  })),
});

const R = (...c) => c;
const won = (t) => ({ t, align: AlignmentType.RIGHT });
const ctr = (t) => ({ t, align: AlignmentType.CENTER });
const MERGE = { t: '', vmerge: VerticalMergeType.CONTINUE };

// ══════════════════════════════════════════════════════════════════════════
// 표지
// ══════════════════════════════════════════════════════════════════════════
const RULE_THICK = (color, size) => new Paragraph({
  spacing: { before: 0, after: 0, line: 240 },
  border: { bottom: { style: BorderStyle.SINGLE, size, color, space: 0 } },
  children: [],
});

const coverInfo = table([2200, 5900], [
  [{ t: '문 서 정 보', span: 2, align: AlignmentType.CENTER }],
  R({ t: '과 업 명', bold: true, fill: 'F2F2F2', align: AlignmentType.CENTER },
    { t: '한국항공대학교 바이브 코딩(Vibe Coding) 기반 학생창업 경진대회 및 창업 특강 운영 용역', fill: 'FFFFFF' }),
  R({ t: '발 주 처', bold: true, fill: 'F2F2F2', align: AlignmentType.CENTER },
    { t: '한국항공대학교', fill: 'FFFFFF' }),
  R({ t: '용역 수행사', bold: true, fill: 'F2F2F2', align: AlignmentType.CENTER },
    { t: '(주)리본마켓', fill: 'FFFFFF' }),
  R({ t: '과업 예산', bold: true, fill: 'F2F2F2', align: AlignmentType.CENTER },
    { t: '금 10,000,000원 (부가가치세 포함)', fill: 'FFFFFF' }),
  R({ t: '작 성 일', bold: true, fill: 'F2F2F2', align: AlignmentType.CENTER },
    { t: '2026. 09. 01.', fill: 'FFFFFF' }),
  R({ t: '문서 상태', bold: true, fill: 'F2F2F2', align: AlignmentType.CENTER },
    { t: '협의용 초안 (미확정)', fill: 'FFFFFF', bold: true, color: DRAFT }),
], { align: AlignmentType.CENTER });

const cover = [
  new Paragraph({ spacing: { after: 700 }, children: [] }),
  P('한국항공대학교', { align: AlignmentType.CENTER, size: 24, color: NAVY_L, bold: true, spacing: 80, after: 500 }),
  RULE_THICK(NAVY, 18),
  new Paragraph({ spacing: { after: 60 }, children: [] }),
  P('과  업  지  시  서', {
    align: AlignmentType.CENTER, bold: true, size: 58, color: NAVY, spacing: 90, after: 100,
  }),
  RULE_THICK(NAVY, 18),
  new Paragraph({ spacing: { after: 420 }, children: [] }),
  P('바이브 코딩(Vibe Coding) 기반', { align: AlignmentType.CENTER, bold: true, size: 30, after: 100 }),
  P('학생창업 경진대회 및 창업 특강 운영 용역', { align: AlignmentType.CENTER, bold: true, size: 30, after: 850 }),
  coverInfo,
  new Paragraph({ spacing: { after: 260 }, children: [] }),
  noticeBox('※ 본 문서는 확정본이 아닌 협의용 초안입니다. 과업 내용·일정·예산은 발주처와의 협의 과정에서 변경될 수 있으며, 최종 내용은 계약 체결 시 확정합니다.'),
  new Paragraph({ spacing: { after: 480 }, children: [] }),
  P('2 0 2 6.  0 9.  0 1.', { align: AlignmentType.CENTER, size: 24, spacing: 40, after: 300 }),
  P('( 주 ) 리 본 마 켓', { align: AlignmentType.CENTER, bold: true, size: 28, spacing: 60 }),
];

// ══════════════════════════════════════════════════════════════════════════
// Ⅰ. 과업 개요
// ══════════════════════════════════════════════════════════════════════════
const s1 = [
  H1('Ⅰ.  과업 개요'),
  bullet('과 업 명 : 한국항공대학교 바이브 코딩(Vibe Coding) 기반 학생창업 경진대회 및 창업 특강 운영 용역'),
  bullet('과업 목적 :'),
  bullet('AI 코딩 도구를 활용해 아이디어를 직접 동작하는 프로토타입으로 구현하는 「바이브 코딩」 역량을 학내에 확산하고, 비전공 학생도 제품을 만들어 볼 수 있는 창업 분위기를 조성한다.', 1),
  bullet('특강(실습) → 1:1 멘토링 → 예선(서류) → 결승(PT)으로 이어지는 체계적인 액셀러레이팅을 통해 학생 창업팀의 실질적 사업화를 지원한다.', 1),
  bullet('예선에서는 사업계획서로 아이템의 타당성을 가리고, 결승에서는 실제로 동작하는 프로토타입을 시연하도록 하여 기획과 구현을 단계적으로 검증한다.', 1),
  bullet('과업 기간 : 계약체결일로부터 ~ 2026년 11월 6일(금)까지'),
  bullet('과업 예산 : 금 10,000,000원 (부가가치세 포함)'),
  bullet('참가 대상 : 한국항공대학교 학부 및 대학원 재학생 (개인 또는 팀, 팀당 1~4인)'),
  bullet('참가 분야 : 바이브 코딩으로 직접 구현한 프로토타입 기반 창업 아이템 (전 산업 분야 자유 주제)'),
  callout('※ 「바이브 코딩」의 정의 — 본 과업에서 「바이브 코딩」은 Claude Code, Cursor, GitHub Copilot 등 AI 코딩 에이전트에게 자연어로 요구사항을 전달하여, 코드 작성 경험이 적은 참가자도 웹·앱 형태의 동작하는 프로토타입(MVP)을 직접 완성하는 개발 방식을 말한다.'),
];

// ══════════════════════════════════════════════════════════════════════════
// Ⅱ. 추진 일정
// ══════════════════════════════════════════════════════════════════════════
const s2 = [
  PB(),
  H1('Ⅱ.  추진 일정'),
  P('행사는 매주 1회, 수·목·금요일 중 지정된 요일에 개최하는 것을 원칙으로 한다. (창업 특강은 발주처가 지정한 9월 28일(월)에 개최한다.)', { after: 200 }),
  table([2400, 1750, 5204], [
    R('단계', '일자', '주요 내용'),
    R({ t: '홍보 및 모집' }, ctr('9.7(월) ~ 9.25(금)'), '포스터·현수막 제작 및 배포, 온라인 홍보, 창업 특강 사전 신청 접수'),
    R({ t: '① 창업 특강 (바이브 코딩 실습)', bold: true }, ctr('9.28(월)'), '외부 전문 강사 특강 2시간(실습 병행), 경진대회 참가 접수 및 멘토링 신청 개시'),
    R({ t: '② 1:1 창업 멘토링', bold: true }, ctr('10.8(목)'), '멘토링 신청 팀(10개 팀) 대상 전문가 1:1 멘토링'),
    R({ t: '예선 접수 마감' }, ctr('10.13(화) 18:00'), '사업계획서 제출 마감 (프로토타입 미제출)'),
    R({ t: '③ 예선 (서류평가)', bold: true }, ctr('10.15(목)'), '심사위원 2인 서류평가, 결승 진출 10개 팀 선정'),
    R({ t: '예선 결과 발표' }, ctr('10.16(금)'), '결승 진출 팀 개별 통보'),
    R({ t: '④ 결승 (PT) 및 시상식', bold: true }, ctr('10.22(목)'), '현직 VC 3인 심사, 팀별 발표·라이브 데모 및 시상'),
    R({ t: '성과물 제출' }, ctr('~ 11.5(목)'), '용역 완료보고서 및 최종 발표자료 제출·검수'),
  ]),
];

// ══════════════════════════════════════════════════════════════════════════
// Ⅲ. 세부 과업 내용
// ══════════════════════════════════════════════════════════════════════════
const s3 = [
  PB(),
  H1('Ⅲ.  세부 과업 내용'),
  P('본 과업을 수행하는 업체(이하 “과업수행자”라 한다)는 다음의 행사 프로세스 전반을 기획하고 운영하여야 한다.', { after: 100 }),

  H2('가. 홍보 및 참가자 모집  (~ 9월 25일(금) 특강 신청 마감)'),
  bullet('홍보물 제작 및 배포 : 교내 배포용 포스터 디자인 및 대형 현수막 제작(출력 포함)을 진행하여야 한다. 홍보물에는 「코딩을 몰라도 2시간 만에 내 서비스를 만든다」는 바이브 코딩의 메시지가 드러나도록 한다.'),
  bullet('온라인 홍보 : 교내 정보광장 게시, 학과 단체채팅방 및 학생 커뮤니티 홍보를 9월 2주 차부터 개시하여야 한다.'),
  bullet('접수 관리 : 온라인 신청 폼을 개설하여 창업 특강 참가 신청을 접수하고, 참가자 DB(소속·학번·연락처·팀 구성 여부)를 구축하여야 한다.'),
  bullet('사전 안내 : 특강은 실습형으로 진행되므로 신청자에게 노트북 지참 및 사전 계정 생성(AI 코딩 도구) 안내를 발송하여야 한다.'),

  H2('나. 바이브 코딩 창업 특강 개최  (9월 28일(월), 2시간)'),
  bullet('강사 섭외 : 「바이브 코딩을 활용한 1인 창업」 및 「AI 코딩 도구로 만드는 MVP」를 주제로 실무 경험을 갖춘 외부 전문 강사를 섭외하여 특강(2시간 기준)을 진행한다.'),
  bullet('구성 : 이론 40분(바이브 코딩 개요·AI 창업 트렌드·대학생 창업 사례) + 실습 80분(참가자가 본인 아이디어를 랜딩페이지 또는 간단한 웹 서비스 형태로 직접 구현)으로 운영한다.'),
  bullet('실습 환경 : 과업수행자는 예제 프롬프트·템플릿과 실습 가이드 자료를 사전에 준비하여 제공하여야 한다. AI 코딩 도구는 특강 참가자 전원에게 무료 체험 계정을, 멘토링 대상 10개 팀에게는 결승 프로토타입 제작을 위해 1인당 50,000원 상당의 유료 크레딧을 지급한다.'),
  bullet('대상 : 경진대회 참가 희망자 전체 및 바이브 코딩·AI 창업에 관심 있는 항공대 재학생 누구나 참여할 수 있도록 운영한다. (정원 60명 내외)'),
  bullet('연계 운영 : 특강 종료 시점에 경진대회 참가 접수와 1:1 멘토링 신청을 동시에 개시하여, 특강 참여가 대회 참가로 이어지도록 한다.'),

  H2('다. 1:1 창업 멘토링 운영  (10월 8일(목))'),
  bullet('대상 선정 : 창업 특강 참가자 및 경진대회 참가 신청자 중 멘토링을 신청한 팀을 대상으로 하며, 신청 순 및 아이템 구체화 정도를 고려하여 총 10개 팀을 배정한다. 신청 팀이 10개 팀을 초과할 경우 발주처와 협의하여 선정 기준을 확정한다.'),
  bullet('멘토링 진행 : 팀당 60분 이상 온/오프라인 멘토링을 1회 이상 진행하며, 하루 내 소화를 위해 2개 트랙을 병행 운영한다.'),
  bullet('과업 목표 : 특강에서 만든 프로토타입에 대한 기능 점검 및 개선 방향 제시, 비즈니스 모델 고도화, 10월 13일 예선 제출용 사업계획서 작성 지도를 수행할 수 있는 전문가를 매칭하여야 한다.'),
  bullet('결과 정리 : 멘토링 종료 후 팀별 멘토링 결과 요약(개선 과제 목록)을 정리하여 참가팀에 회신하여야 한다.'),

  H2('라. 예선(서류) 평가 운영  (10월 13일(화) 접수 마감 ~ 10월 16일(금) 발표)'),
  bullet('제출물 : 참가팀은 「AI 창업 아이템 사업계획서」를 10월 13일(화) 18시까지 제출하여야 한다. 예선 단계에서는 프로토타입을 제출받지 않으며, 사업계획서만으로 평가한다.'),
  bullet('평가 운영 : 접수된 제출물을 대상으로 내/외부 심사위원 2인을 섭외하여 10월 15일(목) 서류평가를 운영한다.'),
  bullet('결과 발표 : 10월 16일(금)까지 결승 진출 총 10개 팀을 확정하여 개별 통보하고, 결승 발표 준비 안내(발표 순서·자료 제출 기한·프로토타입 데모 환경)를 완료하여야 한다. 프로토타입은 결승 단계에서 평가한다.'),
  bullet('심사 기준 : 아래의 배점 기준을 적용한다.'),
  table([3200, 1200, 4954], [
    R('심사 항목', '배점', '평가 내용'),
    R({ t: '아이템 적합성', bold: true }, ctr('30%'), '바이브 코딩을 활용한 창업 아이템으로 적합하며 구현 계획이 구체적인가'),
    R('문제 정의 및 해결방안', ctr('30%'), '해결하려는 문제가 분명하고 해법이 타당한가'),
    R('시장성', ctr('20%'), '목표 고객과 시장 규모가 구체적인가'),
    R('실현 가능성', ctr('20%'), '팀 역량과 자원으로 사업화가 가능한가'),
    R({ t: '합계', bold: true, fill: 'F2F2F2' }, { t: '100%', bold: true, fill: 'F2F2F2', align: AlignmentType.CENTER }, { t: '', fill: 'F2F2F2' }),
  ]),

  H2('마. 결승 경진대회 및 시상식 운영  (10월 22일(목))'),
  bullet('심사위원 섭외 : 현직 벤처투자자(VC) 3명을 초빙하여 심사위원단을 구성한다.'),
  bullet('대회 운영 : 팀당 5분 발표 및 5분 질의응답(Q&A) 방식으로 진행하며, 발표 시간 내에 프로토타입 라이브 데모(또는 시연 영상)를 반드시 포함하도록 한다.'),
  bullet('데모 환경 : 과업수행자는 현장 인터넷(유선/무선), 화면 미러링, 예비 노트북 등 라이브 데모가 가능한 환경을 사전에 구축·점검하여야 한다.'),
  bullet('최종 평가 : 예선 서류 점수(40%)와 결승 발표 점수(60%)를 합산하여 최종 순위를 산출한다.'),
  bullet('행사 준비물 : 심사용 발표 자료집 책자, 상장 및 케이스, 배너, 행사 당일 참석자(학생·심사위원·스태프)를 위한 식대(도시락) 및 다과를 준비하여야 한다. 참가자 기념품은 본 과업에서 제외한다.'),
];

// ══════════════════════════════════════════════════════════════════════════
// Ⅳ. 과업 예산 집행 지침
// ══════════════════════════════════════════════════════════════════════════
const VM = { vmerge: VerticalMergeType.RESTART, bold: true, align: AlignmentType.CENTER };
const s4 = [
  PB(),
  H1('Ⅳ.  과업 예산 집행 지침'),
  P('과업수행자는 성공적인 행사 개최를 위해 아래의 예산 배분 기준을 참고하여 용역을 수행하여야 한다. (본 계약은 총액계약으로 진행함)', { after: 200 }),
  table([1750, 2200, 3604, 1800], [
    R('구분', '항목', '세부 내역', '금액 (원)'),
    R({ t: '상금 및 부상', ...VM }, '대상 (1등)', '1,000,000원 × 1팀', won('1,000,000')),
    R(MERGE, '최우수상 (2등)', '500,000원 × 1팀', won('500,000')),
    R(MERGE, '우수상 (3등)', '300,000원 × 1팀', won('300,000')),
    R(MERGE, '장려상 (4~10등)', '100,000원 상당 상품 × 7팀', won('700,000')),
    R({ t: '전문가 활용비', ...VM }, '창업 특강 강사료', '바이브 코딩 실습 특강 외부 전문 강사 (2시간 기준)', won('500,000')),
    R(MERGE, '1:1 창업 멘토링비', '150,000원 × 10개 팀', won('1,500,000')),
    R(MERGE, '예선 서류 평가료', '150,000원 × 2명 (내/외부 위원)', won('300,000')),
    R(MERGE, '결승 심사수당', '현직 VC 3명 × 400,000원', won('1,200,000')),
    R({ t: '실습 환경비', bold: true, align: AlignmentType.CENTER }, 'AI 코딩 도구 이용료', '멘토링 대상 10개 팀(팀당 3인 기준) 1인당 50,000원 × 30명', won('1,500,000')),
    R({ t: '홍보 및 인쇄비', bold: true, align: AlignmentType.CENTER }, '포스터/자료집 등', '포스터, 현수막, 자료집, 상장 인쇄비', won('700,000')),
    R({ t: '행사 운영비 및 일반관리비', bold: true, align: AlignmentType.CENTER }, '식대/운영/대행수수료', '당일 식대·다과, 소모품, 현장 운영 인력 및 대행 수수료 (기념품 제외)', won('1,800,000')),
    R({ t: '총 합계', span: 3, bold: true, fill: NAVY, color: 'FFFFFF', align: AlignmentType.CENTER, size: 20 },
      { t: '10,000,000', bold: true, fill: NAVY, color: 'FFFFFF', align: AlignmentType.RIGHT, size: 20 }),
  ]),
  callout('※ 원 과업지시서 대비 조정 내역 — ① 장려상 단가(200,000원 → 100,000원)와 결승 심사수당(500,000원 → 400,000원)을 조정하고 참가자 기념품 항목을 제외하여 1,700,000원을 확보하였다. ② 확보한 재원은 「실습 환경비」 신설·증액(+1,200,000원)과 1:1 창업 멘토링비 증액(팀당 100,000원 → 150,000원, +500,000원)에 재배분하였다. ③ 총 예산 10,000,000원(부가가치세 포함)은 변동이 없다.'),
  noticeBox('※ 본 예산 배분은 협의용 초안이며, 발주처와의 협의를 거쳐 확정합니다.'),
];

// ══════════════════════════════════════════════════════════════════════════
// Ⅴ~Ⅵ
// ══════════════════════════════════════════════════════════════════════════
const s5 = [
  PB(),
  H1('Ⅴ.  과업 수행 및 성과물 제출'),
  H2('가. 착수계 제출'),
  bullet('과업수행자는 계약체결일로부터 7일 이내에 착수계, 세부 과업 수행계획서, 투입인력 명단, 보안각서 등을 발주처에 제출하여야 한다.'),
  H2('나. 성과물(최종 보고) 제출'),
  bullet('과업수행자는 행사 종료 후 14일 이내(과업 종료일 전)에 다음의 성과물을 제출하여 검수를 받아야 한다.'),
  bullet('용역 완료보고서(결과보고서) 1부 (행사 사진, 만족도 조사 결과 등 포함)', 1),
  bullet('결승 진출 10개 팀의 최종 발표자료(IR 피치덱) 원본 파일', 1),
  bullet('결승 진출 10개 팀의 프로토타입 데모 링크 및 실행 화면 자료', 1),
  bullet('창업 특강 실습 자료(프롬프트 템플릿, 실습 가이드) 원본 파일', 1),

  PB(),
  H1('Ⅵ.  일반 조건 및 보안 사항'),
  bullet('본 과업지시서는 확정본이 아닌 협의용 초안이다. 과업의 세부 내용, 추진 일정 및 예산 배분은 발주처와 과업수행자의 협의를 거쳐 조정될 수 있으며, 최종 내용은 계약 체결 시 확정한다.'),
  bullet('과업수행자는 본 과업을 수행함에 있어 발주처의 지침을 준수하여야 하며, 행사 진행 중 안전사고가 발생하지 않도록 사전 관리를 철저히 하여야 한다.'),
  bullet('본 과업 수행 중 취득한 참가자의 개인정보, 아이디어(기획서 내용 등), 프로토타입 소스코드 등 모든 정보는 발주처의 동의 없이 외부로 유출할 수 없으며, 과업 종료 시 즉각 폐기하여야 한다.'),
  bullet('참가팀이 제출한 프로토타입의 지식재산권은 참가팀에 귀속하며, 과업수행자와 발주처는 홍보 및 성과 보고 목적에 한하여 이를 활용할 수 있다.'),
  bullet('과업수행자는 참가팀에게 AI 코딩 도구 사용 시의 라이선스 및 개인정보 처리 유의사항을 사전에 안내하여야 한다.'),
  bullet('천재지변 등 불가항력적인 사유로 행사 일정이 변경되거나 취소될 경우, 발주처와 과업수행자는 협의하여 과업을 조정할 수 있다.'),
  new Paragraph({ spacing: { before: 600 }, children: [] }),
  P('- 이 하 여 백 -', { align: AlignmentType.CENTER, size: 19, color: GRAY }),
];

// ══════════════════════════════════════════════════════════════════════════
const margins = { top: convertMillimetersToTwip(25), bottom: convertMillimetersToTwip(20), left: MARGIN, right: MARGIN };

const doc = new Document({
  styles: { default: { document: { run: { font: F, size: 21 }, paragraph: { spacing: { line: 340 } } } } },
  numbering: {
    config: [{
      reference: 'body',
      levels: [
        { level: 0, format: LevelFormat.BULLET, text: '■', alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 400, hanging: 280 } }, run: { size: 14, color: NAVY_L, font: F } } },
        { level: 1, format: LevelFormat.BULLET, text: '–', alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 780, hanging: 280 } }, run: { size: 20, color: GRAY, font: F } } },
      ],
    }],
  },
  sections: [
    // 표지 — 테두리를 두르고 머리말/쪽번호는 넣지 않는다
    {
      properties: {
        page: {
          margin: margins,
          borders: {
            pageBorders: { offsetFrom: PageBorderOffsetFrom.PAGE },
            pageBorderTop: { style: BorderStyle.DOUBLE, size: 12, color: NAVY, space: 24 },
            pageBorderBottom: { style: BorderStyle.DOUBLE, size: 12, color: NAVY, space: 24 },
            pageBorderLeft: { style: BorderStyle.DOUBLE, size: 12, color: NAVY, space: 24 },
            pageBorderRight: { style: BorderStyle.DOUBLE, size: 12, color: NAVY, space: 24 },
          },
        },
      },
      children: cover,
    },
    // 본문 — 머리말에 과업명, 바닥글에 쪽번호
    {
      properties: {
        type: SectionType.NEXT_PAGE,
        page: { margin: margins, pageNumbers: { start: 1 } },
      },
      headers: {
        default: new Header({
          children: [new Paragraph({
            alignment: AlignmentType.RIGHT,
            spacing: { after: 0, line: 240 },
            border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: RULE, space: 6 } },
            children: [
              run('한국항공대학교 바이브 코딩 기반 학생창업 경진대회 및 창업 특강 운영 용역   |   ', { size: 16, color: GRAY }),
              run('협의용 초안', { size: 16, color: DRAFT, bold: true }),
            ],
          })],
        }),
      },
      footers: {
        default: new Footer({
          children: [new Paragraph({
            alignment: AlignmentType.CENTER,
            spacing: { before: 120, line: 240 },
            children: [new TextRun({ children: ['- ', PageNumber.CURRENT, ' -'], size: 18, color: GRAY, font: F })],
          })],
        }),
      },
      children: [...s1, ...s2, ...s3, ...s4, ...s5],
    },
  ],
});

// docx-js는 w:pBdr의 자식을 top→bottom→left→right 순으로 내보내는데, OOXML 스키마는
// top→left→bottom→right를 요구한다. 워드는 눈감아 주지만 검증은 통과하지 못하므로
// 압축을 풀어 순서만 바로잡는다.
const PBDR_ORDER = ['top', 'left', 'bottom', 'right', 'between', 'bar'];
const fixPBdr = (xml) => xml.replace(/<w:pBdr>([\s\S]*?)<\/w:pBdr>/g, (_, inner) => {
  const kids = inner.match(/<w:(?:top|left|bottom|right|between|bar)\b[^>]*\/>/g) || [];
  const sorted = kids.slice().sort(
    (a, b) => PBDR_ORDER.indexOf(a.match(/<w:(\w+)/)[1]) - PBDR_ORDER.indexOf(b.match(/<w:(\w+)/)[1]),
  );
  return `<w:pBdr>${sorted.join('')}</w:pBdr>`;
});

Packer.toBuffer(doc)
  .then((b) => require('jszip').loadAsync(b))
  .then(async (zip) => {
    zip.file('word/document.xml', fixPBdr(await zip.file('word/document.xml').async('string')));
    return zip.generateAsync({ type: 'nodebuffer', compression: 'DEFLATE' });
  })
  .then((b) => {
    fs.writeFileSync(process.argv[2], b);
    console.log('wrote', process.argv[2], b.length, 'bytes');
  });
