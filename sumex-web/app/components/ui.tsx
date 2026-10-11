import { ArrowRight, MessageCircle } from "lucide-react";
import { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";
import { Link } from "react-router";
import { CONTACT } from "~/config/site";
import type { CategoryId, Specialty } from "~/data/products";
import { SPECIALTY_LABEL } from "~/data/products";

const cx = (...c: (string | false | null | undefined)[]) => c.filter(Boolean).join(" ");
export { cx };

/* ── Button ───────────────────────────────────────────── */
type Variant = "primary" | "secondary" | "ghost" | "kakao";
const base =
  "group inline-flex items-center justify-center gap-2 whitespace-nowrap t-label transition-colors duration-200 ease-[var(--ease-sumex)]";
const variants: Record<Variant, string> = {
  primary: "h-[52px] px-5 rounded-xs bg-primary text-on-primary hover:bg-primary-hover active:bg-primary-pressed",
  secondary: "h-[52px] px-5 rounded-xs border border-fg/80 text-fg hover:bg-overlay",
  ghost: "h-auto px-0 py-2 text-muted hover:text-fg",
  kakao: "h-[52px] px-5 rounded-xs bg-raised text-fg border border-line hover:border-line-strong",
};

type ButtonProps = {
  variant?: Variant;
  to?: string;
  href?: string;
  onClick?: () => void;
  arrow?: boolean;
  className?: string;
  children: React.ReactNode;
  type?: "button" | "submit";
};

export function Button({ variant = "primary", to, href, onClick, arrow, className, children, type = "button" }: ButtonProps) {
  const cls = cx(base, variants[variant], className);
  const inner = (
    <>
      {variant === "kakao" && (
        <span className="grid size-6 place-items-center rounded-full bg-kakao text-black" aria-hidden>
          <MessageCircle size={14} strokeWidth={2} />
        </span>
      )}
      <span>{children}</span>
      {arrow && <ArrowRight size={16} strokeWidth={1.5} className="transition-transform duration-200 group-hover:translate-x-1" aria-hidden />}
    </>
  );
  if (to) return <Link to={to} className={cls}>{inner}</Link>;
  if (href) return <a href={href} target="_blank" rel="noopener noreferrer" className={cls}>{inner}</a>;
  return <button type={type} onClick={onClick} className={cls}>{inner}</button>;
}

/** 카카오 오픈채팅: URL이 없으면 준비중 토스트 */
export function KakaoButton({ className, label = "카카오톡 오픈채팅 참여하기" }: { className?: string; label?: string }) {
  const toast = useToast();
  if (CONTACT.kakaoOpenChatUrl) return <Button variant="kakao" href={CONTACT.kakaoOpenChatUrl} className={className}>{label}</Button>;
  return <Button variant="kakao" onClick={() => toast("오픈채팅방을 준비중입니다. 곧 찾아뵙겠습니다.")} className={className}>{label}</Button>;
}

/* ── Chips ────────────────────────────────────────────── */
export function SpecialtyChip({ s, selected, onClick }: { s: Specialty | "ALL"; selected?: boolean; onClick?: () => void }) {
  const label = s === "ALL" ? "전체" : `${s} ${SPECIALTY_LABEL[s]}`;
  const cls = cx(
    "inline-flex h-8 items-center rounded-full border px-3 t-label-sm transition-colors",
    selected ? "border-fg bg-fg text-bg" : "border-fg/40 text-fg hover:border-fg",
  );
  if (onClick) return <button type="button" aria-pressed={selected} onClick={onClick} className={cls}>{label}</button>;
  return <span className={cls}>{label}</span>;
}

const catChip: Record<CategoryId | "1788", string> = {
  arthro: "bg-arthro/15 text-arthro",
  laparo: "bg-laparo/15 text-laparo",
  instrument: "bg-instrument/15 text-instrument",
  "1788": "bg-primary/15 text-primary",
};
export function CategoryChip({ c }: { c: CategoryId | "1788" }) {
  return <span className={cx("inline-flex h-7 items-center rounded-full px-3 t-label-sm", catChip[c])}>{c === "1788" ? "1788" : c.toUpperCase()}</span>;
}

/* ── Section label / head ─────────────────────────────── */
export function TechLabel({ children, className }: { children: React.ReactNode; className?: string }) {
  return <p className={cx("t-label-sm text-subtle", className)}>{children}</p>;
}

export function SectionHead({ label, bold, thin, children, as: As = "h2" }: { label?: string; bold: string; thin?: string; children?: React.ReactNode; as?: "h1" | "h2" }) {
  return (
    <div className="flex flex-col gap-5">
      {label && <TechLabel>{label}</TechLabel>}
      <As className="flex flex-wrap items-baseline gap-x-4 gap-y-1">
        <span className="t-h1">{bold}</span>
        {thin && <span className="t-h1-thin text-muted">{thin}</span>}
      </As>
      {children}
    </div>
  );
}

export function Crosshair({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 16 16" className={cx("size-4 text-fg/30", className)} aria-hidden>
      <path d="M8 0v16M0 8h16" stroke="currentColor" strokeWidth="1" />
    </svg>
  );
}

/* ── JSON-LD ─────────────────────────────────────────── */
export function JsonLd({ data }: { data: object | object[] }) {
  return <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(data) }} />;
}

/* ── Triangle spinner (로고 삼각형 모티프) ─────────────── */
export function TriSpinner({ label = "불러오는 중" }: { label?: string }) {
  const colors = ["#FFD400", "#00AF85", "#8894FF", "#FFD400"];
  return (
    <div role="status" className="flex flex-col items-center gap-3">
      <svg viewBox="0 0 48 48" className="size-12" aria-hidden>
        {[0, 1, 2, 3].map((i) => (
          <path key={i} d="M24 6 L38 30 H10 Z" fill="none" stroke={colors[i]} strokeWidth="2" strokeLinejoin="round"
            transform={`rotate(${i * 90} 24 24) scale(0.6) translate(16 16)`} style={{ animation: `tri 1.2s ${i * 0.3}s infinite` }} />
        ))}
      </svg>
      <span className="t-label-sm text-subtle">{label}</span>
    </div>
  );
}

/* ── SpecCounter: 평소엔 최종 값을 보여주고, 스크롤로 화면에 들어올 때만 0부터 카운트업 ── */
export function SpecCounter({ value, unit, label }: { value: string; unit?: string; label: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const [display, setDisplay] = useState(value);
  useEffect(() => {
    const el = ref.current;
    const m = value.match(/^([\d,]+)/);
    if (!el || !m || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    if (el.getBoundingClientRect().top < window.innerHeight) return; // 이미 보이는 곳이면 그대로
    const target = Number(m[1].replace(/,/g, ""));
    const rest = value.slice(m[1].length);
    const fmt = (n: number) => Math.round(n).toLocaleString("en-US") + rest;
    const io = new IntersectionObserver(([e]) => {
      if (!e.isIntersecting) return;
      io.disconnect();
      setDisplay(fmt(0));
      const t0 = performance.now();
      const tick = (t: number) => {
        const p = Math.min(1, (t - t0) / 1200);
        setDisplay(fmt(target * (1 - Math.pow(1 - p, 3))));
        if (p < 1) requestAnimationFrame(tick);
        else setDisplay(value);
      };
      requestAnimationFrame(tick);
    });
    io.observe(el);
    return () => io.disconnect();
  }, [value]);
  return (
    <div ref={ref} className="flex min-w-0 flex-col gap-3 border-t border-line pt-5">
      <p className="flex flex-wrap items-baseline gap-x-2 gap-y-1">
        <span className={cx("t-spec text-fg", value.length > 6 && "!text-[32px] md:!text-[40px] xl:!text-[52px]")}>{display}</span>
        {unit && <span className="t-unit text-primary">{unit}</span>}
      </p>
      <p className="t-label-sm text-muted">{label}</p>
    </div>
  );
}

/* ── Toast ───────────────────────────────────────────── */
const ToastCtx = createContext<(msg: string) => void>(() => {});
export const useToast = () => useContext(ToastCtx);

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [msg, setMsg] = useState<string | null>(null);
  const timer = useRef<number>(0);
  const show = useCallback((m: string) => {
    setMsg(m);
    window.clearTimeout(timer.current);
    timer.current = window.setTimeout(() => setMsg(null), 2500);
  }, []);
  return (
    <ToastCtx.Provider value={show}>
      {children}
      <div role="status" aria-live="polite" className="pointer-events-none fixed inset-x-0 bottom-0 z-[100]" style={{ paddingBottom: "env(safe-area-inset-bottom, 0px)" }}>
        {msg && (
          <div
            className="t-body-sm absolute bottom-6 left-1/2 flex max-w-[calc(100vw-40px)] items-center gap-3 rounded-sm border-l-[3px] border-primary bg-overlay px-4 py-4 text-fg"
            style={{ animation: "toast-in 300ms var(--ease-sumex) both" }}
          >
            {msg}
          </div>
        )}
      </div>
    </ToastCtx.Provider>
  );
}
