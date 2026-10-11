import { isRouteErrorResponse, Links, Meta, Outlet, Scripts, ScrollRestoration } from "react-router";
import type { Route } from "./+types/root";
import "./app.css";

export const links: Route.LinksFunction = () => [
  { rel: "icon", type: "image/png", href: "/brand/sumex-symbol.png" },
];

export function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
        <meta name="theme-color" content="#000000" />
        <Meta />
        <Links />
      </head>
      <body>
        {children}
        <ScrollRestoration />
        <Scripts />
      </body>
    </html>
  );
}

export default function App() {
  return <Outlet />;
}

export function HydrateFallback() {
  return (
    <div className="grid min-h-screen place-items-center bg-bg">
      <span className="t-label-sm text-subtle">LOADING</span>
    </div>
  );
}

export function ErrorBoundary({ error }: Route.ErrorBoundaryProps) {
  let message = "문제가 발생했습니다";
  let details = "잠시 후 다시 시도해 주세요.";
  if (isRouteErrorResponse(error) && error.status === 404) {
    message = "페이지를 찾을 수 없습니다";
    details = "주소를 다시 확인해 주세요.";
  }
  return (
    <main className="wrap section">
      <h1 className="t-h1">{message}</h1>
      <p className="t-body mt-4 text-muted">{details}</p>
      <a href="/" className="t-label mt-8 inline-block text-primary">홈으로 →</a>
    </main>
  );
}
