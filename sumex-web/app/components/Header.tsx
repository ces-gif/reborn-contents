import { Menu, MessageCircle, X } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, NavLink, useLocation } from "react-router";
import { CONTACT, NAV } from "~/config/site";
import { SocialButtons } from "./Footer";
import { Button, cx, useToast } from "./ui";

export function Logo({ className }: { className?: string }) {
  return (
    <Link to="/" aria-label="SUMEX 홈" className={cx("inline-flex shrink-0 items-center", className)}>
      <img src="/brand/sumex-logo-white.png" alt="SUMEX" width={100} height={28} className="h-7 w-auto" />
    </Link>
  );
}

export function Header() {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);
  const { pathname } = useLocation();
  const toast = useToast();

  useEffect(() => {
    const on = () => setScrolled(window.scrollY > 8);
    on();
    window.addEventListener("scroll", on, { passive: true });
    return () => window.removeEventListener("scroll", on);
  }, []);
  useEffect(() => setOpen(false), [pathname]);
  useEffect(() => {
    document.body.style.overflow = open ? "hidden" : "";
  }, [open]);

  const kakao = () => (CONTACT.kakaoOpenChatUrl ? window.open(CONTACT.kakaoOpenChatUrl, "_blank", "noopener") : toast("오픈채팅방을 준비중입니다. 곧 찾아뵙겠습니다."));

  return (
    <header
      className={cx(
        "sticky z-50 border-b transition-colors duration-300",
        scrolled || open ? "border-line bg-bg/80 backdrop-blur-[16px]" : "border-transparent bg-bg",
      )}
      style={{ top: "env(safe-area-inset-top, 0px)" }}
    >
      <div className="wrap flex h-[72px] items-center justify-between gap-6">
        <Logo />
        <nav aria-label="주 메뉴" className="hidden items-center gap-6 xl:flex">
          {NAV.slice(0, -1).map((n) => (
            <NavLink
              key={n.to}
              to={n.to}
              className={({ isActive }) =>
                cx("relative flex h-[72px] items-center gap-1.5 t-label-sm tracking-[0.12em] transition-colors", isActive ? "text-primary" : "text-muted hover:text-fg")
              }
            >
              {({ isActive }) => (
                <>
                  {"dot" in n && n.dot && <span className="size-1.5 rounded-full bg-primary" aria-hidden />}
                  {n.label}
                  {isActive && <span className="absolute inset-x-0 bottom-0 h-0.5 bg-primary" aria-hidden />}
                </>
              )}
            </NavLink>
          ))}
        </nav>
        <div className="flex items-center gap-2">
          <button type="button" onClick={kakao} aria-label="카카오톡 오픈채팅" className="grid size-10 place-items-center rounded-xs border border-line text-muted hover:border-line-strong hover:text-fg">
            <MessageCircle size={18} strokeWidth={1.5} />
          </button>
          <Button to="/contact" arrow className="hidden !h-10 sm:inline-flex">문의하기</Button>
          <button
            type="button"
            onClick={() => setOpen((v) => !v)}
            aria-label={open ? "메뉴 닫기" : "메뉴 열기"}
            aria-expanded={open}
            className="grid size-10 place-items-center rounded-xs border border-line text-fg xl:hidden"
          >
            {open ? <X size={18} strokeWidth={1.5} /> : <Menu size={18} strokeWidth={1.5} />}
          </button>
        </div>
      </div>

      {open && (
        <div className="absolute inset-x-0 top-full z-40 h-[calc(100dvh-72px)] overflow-y-auto border-t border-line bg-bg xl:hidden">
          <nav aria-label="모바일 메뉴" className="wrap flex flex-col gap-1 py-8">
            {NAV.map((n, i) => (
              <NavLink key={n.to} to={n.to} className={({ isActive }) => cx("flex items-baseline gap-4 border-b border-line py-4", isActive ? "text-primary" : "text-fg")}>
                <span className="t-label-sm w-6 text-subtle tnum">{String(i + 1).padStart(2, "0")}</span>
                <span className="t-h2">{n.label}</span>
              </NavLink>
            ))}
            <div className="mt-8 flex flex-col gap-6">
              <Button to="/contact" arrow>문의하기</Button>
              <SocialButtons />
            </div>
          </nav>
        </div>
      )}
    </header>
  );
}
