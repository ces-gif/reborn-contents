import { BODY_PARTS } from "./bodyParts";
import { CATEGORIES, PRODUCTS } from "./products";

/** 프리렌더(정적 HTML 생성)와 사이트맵에 쓰는 공개 경로 목록 */
export function allPaths() {
  return [
    "/",
    "/about",
    "/products/1788",
    "/products/library",
    ...Object.keys(CATEGORIES).map((c) => `/products/${c}`),
    ...PRODUCTS.map((p) => `/products/${p.category}/${p.slug}`),
    "/explore",
    ...BODY_PARTS.map((b) => `/explore/${b.id}`),
    "/newsletter",
    "/contact",
  ];
}
