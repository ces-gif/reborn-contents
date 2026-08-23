#!/usr/bin/env python3
"""구글 드라이브 연결 설치 마법사 (갈래 B — 내 계정 OAuth).

조직 정책 때문에 서비스 계정 키를 만들 수 없을 때 쓰는 방법을, 처음부터 끝까지
안내하고 검증까지 해준다. 은성님이 직접 하실 일은 딱 두 가지다:
  1. 브라우저에서 OAuth 클라이언트 만들고 값 2개 붙여넣기
  2. 구글 로그인 창에서 '허용' 누르기

나머지(콘솔 페이지 열기, 토큰 발급, 드라이브 연결 검증, 결과 파일 저장)는 이 스크립트가 한다.

실행:
    python scripts/setup_google.py
"""

from __future__ import annotations

import json
import sys
import webbrowser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

SCOPES = ["https://www.googleapis.com/auth/drive"]
REPO_SECRETS_URL = "https://github.com/ces-gif/reborn-contents/settings/secrets/actions/new"
CONSENT_URL = "https://console.cloud.google.com/auth/overview"
CREDENTIALS_URL = "https://console.cloud.google.com/apis/credentials"
DRIVE_API_URL = "https://console.cloud.google.com/apis/library/drive.googleapis.com"

OUT_FILE = Path("google-secrets.txt")
LOG_FILE = Path("setup-log.txt")


def _init_console() -> None:
    """윈도우 콘솔에서 한글이 깨지지 않게 한다."""
    if sys.platform != "win32":
        return
    try:  # 파이썬 3.7+ 는 콘솔에 UTF-8 로 쓸 수 있다
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    try:
        import ctypes

        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
        ctypes.windll.kernel32.SetConsoleCP(65001)
    except Exception:
        pass


def say(text: str = "") -> None:
    print(text, flush=True)


def rule(title: str = "") -> None:
    say()
    say("=" * 68)
    if title:
        say(title)
        say("=" * 68)


def pause(message: str) -> None:
    input(f"\n{message}\n  → 다 하셨으면 Enter: ")


def open_page(url: str, label: str) -> None:
    say(f"  브라우저를 엽니다: {label}")
    say(f"  ({url})")
    try:
        webbrowser.open(url)
    except Exception:
        say("  * 자동으로 안 열리면 위 주소를 직접 복사해서 여세요.")


def step_drive_api() -> None:
    rule("1/4 · 드라이브 API 켜기")
    say("구글 클라우드에서 Drive API 를 켜야 파이프라인이 드라이브를 읽고 쓸 수 있습니다.")
    open_page(DRIVE_API_URL, "Google Drive API")
    say()
    say("  · 버튼이 [사용] 이면 눌러서 켜주세요.")
    say("  · 이미 [관리] 로 보이면 켜져 있는 겁니다. 그냥 넘어가세요.")
    pause("Drive API 를 켰습니다.")


def step_consent_screen() -> None:
    rule("2/4 · OAuth 동의 화면을 '내부'로 설정")
    say("여기가 제일 중요합니다.")
    say()
    say("  ⚠️  User Type 을 반드시 [내부 / Internal] 로 고르세요.")
    say("      [외부 / External] 로 두면 리프레시 토큰이 7일 만에 만료돼서")
    say("      매주 이 작업을 다시 해야 합니다.")
    say()
    open_page(CONSENT_URL, "OAuth 동의 화면")
    pause("동의 화면을 '내부'로 설정했습니다.")


def step_client() -> tuple[str, str]:
    rule("3/4 · OAuth 클라이언트 ID 만들기")
    say("  · [사용자 인증 정보 만들기] → [OAuth 클라이언트 ID]")
    say("  · 애플리케이션 유형: [데스크톱 앱]  ← 반드시 데스크톱 앱")
    say("  · 이름은 아무거나 (예: reborn-desktop)")
    say()
    open_page(CREDENTIALS_URL, "사용자 인증 정보")
    say()
    say("만들고 나면 클라이언트 ID 와 보안 비밀번호가 화면에 뜹니다.")
    say("아래에 그대로 붙여넣어 주세요. (이 값은 이 컴퓨터 밖으로 나가지 않습니다)")
    say()

    client_id = input("  클라이언트 ID     : ").strip()
    client_secret = input("  클라이언트 보안 비밀번호 : ").strip()

    if not client_id or not client_secret:
        say("\n값이 비어 있습니다. 다시 실행해 주세요.")
        raise SystemExit(1)
    if not client_id.endswith(".apps.googleusercontent.com"):
        say("\n  ⚠️  클라이언트 ID 는 보통 '...apps.googleusercontent.com' 으로 끝납니다.")
        say("      잘못 붙여넣으신 게 아닌지 확인해 주세요.")
        if input("  그래도 계속할까요? (y/N): ").strip().lower() != "y":
            raise SystemExit(1)
    return client_id, client_secret


def _client_config(client_id: str, client_secret: str) -> dict:
    return {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"],
        }
    }


def _show_url(url: str) -> None:
    say()
    say("-" * 68)
    say("아래 주소를 브라우저 주소창에 복사해서 붙여넣으세요:")
    say("-" * 68)
    say(url)
    say("-" * 68)
    say()
    say("  복사하는 법: 위 주소를 마우스로 드래그해서 선택 → Enter (복사됨)")
    say("               브라우저 주소창에 Ctrl+V 로 붙여넣고 Enter")
    say()


def _manual_flow(config: dict):
    """브라우저 자동 실행이나 로컬 서버가 안 될 때 쓰는 수동 방식.

    구글이 http://localhost 로 돌려보내면 '페이지를 열 수 없음' 이 뜨는데,
    그때 **주소창의 주소 전체**를 복사해 오면 된다. 그 안에 인증 코드가 들어 있다.
    """
    from google_auth_oauthlib.flow import InstalledAppFlow

    flow = InstalledAppFlow.from_client_config(config, SCOPES)
    flow.redirect_uri = "http://localhost:8080/"
    url, _ = flow.authorization_url(access_type="offline", prompt="consent")

    say()
    say("  자동으로 창이 안 열려서 수동으로 진행합니다. 어렵지 않습니다.")
    _show_url(url)
    say("  로그인하고 [계속] 을 누르면 브라우저가")
    say("  'localhost 에서 연결을 거부했습니다' 같은 빈 페이지로 갑니다. 정상입니다!")
    say("  그 상태에서 **주소창의 주소 전체**를 복사해서 아래에 붙여넣어 주세요.")
    say("  (http://localhost:8080/?code=... 로 시작하는 긴 주소)")
    say()

    pasted = input("  주소 붙여넣기: ").strip()
    if not pasted.startswith("http"):
        raise RuntimeError("주소가 올바르지 않습니다. http://localhost:8080/?code=... 형태여야 합니다.")
    flow.fetch_token(authorization_response=pasted)
    return flow.credentials


def step_authorize(client_id: str, client_secret: str) -> str:
    rule("4/4 · 구글 로그인해서 권한 주기")
    say("브라우저가 열립니다. 리본마켓 드라이브를 쓰는 계정(ces@rebornmarket.org)으로")
    say("로그인하고 [계속] 을 눌러주세요.")
    say()
    say("  * '이 앱은 확인되지 않았습니다' 가 나오면")
    say("    [고급] → [(안전하지 않음) 이동] 을 누르시면 됩니다.")
    say("    은성님이 방금 직접 만든 앱이라 안전합니다.")
    pause("준비되셨으면 Enter 를 눌러 로그인 창을 엽니다.")

    from google_auth_oauthlib.flow import InstalledAppFlow

    config = _client_config(client_id, client_secret)
    creds = None
    try:
        flow = InstalledAppFlow.from_client_config(config, SCOPES)
        say()
        say("  브라우저를 여는 중입니다... (창이 뒤에 숨어 있을 수 있으니 Alt+Tab 확인)")
        say("  창이 안 뜨면 아래에 주소가 나옵니다. 그걸 복사해서 여세요.")
        creds = flow.run_local_server(
            port=0,
            access_type="offline",
            prompt="consent",
            authorization_prompt_message="\n주소: {url}\n",
            success_message="인증 완료! 이 창을 닫고 검은 마법사 창으로 돌아가세요.",
            open_browser=True,
        )
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        say()
        say(f"  자동 로그인이 안 됐습니다: {exc}")
        creds = _manual_flow(config)

    if not creds or not creds.refresh_token:
        say()
        say("  ✗ 리프레시 토큰을 받지 못했습니다.")
        say("    https://myaccount.google.com/permissions 에서 방금 만든 앱 권한을 지우고")
        say("    이 마법사를 다시 실행해 주세요.")
        raise SystemExit(1)
    return creds.refresh_token


def verify(client_id: str, client_secret: str, refresh_token: str) -> bool:
    """정말로 드라이브가 읽히는지, 발행 폴더에 쓸 수 있는지 확인한다."""
    rule("확인 · 드라이브에 실제로 연결되는지 검사")
    import os

    os.environ["GOOGLE_OAUTH_CLIENT_ID"] = client_id
    os.environ["GOOGLE_OAUTH_CLIENT_SECRET"] = client_secret
    os.environ["GOOGLE_OAUTH_REFRESH_TOKEN"] = refresh_token
    os.environ.pop("GOOGLE_SERVICE_ACCOUNT_JSON", None)

    from reborn.config import load_settings
    from reborn.drive import Drive

    settings = load_settings()
    drive = Drive()

    ok = True
    for source in settings.sources:
        try:
            files = drive.list_children(source.folder_id, only_images=True)
            say(f"  ✓ [{source.name}] 폴더 읽기 성공 — 사진 {len(files)}장")
        except Exception as exc:
            ok = False
            say(f"  ✗ [{source.name}] 폴더를 못 읽었습니다: {exc}")

    try:
        parent = settings.publish_parent_id or drive.get_parent(settings.sources[0].folder_id)
        folder = drive.ensure_folder(settings.publish_folder_name, parent)
        say(f"  ✓ '{settings.publish_folder_name}' 폴더 쓰기 권한 확인")
        say(f"    https://drive.google.com/drive/folders/{folder}")
    except Exception as exc:
        ok = False
        say(f"  ✗ 발행 폴더를 만들지 못했습니다: {exc}")

    try:
        from reborn import branding
        from reborn.pipeline import ensure_logo

        path = ensure_logo(drive, settings)
        say(f"  ✓ 리본마켓 로고 확인 — {path.name} ({path.stat().st_size:,} bytes)")
    except Exception as exc:
        ok = False
        say(f"  ✗ 로고를 가져오지 못했습니다: {exc}")

    return ok


def finish(client_id: str, client_secret: str, refresh_token: str) -> None:
    lines = [
        "리본마켓 콘텐츠 자동화 — 깃허브 시크릿",
        "",
        "아래 3개를 깃허브 저장소 시크릿으로 등록하세요.",
        "Settings → Secrets and variables → Actions → New repository secret",
        "",
        f"GOOGLE_OAUTH_CLIENT_ID\n{client_id}",
        "",
        f"GOOGLE_OAUTH_CLIENT_SECRET\n{client_secret}",
        "",
        f"GOOGLE_OAUTH_REFRESH_TOKEN\n{refresh_token}",
        "",
        "그리고 ANTHROPIC_API_KEY 도 하나 더 필요합니다.",
        "https://console.anthropic.com/ → API Keys → Create Key",
        "",
        "※ 이 파일에는 비밀값이 들어 있습니다. 등록이 끝나면 삭제하세요.",
        "※ 이 값은 절대 채팅창이나 남에게 붙여넣지 마세요.",
    ]
    OUT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")

    rule("완료")
    say(f"  값 3개를 {OUT_FILE.resolve()} 에 저장했습니다.")
    say()
    say("  이제 깃허브에 등록만 하면 끝입니다. 브라우저를 엽니다.")
    open_page(REPO_SECRETS_URL, "깃허브 시크릿 등록")
    say()
    say("  파일을 열어 이름/값을 하나씩 복사해 넣으세요 (3번 반복).")
    say("  등록이 끝나면 그 파일은 지우시면 됩니다.")
    say()
    say("  마지막으로 ANTHROPIC_API_KEY 도 같은 방법으로 넣어주세요.")
    say()
    say("  그다음 Actions 탭에서 워크플로를 한 번 돌려보시면 됩니다.")


def main() -> int:
    _init_console()
    rule("리본마켓 · 구글 드라이브 연결 설치 마법사")
    say("서비스 계정 키를 못 만드는 조직에서 쓰는 방법(내 계정 OAuth)으로 연결합니다.")
    say("총 4단계, 5분쯤 걸립니다.")

    step_drive_api()
    step_consent_screen()
    client_id, client_secret = step_client()
    refresh_token = step_authorize(client_id, client_secret)

    if not verify(client_id, client_secret, refresh_token):
        rule("연결 검사 실패")
        say("  위 ✗ 항목을 확인해 주세요. 흔한 원인:")
        say("   · Drive API 가 아직 안 켜졌다 (1단계)")
        say("   · 로그인한 계정이 그 폴더에 접근 권한이 없다")
        say("  고친 뒤 이 스크립트를 다시 실행하시면 됩니다.")
        return 1

    finish(client_id, client_secret, refresh_token)
    return 0


def _hold(code: int) -> int:
    """무슨 일이 있어도 창이 그냥 닫히지 않게 붙잡는다."""
    say()
    say("=" * 68)
    try:
        input("  이 창을 닫으려면 Enter 를 누르세요. ")
    except Exception:
        pass
    return code


if __name__ == "__main__":
    import traceback

    try:
        _code = main()
    except KeyboardInterrupt:
        say("\n중단했습니다.")
        _code = 130
    except SystemExit as exc:
        _code = int(exc.code or 0)
    except Exception:
        say()
        say("  ✗ 예상하지 못한 오류가 났습니다. 아래 내용을 그대로 알려주시면 고쳐드립니다.")
        say()
        say(traceback.format_exc())
        try:
            LOG_FILE.write_text(traceback.format_exc(), encoding="utf-8")
            say(f"  같은 내용을 {LOG_FILE.resolve()} 에도 저장했습니다.")
        except Exception:
            pass
        _code = 1
    raise SystemExit(_hold(_code))
