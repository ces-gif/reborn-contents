import { Outlet } from "react-router";
import { Footer } from "~/components/Footer";
import { Header } from "~/components/Header";
import { JsonLd, ToastProvider } from "~/components/ui";
import { organizationLd } from "~/lib/seo";

export default function SiteLayout() {
  return (
    <ToastProvider>
      <a href="#main" className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[200] focus:bg-primary focus:px-4 focus:py-2 focus:text-black">
        본문 바로가기
      </a>
      {/* TODO: 정식 오픈 전 제거 */}
      <div className="border-b border-line bg-surface py-2 text-center t-label-sm normal-case tracking-[0.04em] text-muted">
        개발 시안 · 제품 문구와 수치는 한국스트라이커 검수 전입니다
      </div>
      <Header />
      <main id="main">
        <Outlet />
      </main>
      <Footer />
      <JsonLd data={organizationLd} />
    </ToastProvider>
  );
}
