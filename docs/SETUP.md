# 최초 설정 (한 번만 하면 됩니다)

전체 20~30분 정도 걸립니다. 순서대로 따라오시면 됩니다.

- [1. 구글 드라이브 접근 권한 만들기](#1-구글-드라이브-접근-권한-만들기)
- [2. Anthropic API 키 만들기](#2-anthropic-api-키-만들기)
- [3. 깃허브에 비밀값 넣기](#3-깃허브에-비밀값-넣기)
- [4. 첫 실행 확인](#4-첫-실행-확인)
- [5. (선택) 카카오톡 자동 전송](#5-선택-카카오톡-자동-전송)
- [6. (선택) 텔레그램 · 슬랙 · 디스코드로 완전 자동 게시](#6-선택-텔레그램--슬랙--디스코드로-완전-자동-게시)
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
6. 드라이브에서 아래 두 가지를 이 이메일에 **공유**합니다.
   - **상품 사진 폴더** → 우클릭 → 공유 → 위 이메일 붙여넣기 → **뷰어**
   - **`콘텐츠 발행` 폴더를 만들 상위 폴더**(보통 내 드라이브의 상품 사진 폴더와 같은 위치)
     → 공유 → 같은 이메일 → **편집자**
   - **리본마켓 로고 PNG 파일** → 공유 → 같은 이메일 → **뷰어**

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

사진 속 가격표를 읽고 블로그 글을 쓰는 데 씁니다.

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
| `KAKAO_REST_API_KEY` | 5단계 참고 | 선택 |
| `KAKAO_REFRESH_TOKEN` | 5단계 참고 | 선택 |
| `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` | 6단계 참고 | 선택 |
| `NOTIFY_WEBHOOK_URL` | 슬랙/디스코드 웹훅 주소 | 선택 |

폴더 ID나 매장명을 바꾸고 싶으면 같은 화면의 **Variables** 탭에
`SOURCE_FOLDER_ID`, `PUBLISH_FOLDER_NAME`, `LOGO_FILE_ID`, `STORE_NAME`,
`MAX_CARDS_PER_DAY` 를 넣으면 됩니다. (안 넣으면 `config/settings.yaml` 값이 쓰입니다.)

## 4. 첫 실행 확인

자동 실행은 매일 09:00 UTC = **한국시간 18:00** 입니다.
기다리지 말고 바로 한번 돌려보세요.

저장소 → **Actions → "매일 카드뉴스 + BEST5 블로그" → Run workflow**

- `date`: 사진이 확실히 올라와 있는 날짜 (예: `2026-08-21`)
- `dry_run`: 처음엔 **체크** — 드라이브에 올리지 않고 결과만 확인
- 실행이 끝나면 아래 **Artifacts** 에서 `reborn-contents-N.zip` 을 받아 카드뉴스를 눈으로 확인

문제 없으면 `dry_run` 없이 다시 한 번 돌려서 드라이브 업로드까지 확인합니다.

> 자동 실행 시각을 바꾸려면 `.github/workflows/daily-content.yml` 의 `cron: "0 9 * * *"` 을 고칩니다.
> **cron 은 UTC 기준**이라 한국시간에서 9시간을 빼면 됩니다 (18:00 KST → 09:00 UTC).

## 5. (선택) 카카오톡 자동 전송

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

## 6. (선택) 텔레그램 · 슬랙 · 디스코드로 완전 자동 게시

이쪽은 API 가 열려 있어서 **사람 손 없이 방에 바로 올라갑니다.**

**텔레그램**
1. 카톡처럼 텔레그램에서 `@BotFather` 에게 `/newbot` → 토큰 발급 → `TELEGRAM_BOT_TOKEN`
2. 공지방을 만들고 봇을 초대 → 방에 아무 메시지나 쓴 뒤
   `https://api.telegram.org/bot<토큰>/getUpdates` 접속 → `chat.id` 확인 → `TELEGRAM_CHAT_ID`

**슬랙 / 디스코드**
채널 설정에서 **Incoming Webhook** 주소를 만들어 `NOTIFY_WEBHOOK_URL` 에 넣으면 됩니다.

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

**가격이 비어 있고 "확인 필요"로 넘어감**
사진에 가격표가 안 찍혔거나 흐려서 못 읽은 경우입니다. 가격을 지어내지 않도록 일부러 막아둔 동작입니다.
가격표가 잘 보이게 한 장 더 찍어서 올리고 다시 실행하면 됩니다.

**카드가 너무 많이 만들어짐**
Variables 에 `MAX_CARDS_PER_DAY` 를 `8` 처럼 넣으면 그날 앞쪽 상품 8개까지만 만듭니다.

**상품이 잘못 묶임 (두 상품이 한 장에 / 한 상품이 두 장에)**
`MAX_GAP_SECONDS` 로 조절합니다. 상품 사이 이동이 빠르면 값을 줄이고(예: 90),
한 상품을 오래 찍는 편이면 늘리세요(예: 240).
