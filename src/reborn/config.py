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
    logo_folder_id: str
    logo_asset: str
    logo_wordmark: bool

    timezone: str
    publish_hour: int

    max_gap_seconds: int
    max_photos_per_group: int
    max_cards_per_day: int

    provider: str
    vision_model: str
    writing_model: str
    cli_vision_model: str
    cli_writing_model: str

    store_id: str
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
    reel_enabled: bool
    reel_seconds_per_card: float
    reel_headline: str

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
    def gemini_api_key(self) -> str | None:
        return _env("GEMINI_API_KEY") or _env("GOOGLE_API_KEY")

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
    """첫 번째 매장의 설정. 매장이 하나였을 때부터 쓰던 입구다."""
    return load_stores(path)[0]


def load_stores(path: Path | str | None = None) -> list[Settings]:
    """매장별 설정을 순서대로 돌려준다.

    리본마켓 평택점과 여우마켓 일산점처럼 매장이 여럿이면 settings.yaml 의
    `stores:` 에 매장마다 다른 값만 적는다. 나머지는 공통 설정을 그대로 쓴다.
    같은 파이프라인을 매장 수만큼 돌리는 구조라 매장이 더 늘어도 코드는 그대로다.
    """
    data = _read_yaml(path)
    stores = data.get("stores") or []
    if not stores:
        return [_settings_from(data)]

    only = _env("ONLY_STORE")  # 한 매장만 급히 돌릴 때
    built = []
    for entry in stores:
        merged = _deep_merge(data, {k: v for k, v in entry.items() if k != "id"})
        merged.pop("stores", None)
        settings = _settings_from(merged)
        settings.store_id = entry.get("id") or settings.store_name
        if only and only not in (settings.store_id, settings.store_name):
            continue
        built.append(settings)
    if not built:
        raise ValueError(f"ONLY_STORE={only!r} 에 해당하는 매장이 설정에 없습니다")
    return built


def _read_yaml(path: Path | str | None) -> dict:
    path = Path(path) if path else DEFAULT_SETTINGS
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _deep_merge(base: dict, over: dict) -> dict:
    """매장별 설정을 공통 설정 위에 덮는다 (한 단계 아래까지)."""
    out = {k: (dict(v) if isinstance(v, dict) else v) for k, v in base.items()}
    for key, value in over.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = {**out[key], **value}
        else:
            out[key] = value
    return out


def _settings_from(data: dict) -> Settings:
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
        # 로고 파일을 직접 지정하는 대신 폴더를 지정하면, 그 안의 최신 이미지를 쓴다.
        # 새 매장이 로고를 드라이브에 넣기만 하면 다음 실행부터 바로 반영된다.
        logo_folder_id=_env("LOGO_FOLDER_ID", drive.get("logo_folder_id", "") or ""),
        logo_asset=str(drive.get("logo_asset", "") or ""),
        # 로고 파일이 아직 없는 매장만 true. 매장 이름을 글자로 찍는다.
        logo_wordmark=bool(drive.get("logo_wordmark", False)),
        timezone=_env("TIMEZONE", schedule.get("timezone", "Asia/Seoul")),
        publish_hour=_env_int("PUBLISH_HOUR", int(schedule.get("publish_hour", 18))),
        max_gap_seconds=_env_int("MAX_GAP_SECONDS", int(grouping.get("max_gap_seconds", 150))),
        max_photos_per_group=_env_int(
            "MAX_PHOTOS_PER_GROUP", int(grouping.get("max_photos_per_group", 6))
        ),
        max_cards_per_day=_env_int("MAX_CARDS_PER_DAY", int(grouping.get("max_cards_per_day", 0))),
        provider=_env("LLM_PROVIDER", model.get("provider", "auto")),
        vision_model=_env("VISION_MODEL", model.get("vision", "gemini-3.6-flash")),
        writing_model=_env("WRITING_MODEL", model.get("writing", "gemini-3.6-flash")),
        cli_vision_model=_env("CLI_VISION_MODEL", model.get("cli_vision", "claude-sonnet-5")),
        cli_writing_model=_env("CLI_WRITING_MODEL", model.get("cli_writing", "claude-sonnet-5")),
        store_id=str(store.get("id", "") or store.get("name", "매장")),
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
        reel_enabled=_env_bool("REEL_ENABLED", bool(instagram.get("reel_enabled", True))),
        reel_seconds_per_card=float(
            _env("REEL_SECONDS_PER_CARD", str(instagram.get("reel_seconds_per_card", 0.8)))
        ),
        reel_headline=_env("REEL_HEADLINE", instagram.get("reel_headline", "오늘의 추천템")),
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
