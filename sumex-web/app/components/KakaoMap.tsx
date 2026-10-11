import { ExternalLink, MapPin } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { COMPANY, KAKAO_MAP_LINK, KAKAO_ROUTE_LINK } from "~/config/site";

declare global {
  interface Window {
    kakao?: any;
  }
}

const KEY = import.meta.env.VITE_KAKAO_JS_KEY as string | undefined;

/** 카카오맵. 키(VITE_KAKAO_JS_KEY)가 없거나 로드에 실패하면 주소 카드만 보여준다. */
export function KakaoMap() {
  const ref = useRef<HTMLDivElement>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    if (!KEY || !ref.current) return;
    const init = () =>
      window.kakao.maps.load(() => {
        const { kakao } = window;
        new kakao.maps.services.Geocoder().addressSearch(COMPANY.addressShort, (res: any[], status: string) => {
          if (status !== kakao.maps.services.Status.OK || !ref.current) return;
          const pos = new kakao.maps.LatLng(res[0].y, res[0].x);
          const map = new kakao.maps.Map(ref.current, { center: pos, level: 3 });
          map.setZoomable(false);
          map.addControl(new kakao.maps.ZoomControl(), kakao.maps.ControlPosition.RIGHT);
          const marker = new kakao.maps.Marker({ position: pos, map });
          const open = () => window.open(`https://map.kakao.com/link/map/${COMPANY.name},${res[0].y},${res[0].x}`, "_blank", "noopener");
          kakao.maps.event.addListener(marker, "click", open);
          setReady(true);
        });
      });
    if (window.kakao?.maps) return init();
    const s = document.createElement("script");
    s.src = `https://dapi.kakao.com/v2/maps/sdk.js?appkey=${KEY}&libraries=services&autoload=false`;
    s.async = true;
    s.onload = init;
    document.head.appendChild(s);
  }, []);

  return (
    <div className="relative h-[320px] overflow-hidden rounded-sm border border-line bg-surface md:h-[480px]">
      <div ref={ref} className="absolute inset-0" style={{ filter: "grayscale(0.2) brightness(0.9)" }} />
      {!ready && (
        <div className="absolute inset-0 bg-grid" aria-hidden>
          <svg viewBox="0 0 100 100" preserveAspectRatio="none" className="h-full w-full opacity-40">
            <path d="M0 62 L100 48 M30 0 L42 100 M70 0 L64 100 M0 20 L100 30" stroke="#2E3136" strokeWidth="0.6" fill="none" vectorEffect="non-scaling-stroke" />
          </svg>
          <span className="absolute left-1/2 top-1/2 grid -translate-x-1/2 -translate-y-1/2 place-items-center">
            <span className="absolute size-6 rounded-full bg-primary/40" style={{ animation: "pulse-ring 2s ease-out infinite" }} />
            <MapPin size={28} strokeWidth={1.5} className="relative text-primary" />
          </span>
        </div>
      )}
      <p className="t-label-sm absolute left-5 top-5 text-subtle">SONGPA-GU, SEOUL</p>
      <div className="absolute bottom-4 left-4 right-4 flex max-w-md flex-col gap-3 rounded-sm border-l-[3px] border-primary bg-raised p-5 sm:right-auto">
        <p className="flex flex-col gap-1">
          <span className="t-label-sm text-primary">SUMEX</span>
          <span className="t-title-md">{COMPANY.name}</span>
        </p>
        <p className="t-body-sm text-muted">{COMPANY.address}</p>
        <div className="flex flex-wrap gap-4">
          <a href={KAKAO_MAP_LINK} target="_blank" rel="noopener noreferrer" className="t-label-sm inline-flex items-center gap-1.5 text-fg hover:text-primary">카카오맵에서 보기 <ExternalLink size={12} strokeWidth={1.5} /></a>
          <a href={KAKAO_ROUTE_LINK} target="_blank" rel="noopener noreferrer" className="t-label-sm inline-flex items-center gap-1.5 text-fg hover:text-primary">길찾기 <ExternalLink size={12} strokeWidth={1.5} /></a>
        </div>
      </div>
    </div>
  );
}
