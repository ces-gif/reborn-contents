import { ArrowRight } from "lucide-react";
import { Link } from "react-router";
import { BodyMap } from "~/components/Visuals";
import { Button, CategoryChip, JsonLd, SpecialtyChip, TechLabel, cx } from "~/components/ui";
import { BODY_PARTS, getBodyPart } from "~/data/bodyParts";
import { getProductById, productPath, type Product } from "~/data/products";
import { breadcrumb, seo } from "~/lib/seo";
import type { Route } from "./+types/explore";

export const meta = ({ params }: Route.MetaArgs) => {
  const b = getBodyPart(params.part);
  if (!b) {
    return seo({
      title: "인체로 찾기 – 수술 부위별 Stryker 장비",
      description: "어깨, 무릎, 척추, 뇌, 복부, 손, 발 등 수술 부위를 선택하면 관련 Stryker 관절경·복강경·파워툴 제품을 안내합니다.",
      path: "/explore",
    });
  }
  return seo({
    title: `${b.label} 수술 장비 – ${b.keywords[0]}`,
    description: `${b.label}(${b.keywords.join(", ")}) 수술에 쓰는 Stryker 장비를 안내합니다. 관련 제품 ${b.productIds.length}종과 제품 자료를 확인하세요.`.slice(0, 120),
    path: `/explore/${b.id}`,
  });
};

export default function Explore({ params }: Route.ComponentProps) {
  const part = getBodyPart(params.part);
  const products = (part?.productIds ?? []).map(getProductById).filter((p): p is Product => !!p);
  const order = BODY_PARTS.findIndex((b) => b.id === part?.id) + 1;

  return (
    <section className="border-b border-line">
      <div className="wrap grid gap-8 py-10 lg:grid-cols-12 lg:py-14">
        {/* 부위 목록: 3D/2D와 별개로 항상 제공 (키보드 접근) */}
        <nav aria-label="수술 부위" className="min-w-0 lg:col-span-2">
          <TechLabel className="mb-4">BODY PARTS</TechLabel>
          <ul className="no-scrollbar -mx-5 flex gap-2 overflow-x-auto px-5 lg:mx-0 lg:flex-col lg:gap-0 lg:px-0">
            {BODY_PARTS.map((b) => (
              <li key={b.id} className="shrink-0">
                <Link
                  to={`/explore/${b.id}`}
                  preventScrollReset
                  aria-label={`${b.label} 관련 제품 보기`}
                  aria-current={part?.id === b.id ? "page" : undefined}
                  className={cx(
                    "flex h-10 items-center gap-2 rounded-full border px-4 transition-colors lg:h-auto lg:rounded-none lg:border-0 lg:border-b lg:border-line lg:px-0 lg:py-4",
                    part?.id === b.id ? "border-fg text-fg lg:text-primary" : "border-line text-muted hover:text-fg",
                  )}
                >
                  <span className="t-label-sm">{b.labelEn}</span>
                  <span className="t-body-sm">{b.label}</span>
                </Link>
              </li>
            ))}
          </ul>
        </nav>

        <div className="relative h-[460px] min-w-0 overflow-hidden rounded-sm border border-line bg-surface md:h-[620px] lg:col-span-5">
          <div className="absolute inset-0 bg-grid" aria-hidden />
          <div aria-hidden className="pointer-events-none absolute inset-x-0 top-0 h-10 bg-gradient-to-b from-transparent via-tertiary/15 to-transparent" style={{ animation: "scan 6s linear infinite" }} />
          <TechLabel className="absolute left-5 top-5">HOLOGRAM VIEW · 2D</TechLabel>
          <div className="relative h-full p-6 pt-12"><BodyMap activeId={part?.id} /></div>
        </div>

        <div className="flex min-w-0 flex-col gap-6 rounded-sm border border-line bg-raised p-6 md:p-8 lg:col-span-5">
          {part ? (
            <>
              <TechLabel className="tnum">{String(order).padStart(2, "0")} / {part.labelEn}</TechLabel>
              <h1 className="flex flex-wrap items-baseline gap-x-3">
                <span className="t-h2">{part.label}</span>
                <span className="t-h2-thin text-muted">수술 장비</span>
              </h1>
              <div className="flex flex-wrap gap-2">{part.specialty.map((s) => <SpecialtyChip key={s} s={s} />)}</div>
              <ul aria-label="관련 수술" className="flex flex-wrap gap-2">
                {part.keywords.map((k) => <li key={k} className="t-body-sm rounded-xs bg-overlay px-3 py-1.5 text-muted">{k}</li>)}
              </ul>
              <h2 className="t-label-sm mt-2 text-subtle">관련 제품 {products.length}</h2>
              <ul className="-mx-2 flex flex-col">
                {part.link1788 && (
                  <li>
                    <Link to="/products/1788" className="group flex items-center justify-between gap-4 rounded-xs px-2 py-3 hover:bg-overlay">
                      <span className="flex flex-col gap-1">
                        <span className="t-body font-semibold">1788 4K OLED Platform</span>
                        <span className="t-body-sm text-muted">4K 수술 영상 시스템</span>
                      </span>
                      <CategoryChip c="1788" />
                    </Link>
                  </li>
                )}
                {products.map((p) => (
                  <li key={p.id}>
                    <Link to={productPath(p)} className="group flex items-center justify-between gap-4 rounded-xs px-2 py-3 hover:bg-overlay">
                      <span className="flex min-w-0 flex-col gap-1">
                        <span className="t-body font-semibold">{p.name}</span>
                        <span className="t-body-sm truncate text-muted">{p.summary}</span>
                      </span>
                      <CategoryChip c={p.category} />
                    </Link>
                  </li>
                ))}
              </ul>
              <p className="t-body-sm border-t border-line pt-4 text-subtle">수술실 공통 · <Link to="/products/instrument/flyte-steri-shield" className="hover:text-fg">Flyte Steri-Shield</Link></p>
              <div className="mt-auto flex flex-wrap gap-3">
                <Button to={`/ai-search?q=${encodeURIComponent(part.keywords[0])}`} variant="secondary">이 부위 관련 AI에게 묻기</Button>
                <Button to={`/contact?part=${part.id}`} arrow>문의하기</Button>
              </div>
            </>
          ) : (
            <>
              <TechLabel>BODY EXPLORER</TechLabel>
              <h1 className="flex flex-col gap-2">
                <span className="t-h2">어디를 수술하시나요?</span>
                <span className="t-h2-thin text-muted">부위를 누르면 맞는 제품을 보여드려요</span>
              </h1>
              <ul className="flex flex-col">
                {BODY_PARTS.map((b) => (
                  <li key={b.id}>
                    <Link to={`/explore/${b.id}`} preventScrollReset className="group flex items-center justify-between border-b border-line py-4">
                      <span className="flex items-baseline gap-3">
                        <span className="t-title-md">{b.label}</span>
                        <span className="t-body-sm text-muted">{b.keywords.join(" · ")}</span>
                      </span>
                      <ArrowRight size={18} strokeWidth={1.5} className="shrink-0 text-muted group-hover:text-fg" aria-hidden />
                    </Link>
                  </li>
                ))}
              </ul>
              <p className="t-body-sm text-subtle">3D 인체 모델은 GLB 모델 준비 후 적용됩니다. 지금은 2D 홀로그램 화면으로 제공합니다.</p>
            </>
          )}
        </div>
      </div>
      <JsonLd data={breadcrumb(part ? [{ name: "인체로 찾기", path: "/explore" }, { name: part.label, path: `/explore/${part.id}` }] : [{ name: "인체로 찾기", path: "/explore" }])} />
    </section>
  );
}
