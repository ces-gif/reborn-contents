const fs = require('fs');
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle,
  PageBreak, LevelFormat, convertInchesToTwip,
} = require('docx');

const KO = { ascii: '맑은 고딕', hAnsi: '맑은 고딕', eastAsia: '맑은 고딕', cs: '맑은 고딕' };
const NAVY = '1F3864';

const P = (text, o = {}) => new Paragraph({
  alignment: o.align,
  spacing: { before: o.before ?? 0, after: o.after ?? 100, line: 300 },
  indent: o.indent,
  children: [new TextRun({ text, bold: o.bold, size: o.size ?? 20, color: o.color, font: KO })],
});

// 1-depth bullet "●", 2-depth "○" — drawn as literal glyphs inside an indented paragraph
// is discouraged; use real numbering instead.
const bullet = (text, level = 0) => new Paragraph({
  numbering: { reference: 'dots', level },
  spacing: { after: 60, line: 300 },
  children: [new TextRun({ text, size: 20, font: KO })],
});

const H1 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_1,
  spacing: { before: 320, after: 160 },
  children: [new TextRun({ text, bold: true, size: 26, color: NAVY, font: KO })],
});

const H2 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_2,
  spacing: { before: 220, after: 100 },
  children: [new TextRun({ text, bold: true, size: 22, color: '000000', font: KO })],
});

const cell = (text, { w, bold, fill, align } = {}) => new TableCell({
  width: { size: w, type: WidthType.DXA },
  shading: fill ? { type: ShadingType.CLEAR, fill, color: 'auto' } : undefined,
  margins: { top: 60, bottom: 60, left: 100, right: 100 },
  children: [new Paragraph({
    alignment: align ?? AlignmentType.LEFT,
    spacing: { after: 0, line: 260 },
    children: [new TextRun({ text, bold, size: 18, font: KO })],
  })],
});

const table = (widths, rows) => new Table({
  columnWidths: widths,
  width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA },
  rows: rows.map((cells, i) => new TableRow({
    tableHeader: i === 0,
    children: cells.map((c, j) => cell(c.t, {
      w: widths[j], bold: i === 0 || c.bold, fill: i === 0 ? 'D9E2F3' : c.fill, align: c.align,
    })),
  })),
});

const R = (...vals) => vals.map((v) => (typeof v === 'string' ? { t: v } : v));
const num = (t) => ({ t, align: AlignmentType.RIGHT });

// ---------------------------------------------------------------- 표지
const cover = [
  new Paragraph({ spacing: { after: 2400 }, children: [] }),
  P('과  업  지  시  서', { align: AlignmentType.CENTER, bold: true, size: 56, color: NAVY, after: 600 }),
  P('한국항공대학교', { align: AlignmentType.CENTER, bold: true, size: 30, after: 120 }),
  P('바이브 코딩(Vibe Coding) 기반 학생창업 경진대회 및 창업 특강', { align: AlignmentType.CENTER, bold: true, size: 30, after: 120 }),
  P('운영 용역', { align: AlignmentType.CENTER, bold: true, size: 30, after: 3000 }),
  P('2026. 09. 02.', { align: AlignmentType.CENTER, size: 22, after: 200 }),
  P('용역 수행사 : (주)리본마켓', { align: AlignmentType.CENTER, size: 22 }),
  new Paragraph({ children: [new PageBreak()] }),
];

// ---------------------------------------------------------------- 1. 과업 개요
const s1 = [
  H1('1. 과업 개요'),
  bullet('과 업 명 : 한국항공대학교 바이브 코딩(Vibe Coding) 기반 학생창업 경진대회 및 창업 특강 운영 용역'),
  bullet('과업 목적 :'),
  bullet('AI 코딩 도구를 활용해 아이디어를 직접 동작하는 프로토타입으로 구현하는 「바이브 코딩」 역량을 학내에 확산하고, 비전공 학생도 제품을 만들어 볼 수 있는 창업 분위기를 조성한다.', 1),
  bullet('특강(실습) → 1:1 멘토링 → 예선(서류) → 결승(PT)으로 이어지는 체계적인 액셀러레이팅을 통해 학생 창업팀의 실질적 사업화를 지원한다.', 1),
  bullet('기획안에 머무르지 않고, 실제로 실행되는 결과물(프로토타입)을 심사 대상으로 삼아 창업 아이템의 실현 가능성을 검증한다.', 1),
  bullet('과업 기간 : 계약체결일로부터 ~ 2026년 11월 6일(금)까지'),
  bullet('과업 예산 : 금 10,000,000원 (부가가치세 포함)'),
  bullet('참가 대상 : 한국항공대학교 학부 및 대학원 재학생 (개인 또는 팀, 팀당 1~4인)'),
  bullet('참가 분야 : 바이브 코딩으로 직접 구현한 프로토타입 기반 창업 아이템 (전 산업 분야 자유 주제)'),
  bullet('바이브 코딩의 정의 : 본 과업에서 「바이브 코딩」은 Claude Code, Cursor, GitHub Copilot 등 AI 코딩 에이전트에게 자연어로 요구사항을 전달하여, 코드 작성 경험이 적은 참가자도 웹·앱 형태의 동작하는 프로토타입(MVP)을 직접 완성하는 개발 방식을 말한다.'),
];

// ---------------------------------------------------------------- 2. 추진 일정
const s2 = [
  H1('2. 추진 일정'),
  P('행사는 매주 1회, 수·목·금요일 중 지정된 요일에 개최하는 것을 원칙으로 한다. (창업 특강은 발주처가 지정한 9월 28일(월)에 개최한다.)', { after: 160 }),
  table([1700, 1500, 5800], [
    R('단계', '일자', '주요 내용'),
    R('홍보 및 모집', '9.7(월)~9.25(금)', '포스터·현수막 제작 및 배포, 온라인 홍보, 창업 특강 사전 신청 접수'),
    R('① 창업 특강 (바이브 코딩 실습)', '9.28(월)', '외부 전문 강사 특강 2시간(실습 병행), 경진대회 참가 접수 및 멘토링 신청 개시'),
    R('② 1:1 창업 멘토링', '10.8(목)', '멘토링 신청 팀(10개 팀) 대상 전문가 1:1 멘토링'),
    R('예선 접수 마감', '10.13(화) 18:00', '기획서 + 프로토타입 데모 링크 제출 마감'),
    R('③ 예선 (서류평가)', '10.15(목)', '심사위원 2인 서류평가, 결승 진출 10개 팀 선정'),
    R('예선 결과 발표', '10.16(금)', '결승 진출 팀 개별 통보'),
    R('④ 결승 (PT) 및 시상식', '10.22(목)', '현직 VC 3인 심사, 팀별 발표·라이브 데모 및 시상'),
    R('성과물 제출', '~ 11.5(목)', '용역 완료보고서 및 최종 발표자료 제출·검수'),
  ]),
];

// ---------------------------------------------------------------- 3. 세부 과업
const s3 = [
  H1('3. 세부 과업 내용'),
  P('본 과업을 수행하는 업체(이하 “과업수행자”라 한다)는 다음의 행사 프로세스 전반을 기획하고 운영하여야 한다.', { after: 200 }),

  H2('가. 홍보 및 참가자 모집 (~ 9월 25일(금) 특강 신청 마감)'),
  bullet('홍보물 제작 및 배포 : 교내 배포용 포스터 디자인 및 대형 현수막 제작(출력 포함)을 진행하여야 한다. 홍보물에는 「코딩을 몰라도 2시간 만에 내 서비스를 만든다」는 바이브 코딩의 메시지가 드러나도록 한다.'),
  bullet('온라인 홍보 : 교내 정보광장 게시, 학과 단체채팅방 및 학생 커뮤니티 홍보를 9월 2주 차부터 개시하여야 한다.'),
  bullet('접수 관리 : 온라인 신청 폼을 개설하여 창업 특강 참가 신청을 접수하고, 참가자 DB(소속·학번·연락처·팀 구성 여부)를 구축하여야 한다.'),
  bullet('사전 안내 : 특강은 실습형으로 진행되므로 신청자에게 노트북 지참 및 사전 계정 생성(AI 코딩 도구) 안내를 발송하여야 한다.'),

  H2('나. 바이브 코딩 창업 특강 개최 (9월 28일(월), 2시간)'),
  bullet('강사 섭외 : 「바이브 코딩을 활용한 1인 창업」 및 「AI 코딩 도구로 만드는 MVP」를 주제로 실무 경험을 갖춘 외부 전문 강사를 섭외하여 특강(2시간 기준)을 진행한다.'),
  bullet('구성 : 이론 40분(바이브 코딩 개요·AI 창업 트렌드·대학생 창업 사례) + 실습 80분(참가자가 본인 아이디어를 랜딩페이지 또는 간단한 웹 서비스 형태로 직접 구현)으로 운영한다.'),
  bullet('실습 환경 : 과업수행자는 실습에 필요한 AI 코딩 도구 계정 및 크레딧, 예제 프롬프트·템플릿, 실습 가이드 자료를 사전에 준비하여 제공하여야 한다.'),
  bullet('대상 : 경진대회 참가 희망자 전체 및 바이브 코딩·AI 창업에 관심 있는 항공대 재학생 누구나 참여할 수 있도록 운영한다. (정원 60명 내외)'),
  bullet('연계 운영 : 특강 종료 시점에 경진대회 참가 접수와 1:1 멘토링 신청을 동시에 개시하여, 특강 참여가 대회 참가로 이어지도록 한다.'),

  H2('다. 1:1 창업 멘토링 운영 (10월 8일(목))'),
  bullet('대상 선정 : 창업 특강 참가자 및 경진대회 참가 신청자 중 멘토링을 신청한 팀을 대상으로 하며, 신청 순 및 아이템 구체화 정도를 고려하여 총 10개 팀을 배정한다. 신청 팀이 10개 팀을 초과할 경우 발주처와 협의하여 선정 기준을 확정한다.'),
  bullet('멘토링 진행 : 팀당 40분 이상 온/오프라인 멘토링을 1회 이상 진행하며, 하루 내 소화를 위해 2개 트랙을 병행 운영한다.'),
  bullet('과업 목표 : 특강에서 만든 프로토타입에 대한 기능 점검 및 개선 방향 제시, 비즈니스 모델 고도화, 10월 13일 예선 제출물(기획서·데모) 구성 지도를 수행할 수 있는 전문가를 매칭하여야 한다.'),
  bullet('결과 정리 : 멘토링 종료 후 팀별 멘토링 결과 요약(개선 과제 목록)을 정리하여 참가팀에 회신하여야 한다.'),

  H2('라. 예선(서류) 평가 운영 (10월 13일(화) 접수 마감 ~ 10월 16일(금) 발표)'),
  bullet('제출물 : 참가팀은 ① AI 창업 아이템 기획서, ② 바이브 코딩으로 구현한 프로토타입의 데모 URL 또는 3분 이내 실행 영상, ③ 소스 저장소(GitHub 등) 링크를 10월 13일(화) 18시까지 제출하여야 한다.'),
  bullet('평가 운영 : 접수된 제출물을 대상으로 내/외부 심사위원 2인을 섭외하여 10월 15일(목) 서류평가를 운영한다.'),
  bullet('심사 기준 적용 : 프로토타입 구현 완성도(30%), 문제 정의 및 해결방안(30%), 시장성(20%), 실현 가능성(20%)의 배점 기준을 적용한다.'),
  bullet('결과 발표 : 10월 16일(금)까지 결승 진출 총 10개 팀을 확정하여 개별 통보하고, 결승 발표 준비 안내(발표 순서·자료 제출 기한·데모 환경)를 완료하여야 한다.'),

  H2('마. 결승 경진대회 및 시상식 운영 (10월 22일(목))'),
  bullet('심사위원 섭외 : 현직 벤처투자자(VC) 3명을 초빙하여 심사위원단을 구성한다.'),
  bullet('대회 운영 : 팀당 5분 발표 및 5분 질의응답(Q&A) 방식으로 진행하며, 발표 시간 내에 프로토타입 라이브 데모(또는 시연 영상)를 반드시 포함하도록 한다.'),
  bullet('데모 환경 : 과업수행자는 현장 인터넷(유선/무선), 화면 미러링, 예비 노트북 등 라이브 데모가 가능한 환경을 사전에 구축·점검하여야 한다.'),
  bullet('최종 평가 : 예선 서류 점수(40%)와 결승 발표 점수(60%)를 합산하여 최종 순위를 산출한다.'),
  bullet('행사 준비물 : 심사용 발표 자료집 책자, 상장 및 케이스, 참가자 기념품(다이어리 등), 배너, 행사 당일 참석자(학생·심사위원·스태프)를 위한 식대(도시락) 및 다과를 준비하여야 한다.'),
];

// ---------------------------------------------------------------- 4. 예산
const s4 = [
  H1('4. 과업 예산 집행 지침'),
  P('과업수행자는 성공적인 행사 개최를 위해 아래의 예산 배분 기준을 참고하여 용역을 수행하여야 한다. (본 계약은 총액계약으로 진행함)', { after: 160 }),
  table([1700, 2200, 3400, 1700], [
    R('구분', '항목', '세부 내역', '금액 (원)'),
    R('상금 및 부상', '대상 (1등)', '1,000,000원 × 1팀', num('1,000,000')),
    R('', '최우수상 (2등)', '500,000원 × 1팀', num('500,000')),
    R('', '우수상 (3등)', '300,000원 × 1팀', num('300,000')),
    R('', '장려상 (4~10등)', '200,000원 상당 상품 × 7팀', num('1,400,000')),
    R('전문가 활용비', '창업 특강 강사료', '바이브 코딩 실습 특강 외부 전문 강사 (2시간 기준)', num('500,000')),
    R('', '1:1 창업 멘토링비', '100,000원 × 10개 팀', num('1,000,000')),
    R('', '예선 서류 평가료', '150,000원 × 2명 (내/외부 위원)', num('300,000')),
    R('', '결승 심사수당', '현직 VC 3명 × 500,000원', num('1,500,000')),
    R('실습 환경비', 'AI 코딩 도구 이용료', '특강·멘토링 실습용 AI 코딩 도구 계정 및 크레딧 10,000원 × 30팀', num('300,000')),
    R('홍보 및 인쇄비', '포스터/자료집 등', '포스터, 현수막, 자료집, 상장 인쇄비', num('700,000')),
    R('행사 운영비 및 일반관리비', '식대/기념품/대행수수료', '당일 식대·다과, 기념품, 소모품, 현장 운영 인력 및 대행 수수료', num('2,500,000')),
    [{ t: '총 합계', bold: true, fill: 'F2F2F2' }, { t: '', fill: 'F2F2F2' }, { t: '', fill: 'F2F2F2' },
     { t: '10,000,000', bold: true, fill: 'F2F2F2', align: AlignmentType.RIGHT }],
  ]),
  P('※ 원 과업지시서 대비 「행사 운영비 및 일반관리비」에서 300,000원을 조정하여 「실습 환경비」를 신설하였으며, 총 예산 10,000,000원(부가가치세 포함)은 변동이 없다.', { before: 140, size: 18 }),
];

// ---------------------------------------------------------------- 5~6
const s5 = [
  H1('5. 과업 수행 및 성과물 제출'),
  H2('가. 착수계 제출'),
  bullet('과업수행자는 계약체결일로부터 7일 이내에 착수계, 세부 과업 수행계획서, 투입인력 명단, 보안각서 등을 발주처에 제출하여야 한다.'),
  H2('나. 성과물(최종 보고) 제출'),
  bullet('과업수행자는 행사 종료 후 14일 이내(과업 종료일 전)에 다음의 성과물을 제출하여 검수를 받아야 한다.'),
  bullet('용역 완료보고서(결과보고서) 1부 (행사 사진, 만족도 조사 결과 등 포함)', 1),
  bullet('결승 진출 10개 팀의 최종 발표자료(IR 피치덱) 원본 파일', 1),
  bullet('결승 진출 10개 팀의 프로토타입 데모 링크 및 실행 화면 자료', 1),
  bullet('창업 특강 실습 자료(프롬프트 템플릿, 실습 가이드) 원본 파일', 1),

  H1('6. 일반 조건 및 보안 사항'),
  bullet('과업수행자는 본 과업을 수행함에 있어 발주처의 지침을 준수하여야 하며, 행사 진행 중 안전사고가 발생하지 않도록 사전 관리를 철저히 하여야 한다.'),
  bullet('본 과업 수행 중 취득한 참가자의 개인정보, 아이디어(기획서 내용 등), 프로토타입 소스코드 등 모든 정보는 발주처의 동의 없이 외부로 유출할 수 없으며, 과업 종료 시 즉각 폐기하여야 한다.'),
  bullet('참가팀이 제출한 프로토타입의 지식재산권은 참가팀에 귀속하며, 과업수행자와 발주처는 홍보 및 성과 보고 목적에 한하여 이를 활용할 수 있다.'),
  bullet('과업수행자는 참가팀에게 AI 코딩 도구 사용 시의 라이선스 및 개인정보 처리 유의사항을 사전에 안내하여야 한다.'),
  bullet('천재지변 등 불가항력적인 사유로 행사 일정이 변경되거나 취소될 경우, 발주처와 과업수행자는 협의하여 과업을 조정할 수 있다.'),
];

const doc = new Document({
  styles: { default: { document: { run: { font: KO, size: 20 } } } },
  numbering: {
    config: [{
      reference: 'dots',
      levels: [
        { level: 0, format: LevelFormat.BULLET, text: '●', alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 340, hanging: 240 } },
                   run: { size: 14, font: KO } } },
        { level: 1, format: LevelFormat.BULLET, text: '○', alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 700, hanging: 240 } },
                   run: { size: 14, font: KO } } },
      ],
    }],
  },
  sections: [{
    properties: { page: { margin: { top: convertInchesToTwip(1), bottom: convertInchesToTwip(1), left: convertInchesToTwip(1), right: convertInchesToTwip(1) } } },
    children: [...cover, ...s1, ...s2, ...s3, ...s4, ...s5],
  }],
});

Packer.toBuffer(doc).then((b) => {
  fs.writeFileSync(process.argv[2], b);
  console.log('wrote', process.argv[2], b.length, 'bytes');
});
