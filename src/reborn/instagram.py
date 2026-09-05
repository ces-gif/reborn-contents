"""인스타그램 자동 게시 — 스토리 + 피드 게시물 (Instagram Graph API).

흐름은 메타가 정한 3단계다:
  1. 이미지를 공개 URL 로 올린다 (imagehost.py)
  2. POST /{ig_user_id}/media       → 컨테이너 id
  3. POST /{ig_user_id}/media_publish with creation_id=컨테이너 id → 게시

스토리는 카드 한 장이 곧 한 건이고, 피드에는 그날 카드를 이어 붙인 **릴스 한 편**을
올린다. 카드가 이미 1080x1920(9:16)이라 릴스 규격에 그대로 맞는다 — 피드 캐러셀은
4:5 까지만 받아서 가격이 잘린다.

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
# 릴스는 영상 인코딩이 끝날 때까지 시간이 걸린다 — 사진보다 넉넉히 기다린다.
REEL_POLL_SECONDS = 5
REEL_MAX_POLLS = 60
# 캡션은 2200자까지. 넘으면 게시 자체가 거부된다.
CAPTION_MAX = 2200


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


# ---------------------------------------------------------------- 릴스
@dataclass
class ReelReport:
    ok: bool = False
    media_id: str = ""
    video: Path | None = None
    card_count: int = 0
    skipped_reason: str = ""
    error: str = ""


def trim_caption(caption: str, limit: int = CAPTION_MAX) -> str:
    """캡션을 인스타 한도 안으로 줄인다. 줄 단위로 잘라 문장이 끊기지 않게."""
    text = (caption or "").strip()
    if len(text) <= limit:
        return text
    kept: list[str] = []
    used = 0
    for line in text.split("\n"):
        if used + len(line) + 1 > limit - 1:
            break
        kept.append(line)
        used += len(line) + 1
    return ("\n".join(kept).rstrip() + "…")[:limit]


def _wait_for_video(container_id: str, token: str) -> None:
    """릴스 컨테이너가 FINISHED 될 때까지 기다린다 (영상은 사진보다 오래 걸린다)."""
    for _ in range(REEL_MAX_POLLS):
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
            raise RuntimeError(f"릴스 처리 실패: {payload.get('status', '(사유 없음)')}")
        time.sleep(REEL_POLL_SECONDS)
    raise RuntimeError("릴스가 준비되지 않았습니다 (시간 초과)")


def publish_reel(video_url: str, caption: str, *, cover_url: str = "") -> str:
    """공개 MP4 URL 을 릴스로 게시하고 media id 를 돌려준다."""
    user_id, token = _credentials()
    fields = {
        "media_type": "REELS",
        "video_url": video_url,
        "caption": trim_caption(caption),
        # 릴스를 프로필 피드에도 남긴다 (안 켜면 릴스 탭에만 남는다)
        "share_to_feed": "true",
        "access_token": token,
    }
    if cover_url:
        fields["cover_url"] = cover_url

    payload = _post(f"{GRAPH}/{user_id}/media", fields)
    container_id = payload.get("id")
    if not container_id:
        raise RuntimeError(f"릴스 컨테이너 id 를 받지 못했습니다: {payload}")

    _wait_for_video(container_id, token)

    published = _post(
        f"{GRAPH}/{user_id}/media_publish",
        {"creation_id": container_id, "access_token": token},
    )
    media_id = published.get("id", "")
    log.info("인스타 릴스 게시 완료: media_id=%s", media_id)
    return media_id


def publish_reel_video(
    video: Path,
    *,
    caption: str,
    key_prefix: str,
    cover: Path | None = None,
) -> ReelReport:
    """이미 만들어 둔 릴스 영상을 올린다.

    영상 만드는 일은 pipeline 이 먼저 해 둔다 — 인스타 설정이 없는 날에도
    드라이브에는 영상이 남아야 손으로라도 올릴 수 있기 때문이다.
    """
    from . import imagehost

    report = ReelReport(video=video)

    if not video or not video.exists():
        report.skipped_reason = "올릴 영상이 없습니다"
        return report
    if not is_configured():
        report.skipped_reason = "인스타 계정 정보(IG_USER_ID/IG_ACCESS_TOKEN)가 없어 건너뜁니다"
        log.info(report.skipped_reason)
        return report
    if not imagehost.is_configured():
        report.skipped_reason = (
            "영상 공개 호스팅(R2_*)이 설정되지 않아 건너뜁니다 — "
            "인스타그램은 공개 URL 만 받습니다"
        )
        log.warning(report.skipped_reason)
        return report

    try:
        video_url = imagehost.upload_public(video, f"{key_prefix}/{video.name}")
        cover_url = (
            imagehost.upload_public(cover, f"{key_prefix}/{cover.name}")
            if cover and cover.exists()
            else ""
        )
        report.media_id = publish_reel(video_url, caption, cover_url=cover_url)
        report.ok = True
    except Exception as exc:
        log.warning("릴스 게시 실패: %s", exc)
        report.error = str(exc)

    return report
