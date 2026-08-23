"""생성된 콘텐츠를 바깥으로 내보낸다.

카카오톡 오픈채팅방은 카카오가 '방에 글을 쓰는' 공개 API 를 제공하지 않는다.
(비즈니스용 알림톡/친구톡은 카카오 채널 대상이지 오픈채팅방 대상이 아니다.)
그래서 자동화는 이렇게 한다:

1. kakao  — 카카오톡 '나에게 보내기' API 로 은성님 카톡에 공지문 + 드라이브 링크를 보낸다.
             카톡에서 그 메시지를 오픈채팅방으로 '전달'하면 끝 (탭 두 번).
2. telegram / webhook (Slack·Discord 등) — 방을 그쪽으로 운영한다면 완전 자동 게시가 된다.

세 가지 다 환경변수가 있을 때만 동작하고, 실패해도 파이프라인을 멈추지 않는다.
"""

from __future__ import annotations

import logging
import os

import requests

log = logging.getLogger(__name__)

KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
KAKAO_MEMO_URL = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
TIMEOUT = 20


def _kakao_access_token() -> str | None:
    key = os.environ.get("KAKAO_REST_API_KEY")
    refresh = os.environ.get("KAKAO_REFRESH_TOKEN")
    if not (key and refresh):
        return None
    data = {"grant_type": "refresh_token", "client_id": key, "refresh_token": refresh}
    secret = os.environ.get("KAKAO_CLIENT_SECRET")
    if secret:
        data["client_secret"] = secret
    resp = requests.post(KAKAO_TOKEN_URL, data=data, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json().get("access_token")


def send_kakao(text: str, link_url: str | None = None) -> bool:
    """카카오톡 '나에게 보내기'. 오픈채팅방에는 전달 한 번으로 올릴 수 있다."""
    try:
        token = _kakao_access_token()
        if not token:
            return False
        template = {
            "object_type": "text",
            "text": text[:1000],
            "link": {"web_url": link_url or "", "mobile_web_url": link_url or ""},
            "button_title": "드라이브에서 카드뉴스 받기" if link_url else "",
        }
        resp = requests.post(
            KAKAO_MEMO_URL,
            headers={"Authorization": f"Bearer {token}"},
            data={"template_object": __import__("json").dumps(template, ensure_ascii=False)},
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        log.info("카카오톡 나에게 보내기 완료")
        return True
    except Exception as exc:
        log.warning("카카오톡 전송 실패(무시하고 계속): %s", exc)
        return False


def send_telegram(text: str) -> bool:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not (token and chat_id):
        return False
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": text[:4000], "disable_web_page_preview": False},
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        log.info("텔레그램 전송 완료")
        return True
    except Exception as exc:
        log.warning("텔레그램 전송 실패(무시하고 계속): %s", exc)
        return False


def send_webhook(text: str) -> bool:
    """Slack / Discord / 자체 서버 웹훅. Discord 는 content, 그 외는 text 키를 쓴다."""
    url = os.environ.get("NOTIFY_WEBHOOK_URL")
    if not url:
        return False
    payload = {"content": text[:1900]} if "discord.com" in url else {"text": text[:3000]}
    try:
        resp = requests.post(url, json=payload, timeout=TIMEOUT)
        resp.raise_for_status()
        log.info("웹훅 전송 완료")
        return True
    except Exception as exc:
        log.warning("웹훅 전송 실패(무시하고 계속): %s", exc)
        return False


def broadcast(text: str, link_url: str | None = None) -> dict[str, bool]:
    body = text if not link_url else f"{text}\n\n{link_url}"
    return {
        "kakao": send_kakao(text, link_url),
        "telegram": send_telegram(body),
        "webhook": send_webhook(body),
    }
