// 2026 바이브 코딩 창업경진대회 상장 — Word (A4 가로, 1매 1쪽)
// 팀명·팀원은 카카오톡 대화 '본문' 에 적힌 내용만 사용한다.
const fs = require('fs');
const {
  Document, Packer, Paragraph, TextRun, AlignmentType, PageOrientation,
  BorderStyle, PageBorderOffsetFrom, LineRuleType, convertMillimetersToTwip,
} = require('docx');

const F = { ascii: '바탕', hAnsi: '바탕', eastAsia: '바탕', cs: '바탕', hint: 'eastAsia' };
const NAVY = '17365D', DIM = '8A94A6';

const TITLE = '2026 바이브 코딩 창업경진대회';
const DATE = '2026년 10월 22일';
const GIVER = '고 양 산 업 진 흥 원 장';
const GIVER_NAME = '한 동 균';

const BODY = {
  '대상': ['인공지능을 활용한 창의적인 아이디어와 뛰어난 사업화 역량을 선보였으며,',
           '심사 결과 가장 우수한 성적을 거두었으므로',
           '이에 그 성과를 높이 기려 이 상장을 수여합니다.'],
  '최우수상': ['해결하고자 하는 문제를 명확히 정의하고 탄탄한 비즈니스 모델을 제시하였으며,',
               '심사 결과 그 우수성을 인정받았으므로',
               '이에 그 노력을 기려 이 상장을 수여합니다.'],
  '우수상': ['인공지능을 활용한 실현 가능한 해결책과 구체적인 실행 계획을 제시하였으며,',
             '심사 결과 그 성과를 인정받았으므로',
             '이에 그 노력을 기려 이 상장을 수여합니다.'],
  '장려상': ['성실한 준비와 끝까지 포기하지 않는 열정으로 전 과정을 완주하였으며,',
             '창업에 대한 굳은 의지를 보여주었으므로',
             '이에 그 뜻을 기려 이 상장을 수여합니다.'],
};

// [번호, 상격, 수상자] — 팀명은 상장에 적지 않는다
const AWARDS = [
  ['01', '대상',     ['유진수', '박준호']],
  ['02', '최우수상', ['김현수']],
  ['03', '우수상',   ['하정묵']],
  ['04', '장려상',   ['권오규', '장보성']],
  ['05', '장려상',   ['김승준']],
  ['06', '장려상',   ['김효나', '주소민']],
  ['07', '장려상',   ['곽세인', '강미주']],
  ['08', '장려상',   ['김성훈', '김채원', '신재훈', '김수빈']],
  ['09', '장려상',   ['윤지성']],
];

const run = (t, o = {}) => new TextRun({
  text: t, bold: o.bold, color: o.color, size: o.size, font: F,
  characterSpacing: o.sp,
});
const P = (t, o = {}) => new Paragraph({
  alignment: o.align ?? AlignmentType.CENTER,
  spacing: { before: o.before ?? 0, after: o.after ?? 0,
             line: o.line ?? 300, lineRule: LineRuleType.AUTO },
  children: Array.isArray(t) ? t : [run(t, o)],
});

const cert = ([no, rank, members]) => {
  const names = members.join('，　');
  return [
    P(`제 2026-${no}호`, { align: AlignmentType.LEFT, size: 17, color: DIM, after: 360 }),
    P('상    장', { bold: true, size: 112, color: NAVY, sp: 100, before: 200, after: 420 }),
    P(rank, { bold: true, size: 48, color: NAVY, sp: 50, after: 460 }),
    P(`성　　명 ：　${names}`, { size: 34, after: 0 }),
    P(`위 사람은 「${TITLE}」에 참가하여`, { size: 28, before: 500, after: 130 }),
    ...BODY[rank].map((l, i) => P(l, { size: 28, after: i === 2 ? 0 : 130 })),
    P(DATE, { size: 30, sp: 30, before: 620, after: 340 }),
    P([run(`${GIVER}　　${GIVER_NAME}`, { bold: true, size: 42, sp: 40 }),
       run('  (인)', { size: 18, color: DIM })], { after: 0 }),
  ];
};

const B = { style: BorderStyle.DOUBLE, size: 18, color: NAVY, space: 24 };

const doc = new Document({
  styles: { default: { document: { run: { font: F, size: 28 } } } },
  sections: AWARDS.map((a) => ({
    properties: {
      page: {
        size: { orientation: PageOrientation.LANDSCAPE },
        margin: {
          top: convertMillimetersToTwip(22), bottom: convertMillimetersToTwip(18),
          left: convertMillimetersToTwip(28), right: convertMillimetersToTwip(28),
        },
        borders: {
          pageBorderTop: B, pageBorderBottom: B, pageBorderLeft: B, pageBorderRight: B,
          pageBorders: { offsetFrom: PageBorderOffsetFrom.PAGE },
        },
      },
    },
    children: cert(a),
  })),
});

Packer.toBuffer(doc).then((b) => {
  fs.writeFileSync(process.argv[2], b);
  console.log('   ', process.argv[2], `(${AWARDS.length}매, ${b.length} bytes)`);
});
