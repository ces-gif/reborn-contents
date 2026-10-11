import { Camera, NotebookPen, Youtube } from "lucide-react";
import { Link } from "react-router";
import { COMPANY, CONTACT, NAV, SOCIAL } from "~/config/site";
import { Button, KakaoButton, useToast } from "./ui";

const icons = { instagram: Camera, blog: NotebookPen, youtube: Youtube };

export function SocialButtons() {
  const toast = useToast();
  return (
    <div className="flex items-center gap-2">
      {(Object.keys(SOCIAL) as (keyof typeof SOCIAL)[]).map((k) => {
        const Icon = icons[k];
        const s = SOCIAL[k];
        const cls = "grid size-10 place-items-center rounded-full border border-line text-muted transition-colors hover:border-fg hover:text-fg";
        return s.url ? (
          <a key={k} href={s.url} target="_blank" rel="noopener noreferrer" aria-label={s.label} className={cls}>
            <Icon size={18} strokeWidth={1.5} />
          </a>
        ) : (
          <button key={k} type="button" aria-label={`${s.label} (준비중)`} className={cls} onClick={() => toast("준비중입니다. 곧 찾아뵙겠습니다.")}>
            <Icon size={18} strokeWidth={1.5} />
          </button>
        );
      })}
    </div>
  );
}

export function Footer() {
  return (
    <footer className="border-t border-line bg-surface text-muted">
      <div className="wrap grid gap-12 py-16 md:grid-cols-2 xl:grid-cols-4">
        <div className="flex flex-col gap-5">
          <img src="/brand/sumex-logo-white.png" alt="SUMEX" width={100} height={28} className="h-7 w-auto self-start" loading="lazy" />
          <p className="t-body-sm max-w-xs">{COMPANY.tagline}</p>
        </div>
        <nav aria-label="사이트 메뉴" className="grid grid-cols-2 content-start gap-x-6 gap-y-3 t-body-sm">
          {NAV.map((n) => (
            <Link key={n.to} to={n.to} className="hover:text-fg">{n.label}</Link>
          ))}
          <Link to="/products/library" className="hover:text-fg">제품 자료실</Link>
        </nav>
        <div className="flex flex-col gap-3 t-body-sm">
          <p className="t-label-sm text-subtle">CONTACT</p>
          <p>{COMPANY.address}</p>
          <p>전화 {CONTACT.phone ?? "확인 필요"}</p>
          <p>이메일 {CONTACT.email ?? "확인 필요"}</p>
          <div className="mt-2 flex flex-wrap gap-2">
            <Button variant="secondary" to="/contact" className="!h-11">이메일 문의</Button>
            <KakaoButton className="!h-11" label="오픈채팅" />
          </div>
        </div>
        <div className="flex flex-col gap-4">
          <p className="t-label-sm text-subtle">CHANNELS</p>
          <SocialButtons />
          <Button variant="ghost" to="/newsletter" arrow className="self-start">뉴스레터 구독</Button>
        </div>
      </div>
      <div className="border-t border-line">
        <div className="wrap flex flex-col gap-2 py-6 t-body-sm text-subtle md:flex-row md:flex-wrap md:items-center md:gap-x-3">
          <span>{COMPANY.name}</span>
          <span aria-hidden className="hidden md:inline">|</span>
          <span>대표이사 {COMPANY.ceo}</span>
          <span aria-hidden className="hidden md:inline">|</span>
          <span>사업자등록번호 {COMPANY.bizNo}</span>
          <span aria-hidden className="hidden md:inline">|</span>
          <span>{COMPANY.address}</span>
          <span className="md:ml-auto">개인정보처리방침 · © 2026 {COMPANY.nameEn} All rights reserved.</span>
        </div>
      </div>
    </footer>
  );
}
