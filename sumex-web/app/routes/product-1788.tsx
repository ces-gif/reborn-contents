import { Link } from "react-router";
import { DocList } from "~/components/DocList";
import { ModeSwitcher, Tower1788 } from "~/components/Visuals";
import { Button, JsonLd, SectionHead, SpecCounter, TechLabel } from "~/components/ui";
import { LIBRARY } from "~/data/library";
import { P1788, getProductById, productPath } from "~/data/products";
import { abs, breadcrumb, seo } from "~/lib/seo";
import { ContactBand } from "./home";

const DESC =
  "Stryker 1788 4K OLED Platform은 트루 블랙과 10억 개 이상의 컬러, 1,000,000:1 명암비로 수술 시야를 4K로 표현하는 수술 영상 시스템입니다. 형광 영상을 Overlay · ENV · Contrast 모드로 보여줍니다.";

export const meta = () =>
  seo({ title: "Stryker 1788 4K OLED Platform – 4K 형광 수술 영상 시스템", description: DESC.slice(0, 118), path: "/products/1788" });

const FULL_CALLOUTS = [
  { key: "A", label: "4K OLED surgical display", at: [292, 70] as [number, number] },
  { key: "D", label: "1788 AIM 4K CCU", at: [262, 242] as [number, number] },
  { key: "E", label: "1788 AIM 4K Camera head", at: [96, 345] as [number, number] },
  { key: "F", label: "L12 LED Light Source", at: [262, 298] as [number, number] },
  { key: "I", label: "PM304 Irrigation Pump", at: [262, 410] as [number, number] },
];

const FAQ = [
  { q: "1788 플랫폼의 형광 영상 모드는 무엇이 있나요?", a: "Overlay(형광 영상을 일반 영상 위에 겹쳐 4K로 동시 표현), ENV(형광을 회색과 초록색으로 구분해 4K로 표현), Contrast(형광을 흑과 백으로 구분해 4K로 표현) 세 가지 모드가 있습니다." },
  { q: "1788 플랫폼은 어떤 진료과에서 쓰이나요?", a: "일반외과, 비뇨의학과, 정형외과, 산부인과, 이비인후과·신경외과, 흉부외과 수술에 활용됩니다." },
  { q: "데모를 받아볼 수 있나요?", a: "수멕스로 문의하시면 담당자가 일정에 맞춰 데모를 안내해 드립니다." },
];

export default function Product1788() {
  const docs = LIBRARY.filter((d) => d.category === "1788");
  return (
    <>
      <section className="relative overflow-hidden border-b border-line bg-grid">
        <div className="wrap grid items-center gap-12 py-16 lg:grid-cols-12 lg:py-24">
          <div className="flex flex-col gap-8 lg:col-span-6">
            <nav aria-label="위치" className="t-label-sm text-subtle"><Link to="/" className="hover:text-fg">HOME</Link> / PRODUCTS / 1788</nav>
            <h1 className="flex flex-col">
              <span className="t-display-thin">The</span>
              <span className="t-display">1788 Platform</span>
            </h1>
            <p className="t-body-lg max-w-xl text-muted">{DESC}</p>
            <div className="flex flex-wrap gap-3">
              <Button to="/contact?product=1788" arrow>데모 문의</Button>
              <Button to="#docs" variant="secondary">브로슈어 PDF</Button>
            </div>
          </div>
          <div className="mx-auto w-full max-w-[480px] lg:col-span-6">
            <TechLabel className="mb-3 text-right">FIG. 02 — SYSTEM COMPONENTS</TechLabel>
            <Tower1788 callouts={FULL_CALLOUTS} />
          </div>
        </div>
      </section>

      <section className="section border-b border-line" aria-labelledby="components">
        <div className="wrap flex flex-col gap-10">
          <div id="components"><SectionHead label="01 / COMPONENTS" bold="플랫폼 구성" thin="A – I" /></div>
          <ol className="grid gap-px overflow-hidden rounded-sm border border-line bg-line sm:grid-cols-2 lg:grid-cols-3">
            {P1788.components.map((c) => (
              <li key={c.key} className="flex items-center gap-5 bg-bg px-6 py-5">
                <span className="grid size-9 shrink-0 place-items-center rounded-full border border-primary t-label text-primary">{c.key}</span>
                <span className="t-title-md font-medium">{c.name}</span>
              </li>
            ))}
          </ol>
        </div>
      </section>

      <section className="section border-b border-line bg-grid" aria-labelledby="modes">
        <div className="wrap flex flex-col gap-12">
          <div id="modes"><SectionHead label="02 / IMAGING MODES" bold="형광 영상 모드" thin="White Light · Overlay · ENV · Contrast" /></div>
          <ModeSwitcher large />
          <div className="grid grid-cols-2 gap-x-6 gap-y-10 lg:grid-cols-4">
            {P1788.specs.map((s) => <SpecCounter key={s.label} {...s} />)}
          </div>
        </div>
      </section>

      <section className="section border-b border-line" aria-labelledby="usage">
        <div className="wrap grid gap-12 lg:grid-cols-2">
          <div className="flex flex-col gap-8" id="usage">
            <SectionHead label="03 / SPECIALTIES" bold="진료과별 활용" />
            <ul className="grid grid-cols-2 gap-px overflow-hidden rounded-sm border border-line bg-line">
              {P1788.specialties.map((s) => <li key={s} className="t-title-md bg-bg px-5 py-6">{s}</li>)}
            </ul>
          </div>
          <div className="flex flex-col gap-8">
            <SectionHead label="04 / FUNCTIONS" bold="주요 기능" />
            <ul className="flex flex-col">
              {[...P1788.functions, { name: "색 표현", desc: "62.5배 더 많은 색 표현" }].map((f) => (
                <li key={f.name} className="flex items-baseline justify-between gap-4 border-b border-line py-4">
                  <span className="t-title-md">{f.name}</span>
                  {f.desc && <span className="t-body-sm text-muted">{f.desc}</span>}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      <section className="section border-b border-line" aria-labelledby="parts">
        <div className="wrap flex flex-col gap-10">
          <div id="parts"><SectionHead label="05 / PART NUMBERS" bold="구성품" thin="용도설명서 기준" /></div>
          <div className="overflow-x-auto rounded-sm border border-line">
            <table className="w-full min-w-[520px] text-left">
              <thead className="bg-surface">
                <tr>
                  <th scope="col" className="t-label-sm px-6 py-4 text-subtle">제품 코드</th>
                  <th scope="col" className="t-label-sm px-6 py-4 text-subtle">구성품</th>
                </tr>
              </thead>
              <tbody>
                {P1788.parts.map((p) => (
                  <tr key={p.code} className="border-t border-line">
                    <td className="t-body-sm px-6 py-4 tnum text-primary">{p.code}</td>
                    <td className="t-body px-6 py-4">{p.name}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="t-body-sm text-subtle">
            관련 제품:{" "}
            {["spy-fluorescence", "l11-l12", "pneumoclear", "spy-laparoscope", "oled-display"].map((id, i) => {
              const p = getProductById(id)!;
              return <span key={id}>{i > 0 && " · "}<Link to={productPath(p)} className="underline-offset-4 hover:text-fg hover:underline">{p.name}</Link></span>;
            })}
          </p>
        </div>
      </section>

      <section className="section border-b border-line" aria-labelledby="faq">
        <div className="wrap grid gap-12 lg:grid-cols-12">
          <div className="lg:col-span-4" id="faq"><SectionHead label="06 / FAQ" bold="자주 묻는 질문" /></div>
          <dl className="flex flex-col lg:col-span-8">
            {FAQ.map((f) => (
              <div key={f.q} className="border-b border-line py-6">
                <dt className="t-title-md">{f.q}</dt>
                <dd className="t-body mt-3 text-muted">{f.a}</dd>
              </div>
            ))}
          </dl>
        </div>
      </section>

      <section id="docs" className="section border-b border-line">
        <div className="wrap flex flex-col gap-10">
          <SectionHead label="07 / DOCUMENTS" bold="1788 자료" />
          <DocList docs={docs} />
        </div>
      </section>

      <ContactBand />
      <JsonLd
        data={[
          breadcrumb([{ name: "1788 4K OLED Platform", path: "/products/1788" }]),
          {
            "@context": "https://schema.org",
            "@type": "Product",
            name: "Stryker 1788 4K OLED Platform",
            description: DESC,
            brand: { "@type": "Brand", name: "Stryker" },
            manufacturer: { "@type": "Organization", name: "Stryker" },
            category: "수술 영상 시스템",
            url: abs("/products/1788"),
          },
          {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            mainEntity: FAQ.map((f) => ({ "@type": "Question", name: f.q, acceptedAnswer: { "@type": "Answer", text: f.a } })),
          },
        ]}
      />
    </>
  );
}
