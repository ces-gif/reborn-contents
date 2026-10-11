import type { MetaDescriptor } from "react-router";
import { COMPANY, SITE_URL } from "~/config/site";

export const DEFAULT_TITLE = "수멕스(SUMEX) · Stryker 의료기기 유통 – 관절경 · 복강경 · 수술 파워툴";
export const DEFAULT_DESCRIPTION =
  "주식회사 수멕스는 Stryker 관절경·복강경 영상 장비와 수술 파워툴을 정형외과, 신경외과, 일반외과 수술실에 공급하는 의료기기 유통사입니다. 1788 4K OLED 플랫폼 데모와 도입을 문의하세요.";

type SeoInput = { title?: string; description?: string; path: string; image?: string; noindex?: boolean };

/** 페이지별 meta 묶음: title, description, canonical, Open Graph, Twitter */
export function seo({ title, description = DEFAULT_DESCRIPTION, path, image = "/og/default.png", noindex }: SeoInput): MetaDescriptor[] {
  const fullTitle = title ? `${title} | 수멕스(SUMEX)` : DEFAULT_TITLE;
  const url = `${SITE_URL}${path}`;
  const img = image.startsWith("http") ? image : `${SITE_URL}${image}`;
  const tags: MetaDescriptor[] = [
    { title: fullTitle },
    { name: "description", content: description },
    { tagName: "link", rel: "canonical", href: url },
    { property: "og:type", content: "website" },
    { property: "og:site_name", content: `${COMPANY.brand} · ${COMPANY.name}` },
    { property: "og:locale", content: "ko_KR" },
    { property: "og:title", content: fullTitle },
    { property: "og:description", content: description },
    { property: "og:url", content: url },
    { property: "og:image", content: img },
    { name: "twitter:card", content: "summary_large_image" },
  ];
  if (noindex) tags.push({ name: "robots", content: "noindex, follow" });
  return tags;
}

export const abs = (path: string) => `${SITE_URL}${path}`;

export function breadcrumb(items: { name: string; path: string }[]) {
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [{ name: "홈", path: "/" }, ...items].map((it, i) => ({
      "@type": "ListItem",
      position: i + 1,
      name: it.name,
      item: abs(it.path),
    })),
  };
}

export const organizationLd = {
  "@context": "https://schema.org",
  "@type": "Organization",
  name: COMPANY.brand,
  legalName: COMPANY.name,
  alternateName: [COMPANY.nameEn, "수멕스"],
  url: SITE_URL,
  logo: abs("/brand/sumex-symbol.png"),
  foundingDate: COMPANY.founded,
  description: DEFAULT_DESCRIPTION,
  address: {
    "@type": "PostalAddress",
    streetAddress: COMPANY.street,
    addressLocality: COMPANY.locality,
    addressRegion: COMPANY.region,
    addressCountry: "KR",
  },
};

export const localBusinessLd = {
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  name: `${COMPANY.name} (${COMPANY.brand})`,
  url: SITE_URL,
  image: abs("/og/default.png"),
  address: organizationLd.address,
};

export function faqLd(faq: { q: string; a: string }[]) {
  return {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: faq.map((f) => ({ "@type": "Question", name: f.q, acceptedAnswer: { "@type": "Answer", text: f.a } })),
  };
}
