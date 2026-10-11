import { ArrowUpRight, FileText } from "lucide-react";
import { Link } from "react-router";
import { type Product, productPath } from "~/data/products";
import { CategoryChip, SpecialtyChip, cx } from "./ui";

const hoverBorder = { arthro: "hover:bg-arthro", laparo: "hover:bg-laparo", instrument: "hover:bg-instrument" } as const;
const cornerFill = { arthro: "bg-arthro", laparo: "bg-laparo", instrument: "bg-instrument" } as const;

export function ProductCard({ p, reason }: { p: Product; reason?: string }) {
  const spec = p.specs?.[0];
  return (
    <Link
      to={productPath(p)}
      className={cx("group relative block cut-corner bg-line p-px transition-colors duration-300", hoverBorder[p.category])}
    >
      <article className="cut-corner relative flex h-full min-h-[240px] flex-col gap-4 bg-surface p-6 transition-colors duration-300 group-hover:bg-raised">
        <span aria-hidden className={cx("absolute right-0 top-0 size-[18px] opacity-0 transition-opacity group-hover:opacity-100", cornerFill[p.category])} style={{ clipPath: "polygon(0 0,100% 100%,100% 0)" }} />
        <div className="flex flex-wrap gap-2">
          <CategoryChip c={p.category} />
          {p.specialty.map((s) => <SpecialtyChip key={s} s={s} />)}
        </div>
        <div className="flex flex-col gap-2">
          <h3 className="t-title-lg">{p.name}</h3>
          <p className="t-body-sm line-clamp-2 font-light text-muted">{reason ?? p.summary}</p>
        </div>
        <div className="mt-auto flex items-end justify-between gap-4 border-t border-line pt-4">
          {spec ? (
            <p className="flex flex-col gap-1">
              <span className="text-[28px] font-extralight leading-none tracking-tight tnum">{spec.value}</span>
              <span className="t-label-sm text-subtle">{spec.label}</span>
            </p>
          ) : (
            <span className="t-label-sm text-subtle">{p.group}</span>
          )}
          <span className="flex items-center gap-3 text-muted">
            {p.libraryDocIds.length > 0 && <FileText size={18} strokeWidth={1.5} aria-label="제품 자료 있음" />}
            <ArrowUpRight size={18} strokeWidth={1.5} className="transition-transform group-hover:-translate-y-0.5 group-hover:translate-x-0.5" aria-hidden />
          </span>
        </div>
      </article>
    </Link>
  );
}
