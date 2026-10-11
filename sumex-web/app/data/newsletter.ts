// 뉴스레터 데이터. 현재는 화면 구성 확인용 샘플이며 실제 발행 콘텐츠로 교체한다.
// 운영 시 newsletter/{YYYY-MM-DD} 단위로 추가. 뉴스는 원문 전재 금지, 요약 + 출처 + 원문 링크.
export type NewsletterIssue = {
  date: string;
  sample: boolean;
  cards: { title: string; sub: string }[];
  news: { source: string; date: string; title: string; summary: string; specialty: string[]; url: string | null }[];
};

export const ISSUES: NewsletterIssue[] = [
  {
    date: "2026-10-10",
    sample: true,
    cards: [
      { title: "SUMEX DAILY", sub: "2026.10.10 오늘의 헬스케어 브리핑" },
      { title: "오늘의 키워드", sub: "샘플 카드 · 실제 발행 시 교체" },
      { title: "국내 의료기기", sub: "샘플 카드 · 실제 발행 시 교체" },
      { title: "해외 의료기기", sub: "샘플 카드 · 실제 발행 시 교체" },
      { title: "병원 · 정책", sub: "샘플 카드 · 실제 발행 시 교체" },
      { title: "제품 노트", sub: "샘플 카드 · 실제 발행 시 교체" },
      { title: "구독 안내", sub: "매일 아침 7장 카드뉴스로 받아보세요" },
    ],
    news: [
      { source: "출처 예시", date: "2026.10.10", title: "샘플 기사 제목 1", summary: "실제 발행 시 기사 요약 3줄과 출처, 원문 링크가 표시됩니다.", specialty: ["OS"], url: null },
      { source: "출처 예시", date: "2026.10.10", title: "샘플 기사 제목 2", summary: "뉴스 기사는 원문을 옮기지 않고 요약과 출처, 원문 링크로만 소개합니다.", specialty: ["GS"], url: null },
      { source: "출처 예시", date: "2026.10.09", title: "샘플 기사 제목 3", summary: "진료과 태그로 관심 분야 기사를 빠르게 찾을 수 있습니다.", specialty: ["NS"], url: null },
    ],
  },
];

export const LATEST_ISSUE = ISSUES[0];
