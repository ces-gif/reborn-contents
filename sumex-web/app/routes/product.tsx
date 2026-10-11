import { Link } from "react-router";
import { DocList } from "~/components/DocList";
import { ProductCard } from "~/components/ProductCard";
import { Button, CategoryChip, JsonLd, KakaoButton, SpecialtyChip, TechLabel } from "~/components/ui";
import { BODY_PARTS } from "~/data/bodyParts";
import { getDoc } from "~/data/library";
import { CATEGORIES, PRODUCTS, getProduct, productPath } from "~/data/products";
import { abs, breadcrumb, seo } from "~/lib/seo";
import type { Route } from "./+types/product";

export const meta = ({ params }: Route.MetaArgs) => {
  const p = getProduct(params.category, params.slug);
  if (!p) return [{ title: "페이지를 찾을 수 없습니다 | 수멕스(SUMEX)" }];
  const c = CATEGORIES[p.category];
  return seo({ title: `${p.name} – ${c.name} ${c.ko}`, description: p.summary.slice(0, 118), path: productPath(p) });
};

const lineColor = { arthro: "bg-arthro", laparo: "bg-laparo", instrument: "bg-instrument" } as const;

export default function ProductPage({ params }: Route.ComponentProps) {
  const p = getProduct(params.category, params.slug);
  if (!p) throw new Response("Not Found", { status: 404 });
  const c = CATEGORIES[p.category];
  const parts = BODY_PARTS.filter((b) => b.productIds.includes(p.id));
  const docs = p.libraryDocIds.map(getDoc).filter((d) => !!d);
  const related = PRODUCTS.filter((x) => x.category === p.category && x.group === p.group && x.id !== p.id).slice(0, 3);

  return (
    <>
      <section className="relative border-b border-line bg-grid">
        <span aria-hidden className={`absolute inset-x-0 top-0 h-[3px] ${lineColor[p.category]}`} />
        <div className="wrap flex flex-col gap-8 py-16 lg:py-20">
          <nav aria-label="위치" className="t-label-sm flex flex-wrap gap-2 text-subtle">
            <Link to="/" className="hover:text-fg">HOME</Link>/<Link to={`/products/${c.id}`} className="hover:text-fg">{c.name}</Link>/<span className="text-muted">{p.group}</span>
          </nav>
          <div className="flex flex-wrap gap-2">
            <CategoryChip c={p.category} />
            {p.specialty.map((s) => <SpecialtyChip key={s} s={s} />)}
          </div>
          <h1 className="t-h1 max-w-4xl">{p.name}</h1>
          <p className="t-body-lg max-w-2xl text-muted">{p.summary}</p>
          <div className="flex flex-wrap gap-3">
            <Button to={`/contact?product=${p.slug}`} arrow>이 제품 문의하기</Button>
            <KakaoButton />
          </div>
        </div>
      </section>

      <section className="section border-b border-line">
        <div className="wrap grid gap-16 lg:grid-cols-12">
          <div className="flex flex-col gap-6 lg:col-span-7">
            <TechLabel>01 / FEATURES</TechLabel>
            <h2 className="t-h2">특장점</h2>
            <ul className="flex flex-col">
              {p.features.map((f, i) => (
                <li key={f} className="flex items-baseline gap-5 border-b border-line py-5">
                  <span className="t-label-sm text-primary tnum">{String(i + 1).padStart(2, "0")}</span>
                  <span className="t-title-md font-medium">{f}</span>
                </li>
              ))}
            </ul>
          </div>
          <div className="flex flex-col gap-10 lg:col-span-5">
            {p.specs && (
              <div className="flex flex-col gap-6">
                <TechLabel>02 / SPECIFICATIONS</TechLabel>
                <table className="w-full text-left">
                  <tbody>
                    {p.specs.map((s) => (
                      <tr key={s.label} className="border-b border-line">
                        <th scope="row" className="t-body-sm py-4 pr-4 font-normal text-muted">{s.label}</th>
                        <td className="py-4 text-[22px] font-extralight tracking-tight tnum">{s.value}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
            {parts.length > 0 && (
              <div className="flex flex-col gap-4">
                <TechLabel>관련 수술 부위</TechLabel>
                <ul className="flex flex-wrap gap-2">
                  {parts.map((b) => (
                    <li key={b.id}>
                      <Link to={`/explore/${b.id}`} className="inline-flex h-9 items-center gap-2 rounded-full border border-line px-4 t-label-sm text-muted hover:border-fg hover:text-fg">
                        {b.labelEn} <span className="normal-case tracking-normal">{b.label}</span>
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            <div className="flex flex-col gap-3">
              <TechLabel>검색 키워드</TechLabel>
              <p className="t-body-sm text-muted">{p.keywords.join(" · ")}</p>
            </div>
          </div>
        </div>
      </section>

      <section className="section border-b border-line">
        <div className="wrap flex flex-col gap-8">
          <h2 className="t-h2">제품 자료</h2>
          <DocList docs={docs} />
        </div>
      </section>

      {related.length > 0 && (
        <section className="section border-b border-line">
          <div className="wrap flex flex-col gap-8">
            <h2 className="flex flex-wrap items-baseline gap-x-4"><span className="t-h2">함께 보는 제품</span><span className="t-h2-thin text-muted">{p.group}</span></h2>
            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">{related.map((r) => <ProductCard key={r.id} p={r} />)}</div>
          </div>
        </section>
      )}

      <JsonLd
        data={[
          breadcrumb([{ name: `${c.name} ${c.ko}`, path: `/products/${c.id}` }, { name: p.name, path: productPath(p) }]),
          {
            "@context": "https://schema.org",
            "@type": "Product",
            name: p.name,
            description: p.summary,
            brand: { "@type": "Brand", name: p.id === "laparoclick" ? "LaparoTools" : "Stryker" },
            manufacturer: { "@type": "Organization", name: p.id === "laparoclick" ? "LaparoTools" : "Stryker" },
            category: `${c.ko} · ${p.group}`,
            keywords: p.keywords.join(", "),
            url: abs(productPath(p)),
          },
        ]}
      />
    </>
  );
}
