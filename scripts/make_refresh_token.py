#!/usr/bin/env python3
"""구글 OAuth 리프레시 토큰을 만든다 (서비스 계정 키를 못 만들 때 쓰는 우회로).

조직 정책 iam.disableServiceAccountKeyCreation 때문에 서비스 계정 키 생성이
막혀 있으면 이 방법을 쓴다. 은성님 계정 권한으로 드라이브를 읽고 쓴다.

준비:
  1. Google Cloud Console → API 및 서비스 → OAuth 동의 화면
     - User Type: 내부(Internal)  ← Workspace 조직이면 이걸 고른다.
       (외부/테스트로 두면 리프레시 토큰이 7일 만에 만료된다)
  2. 사용자 인증 정보 → 사용자 인증 정보 만들기 → OAuth 클라이언트 ID
     - 애플리케이션 유형: **데스크톱 앱**
     - 만들어진 클라이언트 ID / 보안 비밀번호를 아래 환경변수로 넣는다

실행:
    pip install -r requirements.txt
    GOOGLE_OAUTH_CLIENT_ID=xxx GOOGLE_OAUTH_CLIENT_SECRET=yyy \
        python scripts/make_refresh_token.py

브라우저가 열리고 로그인하면 리프레시 토큰이 화면에 찍힌다.
그 값을 깃허브 시크릿 GOOGLE_OAUTH_REFRESH_TOKEN 에 넣으면 끝.
"""

from __future__ import annotations

import os
import sys

SCOPES = ["https://www.googleapis.com/auth/drive"]


def main() -> int:
    client_id = os.environ.get("GOOGLE_OAUTH_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")
    if not (client_id and client_secret):
        print(
            "GOOGLE_OAUTH_CLIENT_ID 와 GOOGLE_OAUTH_CLIENT_SECRET 을 환경변수로 넣어주세요.\n"
            "구글 클라우드 콘솔 → 사용자 인증 정보 → OAuth 클라이언트 ID(데스크톱 앱)에서 받습니다.",
            file=sys.stderr,
        )
        return 1

    from google_auth_oauthlib.flow import InstalledAppFlow

    flow = InstalledAppFlow.from_client_config(
        {
            "installed": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost"],
            }
        },
        SCOPES,
    )
    # access_type=offline + prompt=consent 라야 리프레시 토큰이 나온다
    creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")

    if not creds.refresh_token:
        print("리프레시 토큰을 받지 못했습니다. 구글 계정의 앱 권한을 지우고 다시 시도하세요.", file=sys.stderr)
        return 1

    print("\n" + "=" * 70)
    print("깃허브 시크릿에 아래 3개를 넣으세요:")
    print("=" * 70)
    print(f"GOOGLE_OAUTH_CLIENT_ID     = {client_id}")
    print(f"GOOGLE_OAUTH_CLIENT_SECRET = {client_secret}")
    print(f"GOOGLE_OAUTH_REFRESH_TOKEN = {creds.refresh_token}")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
