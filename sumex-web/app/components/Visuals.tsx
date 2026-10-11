import { useState } from "react";
import { Link } from "react-router";
import { BODY_PARTS, type BodyPart } from "~/data/bodyParts";
import { P1788 } from "~/data/products";
import { cx } from "./ui";

/* ── 1788 플랫폼 구성도 (실사 이미지 준비 전 사용하는 공학 도면 스타일 SVG) ── */
type Callout = { key: string; label: string; at: [number, number] };
const HOME_CALLOUTS: Callout[] = [
  { key: "A", label: "4K OLED Display", at: [292, 92] },
  { key: "B", label: "1788 AIM 4K Camera", at: [96, 300] },
  { key: "C", label: "L12 LED Light Source", at: [262, 318] },
];

export function Tower1788({ callouts = HOME_CALLOUTS, className }: { callouts?: Callout[]; className?: string }) {
  const unit = (y: number, h: number, i: number) => (
    <g key={i}>
      <rect x="132" y={y} width="136" height={h} rx="3" fill="#111214" stroke="#2E3136" />
      <rect x="142" y={y + 8} width="34" height={h - 16} rx="1.5" fill="#000" stroke="#2E3136" />
      <circle cx="248" cy={y + h / 2} r="5" fill="none" stroke="#6B7079" />
      <circle cx="230" cy={y + h / 2} r="2.5" fill={i === 1 ? "#00AF85" : "#FFD400"} />
      <path d={`M186 ${y + h / 2}h28`} stroke="#2E3136" />
    </g>
  );
  return (
    <svg viewBox="-50 0 500 540" className={cx("h-auto w-full", className)} role="img" aria-label="Stryker 1788 4K OLED 플랫폼 구성도: 4K OLED 디스플레이, 1788 AIM 4K 카메라, L12 LED 광원">
      <defs>
        <radialGradient id="glow" cx="50%" cy="38%" r="55%">
          <stop offset="0" stopColor="#FFD400" stopOpacity="0.16" />
          <stop offset="0.5" stopColor="#00AF85" stopOpacity="0.08" />
          <stop offset="1" stopColor="#000" stopOpacity="0" />
        </radialGradient>
        <linearGradient id="screen" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#3a0f12" />
          <stop offset="0.55" stopColor="#7a2a2a" />
          <stop offset="1" stopColor="#1a0506" />
        </linearGradient>
      </defs>
      <rect x="-50" width="500" height="540" fill="url(#glow)" />
      {/* monitor */}
      <rect x="88" y="34" width="224" height="140" rx="4" fill="#0A0A0B" stroke="#F5F5F5" strokeOpacity="0.55" />
      <rect x="98" y="44" width="204" height="114" rx="2" fill="url(#screen)" />
      <circle cx="200" cy="101" r="48" fill="none" stroke="#000" strokeOpacity="0.6" strokeWidth="20" />
      <path d="M168 92c14-10 30 6 46-4s22 10 30 4" fill="none" stroke="#00AF85" strokeWidth="2.5" strokeLinecap="round" />
      <path d="M176 116c10 6 24-4 38 4" fill="none" stroke="#00AF85" strokeWidth="2" strokeLinecap="round" opacity="0.8" />
      <text x="106" y="168" fill="#6B7079" fontSize="7" letterSpacing="1.5">4K · OLED</text>
      {/* arm & pole */}
      <path d="M200 174v24M200 198h0" stroke="#F5F5F5" strokeOpacity="0.4" strokeWidth="6" strokeLinecap="round" />
      <rect x="194" y="196" width="12" height="276" fill="#17181B" stroke="#2E3136" />
      {/* cart */}
      <rect x="120" y="206" width="160" height="268" rx="4" fill="none" stroke="#F5F5F5" strokeOpacity="0.35" />
      {[0, 1, 2, 3].map((i) => unit(220 + i * 56, 44, i))}
      {/* camera head + cable */}
      <path d="M120 260c-30 10-36 60-20 84" fill="none" stroke="#8894FF" strokeOpacity="0.7" strokeWidth="2" />
      <rect x="84" y="336" width="34" height="18" rx="9" fill="#111214" stroke="#F5F5F5" strokeOpacity="0.55" />
      <rect x="70" y="341" width="16" height="8" rx="2" fill="#17181B" stroke="#6B7079" />
      {/* base */}
      <rect x="108" y="474" width="184" height="12" rx="2" fill="#111214" stroke="#2E3136" />
      {[124, 276].map((x) => (
        <g key={x}>
          <circle cx={x} cy="500" r="11" fill="#0A0A0B" stroke="#6B7079" />
          <circle cx={x} cy="500" r="3" fill="#6B7079" />
        </g>
      ))}
      {/* callouts */}
      {callouts.map((c, i) => {
        const right = c.at[0] > 200;
        const ex = right ? 446 : -46;
        const ey = c.at[1] - 18;
        const len = Math.abs(ex - c.at[0]) + 30;
        return (
          <g key={c.key}>
            <circle cx={c.at[0]} cy={c.at[1]} r="3.5" fill="#FFD400" />
            <path
              d={`M${c.at[0]} ${c.at[1]} L${c.at[0] + (right ? 18 : -18)} ${ey} H${ex}`}
              fill="none"
              stroke="#FFD400"
              strokeOpacity="0.8"
              className="anim-draw"
              style={{ ["--len" as string]: len, animationDelay: `${600 + i * 180}ms` }}
            />
            <text x={ex} y={ey - 7} textAnchor={right ? "end" : "start"} fill="#F5F5F5" fontSize="11" fontWeight="600" letterSpacing="0.6">
              <tspan fill="#FFD400" fontWeight="700">{c.key}</tspan> {c.label}
            </text>
          </g>
        );
      })}
    </svg>
  );
}

/* ── 1788 모드 전환 시뮬레이터 ── */
type Mode = (typeof P1788.modes)[number]["id"];
const VESSELS = [
  "M150 210c40-30 70 10 110-20s60 20 100 0 50-40 90-20",
  "M190 140c30 30 20 60 60 80s30 60 70 70",
  "M330 110c-10 40 20 70 0 110s-10 60 20 80",
  "M230 260c30-10 60 10 90-10s50 0 80-20",
  "M260 170c20 10 40 0 60 14",
];

export function ModeSwitcher({ large = false }: { large?: boolean }) {
  const [mode, setMode] = useState<Mode>("overlay");
  const [scanKey, setScanKey] = useState(0);
  const tissue = mode === "env" ? "url(#tGray)" : mode === "contrast" ? "#050505" : "url(#tColor)";
  const vessel = mode === "white" ? "#5a1214" : mode === "contrast" ? "#FFFFFF" : "#00E0A8";
  const glow = mode === "overlay" || mode === "env";
  const active = P1788.modes.find((m) => m.id === mode)!;
  return (
    <div className="flex flex-col gap-6">
      <div className="relative overflow-hidden rounded-sm border border-line bg-black">
        <svg viewBox="0 0 640 360" className="block h-auto w-full" role="img" aria-label={`1788 ${active.name} 모드 시뮬레이션 그래픽`}>
          <defs>
            <radialGradient id="tColor" cx="45%" cy="45%" r="60%">
              <stop offset="0" stopColor="#e8a08a" />
              <stop offset="0.45" stopColor="#b8524a" />
              <stop offset="1" stopColor="#3a0c0e" />
            </radialGradient>
            <radialGradient id="tGray" cx="45%" cy="45%" r="60%">
              <stop offset="0" stopColor="#bdbdbd" />
              <stop offset="0.5" stopColor="#6e6e6e" />
              <stop offset="1" stopColor="#151515" />
            </radialGradient>
            <filter id="vglow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="5" result="b" />
              <feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge>
            </filter>
            <clipPath id="scope"><circle cx="320" cy="180" r="168" /></clipPath>
          </defs>
          <g clipPath="url(#scope)">
            <rect width="640" height="360" fill={tissue} style={{ transition: "fill 300ms" }} />
            {mode !== "contrast" && (
              <g opacity="0.35">
                <ellipse cx="250" cy="150" rx="70" ry="40" fill={mode === "env" ? "#9a9a9a" : "#f0b6a0"} />
                <ellipse cx="390" cy="240" rx="80" ry="36" fill={mode === "env" ? "#4a4a4a" : "#7e2a28"} />
              </g>
            )}
            <g filter={glow ? "url(#vglow)" : undefined} fill="none" strokeLinecap="round">
              {VESSELS.map((d, i) => (
                <path key={i} d={d} stroke={vessel} strokeWidth={i < 2 ? 7 : 4} style={{ transition: "stroke 300ms" }} />
              ))}
            </g>
            <rect key={scanKey} x="0" y="0" width="640" height="30" fill="url(#tColor)" opacity="0" />
          </g>
          <circle cx="320" cy="180" r="168" fill="none" stroke="#000" strokeWidth="6" />
          <path d="M320 168v24M308 180h24" stroke="#FFD400" strokeOpacity="0.7" />
          <text x="20" y="30" fill="#F5F5F5" fontSize="12" fontWeight="600" letterSpacing="1.5">MODE · {active.name.toUpperCase()}</text>
          <text x="620" y="340" textAnchor="end" fill="#6B7079" fontSize="10" letterSpacing="1">시뮬레이션 그래픽 · 실제 수술 영상 아님</text>
        </svg>
        <div key={scanKey} aria-hidden className="pointer-events-none absolute inset-x-0 top-0 h-[10%] bg-gradient-to-b from-transparent via-primary/25 to-transparent" style={{ animation: scanKey ? "scan 700ms var(--ease-sumex) both" : "none", opacity: 0 }} />
      </div>
      <div role="tablist" aria-label="1788 영상 모드" className="grid grid-cols-2 gap-2 md:grid-cols-4">
        {P1788.modes.map((m) => (
          <button
            key={m.id}
            role="tab"
            aria-selected={mode === m.id}
            onClick={() => { setMode(m.id); setScanKey((k) => k + 1); }}
            className={cx(
              "flex flex-col items-start gap-2 rounded-xs border p-4 text-left transition-colors",
              mode === m.id ? "border-primary bg-primary/10" : "border-line hover:border-line-strong",
            )}
          >
            <span className={cx("t-label", mode === m.id ? "text-primary" : "text-fg")}>{m.name}</span>
            <span className={cx("t-body-sm text-muted", !large && "hidden md:block")}>{m.desc}</span>
          </button>
        ))}
      </div>
      <p className="t-body-sm text-muted md:hidden">{active.desc}</p>
    </div>
  );
}

/* ── 2D 홀로그램 인체 + 핫스팟 (3D 뷰어 준비 전/저사양 대체용) ── */
const colorOf: Record<BodyPart["color"], string> = { arthro: "#8894FF", laparo: "#00AF85", instrument: "#FFD400" };

export function BodyMap({ activeId, compact = false }: { activeId?: string; compact?: boolean }) {
  return (
    <svg viewBox="-60 0 320 450" className="h-full w-full" role="img" aria-label="인체 부위 선택 지도">
      <defs>
        <pattern id="scanlines" width="6" height="6" patternUnits="userSpaceOnUse">
          <path d="M0 0.5H6" stroke="#F5F5F5" strokeOpacity="0.28" strokeWidth="1" />
        </pattern>
        <mask id="body">
          <g fill="#fff" stroke="#fff" strokeLinecap="round" strokeLinejoin="round">
            <ellipse cx="100" cy="32" rx="17" ry="21" />
            <rect x="92" y="50" width="16" height="16" />
            <path d="M68 66Q100 56 132 66L138 120Q133 170 128 200H72Q67 170 62 120Z" />
            <path d="M72 196H128L134 230H66Z" />
            <path d="M70 72L52 150L38 226" fill="none" strokeWidth="16" />
            <path d="M130 72L148 150L162 226" fill="none" strokeWidth="16" />
            <circle cx="36" cy="238" r="9" />
            <circle cx="164" cy="238" r="9" />
            <path d="M86 226L84 320L82 410" fill="none" strokeWidth="22" />
            <path d="M114 226L116 320L118 410" fill="none" strokeWidth="22" />
            <ellipse cx="78" cy="424" rx="13" ry="7" />
            <ellipse cx="122" cy="424" rx="13" ry="7" />
          </g>
        </mask>
        <filter id="edge"><feGaussianBlur stdDeviation="2.5" /></filter>
      </defs>
      {/* 바닥 스캔 링 */}
      {[60, 90].map((r) => (
        <ellipse key={r} cx="100" cy="434" rx={r} ry={r / 6} fill="none" stroke="#FFD400" strokeOpacity={r === 60 ? 0.35 : 0.15} />
      ))}
      <rect x="-60" width="320" height="450" fill="#8894FF" opacity="0.18" mask="url(#body)" filter="url(#edge)" />
      <rect x="-60" width="320" height="450" fill="url(#scanlines)" mask="url(#body)" />
      <rect x="-60" width="320" height="450" fill="#F5F5F5" opacity="0.04" mask="url(#body)" />
      <path d="M100 60V228" stroke="#F5F5F5" strokeOpacity="0.15" strokeDasharray="2 4" />
      {BODY_PARTS.map((b) => {
        const [x, y] = b.spot;
        const on = activeId === b.id;
        const c = colorOf[b.color];
        const right = x >= 100;
        const lx = right ? 200 : 0;
        return (
          <Link key={b.id} to={`/explore/${b.id}`} preventScrollReset aria-label={`${b.label} 관련 제품 보기`} className="group">
            <circle cx={x} cy={y} r="5" fill={c} className="pulse-ring" opacity={on ? 0.9 : 0.6} />
            <circle cx={x} cy={y} r={on ? 7 : 5} fill={on ? "#F5F5F5" : c} stroke="#000" strokeWidth="1.5" />
            <circle cx={x} cy={y} r="16" fill="transparent" />
            {!compact && (
              <>
                <path d={`M${x} ${y}L${lx} ${y}`} stroke={c} strokeOpacity={on ? 0.9 : 0.35} />
                <text x={right ? lx + 4 : lx - 4} y={y + 4} textAnchor={right ? "start" : "end"} fontSize="10" fontWeight="600" letterSpacing="1.2" fill={on ? "#F5F5F5" : "#A1A6AE"} className="group-hover:fill-[#F5F5F5]">
                  {b.labelEn} <tspan fontWeight="400">{b.label}</tspan>
                </text>
              </>
            )}
          </Link>
        );
      })}
    </svg>
  );
}
