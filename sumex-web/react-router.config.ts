import type { Config } from "@react-router/dev/config";
import { allPaths } from "./app/data/paths";

// ssr:false + prerender → 모든 공개 페이지를 빌드 시 완성된 HTML로 생성 (SEO/GEO).
// 정적 호스팅(Vercel, Firebase Hosting 등)에 build/client 폴더만 올리면 된다.
export default {
  ssr: false,
  async prerender() {
    return [...allPaths(), "/sitemap.xml"];
  },
} satisfies Config;
