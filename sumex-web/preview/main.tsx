// 링크 공유용 미리보기 빌드: 모든 페이지를 HTML 파일 하나에 담는다 (주소창은 바뀌지 않는 MemoryRouter).
// 실제 사이트는 react-router.config.ts의 프리렌더 빌드를 쓴다.
import { useEffect } from "react";
import { createRoot } from "react-dom/client";
import { createMemoryRouter, RouterProvider, useLocation, useParams, Outlet } from "react-router";
import "~/app.css";
import SiteLayout from "~/routes/_layout";
import Home from "~/routes/home";
import About from "~/routes/about";
import Product1788 from "~/routes/product-1788";
import Library from "~/routes/library";
import Category from "~/routes/category";
import ProductPage from "~/routes/product";
import Explore from "~/routes/explore";
import AiSearch from "~/routes/ai-search";
import Newsletter from "~/routes/newsletter";
import Contact from "~/routes/contact";
import NotFound from "~/routes/not-found";

// 프레임워크 모드처럼 params를 props로 넘겨준다
function WithParams({ C }: { C: React.ComponentType<any> }) {
  const params = useParams();
  return <C params={params} />;
}

function ScrollTop() {
  const { pathname, hash } = useLocation();
  useEffect(() => {
    if (hash) return document.getElementById(hash.slice(1))?.scrollIntoView();
    if (!pathname.startsWith("/explore")) window.scrollTo(0, 0);
  }, [pathname, hash]);
  return <Outlet />;
}

const router = createMemoryRouter([
  {
    element: <ScrollTop />,
    children: [
      {
        element: <SiteLayout />,
        children: [
          { index: true, element: <Home /> },
          { path: "about", element: <About /> },
          { path: "products/1788", element: <Product1788 /> },
          { path: "products/library", element: <Library /> },
          { path: "products/:category", element: <WithParams C={Category} />, errorElement: <NotFound /> },
          { path: "products/:category/:slug", element: <WithParams C={ProductPage} />, errorElement: <NotFound /> },
          { path: "explore", element: <WithParams C={Explore} /> },
          { path: "explore/:part", element: <WithParams C={Explore} /> },
          { path: "ai-search", element: <AiSearch /> },
          { path: "newsletter", element: <Newsletter /> },
          { path: "contact", element: <Contact /> },
          { path: "*", element: <NotFound /> },
        ],
      },
    ],
  },
]);

createRoot(document.getElementById("root")!).render(<RouterProvider router={router} />);
