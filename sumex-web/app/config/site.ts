// 사이트 전역 설정. null 값은 확인 후 채운다 (DESIGN.md "설정값 placeholder").
export const SITE_URL = "http://localhost:5173"; // TODO: 실제 도메인으로 교체

export const COMPANY = {
  name: "주식회사 수멕스",
  nameEn: "SUMEX Corp.",
  brand: "SUMEX",
  ceo: "최승수",
  founded: "2023-08-21",
  foundedLabel: "2023년 8월 21일",
  business: "의료기기 도매업",
  bizNo: "435-81-03240",
  address: "서울특별시 송파구 충민로 66, 가든파이브라이프 T동 8층 T-8008호 (문정동)",
  addressShort: "서울특별시 송파구 충민로 66",
  street: "충민로 66, 가든파이브라이프 T동 8층 T-8008호",
  locality: "송파구",
  region: "서울특별시",
  postalCode: null as string | null,
  tagline: "Surgical & Medical healthcare supplier delivering Excellence",
};

export const CONTACT = {
  email: null as string | null, // TODO: 회사 대표 메일
  phone: null as string | null, // TODO: 대표 번호
  kakaoOpenChatUrl: null as string | null, // TODO: 오픈채팅방 개설 후 입력
};

export const SOCIAL = {
  instagram: { url: null as string | null, label: "Instagram" },
  blog: { url: null as string | null, label: "Blog" },
  youtube: { url: null as string | null, label: "YouTube" },
};

export const KAKAO_MAP_LINK = `https://map.kakao.com/?q=${encodeURIComponent(COMPANY.addressShort)}`;
export const KAKAO_ROUTE_LINK = `https://map.kakao.com/link/search/${encodeURIComponent(COMPANY.addressShort)}`;

export const NAV = [
  { to: "/about", label: "회사소개" },
  { to: "/products/1788", label: "1788", dot: true },
  { to: "/explore", label: "인체로 찾기" },
  { to: "/products/arthro", label: "ARTHRO" },
  { to: "/products/laparo", label: "LAPARO" },
  { to: "/products/instrument", label: "INSTRUMENT" },
  { to: "/ai-search", label: "AI 제품검색" },
  { to: "/newsletter", label: "뉴스레터" },
  { to: "/contact", label: "문의" },
] as const;
