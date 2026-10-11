import { Search } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { Form, Link, useSearchParams } from "react-router";
import { ProductCard } from "~/components/ProductCard";
import { Button, KakaoButton, TechLabel } from "~/components/ui";
import { CATEGORIES, PRODUCTS, type Product } from "~/data/products";
import { seo } from "~/lib/seo";

export const meta = () =>
  seo({
    title: "AI 제품검색",
    description: "수술명이나 부위로 필요한 Stryker 장비를 찾아보세요. 수멕스 취급 제품 안에서 관련 제품을 추천합니다.",
    path: "/ai-search",
    noindex: true,
  });

const EXAMPLES = ["복강경 형광 영상 장비", "척추 수술용 고속 드릴", "어깨 봉합 앵커", "수술 연기 배출 기복기"];

/**
 * 1차 버전: products.ts 키워드 매칭 (브라우저에서 실행).
 * TODO: 서버리스 함수(/api/ai-search)에서 Gemini 호출로 교체.
 *  - products.ts 안의 제품만 추천, 목록에 없으면 "담당자 문의"로 안내, 효능 단정 금지
 *  - API 키는 서버에서만 사용
 */
function search(q: string): { product: Product; hits: string[] }[] {
  const tokens = q.toLowerCase().replace(/[^\p{L}\p{N}\s]/gu, " ").split(/\s+/).filter((t) => t.length >= 2);
  if (!tokens.length) return [];
  return PRODUCTS.map((p) => {
    const hay = [p.name, p.group, p.summary, ...p.keywords, ...p.features, CATEGORIES[p.category].ko].map((s) => s.toLowerCase());
    const hits = new Set<string>();
    let score = 0;
    for (const t of tokens) {
      p.keywords.forEach((k) => { if (k.toLowerCase().includes(t) || t.includes(k.toLowerCase())) { score += 3; hits.add(k); } });
      if (hay.some((h) => h.includes(t))) score += 1;
    }
    return { product: p, score, hits: [...hits] };
  })
    .filter((r) => r.score > 1)
    .sort((a, b) => b.score - a.score)
    .slice(0, 6);
}

export default function AiSearch() {
  const [sp] = useSearchParams();
  const q = sp.get("q")?.trim() ?? "";
  const results = useMemo(() => search(q), [q]);
  const answer = q
    ? results.length
      ? `“${q}”와 관련된 수멕스 취급 제품 ${results.length}개를 찾았습니다. ${results.slice(0, 2).map((r) => r.product.name).join(", ")} 등이 해당됩니다. 정확한 구성과 사양은 담당자가 안내해 드립니다.`
      : ""
    : "";
  const typed = useTyping(answer);

  return (
    <section className="border-b border-line">
      <div className="wrap flex max-w-[1080px] flex-col gap-10 py-16 lg:py-24">
        <div className="flex flex-col gap-5">
          <TechLabel>AI PRODUCT SEARCH</TechLabel>
          <h1 className="flex flex-wrap items-baseline gap-x-4">
            <span className="t-h1">AI 제품검색</span>
            <span className="t-h1-thin text-muted">수술명으로 찾아보세요</span>
          </h1>
        </div>
        <Form method="get" className="flex h-[72px] items-center gap-4 rounded-sm border border-line bg-raised px-6 transition-shadow focus-within:border-tertiary focus-within:shadow-[0_0_0_1px_#8894FF66,0_0_40px_#8894FF1F]">
          <Search size={22} strokeWidth={1.5} className="shrink-0 text-tertiary" aria-hidden />
          <label htmlFor="q" className="sr-only">검색어</label>
          <input key={q} id="q" name="q" defaultValue={q} placeholder="예) 무릎 관절경에 쓰는 4K 카메라" className="t-title-md min-w-0 flex-1 bg-transparent font-normal outline-none placeholder:text-subtle" />
          <button type="submit" className="t-label shrink-0 text-tertiary hover:text-fg">검색</button>
        </Form>
        <ul className="-mt-4 flex flex-wrap gap-2">
          {EXAMPLES.map((e) => (
            <li key={e}><Link to={`?q=${encodeURIComponent(e)}`} className="inline-flex h-9 items-center rounded-full border border-line px-4 t-body-sm text-muted hover:border-tertiary hover:text-fg">{e}</Link></li>
          ))}
        </ul>

        {q && results.length > 0 && (
          <>
            <div className="border-l-2 border-tertiary bg-overlay p-6" aria-live="polite">
              <p className="t-label-sm mb-3 text-tertiary">AI 요약</p>
              <p className="t-body min-h-[3.4em]">{typed}</p>
            </div>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {results.map((r) => (
                <ProductCard key={r.product.id} p={r.product} reason={r.hits.length ? `추천 이유: ‘${r.hits.slice(0, 3).join("’, ‘")}’ 관련 제품` : undefined} />
              ))}
            </div>
          </>
        )}
        {q && results.length === 0 && (
          <div className="flex flex-col gap-5 rounded-sm border border-line bg-surface p-8">
            <p className="t-title-md">찾으시는 제품을 담당자가 직접 안내해 드릴게요.</p>
            <div className="flex flex-wrap gap-3">
              <Button to={`/contact?q=${encodeURIComponent(q)}`} arrow>문의하기</Button>
              <KakaoButton />
            </div>
          </div>
        )}
        <p className="t-label-sm normal-case tracking-[0.02em] text-subtle">
          AI 검색 결과는 제품 정보 안내용이며 의학적 판단을 대신하지 않습니다. 정확한 사양은 담당자에게 문의해 주세요.
        </p>
      </div>
    </section>
  );
}

function useTyping(text: string) {
  const [out, setOut] = useState(text);
  useEffect(() => {
    if (!text || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return setOut(text);
    let i = 0;
    setOut("");
    const id = window.setInterval(() => {
      i += 2;
      setOut(text.slice(0, i));
      if (i >= text.length) window.clearInterval(id);
    }, 24);
    return () => window.clearInterval(id);
  }, [text]);
  return out;
}
