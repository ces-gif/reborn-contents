"""인스타그램 스토리 자동 게시 (Instagram Graph API).

흐름은 메타가 정한 3단계다:
  1. 이미지를 공개 URL 로 올린다 (imagehost.py)
  2. POST /{ig_user_id}/media  with media_type=STORIES, image_url=...   → 컨테이너 id
  3. POST /{ig_user_id}/media_publish with creation_id=컨테이너 id      → 게시

필요한 것 (docs/SETUP.md 5단계):
  - 인스타그램 **비즈니스/크리에이터** 계정 + 연결된 페이스북 페이지
  - 메타 개발자 앱 + instagram_basic, instagram_content_publish 권한
  - 장기 액세스 토큰 (IG_ACCESS_TOKEN)

제한: 계정당 24시간에 25건 (스토리·릴스 합산). 그래서 settings.yaml 에서 하루 장수를 막아둔다.
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path

import requests

log = logging.getLogger(__name__)

GRAPH = "https://graph.facebook.com/v21.0"
TIMEOUT = 60
# 컨테이너가 준비될 때까지 기다린다 (이미지는 보통 몇 초면 끝난다)
STATUS_POLL_SECONDS = 3
STATUS_MAX_POLLS = 20


class InstagramNotConfigured(RuntimeError):
    pass


@dataclass
class StoryResult:
    card: Path
    ok: bool
    media_id: str = ""
    url: str = ""
    error: str = ""


@dataclass
class PublishReport:
    results: list[StoryResult] = field(default_factory=list)
    skipped_reason: str = ""

    @property
    def published(self) -> list[StoryResult]:
        return [r for r in self.results if r.ok]

    @property
    def failed(self) -> list[StoryResult]:
        return [r for r in self.results if not r.ok]


def is_configured() -> bool:
    return bool(os.environ.get("IG_USER_ID") and os.environ.get("IG_ACCESS_TOKEN"))


def _credentials() -> tuple[str, str]:
    user_id = os.environ.get("IG_USER_ID")
    token = os.environ.get("IG_ACCESS_TOKEN")
    if not (user_id and token):
        raise InstagramNotConfigured(
            "IG_USER_ID / IG_ACCESS_TOKEN 이 없습니다. (docs/SETUP.md 5단계 참고)"
        )
    return user_id, token


def _post(url: str, data: dict) -> dict:
    response = requests.post(url, data=data, timeout=TIMEOUT)
    payload = response.json() if response.content else {}
    if response.status_code >= 400:
        message = (payload.get("error") or {}).get("message", response.text[:300])
        raise RuntimeError(f"인스타그램 API 오류 {response.status_code}: {message}")
    return payload


def _wait_until_ready(container_id: str, token: str) -> None:
    """컨테이너가 FINISHED 가 될 때까지 기다린다. ERROR 면 예외."""
    for _ in range(STATUS_MAX_POLLS):
        response = requests.get(
            f"{GRAPH}/{container_id}",
            params={"fields": "status_code,status", "access_token": token},
            timeout=TIMEOUT,
        )
        payload = response.json() if response.content else {}
        status = payload.get("status_code")
        if status == "FINISHED":
            return
        if status == "ERROR":
            raise RuntimeError(f"컨테이너 처리 실패: {payload.get('status', '(사유 없음)')}")
        time.sleep(STATUS_POLL_SECONDS)
    raise RuntimeError("컨테이너가 준비되지 않았습니다 (시간 초과)")


def publish_story(image_url: str) -> str:
    """공개 이미지 URL 을 스토리로 게시하고 media id 를 돌려준다."""
    user_id, token = _credentials()

    container = _post(
        f"{GRAPH}/{user_id}/media",
        {"media_type": "STORIES", "image_url": image_url, "access_token": token},
    )
    container_id = container.get("id")
    if not container_id:
        raise RuntimeError(f"컨테이너 id 를 받지 못했습니다: {container}")

    _wait_until_ready(container_id, token)

    published = _post(
        f"{GRAPH}/{user_id}/media_publish",
        {"creation_id": container_id, "access_token": token},
    )
    media_id = published.get("id", "")
    log.info("인스타 스토리 게시 완료: media_id=%s", media_id)
    return media_id


def publish_cards(
    cards: list[Path],
    *,
    key_prefix: str,
    max_stories: int = 10,
    delay_seconds: int = 20,
) -> PublishReport:
    """카드뉴스 PNG 들을 공개 URL 로 올린 뒤 스토리로 순서대로 게시한다.

    한 장이 실패해도 나머지는 계속 시도한다. 설정이 없으면 그냥 건너뛴다.
    """
    from . import imagehost

    report = PublishReport()

    if not is_configured():
        report.skipped_reason = "인스타 계정 정보(IG_USER_ID/IG_ACCESS_TOKEN)가 없어 건너뜁니다"
        log.info(report.skipped_reason)
        return report
    if not imagehost.is_configured():
        report.skipped_reason = (
            "이미지 공개 호스팅(R2_*)이 설정되지 않아 건너뜁니다 — "
            "인스타그램은 공개 URL 만 받습니다"
        )
        log.warning(report.skipped_reason)
        return report

    targets = cards[:max_stories]
    if len(cards) > len(targets):
        log.warning(
            "카드 %d장 중 %d장만 스토리로 올립니다 (인스타 24시간 25건 제한 때문에 제한해 둠)",
            len(cards),
            len(targets),
        )

    for i, card in enumerate(targets):
        try:
            url = imagehost.upload_public(card, f"{key_prefix}/{card.name}")
            media_id = publish_story(url)
            report.results.append(StoryResult(card=card, ok=True, media_id=media_id, url=url))
        except Exception as exc:
            log.warning("스토리 게시 실패 (%s): %s", card.name, exc)
            report.results.append(StoryResult(card=card, ok=False, error=str(exc)))
        if i < len(targets) - 1 and delay_seconds:
            time.sleep(delay_seconds)

    return report
