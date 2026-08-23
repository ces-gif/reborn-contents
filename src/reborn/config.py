"""설정 로딩. config/settings.yaml 을 읽고 환경변수로 덮어쓴다."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SETTINGS = REPO_ROOT / "config" / "settings.yaml"
ASSETS = REPO_ROOT / "assets"
FONTS = ASSETS / "fonts"


def _env(name: str, default: Any = None) -> Any:
    value = os.environ.get(name)
    if value is None or value == "":
        return default
    return value


def _env_bool(name: str, default: bool) -> bool:
    raw = _env(name)
    if raw is None:
        return default
    return str(raw).strip().lower() in ("1", "true", "yes", "on", "y")


def _env_int(name: str, default: int) -> int:
    raw = _env(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


@dataclass
class Source:
    """상품 사진이 올라오는 드라이브 폴더 하나."""

    name: str
    folder_id: str
    kind: str = "refurb"  # refurb = 검수된 리퍼브, new = 제조사 직거래 새상품
    eyebrow: str = "오늘의 리본 특가"

    @property
    def is_new_goods(self) -> bool:
        return self.kind == "new"


@dataclass
class Settings:
    sources: list[Source]
    publish_folder_name: str
    publish_parent_id: str
    logo_file_id: str

    timezone: str
    publish_hour: int

    max_gap_seconds: int
    max_photos_per_group: int
    max_cards_per_day: int

    vision_model: str
    writing_model: str

    store_name: str
    store_handle: str
    footer_note: str
    visit_line: str

    card_width: int
    card_height: int
    orig_label: str
    sale_label: str

    best_count: int

    instagram_enabled: bool
    max_stories_per_day: int
    story_delay_seconds: int

    raw: dict = field(default_factory=dict, repr=False)

    # --- 비밀값 (환경변수 전용, 파일에 절대 저장하지 않는다) ---
    @property
    def source_folder_ids(self) -> list[str]:
        return [s.folder_id for s in self.sources]

    def source_for(self, folder_id: str) -> Source:
        for source in self.sources:
            if source.folder_id == folder_id:
                return source
        return self.sources[0]

    @property
    def anthropic_api_key(self) -> str | None:
        return _env("ANTHROPIC_API_KEY")

    @property
    def service_account_json(self) -> str | None:
        return _env("GOOGLE_SERVICE_ACCOUNT_JSON")

    @property
    def oauth_refresh_token(self) -> str | None:
        return _env("GOOGLE_OAUTH_REFRESH_TOKEN")

    @property
    def oauth_client_id(self) -> str | None:
        return _env("GOOGLE_OAUTH_CLIENT_ID")

    @property
    def oauth_client_secret(self) -> str | None:
        return _env("GOOGLE_OAUTH_CLIENT_SECRET")


def load_settings(path: Path | str | None = None) -> Settings:
    path = Path(path) if path else DEFAULT_SETTINGS
    data: dict = {}
    if path.exists():
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    drive = data.get("drive", {}) or {}
    schedule = data.get("schedule", {}) or {}
    grouping = data.get("grouping", {}) or {}
    model = data.get("model", {}) or {}
    store = data.get("store", {}) or {}
    card = data.get("card", {}) or {}
    blog = data.get("blog", {}) or {}
    instagram = data.get("instagram", {}) or {}

    return Settings(
        sources=_load_sources(drive),
        publish_folder_name=_env(
            "PUBLISH_FOLDER_NAME", drive.get("publish_folder_name", "콘텐츠 발행")
        ),
        publish_parent_id=_env("PUBLISH_PARENT_ID", drive.get("publish_parent_id", "") or ""),
        logo_file_id=_env("LOGO_FILE_ID", drive.get("logo_file_id", "") or ""),
        timezone=_env("TIMEZONE", schedule.get("timezone", "Asia/Seoul")),
        publish_hour=_env_int("PUBLISH_HOUR", int(schedule.get("publish_hour", 18))),
        max_gap_seconds=_env_int("MAX_GAP_SECONDS", int(grouping.get("max_gap_seconds", 150))),
        max_photos_per_group=_env_int(
            "MAX_PHOTOS_PER_GROUP", int(grouping.get("max_photos_per_group", 4))
        ),
        max_cards_per_day=_env_int("MAX_CARDS_PER_DAY", int(grouping.get("max_cards_per_day", 0))),
        vision_model=_env("VISION_MODEL", model.get("vision", "claude-sonnet-5")),
        writing_model=_env("WRITING_MODEL", model.get("writing", "claude-opus-5")),
        store_name=_env("STORE_NAME", store.get("name", "리본마켓 평택점")),
        store_handle=_env("STORE_HANDLE", store.get("handle", "@reborn.mk")),
        footer_note=_env("FOOTER_NOTE", store.get("footer_note", "")),
        visit_line=_env("VISIT_LINE", store.get("visit_line", "")),
        card_width=_env_int("CARD_WIDTH", int(card.get("width", 1080))),
        card_height=_env_int("CARD_HEIGHT", int(card.get("height", 1920))),
        orig_label=_env("ORIG_LABEL", card.get("orig_label", "온라인 판매가")),
        sale_label=_env("SALE_LABEL", card.get("sale_label", "리본마켓 초특가")),
        best_count=_env_int("BEST_COUNT", int(blog.get("best_count", 5))),
        instagram_enabled=_env_bool("INSTAGRAM_ENABLED", bool(instagram.get("enabled", True))),
        max_stories_per_day=_env_int(
            "MAX_STORIES_PER_DAY", int(instagram.get("max_stories_per_day", 10))
        ),
        story_delay_seconds=_env_int(
            "STORY_DELAY_SECONDS", int(instagram.get("delay_between_seconds", 20))
        ),
        raw=data,
    )


def _load_sources(drive: dict) -> list[Source]:
    """설정의 sources 목록을 읽는다.

    SOURCE_FOLDER_ID 환경변수가 있으면 그 폴더 하나만 쓴다 (특정 폴더만 급히 돌릴 때).
    """
    override = _env("SOURCE_FOLDER_ID")
    if override:
        return [Source(name="지정 폴더", folder_id=override)]

    raw_sources = drive.get("sources") or []
    sources = [
        Source(
            name=item.get("name", "상품"),
            folder_id=item["folder_id"],
            kind=item.get("kind", "refurb"),
            eyebrow=item.get("eyebrow", "오늘의 리본 특가"),
        )
        for item in raw_sources
        if item.get("folder_id")
    ]
    if sources:
        return sources
    # 예전 설정 형식(단일 폴더)도 계속 받아준다
    legacy = drive.get("source_folder_id")
    if legacy:
        return [Source(name="상품", folder_id=legacy)]
    raise ValueError("설정에 상품 사진 폴더(drive.sources)가 없습니다")
