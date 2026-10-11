import { LayoutGrid, List, Search } from "lucide-react";
import { useMemo, useState } from "react";
import { DocList } from "~/components/DocList";
import { JsonLd, TechLabel, cx } from "~/components/ui";
import { DOC_TYPE_LABEL, LIBRARY, type DocType } from "~/data/library";
import type { Specialty } from "~/data/products";
import { breadcrumb, seo } from "~/lib/seo";

export const meta = () =>
  seo({
    title: "제품 자료실 – Stryker 브로슈어 · 카탈로그",
    description: "1788, ARTHRO, LAPARO, INSTRUMENT 카테고리별 Stryker 제품 브로슈어와 카탈로그, 용도설명서를 한곳에서 확인하세요.",
    path: "/products/library",
  });

const CATS = ["1788", "ARTHRO", "LAPARO", "INSTRUMENT"] as const;

export default function Library() {
  const [q, setQ] = useState("");
  const [cat, setCat] = useState<string>("");
  const [spec, setSpec] = useState<Specialty | "">("");
  const [type, setType] = useState<DocType | "">("");
  const [view, setView] = useState<"list" | "card">("list");

  const docs = useMemo(
    () =>
      LIBRARY.filter(
        (d) =>
          (!q || d.title.toLowerCase().includes(q.toLowerCase())) &&
          (!cat || d.category === cat) &&
          (!spec || d.specialty.includes(spec)) &&
          (!type || d.docType === type),
      ),
    [q, cat, spec, type],
  );
  const select = "t-body-sm h-11 rounded-xs border border-line bg-surface px-3 text-fg outline-none focus:border-fg";

  return (
    <>
      <section className="border-b border-line bg-grid">
        <div className="wrap flex flex-col gap-5 py-16 lg:py-20">
          <TechLabel>PRODUCT LIBRARY</TechLabel>
          <h1 className="flex flex-wrap items-baseline gap-x-4"><span className="t-h1">제품 자료실</span><span className="t-h1-thin text-muted">브로슈어 · 카탈로그</span></h1>
          <p className="t-body text-muted">자료는 순차적으로 등록됩니다. 아직 등록되지 않은 자료는 담당자에게 요청해 주세요.</p>
        </div>
      </section>
      <section className="section !pt-12 border-b border-line">
        <div className="wrap flex flex-col gap-6">
          <div className="flex flex-col gap-3 lg:flex-row lg:items-center">
            <label className="flex h-11 flex-1 items-center gap-3 rounded-xs border border-line bg-surface px-4 focus-within:border-fg">
              <Search size={16} strokeWidth={1.5} className="text-muted" aria-hidden />
              <span className="sr-only">문서 검색</span>
              <input id="lib-q" value={q} onChange={(e) => setQ(e.target.value)} placeholder="문서명 검색" className="t-body-sm min-w-0 flex-1 bg-transparent outline-none placeholder:text-subtle" />
            </label>
            <div className="flex flex-wrap gap-2">
              <select id="lib-cat" aria-label="카테고리" value={cat} onChange={(e) => setCat(e.target.value)} className={select}>
                <option value="">전체 카테고리</option>
                {CATS.map((c) => <option key={c}>{c}</option>)}
              </select>
              <select id="lib-spec" aria-label="진료과" value={spec} onChange={(e) => setSpec(e.target.value as Specialty | "")} className={select}>
                <option value="">전체 진료과</option>
                <option value="OS">OS 정형외과</option><option value="NS">NS 신경외과</option><option value="GS">GS 일반외과</option>
              </select>
              <select id="lib-type" aria-label="문서 종류" value={type} onChange={(e) => setType(e.target.value as DocType | "")} className={select}>
                <option value="">전체 종류</option>
                {(Object.keys(DOC_TYPE_LABEL) as DocType[]).map((t) => <option key={t} value={t}>{DOC_TYPE_LABEL[t]}</option>)}
              </select>
              <div role="group" aria-label="보기 방식" className="flex overflow-hidden rounded-xs border border-line">
                {(["list", "card"] as const).map((v) => (
                  <button key={v} type="button" aria-pressed={view === v} aria-label={v === "list" ? "리스트형" : "카드형"} onClick={() => setView(v)} className={cx("grid size-11 place-items-center", view === v ? "bg-fg text-bg" : "text-muted hover:text-fg")}>
                    {v === "list" ? <List size={16} strokeWidth={1.5} /> : <LayoutGrid size={16} strokeWidth={1.5} />}
                  </button>
                ))}
              </div>
            </div>
          </div>
          <p className="t-label-sm text-subtle tnum">{docs.length} DOCUMENTS</p>
          <DocList docs={docs} view={view} />
        </div>
      </section>
      <JsonLd data={breadcrumb([{ name: "제품 자료실", path: "/products/library" }])} />
    </>
  );
}
