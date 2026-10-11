# SUMEX 홈페이지 (개발 시안)

주식회사 수멕스 공식 홈페이지. 디자인 기준은 `../sumex-homepage`의 DESIGN.md("True Black Engineering")입니다.

- React 19 + TypeScript + Vite
- React Router v7 프레임워크 모드, `ssr: false` + `prerender`: 모든 공개 페이지를 빌드할 때 완성된 HTML로 만듭니다 (검색엔진·AI 크롤러용)
- Tailwind CSS v4 (토큰: `app/app.css`의 `@theme`)
- 폰트: Pretendard Variable

## 실행

```bash
npm install
npm run dev        # http://localhost:5173 (개발 서버)
npm run build      # build/client 에 정적 사이트 생성
npm run preview    # http://localhost:4173 (빌드 결과 확인)
npm run typecheck
```

배포는 `build/client` 폴더를 Vercel, Firebase Hosting, Netlify 등 정적 호스팅에 올리면 됩니다.
404·SPA 경로는 `build/client/__spa-fallback.html`로 연결합니다.

## 구조

| 경로 | 내용 |
|---|---|
| `app/data/products.ts` | 제품 카탈로그 (카테고리, 그룹, 진료과, 설명, 특장점, 스펙) |
| `app/data/bodyParts.ts` | 인체 부위 ↔ 제품 매핑 |
| `app/data/library.ts` | PDF 자료 목록 (`driveId`를 채우면 보기/다운로드 동작) |
| `app/data/newsletter.ts` | 뉴스레터 호 (현재 샘플) |
| `app/data/paths.ts` | 프리렌더·사이트맵 경로 목록 |
| `app/config/site.ts` | 회사 정보, 연락처, SNS, 카카오 오픈채팅 URL |
| `app/lib/seo.ts` | 페이지별 meta, JSON-LD 헬퍼 |
| `app/routes/*` | 페이지 |
| `public/robots.txt`, `public/llms.txt` | 크롤러 설정 |

## 페이지

`/` 홈 · `/products/1788` · `/products/{arthro|laparo|instrument}` · `/products/{카테고리}/{제품}` (제품 35종) ·
`/explore`, `/explore/{부위}` (7곳) · `/products/library` · `/ai-search` · `/newsletter` · `/about` · `/contact` · `/sitemap.xml`

## 오픈 전 해야 할 일

- [ ] 제품 설명·스펙 전체 한국스트라이커 검수 (광고 심의 기준), 이후 상단 "개발 시안" 띠 제거 (`app/routes/_layout.tsx`)
- [ ] `app/config/site.ts`: 실제 도메인(`SITE_URL`), 대표 전화·이메일, 카카오 오픈채팅 URL
- [ ] `public/robots.txt`, `public/llms.txt`의 도메인 교체
- [ ] `.env`에 `VITE_KAKAO_JS_KEY` (없으면 지도 대신 주소 카드가 표시됨)
- [ ] `app/data/library.ts`의 `driveId` (Google Drive 업로드 후, 외부 배포 가능 여부 확인)
- [ ] 1788 실사 이미지 / 모드별 수술 영상 이미지 (현재는 도면·시뮬레이션 그래픽)
- [ ] 대표이사 인사말 확정, 대표 사진, 연혁 상세
- [ ] OG 이미지 `public/og/default.png` (1200×630)
- [ ] 문의 폼·뉴스레터 구독 실제 발송 연동 (Resend, 스티비)
- [ ] AI 검색: 현재는 키워드 매칭, 서버리스 함수 + Gemini로 교체
- [ ] 3D 인체 모델(GLB) 적용 (현재는 2D 홀로그램)
