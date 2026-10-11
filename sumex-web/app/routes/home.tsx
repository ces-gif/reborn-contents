import { ArrowRight, Search } from "lucide-react";
import { useState } from "react";
import { Form, Link } from "react-router";
import { BodyMap, ModeSwitcher, Tower1788 } from "~/components/Visuals";
import { Button, Crosshair, KakaoButton, SectionHead, SpecCounter, SpecialtyChip, TechLabel, cx } from "~/components/ui";
import { BODY_PARTS } from "~/data/bodyParts";
import { LATEST_ISSUE } from "~/data/newsletter";
import { CATEGORIES, P1788, PRODUCTS, type CategoryId } from "~/data/products";
import { COMPANY } from "~/config/site";
import { seo } from "~/lib/seo";

export const meta = () => seo({ path: "/" });

const AI_EXAMPLES = ["복강경 형광 영상 장비", "척추 수술용 고속 드릴", "어깨 봉합 앵커", "수술 연기 배출 기복기"];

export default function Home() {
  return (
    <>
      <Hero />
      <TrustBar />
      <Spotlight1788 />
      <BodyPreview />
      <CategoryTrio />
      <AiTeaser />
      <NewsletterStrip />
      <CeoTeaser />
      <ContactBand />
    </>
  );
}

function Hero() {
  return (
    <section className="relative overflow-hidden border-b border-line bg-grid">
      <Crosshair className="absolute left-[80px] top-[80px] hidden md:block" />
      <Crosshair className="absolute right-[160px] top-[400px] hidden md:block" />
      <div className="wrap relative grid min-h-[640px] items-center gap-12 py-16 lg:grid-cols-12 lg:py-24">
        <div className="flex flex-col gap-8 lg:col-span-7">
          <TechLabel>STRYKER AUTHORIZED DISTRIBUTOR · OS / NS / GS</TechLabel>
          <h1 className="anim-rise flex flex-col">
            <span className="t-display">No Gray,</span>
            <span className="t-display-thin">Only Great.</span>
          </h1>
          <p className="t-body-lg max-w-xl text-muted">
            정형외과 · 신경외과 · 일반외과 수술실을 위한 Stryker 솔루션 파트너, <strong className="font-semibold text-fg">수멕스</strong>
          </p>
          <div className="flex flex-wrap gap-3">
            <Button to="/contact" arrow>문의하기</Button>
            <Button to="/products/1788" variant="secondary" arrow>1788 살펴보기</Button>
          </div>
        </div>
        <div className="relative mx-auto w-full max-w-[460px] lg:col-span-5">
          <TechLabel className="mb-3 text-right">FIG. 01 — 1788 4K OLED PLATFORM</TechLabel>
          <Tower1788 />
        </div>
      </div>
      <div aria-hidden className="absolute bottom-6 left-1/2 hidden h-12 w-px -translate-x-1/2 overflow-hidden bg-line md:block">
        <span className="block h-full w-full bg-primary" style={{ animation: "scroll-line 2s var(--ease-sumex) infinite" }} />
      </div>
    </section>
  );
}

function TrustBar() {
  const items = ["Stryker 공식 대리점", "OS 정형외과", "NS 신경외과", "GS 일반외과"];
  return (
    <section aria-label="취급 분야" className="border-b border-line">
      <ul className="wrap grid grid-cols-2 md:grid-cols-4">
        {items.map((t, i) => (
          <li key={t} className={cx("t-label py-6 text-center text-muted", i > 0 && "md:border-l md:border-line", i % 2 === 1 && "border-l border-line md:border-l")}>
            {t}
          </li>
        ))}
      </ul>
    </section>
  );
}

function Spotlight1788() {
  return (
    <section className="section relative border-b border-line bg-grid" aria-labelledby="s1788">
      <div className="wrap flex flex-col gap-16">
        <div className="grid gap-8 lg:grid-cols-12 lg:items-end">
          <div className="lg:col-span-7" id="s1788">
            <SectionHead label="01 / 1788 PLATFORM" bold="1788 4K OLED Platform" thin="새로운 수술 시각화의 기준" />
          </div>
          <p className="t-body-lg text-muted lg:col-span-5">
            트루 블랙과 10억 개 이상의 컬러, 1,000,000:1 명암비로 수술 시야를 4K로 표현합니다. 형광 영상을 Overlay · ENV · Contrast 세 가지 방식으로 볼 수 있습니다.
          </p>
        </div>
        <ModeSwitcher />
        <div className="grid grid-cols-2 gap-x-6 gap-y-10 lg:grid-cols-4">
          {P1788.specs.map((s) => <SpecCounter key={s.label} {...s} />)}
        </div>
        <div className="grid gap-10 lg:grid-cols-12">
          <div className="lg:col-span-7">
            <TechLabel className="mb-5">진료과 활용</TechLabel>
            <ul className="grid grid-cols-2 gap-px overflow-hidden rounded-sm border border-line bg-line md:grid-cols-3">
              {P1788.specialties.map((s) => (
                <li key={s} className="t-title-md bg-bg px-5 py-6">{s}</li>
              ))}
            </ul>
          </div>
          <div className="lg:col-span-5">
            <TechLabel className="mb-5">추가 기능</TechLabel>
            <ul className="flex flex-col">
              {P1788.functions.map((f) => (
                <li key={f.name} className="flex items-baseline justify-between gap-4 border-b border-line py-4">
                  <span className="t-title-md">{f.name}</span>
                  {f.desc && <span className="t-body-sm text-muted">{f.desc}</span>}
                </li>
              ))}
            </ul>
          </div>
        </div>
        <div className="flex flex-wrap gap-3">
          <Button to="/products/1788" variant="secondary" arrow>1788 상세 보기</Button>
          <Button to="/products/library" variant="secondary">브로슈어 PDF</Button>
          <Button to="/contact?product=1788" arrow>데모 문의</Button>
        </div>
      </div>
    </section>
  );
}

function BodyPreview() {
  return (
    <section className="section border-b border-line" aria-labelledby="sbody">
      <div className="wrap grid gap-12 lg:grid-cols-12 lg:items-center">
        <div className="flex flex-col gap-8 lg:col-span-5" id="sbody">
          <SectionHead label="02 / BODY EXPLORER" bold="어디를 수술하시나요?" thin="부위를 누르면 맞는 제품을 보여드려요" />
          <ul className="flex flex-wrap gap-2">
            {BODY_PARTS.map((b) => (
              <li key={b.id}>
                <Link to={`/explore/${b.id}`} className="inline-flex h-10 items-center gap-2 rounded-full border border-line px-4 t-label-sm text-muted transition-colors hover:border-fg hover:text-fg">
                  {b.labelEn} <span className="normal-case tracking-normal">{b.label}</span>
                </Link>
              </li>
            ))}
          </ul>
          <Button to="/explore" variant="ghost" arrow className="self-start">인체로 찾기 전체 보기</Button>
        </div>
        <div className="relative h-[520px] rounded-sm border border-line bg-surface lg:col-span-7">
          <div className="absolute inset-0 bg-grid opacity-60" aria-hidden />
          <div className="relative h-full p-6"><BodyMap /></div>
        </div>
      </div>
    </section>
  );
}

const catTop: Record<CategoryId, string> = { arthro: "bg-arthro", laparo: "bg-laparo", instrument: "bg-instrument" };
const FEATURED: Record<CategoryId, string[]> = {
  arthro: ["1688-aim-4k", "crossfire-2", "crossflow", "iconix"],
  laparo: ["spy-fluorescence", "pneumoclear", "ahto", "spy-laparoscope"],
  instrument: ["system-9", "signature-2", "tpx", "bipolar-forceps"],
};

function CategoryTrio() {
  const [hover, setHover] = useState<CategoryId | null>(null);
  return (
    <section className="section border-b border-line" aria-labelledby="scat">
      <div className="wrap flex flex-col gap-12">
        <div id="scat"><SectionHead label="03 / PRODUCTS" bold="취급 제품" thin="세 개의 카테고리" /></div>
        <div className="flex flex-col gap-4 lg:h-[420px] lg:flex-row" onMouseLeave={() => setHover(null)}>
          {(Object.values(CATEGORIES)).map((c) => (
            <Link
              key={c.id}
              to={`/products/${c.id}`}
              onMouseEnter={() => setHover(c.id)}
              onFocus={() => setHover(c.id)}
              className={cx(
                "group relative flex flex-col justify-between gap-8 overflow-hidden rounded-sm border border-line bg-surface p-8 transition-[flex-grow,background-color] duration-500 ease-[var(--ease-sumex)] hover:bg-raised",
                hover === c.id ? "lg:grow-[1.8]" : "lg:grow",
              )}
              style={{ flexBasis: 0 }}
            >
              <span aria-hidden className={cx("absolute inset-x-0 top-0 h-[3px]", catTop[c.id])} />
              <div className="flex flex-col gap-3">
                <p className="t-label-sm text-subtle">{c.ko}</p>
                <h3 className="text-[40px] font-extrabold leading-none tracking-[-0.03em] md:text-[48px]">{c.name}</h3>
                <p className="t-title-md font-light text-muted">{c.tagline}</p>
              </div>
              <ul className="flex flex-col">
                {FEATURED[c.id].map((id) => (
                  <li key={id} className="t-body-sm truncate border-b border-line py-2.5 text-muted">{PRODUCTS.find((p) => p.id === id)?.name}</li>
                ))}
              </ul>
              <div className="flex items-end justify-between gap-4">
                <div className="flex flex-wrap gap-2">{c.specialty.map((s) => <SpecialtyChip key={s} s={s} />)}</div>
                <ArrowRight size={24} strokeWidth={1.5} className="shrink-0 text-muted transition-transform group-hover:translate-x-1 group-hover:text-fg" aria-hidden />
              </div>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}

function AiTeaser() {
  return (
    <section className="section border-b border-line" aria-labelledby="sai">
      <div className="wrap flex max-w-[1040px] flex-col gap-8">
        <div id="sai"><SectionHead label="04 / AI SEARCH" bold="AI 제품검색" thin="수술명으로 찾아보세요" /></div>
        <Form action="/ai-search" className="flex h-[72px] items-center gap-4 rounded-sm border border-line bg-raised px-6 transition-shadow focus-within:border-tertiary focus-within:shadow-[0_0_0_1px_#8894FF66,0_0_40px_#8894FF1F]">
          <Search size={22} strokeWidth={1.5} className="shrink-0 text-tertiary" aria-hidden />
          <label htmlFor="home-q" className="sr-only">제품 검색어</label>
          <input id="home-q" name="q" placeholder="예) 무릎 관절경에 쓰는 4K 카메라" className="t-title-md min-w-0 flex-1 bg-transparent font-normal outline-none placeholder:text-subtle" />
          <button type="submit" className="t-label shrink-0 text-tertiary hover:text-fg">검색</button>
        </Form>
        <ul className="flex flex-wrap gap-2">
          {AI_EXAMPLES.map((q) => (
            <li key={q}>
              <Link to={`/ai-search?q=${encodeURIComponent(q)}`} className="inline-flex h-9 items-center rounded-full border border-line px-4 t-body-sm text-muted hover:border-tertiary hover:text-fg">{q}</Link>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}

function NewsletterStrip() {
  const d = LATEST_ISSUE.date.replace(/-/g, ".");
  return (
    <section className="section border-b border-line" aria-labelledby="snews">
      <div className="wrap flex flex-col gap-10">
        <div className="flex flex-wrap items-end justify-between gap-6" id="snews">
          <SectionHead label={`TODAY · ${d}`} bold="SUMEX DAILY" thin="오늘의 카드뉴스" />
          <div className="flex flex-wrap gap-3">
            <Button to="/newsletter" arrow>뉴스레터 구독하기</Button>
            <KakaoButton />
          </div>
        </div>
        <ol className="no-scrollbar -mx-5 flex snap-x gap-4 overflow-x-auto px-5 pb-2 md:-mx-10 md:px-10 xl:-mx-16 xl:px-16">
          {LATEST_ISSUE.cards.map((c, i) => (
            <li key={i} className="snap-start">
              <Link to="/newsletter" className="flex aspect-[4/5] w-[240px] flex-col justify-between rounded-sm border border-line bg-surface p-6 transition-colors hover:border-line-strong md:w-[280px]">
                <span className="t-label-sm text-subtle tnum">SUMEX DAILY · {String(i + 1).padStart(2, "0")}/07</span>
                <span className="flex flex-col gap-2">
                  <span className="t-title-lg text-[26px] font-extrabold">{c.title}</span>
                  <span className="t-body-sm font-extralight text-muted">{c.sub}</span>
                </span>
              </Link>
            </li>
          ))}
        </ol>
        {LATEST_ISSUE.sample && <p className="t-body-sm text-subtle">※ 화면 구성 확인용 샘플 카드입니다.</p>}
      </div>
    </section>
  );
}

function CeoTeaser() {
  return (
    <section className="section border-b border-line">
      <figure className="wrap flex max-w-[1080px] flex-col gap-8">
        <TechLabel>05 / CEO MESSAGE</TechLabel>
        <blockquote className="t-h2-thin text-fg">“수술실의 1초, 1mm는 환자의 내일을 바꿉니다.”</blockquote>
        <figcaption className="flex flex-wrap items-center justify-between gap-4">
          <span className="t-body text-muted">{COMPANY.name} 대표이사 <strong className="font-semibold text-fg">{COMPANY.ceo}</strong></span>
          <Button to="/about#ceo" variant="ghost" arrow>인사말 전문</Button>
        </figcaption>
      </figure>
    </section>
  );
}

export function ContactBand() {
  return (
    <section className="relative overflow-hidden border-b border-line bg-surface">
      <span aria-hidden className="line-yg absolute inset-x-0 top-0 h-px" />
      <div className="wrap flex flex-col gap-8 py-20 lg:flex-row lg:items-center lg:justify-between">
        <h2 className="flex flex-wrap items-baseline gap-x-4">
          <span className="t-h1">함께 이야기해요</span>
          <span className="t-h1-thin text-muted">데모 · 도입 · 교육</span>
        </h2>
        <div className="flex flex-wrap gap-3">
          <Button to="/contact" arrow>문의하기</Button>
          <KakaoButton />
        </div>
      </div>
    </section>
  );
}
