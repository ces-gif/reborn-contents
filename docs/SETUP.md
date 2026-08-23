# 최초 설정 (한 번만 하면 됩니다)

전체 20~30분 정도 걸립니다. 순서대로 따라오시면 됩니다.

- [1. 구글 드라이브 접근 권한 만들기](#1-구글-드라이브-접근-권한-만들기)
- [2. Anthropic API 키 만들기](#2-anthropic-api-키-만들기)
- [3. 깃허브에 비밀값 넣기](#3-깃허브에-비밀값-넣기)
- [4. 첫 실행 확인](#4-첫-실행-확인)
- [5. 인스타그램 스토리 자동 게시](#5-인스타그램-스토리-자동-게시)
- [6. (선택) 카카오톡 자동 전송](#6-선택-카카오톡-자동-전송)
- [7. (선택) 텔레그램 · 슬랙 · 디스코드로 완전 자동 게시](#7-선택-텔레그램--슬랙--디스코드로-완전-자동-게시)
- [네이버 블로그는 왜 자동이 안 되나](#네이버-블로그는-왜-자동이-안-되나)
- [자주 겪는 문제](#자주-겪는-문제)

---

## 1. 구글 드라이브 접근 권한 만들기

깃허브 서버가 은성님 대신 드라이브를 읽고 쓰려면 **서비스 계정**이 필요합니다.
사람이 로그인할 필요가 없어서 매일 자동 실행에 가장 잘 맞습니다.

1. <https://console.cloud.google.com/> 접속 → 상단에서 **새 프로젝트** 만들기
   (이름 예: `reborn-contents`)
2. 좌측 메뉴 **API 및 서비스 → 라이브러리** → `Google Drive API` 검색 → **사용 설정**
3. **API 및 서비스 → 사용자 인증 정보 → 사용자 인증 정보 만들기 → 서비스 계정**
   - 이름: `reborn-bot` (아무거나)
   - 역할은 지정하지 않아도 됩니다 → **완료**
4. 만들어진 서비스 계정 클릭 → **키** 탭 → **키 추가 → 새 키 만들기 → JSON** → 파일이 다운로드됩니다
5. 그 JSON 파일을 메모장으로 열면 `"client_email": "reborn-bot@....iam.gserviceaccount.com"`
   같은 줄이 있습니다. **이 이메일 주소를 복사**하세요.
6. 드라이브에서 **`입고상품` 폴더 하나만** 이 이메일에 **편집자**로 공유하면 됩니다.
   (우클릭 → 공유 → 위 이메일 붙여넣기 → 편집자)
   그 안의 `리퍼`, `새상품`, `리본마켓로고.png`, `콘텐츠 발행` 이 전부 함께 공유됩니다.

> **서비스 계정에는 저장 용량이 없습니다.** 위 5~6번처럼 *은성님 폴더에 편집자로 초대*해야
> 그 폴더 안에 파일을 만들 수 있습니다. 폴더 공유를 빼먹으면 업로드가 실패합니다.

<details>
<summary>서비스 계정 대신 내 계정(OAuth)으로 하고 싶다면</summary>

`GOOGLE_OAUTH_CLIENT_ID` / `GOOGLE_OAUTH_CLIENT_SECRET` / `GOOGLE_OAUTH_REFRESH_TOKEN`
세 개를 넣으면 그 계정 권한으로 동작합니다. 리프레시 토큰은
[OAuth 2.0 Playground](https://developers.google.com/oauthplayground/)에서
`https://www.googleapis.com/auth/drive` 범위로 발급받을 수 있습니다.
(서비스 계정이 있으면 그쪽이 우선 사용됩니다.)
</details>

## 2. Anthropic API 키 만들기

사진 속 가격표를 읽고, 상품을 인터넷에서 찾아보고, 블로그 글을 쓰는 데 씁니다.
**웹 검색은 Claude API 에 포함된 기능이라 검색용 API 키를 따로 만들 필요가 없습니다.**

1. <https://console.anthropic.com/> 로그인 → **API Keys → Create Key**
2. `sk-ant-...` 로 시작하는 키를 복사 (창을 닫으면 다시 못 봅니다)
3. **Billing** 에서 결제 수단을 등록하고 소액 충전

> 하루 비용 감각: 상품 10개 기준 사진 판독 + 블로그 1편이면 대략 몇백 원 수준입니다.
> `config/settings.yaml` 의 `model.vision` 을 `claude-haiku-4-5-20251001` 로 바꾸면 더 저렴해지고,
> `model.writing` 을 `claude-sonnet-5` 로 바꾸면 블로그 비용이 줄어듭니다.

## 3. 깃허브에 비밀값 넣기

저장소 → **Settings → Secrets and variables → Actions → New repository secret**

| 이름 | 값 | 필수 |
| --- | --- | --- |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | 1단계에서 받은 JSON 파일 **내용 전체** 붙여넣기 | ✅ |
| `ANTHROPIC_API_KEY` | 2단계 `sk-ant-...` 키 | ✅ |
| `IG_USER_ID` / `IG_ACCESS_TOKEN` | 5단계 — 인스타 스토리 자동 게시 | 선택 |
| `R2_ACCOUNT_ID` / `R2_ACCESS_KEY_ID` / `R2_SECRET_ACCESS_KEY` / `R2_BUCKET` / `R2_PUBLIC_BASE_URL` | 5단계 — 카드뉴스 공개 URL | 인스타 쓰면 필수 |
| `KAKAO_REST_API_KEY` | 6단계 참고 | 선택 |
| `KAKAO_REFRESH_TOKEN` | 6단계 참고 | 선택 |
| `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` | 7단계 참고 | 선택 |
| `NOTIFY_WEBHOOK_URL` | 슬랙/디스코드 웹훅 주소 | 선택 |

매장명이나 하루 장수를 바꾸고 싶으면 같은 화면의 **Variables** 탭에
`PUBLISH_FOLDER_NAME`, `LOGO_FILE_ID`, `STORE_NAME`, `MAX_CARDS_PER_DAY`,
`INSTAGRAM_ENABLED`, `MAX_STORIES_PER_DAY` 를 넣으면 됩니다.
상품 사진 폴더 목록은 `config/settings.yaml` 의 `drive.sources` 에서 바꿉니다.

## 4. 첫 실행 확인

자동 실행은 매일 03:00 UTC = **한국시간 낮 12시** 입니다 (오전 11:30까지 올린 사진이 대상).
기다리지 말고 바로 한번 돌려보세요.

저장소 → **Actions → "매일 카드뉴스 + BEST5 블로그" → Run workflow**

- `date`: 사진이 확실히 올라와 있는 날짜 (예: `2026-08-21`)
- `dry_run`: 처음엔 **체크** — 드라이브에 올리지 않고 결과만 확인
- 실행이 끝나면 아래 **Artifacts** 에서 `reborn-contents-N.zip` 을 받아 카드뉴스를 눈으로 확인

문제 없으면 `dry_run` 없이 다시 한 번 돌려서 드라이브 업로드까지 확인합니다.

> 자동 실행 시각을 바꾸려면 `.github/workflows/daily-content.yml` 의 `cron: "0 3 * * *"` 을 고칩니다.
> **cron 은 UTC 기준**이라 한국시간에서 9시간을 빼면 됩니다 (12:00 KST → 03:00 UTC).

## 5. 인스타그램 스토리 자동 게시

카드뉴스가 만들어지면 **손 안 대고 인스타 스토리로 올라갑니다.** 두 가지가 필요합니다.

### 5-1. 인스타그램 쪽 (IG_USER_ID / IG_ACCESS_TOKEN)

1. 인스타그램 앱 → 설정 → 계정 유형 → **프로페셔널 계정(비즈니스)** 으로 전환
2. 그 계정을 **페이스북 페이지에 연결** (인스타 설정 → 페이지 연결). 페이지가 없으면 새로 만듭니다.
3. <https://developers.facebook.com/> → **내 앱 → 앱 만들기 → 비즈니스**
4. 앱에 **Instagram Graph API** 제품 추가
5. **그래프 API 탐색기**(Graph API Explorer)에서 권한 `instagram_basic`, `instagram_content_publish`,
   `pages_show_list`, `pages_read_engagement` 를 체크하고 토큰 생성
6. **장기 토큰으로 교환** (단기 토큰은 1~2시간이면 만료됩니다):
   ```bash
   curl -G "https://graph.facebook.com/v21.0/oauth/access_token" \
     -d grant_type=fb_exchange_token \
     -d client_id=앱ID -d client_secret=앱시크릿 \
     -d fb_exchange_token=방금_받은_단기토큰
   ```
   나온 값 → 깃허브 시크릿 `IG_ACCESS_TOKEN`
7. 인스타 계정 ID 확인:
   ```bash
   curl -G "https://graph.facebook.com/v21.0/me/accounts" -d access_token=장기토큰
   # 나온 페이지 id 로 ↓
   curl -G "https://graph.facebook.com/v21.0/페이지ID" \
     -d fields=instagram_business_account -d access_token=장기토큰
   ```
   `instagram_business_account.id` → 깃허브 시크릿 `IG_USER_ID`
8. 앱을 **라이브 모드**로 전환하고 앱 검수(App Review)를 신청합니다.
   개발 모드에서는 앱에 등록된 테스트 계정에만 게시됩니다.

> **한도**: 인스타 API 는 계정당 **24시간에 25건**입니다(스토리·릴스 합산).
> `settings.yaml` 의 `instagram.max_stories_per_day` 가 기본 10으로 막아둡니다.

### 5-2. 카드뉴스를 올려둘 공개 주소 (R2_*)

인스타 API 는 파일 업로드를 안 받고 **공개된 이미지 URL** 만 받습니다.
구글 드라이브 링크는 바이러스 검사 안내 페이지 때문에 인스타가 못 읽는 경우가 많아서,
Cloudflare R2(무료 등급 있음)에 올려 그 주소를 씁니다.

1. <https://dash.cloudflare.com/> → **R2** → **Create bucket** (이름 예: `reborn-cards`)
2. 버킷 → **Settings → Public access → R2.dev subdomain → Allow**
   → `https://pub-xxxxxxxx.r2.dev` 주소가 생깁니다 → 시크릿 `R2_PUBLIC_BASE_URL`
3. R2 첫 화면 → **Manage API tokens → Create API token** → 권한 **Object Read & Write**
   → Access Key ID / Secret Access Key → 시크릿 `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`
4. R2 화면 우측의 **Account ID** → 시크릿 `R2_ACCOUNT_ID`
5. 버킷 이름 → 시크릿 `R2_BUCKET`

> AWS S3 나 MinIO 를 이미 쓰신다면 `R2_ENDPOINT` 에 그 주소를 넣으면 그대로 동작합니다.

**둘 중 하나라도 설정이 없으면** 인스타 게시만 조용히 건너뛰고,
카드뉴스·블로그·드라이브 업로드는 평소대로 다 끝납니다.

## 6. (선택) 카카오톡 자동 전송

> **먼저 알아두실 것**: 카카오는 **오픈채팅방에 글을 쓰는 공개 API 를 제공하지 않습니다.**
> (비즈니스용 알림톡·친구톡은 *카카오 채널* 친구에게 보내는 것이지 오픈채팅방이 아닙니다.)
> 그래서 여기서는 **은성님 카카오톡으로 공지문과 드라이브 링크를 자동 발송**합니다.
> 카톡에서 그 메시지를 길게 눌러 오픈채팅방으로 **전달**하면 끝입니다 (탭 두 번).
> 오픈채팅방 게시까지 완전 자동으로 하려면 6단계(텔레그램 등)로 방을 옮기는 방법뿐입니다.

1. <https://developers.kakao.com/> 로그인 → **내 애플리케이션 → 애플리케이션 추가하기**
2. **앱 키** 화면의 `REST API 키` → 깃허브 시크릿 `KAKAO_REST_API_KEY`
3. **카카오 로그인** 메뉴 → 활성화 ON, Redirect URI 에 `https://localhost` 추가
4. **동의항목** → `카카오톡 메시지 전송(talk_message)` 을 **필수 동의**로 설정
5. 브라우저 주소창에 아래를 넣고 접속 → 동의하면 `https://localhost/?code=XXXX` 로 이동합니다.
   주소창의 `code=` 뒤 값을 복사하세요.
   ```
   https://kauth.kakao.com/oauth/authorize?client_id=REST_API_키&redirect_uri=https://localhost&response_type=code&scope=talk_message
   ```
6. 터미널에서 리프레시 토큰을 받습니다.
   ```bash
   curl -X POST https://kauth.kakao.com/oauth/token \
     -d grant_type=authorization_code \
     -d client_id=REST_API_키 \
     -d redirect_uri=https://localhost \
     -d code=5단계에서_복사한_코드
   ```
   결과 JSON 의 `refresh_token` → 깃허브 시크릿 `KAKAO_REFRESH_TOKEN`

## 7. (선택) 텔레그램 · 슬랙 · 디스코드로 완전 자동 게시

이쪽은 API 가 열려 있어서 **사람 손 없이 방에 바로 올라갑니다.**

**텔레그램**
1. 카톡처럼 텔레그램에서 `@BotFather` 에게 `/newbot` → 토큰 발급 → `TELEGRAM_BOT_TOKEN`
2. 공지방을 만들고 봇을 초대 → 방에 아무 메시지나 쓴 뒤
   `https://api.telegram.org/bot<토큰>/getUpdates` 접속 → `chat.id` 확인 → `TELEGRAM_CHAT_ID`

**슬랙 / 디스코드**
채널 설정에서 **Incoming Webhook** 주소를 만들어 `NOTIFY_WEBHOOK_URL` 에 넣으면 됩니다.

---

## 네이버 블로그는 왜 자동이 안 되나

**네이버가 블로그 글쓰기 오픈 API 를 종료했습니다.**
네이버 개발자센터 공지 [블로그 오픈 API 종료 안내](https://developers.naver.com/notice/article/7527)에
"네이버 이용약관과 게시물 운영정책을 위반하는 행위가 발견되어 종료를 결정했다"고 명시돼 있고,
대체 공개 API 는 없습니다.

계정 비밀번호로 자동 로그인해서 글을 쓰는 방식(브라우저 자동화)은
네이버 이용약관 위반이고 캡차·2단계 인증에 계속 막히기 때문에 만들지 않았습니다.

**그래서 이렇게 합니다** — 매일 `블로그/YYYY-MM-DD-best5-blog.html` 이 만들어집니다.
브라우저로 열고 → `Ctrl+A` 전체 선택 → `Ctrl+C` → 네이버 블로그 글쓰기 화면에 `Ctrl+V`.
글자크기 19, 소제목 볼드, 번호 목록, 비교표가 서식 그대로 들어갑니다. 30초면 끝납니다.

> 혹시 블로그 관리 화면에 **'메일로 글쓰기'** 설정이 보이면 알려주세요.
> 그 주소가 있으면 메일 발송으로 완전 자동화할 수 있습니다 (현재 제공 여부를 확인하지 못했습니다).

---

## 자주 겪는 문제

**"오늘 새로 올라온 상품 사진이 없습니다"**
그날 드라이브에 올라온 사진이 없거나, 이미 처리한 사진뿐입니다.
날짜 기준은 **드라이브 업로드 시각(한국시간)** 입니다 — 며칠 전에 찍은 사진이라도 오늘 올리면 오늘 것으로 봅니다.
같은 사진을 일부러 다시 만들려면 `reprocess` 를 체크하고 실행하세요.

**로고를 찾을 수 없다며 멈춤**
서비스 계정에 로고 파일이 공유되지 않았거나 `LOGO_FILE_ID` 가 틀린 경우입니다.
로고 없이 카드를 만들면 브랜딩이 깨지므로 일부러 멈춥니다.
급하면 로고 PNG 를 `assets/reborn_logo.png` 로 직접 커밋해도 됩니다.

**업로드가 403 으로 실패**
`콘텐츠 발행` 폴더를 만들 상위 폴더가 서비스 계정에 **편집자**로 공유되지 않았습니다 (1단계 6번).

**"상품이 보이는 사진이 없습니다"로 넘어감**
그 묶음에 가격표 사진만 있는 경우입니다. 의도된 동작입니다 —
가격표만 찍힌 건 정보 전달용으로 보고 카드뉴스를 만들지 않습니다.
카드뉴스가 필요한 상품이면 상품이 보이는 사진을 한 장 더 올려주세요.

**제품 설명이 비어 있음**
인터넷 검색으로 그 모델을 특정하지 못한 경우입니다. 틀린 스펙을 붙이지 않으려고 일부러 비웁니다.
가격표에 모델명이 정확히 적혀 있으면 특정 확률이 올라갑니다.

**가격이 비어 있고 "확인 필요"로 넘어감**
사진에 가격표가 안 찍혔거나 흐려서 못 읽은 경우입니다. 가격을 지어내지 않도록 일부러 막아둔 동작입니다.
가격표가 잘 보이게 한 장 더 찍어서 올리고 다시 실행하면 됩니다.

**인스타 스토리가 안 올라감**
`_data/리포트.md` 의 "인스타 스토리" 줄에 이유가 적혀 있습니다.
계정 정보(IG_*)가 없거나, 공개 호스팅(R2_*)이 없거나, 앱이 아직 개발 모드인 경우가 대부분입니다.
토큰은 장기 토큰이라도 약 60일마다 갱신해야 합니다.

**카드가 너무 많이 만들어짐**
Variables 에 `MAX_CARDS_PER_DAY` 를 `8` 처럼 넣으면 그날 앞쪽 상품 8개까지만 만듭니다.

**상품이 잘못 묶임 (두 상품이 한 장에 / 한 상품이 두 장에)**
`MAX_GAP_SECONDS` 로 조절합니다. 상품 사이 이동이 빠르면 값을 줄이고(예: 90),
한 상품을 오래 찍는 편이면 늘리세요(예: 240).
