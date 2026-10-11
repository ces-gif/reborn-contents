# SUMEX 홈페이지 – Antigravity 개발 프롬프트 (React)

## 쓰는 방법

1. 빈 폴더(예: `sumex-web`)를 Antigravity에서 엽니다.
2. 그 폴더 루트에 아래 파일 3개를 넣습니다.
   - `DESIGN.md`: 디자인 시스템 + 페이지 설계서 (대화에서 작성한 것)
   - `reference/sumex-home.html`: Stitch 시안 HTML (레이아웃 참고용)
   - `public/brand/sumex-logo.png`: 로고 원본 PNG
3. 아래 **Phase 0** 프롬프트를 Antigravity 에이전트 창에 그대로 붙여넣습니다.
4. 각 Phase가 끝나면 `http://localhost:5173`에서 직접 확인한 뒤 다음 Phase를 붙여넣습니다.
   한 번에 전부 시키면 품질이 떨어지므로 **Phase 단위로 끊어서** 진행합니다.

> 모든 Phase 프롬프트 맨 앞에는 아래 "공통 규칙" 블록을 함께 붙여넣으세요.
> 대화가 길어지면 Antigravity가 앞의 규칙을 잊기 때문입니다.

### 왜 React Router v7 프레임워크 모드인가
DESIGN.md의 스택(React + TypeScript + Vite + React Router)을 그대로 씁니다. 다만 일반 SPA로 만들면 검색엔진과 AI 크롤러가 빈 HTML만 보게 됩니다. React Router v7의 **프레임워크 모드 + prerender**를 켜면, 같은 React 코드로 페이지마다 완성된 HTML이 빌드 시점에 만들어집니다. 개발 방식은 일반 React와 같습니다.

---

## 공통 규칙 (매 Phase 맨 앞에 붙여넣기)

```
[공통 규칙 – 반드시 지킬 것]

0. 프로젝트 루트의 DESIGN.md가 디자인·콘텐츠의 최우선 기준이다. 작업 전에 반드시 다시 읽어라.
   reference/sumex-home.html(Stitch 시안)은 "섹션 구성과 배치"만 참고한다.
   시안의 흰 배경, 그림자, Space Grotesk/Hanken Grotesk 폰트, #4F46E5/#D97706 색은 쓰지 않는다.
   색·폰트·라운드·간격은 전부 DESIGN.md 토큰을 따른다 (배경 #000000, Pretendard, 로고 3색).

1. 스택 (DESIGN.md 기준 + SEO 설정):
   - React 19 + TypeScript + Vite
   - React Router v7 "프레임워크 모드" (app/routes.ts 파일 기반 라우팅, react-router.config.ts에서 prerender 사용)
   - Tailwind CSS v4 (@tailwindcss/vite 플러그인, DESIGN.md 토큰을 @theme 변수로 정의)
   - Framer Motion, lucide-react (1.5px 라인 아이콘)
   - 3D: three + @react-three/fiber + @react-three/drei → 브라우저에서만 렌더 (React.lazy + 마운트 후 렌더하는 ClientOnly 래퍼)
   - 패키지 매니저: npm, 개발 서버: http://localhost:5173

2. SEO/GEO 원칙:
   - 모든 공개 페이지는 prerender 목록에 넣어 빌드 시 완성된 HTML을 만든다.
     JS를 꺼도 본문 텍스트가 보여야 한다 (크롤러·AI가 읽을 수 있게).
   - 데이터는 컴포넌트 안 useEffect로 불러오지 말고 route의 loader에서 불러온다 (그래야 프리렌더 HTML에 들어간다).
   - 페이지마다 route의 meta export로 title, description, canonical(link), og:title/og:description/og:image 지정.
   - window, document, localStorage는 useEffect 안에서만 쓴다 (프리렌더 중 에러 방지).
   - 히어로의 h1과 대표 이미지는 opacity:0에서 시작하는 애니메이션 금지 (LCP 보호). transform만 움직인다.
   - 스펙 숫자(4K, 1,000,000:1 등)는 카운트업 애니메이션과 별개로 실제 숫자가 HTML에 있어야 한다.
   - 이미지는 width/height 지정, 첫 화면 밖은 loading="lazy", alt 필수.
   - 페이지 이동은 반드시 <Link to>. onClick으로 navigate만 하는 링크 금지.

3. 콘텐츠 원칙 (의료기기 광고 규정):
   - 제품 설명은 DESIGN.md에 적힌 내용만 사용한다. 새로운 수치·효능·실적·인증을 지어내지 마라.
   - 금지 예시: "피로도 42% 감소", "15곳 도입", "합병증 예방", "손상 원천 차단", "ISO 13485 인증", "100% 정품 인증", "99.8%".
   - 모르는 값(전화, 이메일, 카카오 URL 등)은 app/config/site.ts의 placeholder로 두고 화면에는 "확인 필요"로 표시한다.

4. 작업 방식:
   - 작업 시작 전에 이번 Phase의 계획(만들 파일 목록)을 먼저 보여주고 진행한다.
   - 작업이 끝나면 `npm run typecheck`와 `npm run build`를 실행해 에러가 없는지 확인한다.
   - 그 다음 `npm run dev`로 http://localhost:5173 을 띄우고, 내장 브라우저로 데스크톱(1440px)과 모바일(390px) 화면을 확인한다.
   - 가로 스크롤이 생기거나 텍스트가 잘리면 고친다.
   - 마지막에 "이번 Phase에서 만든 것 / 확인한 URL / 남은 TODO"를 정리해서 보고한다.
```

---

## Phase 0 – 프로젝트 생성과 디자인 토큰

```
[Phase 0] SUMEX 홈페이지 React 프로젝트를 만들고 localhost에서 띄워줘.

1. 현재 폴더에 React Router v7 프레임워크 모드 프로젝트를 생성해라
   (기존 DESIGN.md, reference/, public/brand/는 지우지 말 것):
   npx create-react-router@7 . --yes
   폴더가 비어있지 않다고 실패하면, 임시 폴더에 만든 뒤 파일을 옮겨라.
   기본 템플릿에 Tailwind v4가 없으면 tailwindcss @tailwindcss/vite 를 설치하고 vite.config.ts에 플러그인 추가.

2. 패키지 설치: framer-motion lucide-react clsx pretendard

3. react-router.config.ts:
   export default { ssr: true, async prerender() { return ["/"]; } } satisfies Config;
   (페이지를 만들 때마다 prerender 목록에 경로를 추가한다. 나중에 app/data에서 자동 생성.)

4. 디자인 토큰 (app/app.css):
   - DESIGN.md 맨 위 YAML의 colors, typography, rounded, spacing을 Tailwind v4 @theme 변수로 옮겨라.
     예: --color-primary:#FFD400; --color-surface:#0A0A0B; --color-category-arthro:#8894FF ...
   - 반응형 폰트 크기(display-xl 112/80/48px 등)는 DESIGN.md "반응형 크기" 표대로.
   - body: 배경 #000000, 글자 #F5F5F5, word-break: keep-all
   - .tnum { font-feature-settings: 'tnum' 1; }
   - 포커스 링: 2px #FFD400 outline
   - prefers-reduced-motion: reduce 이면 모든 애니메이션·트랜지션 끄기

5. 폰트: app/root.tsx에서 import "pretendard/dist/web/variable/pretendardvariable-dynamic-subset.css"
   font-family: "Pretendard Variable", Pretendard, -apple-system, system-ui, sans-serif

6. app/config/site.ts 생성 (DESIGN.md "설정값 placeholder" 표 기준):
   SITE_URL(임시 "http://localhost:5173"), COMPANY(상호, 대표, 사업자번호, 주소, 설립일),
   CONTACT_EMAIL / PHONE / KAKAO_OPENCHAT_URL = null,
   SOCIAL = { instagram:{url:null,label:"Instagram"}, blog:{url:null,label:"Blog"}, youtube:{url:null,label:"YouTube"} }

7. app/root.tsx: <html lang="ko">, <Meta/> <Links/> 유지.
   app/lib/seo.ts 에 공통 meta 헬퍼 작성:
   seo({ title, description, path, image }) → title은 "{title} | 수멕스(SUMEX)", canonical link, og:*, twitter:card 반환.
   홈 기본 title: "수멕스(SUMEX) · Stryker 의료기기 유통 – 관절경 · 복강경 · 수술 파워툴"

8. 임시로 /styleguide 라우트를 만들어 토큰을 확인한다:
   색 스와치 전체, 타이포 스케일 전체(display-xl/thin ~ label-sm), 버튼 4종(primary/secondary/ghost/kakao),
   칩(OS/NS/GS, ARTHRO/LAPARO/INSTRUMENT).

9. npm run dev 실행 후 http://localhost:5173/styleguide 를 열어 검정 배경 + Pretendard + 3색 칩이 보이는지 확인하고 보고해라.
```

---

## Phase 1 – 공통 레이아웃 + 홈 화면

```
[Phase 1] 공통 컴포넌트와 홈(/) 화면을 만들어줘.

A. 공통 컴포넌트 (app/components/):
   - Button (primary / secondary / ghost / kakao): DESIGN.md Components > Buttons 규칙대로.
     primary 호버 시 #FFE14D + 화살표 4px 이동. 화면당 primary는 1개.
   - Chip (specialty 아웃라인 / category 반투명 3색)
   - Header: 72px, sticky, 스크롤 시 #000000CC + backdrop-blur(16px) + 하단 1px #1F2124.
     로고(/brand/sumex-logo.png, 높이 28px) / GNB: 회사소개 · 1788(옐로 점) · 인체로 찾기 · ARTHRO · LAPARO · INSTRUMENT · AI 제품검색 · 뉴스레터 · 문의
     / 우측: 카카오 오픈채팅 아이콘 버튼 + [문의하기] primary.
     활성 메뉴는 <NavLink>로 = 옐로 글자 + 하단 2px 옐로 바. 모바일은 햄버거 → 전체화면 검정 오버레이(메뉴 headline-md 크기).
   - Footer: DESIGN.md "Global: Header & Footer" 4열 + 최하단 사업자 정보 줄.
   - Header/Footer는 app/routes/_layout.tsx (pathless layout route)에 넣고 모든 페이지가 공유.
   - SocialButtons + Toast: url이 null이면 "준비중입니다. 곧 찾아뵙겠습니다." 토스트(하단 중앙, 2.5초, role="status", 왼쪽 3px 옐로 바).
   - GridBackground: 80px 간격 흰색 5% 그리드 + 몇 개 교차점에 + 크로스헤어 (CSS/SVG, aria-hidden).
   - SectionLabel: "01 / ARTHRO" 같은 좌상단 기술 라벨 (label-sm, 회색).
   - SpecCounter: 큰 얇은 숫자(200) + 굵은 단위(700). 화면 진입 시 1.2초 카운트업.
     단, 처음 렌더(프리렌더 HTML)에는 최종 숫자가 들어있어야 한다. 0으로 시작해서 렌더하지 말 것.
   - ClientOnly: 마운트 후에만 children을 렌더하는 래퍼 (3D, 지도 등 브라우저 전용 컴포넌트용).

B. 홈 화면 (app/routes/_layout._index.tsx) – DESIGN.md "1. 홈" S1~S8 순서대로. 배치는 reference/sumex-home.html 참고:
   - S1 Hero: 좌 7컬럼 카피(h1 = "No Gray," 800 / "Only Great." 200), 서브카피, CTA 2개.
     우 5컬럼: 1788 타워 이미지(없으면 public/images/placeholder-1788.svg로 대체)
     + 뒤 옐로→그린 방사형 발광 + A/B/C 리더라인 콜아웃(SVG).
     높이는 100vh 고정하지 말고 콘텐츠 기준(min-height 640px 정도).
   - S2 Trust Bar
   - S3 1788 Spotlight: 모드 탭 4개(White Light/Overlay/ENV/Contrast), 이미지 없으면 DESIGN.md의 CSS filter 방식.
     탭 설명 3개는 DESIGN.md 문구 그대로. 스펙 카운터 4개, 진료과 6칸, 기능 리스트, CTA 3개.
   - S3-1 인체 탐색 미리보기: 3D 대신 정적 SVG 인체 + 7개 핫스팟 <Link to="/explore/shoulder"> 등.
   - S4 Category Trio: 3분할 카드, 데스크톱 호버 시 아코디언 확장.
   - S5 AI 검색 티저: 검색창(<Form action="/ai-search">) + 예시 칩 → /ai-search?q=...
   - S6 오늘의 뉴스레터: 카드 7장 가로 스크롤 (이미지 대신 검정 카드에 텍스트로 임시 구성).
   - S7 대표이사 인사말 티저 → /about#ceo
   - S8 Contact CTA 밴드
   - 시안에 있던 "CALIBRATION 0.00ms", "IN-STOCK", "ISO 13485", "LOCKED 99.8%" 같은 가짜 텔레메트리 문구는 넣지 말 것.
   - meta export: seo({ title: 홈 기본 title, description: 80~120자, path: "/" })

C. 확인: npm run build 통과 → build/client/index.html 을 열어 h1·스펙 숫자·섹션 제목이 HTML 텍스트로 있는지 확인
   → npm run dev → localhost:5173 데스크톱/모바일 스크린샷 확인.
```

---

## Phase 2 – 제품 데이터 + 카테고리 / 제품 상세 페이지

```
[Phase 2] 제품 데이터와 카테고리·제품 상세 페이지를 만들어줘.

1. app/data/products.ts (타입 포함):
   type Product = {
     id: string; slug: string; name: string;
     category: "1788" | "arthro" | "laparo" | "instrument";
     group: string;              // "영상 시스템", "절제·지혈" 등 DESIGN.md 그룹명
     specialty: ("OS"|"NS"|"GS")[];
     summary: string;            // 2~3문장 정의. 첫 문장은 "OO는 ~입니다." 형태
     features: string[];         // DESIGN.md에 적힌 특장점만
     specs?: { label: string; value: string }[];
     keywords: string[];
     bodyParts: string[];        // "shoulder" 등
     libraryDocIds: string[];
     faq?: { q: string; a: string }[];
   }
   DESIGN.md "4. 카테고리 소개 페이지"의 ARTHRO/LAPARO/INSTRUMENT 제품 목록을 전부 등록.
   summary·features는 DESIGN.md 괄호 안 설명을 기반으로만 작성하고, 없는 정보는 비워둔다.
   각 summary 옆에 // TODO: 한국스트라이커 검수 주석.

2. 라우트 (app/routes.ts에 등록, 데이터는 loader에서 반환):
   - /products/:category (arthro, laparo, instrument)
     카테고리 히어로(카테고리 색 라인 + display 타이틀) → 진료과 필터 칩(전체/OS/NS/GS, ?specialty=OS 와 동기화)
     → 그룹별 제품 카드 그리드(3/2/1열) → 카테고리 FAQ → PDF 게시판 자리.
     없는 category면 loader에서 throw data(null, { status: 404 }).
   - /products/:category/:slug : 제품 상세 페이지 (SEO 핵심, 제품마다 고유 URL).
     구성: h1 제품명 → summary → 특장점 → 스펙 <table> → 관련 부위 링크 → FAQ → 관련 PDF → [이 제품 문의하기](/contact?product=slug).
   - Drawer: 카테고리 페이지에서 카드를 누르면 <Link to={상세URL} state={{ drawer: true }}>로 이동하고,
     상세 라우트는 location.state.drawer 가 true면 카테고리 목록 위에 우측 Drawer로, 아니면 전체 페이지로 렌더한다.
     새로고침하거나 주소를 직접 열면 반드시 전체 페이지가 나와야 한다.
   - /products/1788: DESIGN.md "3. 1788 전용 페이지" (구성품 A~I 콜아웃, 모드 전환 크게, 구성품 표는 <table>).

3. react-router.config.ts의 prerender를 app/data/products.ts에서 자동 생성:
   "/", "/products/1788", 카테고리 3개, 모든 제품 상세 경로.

4. ProductCard: DESIGN.md Product Card 사양 (우상단 45° 컷 clip-path, 호버 시 카테고리 색 테두리/컷 채움, 이미지 1.03배).

5. 확인: /products/arthro, /products/arthro/crossfire-2, /products/1788 을 localhost에서 열어보고,
   상세 페이지를 새 탭에서 직접 열었을 때 Drawer가 아닌 전체 페이지로 나오는지 확인.
   npm run build 후 build/client/products/arthro/crossfire-2/index.html 에 제품 설명 텍스트가 있는지 확인.
```

---

## Phase 3 – 회사소개 · 문의 · 자료실 · 뉴스레터

```
[Phase 3] /about, /contact, /products/library, /newsletter 를 만들어줘.

1. /about: DESIGN.md "2. 회사소개". 회사 개요(사업자등록증 기준 값), SUMEX 글자 분해 타이포 인터랙션,
   대표이사 인사말(#ceo, 초안 그대로 + 코드에 "초안 – 대표님 검토 후 확정" 주석),
   연혁 세로 타임라인, 오시는 길(KakaoMap).

2. KakaoMap 컴포넌트 (ClientOnly 안에서 렌더):
   - useEffect에서 <script src="//dapi.kakao.com/v2/maps/sdk.js?appkey=${import.meta.env.VITE_KAKAO_JS_KEY}&libraries=services&autoload=false"> 를 한 번만 주입.
   - DESIGN.md "Location & Kakao Map" 코드와 디자인(정보 카드 오버레이, setZoomable(false), 클릭 시 카카오맵 새 창) 그대로.
   - 키가 없으면 지도 대신 같은 크기의 검정 박스에 주소 텍스트 + [카카오맵에서 보기] 링크 (에러 화면 금지).
   - 주소는 지도와 별개로 항상 HTML 텍스트로도 출력.
   - .env.example 파일에 VITE_KAKAO_JS_KEY= 추가.

3. /contact: DESIGN.md "9. 문의하기" 폼. URL 파라미터(product, part, q)로 자동 입력.
   제출은 같은 라우트의 action(서버)에서 처리 → 지금은 서버 콘솔에 로그만 찍고 성공 메시지
   (Resend 연동은 TODO 주석). 개인정보 수집 동의 체크 필수, action에서도 검증.
   이 페이지 canonical은 항상 /contact 로 고정.

4. /products/library: DESIGN.md "5. 제품 자료실". 이번에는 B안(app/data/library.ts 수동 등록).
   DESIGN.md "1차 업로드 추천 PDF" 표의 파일명으로 목록을 만들되 id는 "TODO_DRIVE_ID".
   검색 + 필터(카테고리/진료과/문서종류) + 카드형/리스트형 전환.
   [보기]는 PdfViewerModal(Drive preview iframe), id가 TODO면 "자료 준비중" 토스트.
   각 문서 행에 제품 상세 페이지 링크를 같이 둔다.

5. /newsletter + /newsletter/:date : DESIGN.md "7. 뉴스레터".
   데이터는 app/data/newsletter/2026-10-10.ts 샘플 1건 (카드 7장 텍스트 + 뉴스 3건, 화면에 "샘플" 표기).
   카드뉴스는 이미지가 있더라도 같은 내용의 텍스트를 HTML로 함께 출력한다.
   구독 모달: 이메일/이름/관심 진료과 + [필수] 개인정보 동의 + [필수] 광고성 정보 수신 동의.
   제출은 /api/subscribe 리소스 라우트(action만 있는 라우트)로 → 지금은 로그만.

6. 새 경로를 prerender 목록에 추가 (/contact는 action이 있으니 ssr로 동작해도 됨, HTML은 prerender).

7. 확인: 각 페이지 localhost 확인, 카카오 키 없이도 /about·/contact가 깨지지 않는지 확인.
```

---

## Phase 4 – 3D 인체 탐색 + AI 제품검색

```
[Phase 4] /explore 와 /ai-search 를 만들어줘.

1. 데이터: app/data/bodyParts.ts – DESIGN.md "8. 3D 인체 탐색"의 BodyPart 타입과 "부위별 제품 매핑" 표 7개 부위.
   productIds는 Phase 2의 products.ts id와 연결.

2. 라우트:
   - /explore: 전체 부위 목록 + 3D 뷰어
   - /explore/:part : 부위별 페이지 7개 (prerender).
     loader가 부위 + 관련 제품을 반환하고, HTML에 h1 "{부위} 수술 장비", 진료과, 수술 키워드, 관련 제품 목록(상세 링크)이 들어간다.
     그 위에 3D 뷰어가 얹히는 구조. DESIGN.md의 ?part= 쿼리 대신 경로를 쓴다.

3. BodyExplorer3D (React.lazy로 불러와 ClientOnly + Suspense 안에서 렌더, fallback은 삼각형 로고 스피너):
   - public/models/human-body.glb 가 있으면 useGLTF로 로드, 없으면 drei 기본 도형으로 임시 인체(캡슐/구 조합).
   - 홀로그램 재질(wireframe, opacity 0.2), 바닥 스캔 링, 자동 회전(40초/바퀴), OrbitControls(줌 범위 제한).
   - 핫스팟 7개(drei Html), 클릭 시 카메라 800ms 줌인 + navigate(`/explore/${id}`, { preventScrollReset: true }).
   - WebGL 미지원 또는 저사양이면 BodyFallback2D(SVG 앞/뒤)로 대체.
   - 왼쪽 부위 버튼 목록은 3D와 별개로 항상 렌더 (<Link>, 키보드 Tab 접근, aria-label="어깨 관련 제품 보기").
   - 모바일: 3D 상단 55%, 부위 칩 가로 스크롤, 제품 패널은 바텀시트.
   - prefers-reduced-motion이면 자동 회전/스캔/펄스 끄기.

4. BodyPanel: DESIGN.md 5단계 흐름 (부위 → 제품 리스트 → 제품 상세 → AI 질문 → 문의 버튼).

5. AI 검색:
   - /api/ai-search 리소스 라우트(action): 지금은 Gemini 호출 대신 products.ts 키워드 매칭 mock
     (요약 문장 + 추천 제품 3~6개 + 추천 이유). process.env.GEMINI_API_KEY 가 있으면 실제 호출하도록 분기만 만들어 둔다.
     키는 서버(action)에서만 쓰고 VITE_ 접두사를 붙이지 않는다 (프론트 노출 금지).
   - 프롬프트 규칙(주석으로 남김): products.ts 안의 제품만 추천, 없으면 "담당자 문의", 효능 단정 금지.
   - /ai-search: DESIGN.md "6. AI 제품검색" UI, useFetcher로 호출, 결과 타이핑 효과, 하단 고지 문구.
     meta에 { name: "robots", content: "noindex" } (검색 결과 페이지 색인 방지). prerender 목록에는 넣지 않는다.
   - AiAskBox(제품별 질문)도 같은 API 사용, 응답 완료 후 [이 제품 문의하기] 버튼이 아래에서 올라옴.

6. 확인: /explore, /explore/knee, /ai-search?q=복강경 형광 을 localhost에서 확인.
   홈(/)에서 three.js 번들을 내려받지 않는지 브라우저 Network 탭으로 확인.
```

---

## Phase 5 – SEO / GEO 마무리

```
[Phase 5] SEO/GEO 설정을 마무리해줘.

1. 메타데이터: 모든 라우트에 meta export (app/lib/seo.ts 사용).
   | 페이지 | title |
   | 홈 | 수멕스(SUMEX) · Stryker 의료기기 유통 – 관절경 · 복강경 · 수술 파워툴 |
   | 1788 | Stryker 1788 4K OLED Platform – 4K 형광 수술 영상 시스템 |
   | 제품 | {제품명} – {카테고리 한글} |
   | 부위 | {부위} 수술 장비 – {대표 키워드} |
   description 80~120자, canonical, og:image(1200×630).
   OG 이미지는 public/og/default.png (검정 배경 + SUMEX 로고 + 1788) 1장을 만들어 공통 사용. 제품별 이미지는 TODO.

2. 구조화 데이터: app/components/JsonLd.tsx (<script type="application/ld+json">) 만들고
   - root: Organization (name "SUMEX", legalName "주식회사 수멕스", address, logo, foundingDate "2023-08-21")
   - /about, /contact: LocalBusiness + PostalAddress (사업자등록증 주소 그대로)
   - 제품 상세: Product (brand/manufacturer: Stryker, category, description) – Offer/가격 넣지 말 것
   - 모든 하위 페이지: BreadcrumbList
   - FAQ 있는 페이지: FAQPage
   - 뉴스레터 호: Article (datePublished, author 주식회사 수멕스)

3. 사이트맵·robots:
   - app/routes/sitemap[.]xml.tsx 리소스 라우트: prerender 목록과 같은 경로로 XML 생성, prerender 목록에 "/sitemap.xml" 추가.
   - public/robots.txt: 전체 허용 + GPTBot, ClaudeBot, PerplexityBot, Google-Extended, Yeti 명시 허용,
     /api/, /ai-search 는 Disallow, Sitemap 경로 포함.

4. public/llms.txt: 회사 소개 3줄 + 주요 페이지 링크(1788, 카테고리 3개, 부위 7개, 회사소개, 문의) 마크다운.

5. 성능: npm run build && npm run start 후 홈 Lighthouse(모바일) 실행, LCP/CLS 점수 보고.
   히어로 이미지 fetchpriority="high", 폰트는 dynamic-subset CSS 사용 확인.

6. 최종 확인 체크리스트를 실행하고 결과를 표로 보고해라:
   - [ ] npm run typecheck, npm run build 성공
   - [ ] build/client/products/1788/index.html 에 "1,000,000" 과 "4K" 텍스트가 있음
   - [ ] build/client/explore/shoulder/index.html 에 제품명들이 있음
   - [ ] /sitemap.xml, /robots.txt, /llms.txt 열림
   - [ ] 제품 상세 HTML에 JSON-LD 3종(Organization, Product, BreadcrumbList) 존재
   - [ ] 모바일 390px에서 가로 스크롤 없음 (전 페이지)
   - [ ] 화면 어디에도 흰 배경 섹션 없음 (PDF 뷰어 내부 제외)
   - [ ] 지어낸 수치·인증 문구 없음 (grep으로 "%", "ISO", "인증" 검색해서 보고)
```

---

## 막혔을 때 붙여넣을 짧은 프롬프트

- 디자인이 시안(흰 배경)처럼 나올 때
  ```
  DESIGN.md를 다시 읽어라. 배경은 무조건 #000000이고 카드는 #0A0A0B/#111214/#17181B 밝기 단계로만 구분한다. 그림자 금지. 지금 화면에서 흰 배경·그림자·Space Grotesk를 쓰는 곳을 모두 찾아 고쳐라.
  ```
- 빌드할 때 "window is not defined" 같은 에러가 날 때
  ```
  프리렌더 중 브라우저 전용 코드가 실행된 것이다. window/document/localStorage 사용처를 전부 찾아 useEffect 안이나 ClientOnly 래퍼 안으로 옮겨라.
  ```
- localhost가 안 열릴 때
  ```
  npm run dev 터미널 출력 전체를 보여주고, 에러 원인을 찾아 고쳐라. 포트 5173이 사용 중이면 기존 프로세스를 종료하거나 다른 포트로 띄우고 URL을 알려줘라.
  ```
- 결과물을 확인하고 싶을 때
  ```
  내장 브라우저로 http://localhost:5173 의 모든 페이지를 데스크톱 1440px, 모바일 390px로 스크린샷 찍고, DESIGN.md와 다른 부분을 목록으로 보고해라. 고치기 전에 먼저 보고만.
  ```
