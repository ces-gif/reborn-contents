import { useSearchParams } from "react-router";
import { DocList } from "~/components/DocList";
import { ProductCard } from "~/components/ProductCard";
import { JsonLd, SpecialtyChip, TechLabel } from "~/components/ui";
import { LIBRARY } from "~/data/library";
import { CATEGORIES, PRODUCTS, isCategory, type Specialty } from "~/data/products";
import { abs, breadcrumb, seo } from "~/lib/seo";
import type { Route } from "./+types/category";
import { ContactBand } from "./home";

export const meta = ({ params }: Route.MetaArgs) => {
  if (!isCategory(params.category)) return [{ title: "페이지를 찾을 수 없습니다 | 수멕스(SUMEX)" }];
  const c = CATEGORIES[params.category];
  return seo({ title: `${c.name} ${c.ko} – ${c.tagline}`, description: c.description.slice(0, 118), path: `/products/${c.id}` });
};

const FILTERS: (Specialty | "ALL")[] = ["ALL", "OS", "NS", "GS"];
const lineColor = { arthro: "bg-arthro", laparo: "bg-laparo", instrument: "bg-instrument" } as const;
const idx = { arthro: "01", laparo: "02", instrument: "03" } as const;

export default function Category({ params }: Route.ComponentProps) {
  const [sp, setSp] = useSearchParams();
  if (!isCategory(params.category)) throw new Response("Not Found", { status: 404 });
  const c = CATEGORIES[params.category];
  const filter = (sp.get("specialty") as Specialty | null) ?? "ALL";
  const items = PRODUCTS.filter((p) => p.category === c.id);
  const visible = filter === "ALL" ? items : items.filter((p) => p.specialty.includes(filter));
  const docs = LIBRARY.filter((d) => d.category === c.name);

  return (
    <>
      <section className="relative overflow-hidden border-b border-line bg-grid">
        <span aria-hidden className={`absolute inset-x-0 top-0 h-[3px] ${lineColor[c.id]}`} />
        <div className="wrap flex flex-col gap-8 py-16 lg:py-24">
          <TechLabel>{idx[c.id]} / {c.name} · {c.ko}</TechLabel>
          <h1 className="flex flex-col gap-2">
            <span className="t-display">{c.name}</span>
            <span className="t-h1-thin text-muted">{c.tagline}</span>
          </h1>
          <p className="t-body-lg max-w-2xl text-muted">{c.description}</p>
        </div>
      </section>

      <section className="section !pt-16 border-b border-line">
        <div className="wrap flex flex-col gap-12">
          <div role="group" aria-label="진료과 필터" className="flex flex-wrap gap-2">
            {FILTERS.map((f) => (
              <SpecialtyChip
                key={f}
                s={f}
                selected={filter === f}
                onClick={() => setSp(f === "ALL" ? {} : { specialty: f }, { replace: true, preventScrollReset: true })}
              />
            ))}
          </div>
          {c.groups.map((g) => {
            const list = visible.filter((p) => p.group === g);
            if (list.length === 0) return null;
            return (
              <div key={g} className="flex flex-col gap-6">
                <h2 className="t-title-lg flex items-baseline gap-3">
                  {g} <span className="t-label-sm text-subtle tnum">{String(list.length).padStart(2, "0")}</span>
                </h2>
                <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
                  {list.map((p) => <ProductCard key={p.id} p={p} />)}
                </div>
              </div>
            );
          })}
          {visible.length === 0 && <p className="t-body text-muted">선택한 진료과의 제품이 없습니다.</p>}
        </div>
      </section>

      <section className="section border-b border-line">
        <div className="wrap flex flex-col gap-8">
          <h2 className="flex flex-wrap items-baseline gap-x-4"><span className="t-h2">{c.name} 자료</span><span className="t-h2-thin text-muted">브로슈어 · 카탈로그</span></h2>
          <DocList docs={docs} />
        </div>
      </section>
      <ContactBand />
      <JsonLd
        data={[
          breadcrumb([{ name: `${c.name} ${c.ko}`, path: `/products/${c.id}` }]),
          {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            name: `${c.name} ${c.ko}`,
            description: c.description,
            hasPart: items.map((p) => ({ "@type": "Product", name: p.name, url: abs(`/products/${p.category}/${p.slug}`) })),
          },
        ]}
      />
    </>
  );
}
