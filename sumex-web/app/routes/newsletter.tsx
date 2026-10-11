import { ChevronLeft, ChevronRight, X } from "lucide-react";
import { useState } from "react";
import { SocialButtons } from "~/components/Footer";
import { Button, JsonLd, KakaoButton, SpecialtyChip, TechLabel, cx } from "~/components/ui";
import { LATEST_ISSUE } from "~/data/newsletter";
import type { Specialty } from "~/data/products";
import { abs, breadcrumb, seo } from "~/lib/seo";

export const meta = () =>
  seo({
    title: "SUMEX DAILY 뉴스레터 – 오늘의 메디컬 브리핑",
    description: "매일 카드뉴스 7장으로 받아보는 의료기기·병원 뉴스 브리핑, SUMEX DAILY. 정형외과·신경외과·일반외과 관련 소식을 요약해 전합니다.",
    path: "/newsletter",
  });

export default function Newsletter() {
  const issue = LATEST_ISSUE;
  const [i, setI] = useState(0);
  const [modal, setModal] = useState(false);
  const d = issue.date.replace(/-/g, ".");
  const go = (n: number) => setI((v) => (v + n + issue.cards.length) % issue.cards.length);

  return (
    <>
      <section className="border-b border-line bg-grid">
        <div className="wrap flex flex-col gap-8 py-16 lg:flex-row lg:items-end lg:justify-between lg:py-24">
          <div className="flex flex-col gap-5">
            <TechLabel className="tnum">TODAY · {d}</TechLabel>
            <h1 className="t-display">SUMEX DAILY</h1>
            <p className="t-body-lg text-muted">매일 아침, 카드뉴스 7장으로 받아보는 메디컬 브리핑</p>
          </div>
          <div className="flex flex-wrap gap-3">
            <Button onClick={() => setModal(true)} arrow>뉴스레터 구독하기</Button>
            <KakaoButton />
          </div>
        </div>
      </section>

      <section className="section border-b border-line" aria-labelledby="cards">
        <div className="wrap flex flex-col gap-8">
          <h2 id="cards" className="t-h2">오늘의 카드뉴스</h2>
          {issue.sample && <p className="t-body-sm -mt-4 text-subtle">※ 화면 구성 확인용 샘플입니다.</p>}
          <div className="flex items-center justify-center gap-4 md:gap-8">
            <button type="button" onClick={() => go(-1)} aria-label="이전 카드" className="grid size-11 shrink-0 place-items-center rounded-full border border-line hover:border-fg"><ChevronLeft size={20} strokeWidth={1.5} /></button>
            <div className="relative flex w-full max-w-[420px] items-center justify-center">
              {issue.cards.map((c, n) => (
                <article
                  key={n}
                  aria-hidden={n !== i}
                  className={cx(
                    "flex aspect-[4/5] w-full flex-col justify-between rounded-sm border border-line bg-surface p-8 transition-opacity duration-300",
                    n === i ? "relative opacity-100" : "pointer-events-none absolute inset-0 opacity-0",
                  )}
                >
                  <span className="t-label-sm text-subtle tnum">SUMEX DAILY · {String(n + 1).padStart(2, "0")}/07</span>
                  <span className="flex flex-col gap-3">
                    <span className="text-[34px] font-extrabold leading-tight tracking-[-0.03em]">{c.title}</span>
                    <span className="text-[18px] font-extralight text-muted">{c.sub}</span>
                  </span>
                  <span className="t-label-sm text-subtle">출처 표기 영역</span>
                </article>
              ))}
            </div>
            <button type="button" onClick={() => go(1)} aria-label="다음 카드" className="grid size-11 shrink-0 place-items-center rounded-full border border-line hover:border-fg"><ChevronRight size={20} strokeWidth={1.5} /></button>
          </div>
          <div className="mx-auto flex w-full max-w-[420px] flex-col gap-3">
            <p className="t-label-sm text-center text-muted tnum">{String(i + 1).padStart(2, "0")} / 07</p>
            <div className="grid grid-cols-7 gap-1">
              {issue.cards.map((_, n) => (
                <button key={n} type="button" aria-label={`${n + 1}번 카드`} onClick={() => setI(n)} className={cx("h-1 rounded-full", n <= i ? "bg-primary" : "bg-line")} />
              ))}
            </div>
          </div>
          {/* 크롤러·AI용 카드 텍스트 (이미지 카드와 같은 내용) */}
          <ol className="sr-only">
            {issue.cards.map((c, n) => <li key={n}>{c.title} – {c.sub}</li>)}
          </ol>
        </div>
      </section>

      <section className="section border-b border-line" aria-labelledby="news">
        <div className="wrap grid gap-12 lg:grid-cols-12">
          <div className="lg:col-span-4"><h2 id="news" className="t-h2">메디컬 뉴스</h2></div>
          <ul className="flex flex-col lg:col-span-8">
            {issue.news.map((n) => (
              <li key={n.title} className="flex flex-col gap-3 border-b border-line py-6">
                <p className="t-label-sm text-subtle">{n.source} · <span className="tnum">{n.date}</span></p>
                <h3 className="t-title-md">{n.title}</h3>
                <p className="t-body-sm line-clamp-3 text-muted">{n.summary}</p>
                <div className="flex flex-wrap items-center gap-2">
                  {n.specialty.map((s) => <SpecialtyChip key={s} s={s as Specialty} />)}
                  {n.url && <a href={n.url} target="_blank" rel="noopener noreferrer" className="t-label-sm ml-auto text-muted hover:text-fg">원문 보기 ↗</a>}
                </div>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className="section border-b border-line">
        <div className="wrap flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
          <div className="flex flex-col gap-2">
            <h2 className="t-h2">지난 호</h2>
            <p className="t-body-sm text-muted">발행이 쌓이면 날짜별로 모아 보여드립니다.</p>
          </div>
          <SocialButtons />
        </div>
      </section>

      {modal && <SubscribeModal onClose={() => setModal(false)} />}
      <JsonLd
        data={[
          breadcrumb([{ name: "뉴스레터", path: "/newsletter" }]),
          { "@context": "https://schema.org", "@type": "Article", headline: `SUMEX DAILY ${d}`, datePublished: issue.date, author: { "@type": "Organization", name: "주식회사 수멕스" }, mainEntityOfPage: abs("/newsletter") },
        ]}
      />
    </>
  );
}

function SubscribeModal({ onClose }: { onClose: () => void }) {
  const [done, setDone] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const submit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    if (!String(fd.get("email") ?? "").includes("@")) return setErr("이메일 주소를 확인해 주세요.");
    if (!fd.get("privacy") || !fd.get("ads")) return setErr("필수 항목에 동의해 주세요.");
    // TODO: 스티비(Stibee) API 연동, 더블 옵트인 메일 발송
    setDone(true);
  };
  const input = "t-body h-[52px] w-full rounded-xs border border-line bg-surface px-4 outline-none focus:border-fg";
  return (
    <div role="dialog" aria-modal="true" aria-labelledby="sub-title" className="fixed inset-0 z-[90] grid place-items-center bg-black/80 p-5" onClick={onClose}>
      <div className="relative w-full max-w-[480px] rounded-sm border border-line bg-raised p-8" onClick={(e) => e.stopPropagation()}>
        <button type="button" onClick={onClose} aria-label="닫기" className="absolute right-4 top-4 grid size-9 place-items-center text-muted hover:text-fg"><X size={18} strokeWidth={1.5} /></button>
        <h2 id="sub-title" className="t-title-lg">뉴스레터 구독</h2>
        {done ? (
          <p role="status" className="t-body mt-6 text-muted">확인 메일을 보냈어요. 메일의 링크를 누르면 구독이 완료됩니다. <span className="text-subtle">(개발 시안: 실제 메일은 발송되지 않습니다)</span></p>
        ) : (
          <form onSubmit={submit} className="mt-6 flex flex-col gap-4" noValidate>
            <label htmlFor="sub-email" className="t-label-sm text-muted">이메일 *</label>
            <input id="sub-email" name="email" type="email" required className={input} autoComplete="email" />
            <label htmlFor="sub-name" className="t-label-sm text-muted">이름 (선택)</label>
            <input id="sub-name" name="name" className={input} autoComplete="name" />
            <fieldset className="flex flex-wrap gap-4">
              <legend className="t-label-sm mb-2 text-muted">관심 진료과</legend>
              {["OS", "NS", "GS"].map((s) => (
                <label key={s} className="t-body-sm flex items-center gap-2"><input type="checkbox" name="specialty" value={s} id={`sub-${s}`} className="accent-[var(--color-primary)]" /> {s}</label>
              ))}
            </fieldset>
            <label className="t-body-sm flex items-start gap-2 text-muted"><input type="checkbox" name="privacy" id="sub-privacy" className="mt-1 accent-[var(--color-primary)]" /> [필수] 개인정보 수집·이용 동의</label>
            <label className="t-body-sm flex items-start gap-2 text-muted"><input type="checkbox" name="ads" id="sub-ads" className="mt-1 accent-[var(--color-primary)]" /> [필수] 광고성 정보(뉴스레터) 수신 동의</label>
            {err && <p role="alert" className="t-body-sm text-error">{err}</p>}
            <Button type="submit" arrow className="mt-2">구독하기</Button>
          </form>
        )}
      </div>
    </div>
  );
}
