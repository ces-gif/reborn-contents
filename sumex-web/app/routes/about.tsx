import { MapPin } from "lucide-react";
import { KakaoMap } from "~/components/KakaoMap";
import { JsonLd, SectionHead, TechLabel } from "~/components/ui";
import { COMPANY } from "~/config/site";
import { breadcrumb, localBusinessLd, seo } from "~/lib/seo";
import { ContactBand } from "./home";

export const meta = () =>
  seo({
    title: "회사소개 – Stryker 의료기기 유통 파트너",
    description: "주식회사 수멕스(SUMEX)는 2023년 설립된 의료기기 도매 기업으로 Stryker 수술 영상 장비와 수술 도구를 정형외과·신경외과·일반외과에 공급합니다.",
    path: "/about",
  });

const LETTERS = [
  { l: "S", w: "Surgical" },
  { l: "U", w: "" },
  { l: "M", w: "Medical" },
  { l: "EX", w: "Excellence" },
];

// TODO: 연혁 상세는 회사 확인 후 채움
const HISTORY = [
  { y: "2023.08", t: "주식회사 수멕스 법인 설립" },
  { y: "2024", t: "Stryker 대리점 계약" },
  { y: "2025 ~", t: "1788 4K 플랫폼 공급 확대" },
];

const AREAS = ["Arthroscopy", "Laparoscopy", "Instruments", "Sports Medicine"];

export default function About() {
  return (
    <>
      <section className="border-b border-line bg-grid">
        <div className="wrap flex flex-col gap-10 py-16 lg:py-24">
          <TechLabel>ABOUT · {COMPANY.nameEn}</TechLabel>
          <h1 className="flex flex-col">
            <span className="t-display">Surgical Excellence,</span>
            <span className="t-display-thin">Engineered.</span>
          </h1>
          <ul aria-label="SUMEX의 의미" className="grid grid-cols-2 gap-px overflow-hidden rounded-sm border border-line bg-line md:grid-cols-4">
            {LETTERS.map((x) => (
              <li key={x.l} className="group flex flex-col gap-3 bg-bg p-6 transition-colors hover:bg-raised">
                <span className="text-[64px] font-extrabold leading-none tracking-[-0.04em] text-fg group-hover:text-primary md:text-[88px]">{x.l}</span>
                <span className="t-label-sm text-muted">{x.w || "—"}</span>
              </li>
            ))}
          </ul>
          <p className="t-body-lg max-w-3xl text-muted">{COMPANY.tagline}</p>
        </div>
      </section>

      <section className="section border-b border-line">
        <div className="wrap grid gap-12 lg:grid-cols-12">
          <div className="lg:col-span-4"><SectionHead label="01 / COMPANY" bold="회사 개요" /></div>
          <dl className="grid gap-px overflow-hidden rounded-sm border border-line bg-line sm:grid-cols-2 lg:col-span-8">
            {[
              ["상호", `${COMPANY.name} (${COMPANY.nameEn})`],
              ["대표이사", COMPANY.ceo],
              ["설립", COMPANY.foundedLabel],
              ["업종", COMPANY.business],
              ["주소", COMPANY.address],
              ["사업 영역", AREAS.join(" · ")],
            ].map(([k, v]) => (
              <div key={k} className="flex flex-col gap-2 bg-bg p-6">
                <dt className="t-label-sm text-subtle">{k}</dt>
                <dd className="t-body">{v}</dd>
              </div>
            ))}
          </dl>
        </div>
      </section>

      {/* TODO: 대표이사 인사말은 초안 – 대표님 검토 후 확정 */}
      <section id="ceo" className="section scroll-mt-24 border-b border-line">
        <div className="wrap grid gap-12 lg:grid-cols-12">
          <div className="flex flex-col gap-6 lg:col-span-4">
            <SectionHead label="02 / CEO MESSAGE" bold="대표이사 인사말" />
            <div className="grid aspect-[4/5] max-w-[320px] place-items-center rounded-sm border border-line bg-surface">
              <span className="t-label-sm text-subtle">대표 사진 (흑백) 준비중</span>
            </div>
          </div>
          <div className="flex max-w-[680px] flex-col gap-6 lg:col-span-8">
            <p className="t-h2-thin">안녕하십니까, {COMPANY.name} 대표이사 {COMPANY.ceo}입니다.</p>
            <p className="t-body-lg text-muted">수술실의 1초, 1mm는 환자의 내일을 바꿉니다. 수멕스는 그 순간을 위해 Stryker의 앞선 수술 영상 장비와 수술 도구를 정형외과, 신경외과, 일반외과 현장에 전하고 있습니다.</p>
            <p className="t-body-lg text-muted">저희는 제품을 공급하는 데서 멈추지 않습니다. 데모와 설치, 교육, 사후 관리까지 의료진 곁에서 함께하며 가장 빠르게 응답하는 파트너가 되겠습니다.</p>
            <p className="t-body-lg text-muted"><strong className="font-semibold text-fg">“No Gray, Only Great.”</strong> 애매함 없이, 최고의 기준으로. 수멕스가 약속드립니다. 감사합니다.</p>
            <p className="mt-4 flex flex-col gap-1">
              <span className="t-body-sm text-subtle">{COMPANY.name} 대표이사</span>
              <span className="text-[32px] font-extralight tracking-[0.1em]">{COMPANY.ceo}</span>
            </p>
          </div>
        </div>
      </section>

      <section className="section border-b border-line">
        <div className="wrap grid gap-12 lg:grid-cols-12">
          <div className="lg:col-span-4"><SectionHead label="03 / HISTORY" bold="연혁" /></div>
          <ol className="relative flex flex-col gap-10 border-l border-line pl-8 lg:col-span-8">
            {HISTORY.map((h) => (
              <li key={h.y} className="relative">
                <span aria-hidden className="absolute -left-[37px] top-2 size-[9px] rounded-full bg-primary" />
                <p className="t-label text-primary tnum">{h.y}</p>
                <p className="t-title-md mt-2">{h.t}</p>
              </li>
            ))}
          </ol>
        </div>
      </section>

      <section id="location" className="section border-b border-line">
        <div className="wrap flex flex-col gap-8">
          <SectionHead label="04 / LOCATION" bold="오시는 길" />
          <p className="t-body flex items-start gap-3 text-muted"><MapPin size={20} strokeWidth={1.5} className="mt-0.5 shrink-0 text-primary" aria-hidden />{COMPANY.address}</p>
          <KakaoMap />
        </div>
      </section>
      <ContactBand />
      <JsonLd data={[breadcrumb([{ name: "회사소개", path: "/about" }]), localBusinessLd]} />
    </>
  );
}
