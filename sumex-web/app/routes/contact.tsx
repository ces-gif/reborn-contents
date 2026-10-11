import { CheckCircle2 } from "lucide-react";
import { useState } from "react";
import { useSearchParams } from "react-router";
import { KakaoMap } from "~/components/KakaoMap";
import { Button, JsonLd, KakaoButton, TechLabel, cx } from "~/components/ui";
import { COMPANY, CONTACT } from "~/config/site";
import { getBodyPart } from "~/data/bodyParts";
import { PRODUCTS } from "~/data/products";
import { breadcrumb, localBusinessLd, seo } from "~/lib/seo";

export const meta = () =>
  seo({
    title: "문의하기 – 데모 · 도입 · 견적",
    description: "Stryker 1788, 관절경, 복강경, 수술 파워툴 데모와 도입을 수멕스에 문의하세요. 이메일 문의와 카카오톡 오픈채팅으로 상담할 수 있습니다.",
    path: "/contact",
  });

const INTEREST = [
  { v: "1788", l: "1788 4K OLED Platform" },
  { v: "arthro", l: "ARTHRO 관절경" },
  { v: "laparo", l: "LAPARO 복강경" },
  { v: "instrument", l: "INSTRUMENT 수술 도구" },
  { v: "etc", l: "기타" },
];

function interestFrom(product: string | null) {
  if (!product) return "";
  if (product === "1788") return "1788";
  return PRODUCTS.find((p) => p.slug === product)?.category ?? "etc";
}

const field = "t-body h-[52px] w-full rounded-xs border border-line bg-surface px-4 text-fg outline-none transition-colors placeholder:text-subtle focus:border-fg";

export default function Contact() {
  const [sp] = useSearchParams();
  const product = sp.get("product");
  const part = getBodyPart(sp.get("part") ?? undefined);
  const q = sp.get("q");
  const productName = product === "1788" ? "1788 4K OLED Platform" : PRODUCTS.find((p) => p.slug === product)?.name;
  const prefill = [productName && `관심 제품: ${productName}`, part && `수술 부위: ${part.label}`, q && `AI 질문: ${q}`].filter(Boolean).join("\n");
  const [sent, setSent] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const onSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    if (!fd.get("agree")) return setErr("개인정보 수집·이용에 동의해 주세요.");
    setErr(null);
    // TODO: 서버리스 함수 + 메일 API(Resend 등)로 CONTACT.email 에 발송
    console.info("[contact]", Object.fromEntries(fd));
    setSent(true);
  };

  return (
    <>
      <section className="border-b border-line">
        <div className="wrap grid gap-12 py-16 lg:grid-cols-12 lg:py-24">
          <div className="flex flex-col gap-10 lg:col-span-7">
            <div className="flex flex-col gap-5">
              <TechLabel>CONTACT</TechLabel>
              <h1 className="flex flex-wrap items-baseline gap-x-4">
                <span className="t-h1">함께 이야기해요</span>
                <span className="t-h1-thin text-muted">데모 · 도입 · 견적</span>
              </h1>
            </div>
            {sent ? (
              <div role="status" className="flex flex-col gap-4 rounded-sm border border-laparo/40 bg-laparo/10 p-8">
                <CheckCircle2 size={28} strokeWidth={1.5} className="text-laparo" />
                <p className="t-title-md">문의 내용이 입력되었습니다.</p>
                <p className="t-body-sm text-muted">개발 시안이라 실제 메일은 발송되지 않습니다. 메일 발송 기능은 연결 후 동작합니다.</p>
                <Button variant="ghost" arrow onClick={() => setSent(false)} className="self-start">다시 작성하기</Button>
              </div>
            ) : (
              <form onSubmit={onSubmit} className="grid gap-5 sm:grid-cols-2" noValidate>
                <Field id="org" label="병원 / 기관명" required><input id="org" name="org" required className={field} autoComplete="organization" /></Field>
                <Field id="name" label="이름" required><input id="name" name="name" required className={field} autoComplete="name" /></Field>
                <Field id="dept" label="진료과">
                  <select id="dept" name="dept" className={field} defaultValue="">
                    <option value="" disabled>선택</option>
                    <option>OS 정형외과</option><option>NS 신경외과</option><option>GS 일반외과</option><option>기타</option>
                  </select>
                </Field>
                <Field id="phone" label="연락처" required><input id="phone" name="phone" type="tel" required className={field} autoComplete="tel" /></Field>
                <Field id="email" label="이메일" required><input id="email" name="email" type="email" required className={field} autoComplete="email" /></Field>
                <Field id="interest" label="관심 제품">
                  <select id="interest" name="interest" className={field} defaultValue={interestFrom(product)}>
                    <option value="">선택</option>
                    {INTEREST.map((i) => <option key={i.v} value={i.v}>{i.l}</option>)}
                  </select>
                </Field>
                <Field id="message" label="문의 내용" required className="sm:col-span-2">
                  <textarea id="message" name="message" rows={6} required defaultValue={prefill} className={cx(field, "h-auto py-3")} />
                </Field>
                <label className="t-body-sm flex items-start gap-3 text-muted sm:col-span-2">
                  <input type="checkbox" name="agree" id="agree" className="mt-1 size-4 accent-[var(--color-primary)]" />
                  <span>[필수] 개인정보 수집·이용에 동의합니다. (수집 항목: 기관명, 이름, 연락처, 이메일 · 목적: 문의 응대 · 보유 기간: 문의 처리 후 1년)</span>
                </label>
                {err && <p role="alert" className="t-body-sm text-error sm:col-span-2">{err}</p>}
                <div className="sm:col-span-2"><Button type="submit" arrow>이메일로 문의 보내기</Button></div>
              </form>
            )}
          </div>
          <aside className="flex flex-col gap-6 rounded-sm border border-line bg-raised p-8 lg:col-span-5 lg:self-start">
            <TechLabel>INFO</TechLabel>
            <dl className="flex flex-col gap-5">
              {[
                ["주소", COMPANY.address],
                ["전화", CONTACT.phone ?? "확인 필요"],
                ["이메일", CONTACT.email ?? "확인 필요"],
              ].map(([k, v]) => (
                <div key={k} className="flex flex-col gap-1.5 border-b border-line pb-5">
                  <dt className="t-label-sm text-subtle">{k}</dt>
                  <dd className="t-body select-all">{v}</dd>
                </div>
              ))}
            </dl>
            <KakaoButton />
          </aside>
        </div>
      </section>
      <section className="section !pt-0 border-b border-line">
        <div className="wrap"><KakaoMap /></div>
      </section>
      <JsonLd data={[breadcrumb([{ name: "문의하기", path: "/contact" }]), localBusinessLd]} />
    </>
  );
}

function Field({ id, label, required, className, children }: { id: string; label: string; required?: boolean; className?: string; children: React.ReactNode }) {
  return (
    <div className={cx("flex flex-col gap-2", className)}>
      <label htmlFor={id} className="t-label-sm text-muted">{label}{required && <span className="text-primary"> *</span>}</label>
      {children}
    </div>
  );
}
