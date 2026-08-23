"""리본마켓 브랜드 토큰과 로고/폰트 로딩."""

from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageFont

from .config import ASSETS, FONTS

log = logging.getLogger(__name__)

# --- 색 (기존 카톡 가격비교 카드에서 쓰던 값 그대로) ---
ORANGE = (253, 111, 35)  # #FD6F23  리본마켓 시그니처
SLATE = (114, 120, 142)  # #72788E  회청색, 할인율 뱃지 배경
INK = (20, 22, 28)  # #14161C  본문 검정
BG = (255, 255, 255)
FOOTER_BG = (34, 37, 46)  # #22252E
MUTED = (140, 146, 162)
WHITE = (255, 255, 255)

LOGO_CACHE = ASSETS / "reborn_logo.png"
LOGO_ENV_PATH = "REBORN_LOGO_PATH"

_WEIGHTS = {
    "regular": "Pretendard-Regular.otf",
    "medium": "Pretendard-Medium.otf",
    "semibold": "Pretendard-SemiBold.otf",
    "bold": "Pretendard-Bold.otf",
    "extrabold": "Pretendard-ExtraBold.otf",
}


class LogoMissing(RuntimeError):
    """실제 로고 파일이 없을 때. 로고를 텍스트로 대체하지 않기 위해 명시적으로 막는다."""


@lru_cache(maxsize=64)
def font(weight: str, size: int) -> ImageFont.FreeTypeFont:
    path = FONTS / _WEIGHTS[weight]
    if not path.exists():  # pragma: no cover - 저장소에 동봉되어 있다
        raise FileNotFoundError(f"폰트가 없습니다: {path}")
    return ImageFont.truetype(str(path), size)


def logo_path(strict: bool = True) -> Path:
    """실제 리본마켓 로고 PNG 경로.

    우선순위: REBORN_LOGO_PATH 환경변수 → assets/reborn_logo.png 캐시.
    둘 다 없으면 LogoMissing. (파이프라인이 실행 초반에 드라이브에서 받아 캐시해 둔다.)
    """
    import os

    override = os.environ.get(LOGO_ENV_PATH)
    if override and Path(override).exists():
        return Path(override)
    if LOGO_CACHE.exists():
        return LOGO_CACHE
    if strict:
        raise LogoMissing(
            "리본마켓 로고 파일을 찾을 수 없습니다. 드라이브에서 로고를 내려받지 못했습니다 "
            f"(설정: drive.logo_file_id). 로고 없이 카드뉴스를 만들지 않습니다. "
            f"수동으로 넣으려면 {LOGO_CACHE} 에 PNG 를 두거나 {LOGO_ENV_PATH} 를 설정하세요."
        )
    raise LogoMissing("로고 없음")


def load_logo(height: int, *, strict: bool = True) -> Image.Image:
    """투명 여백을 잘라내고 원하는 높이로 맞춘 로고를 돌려준다."""
    img = Image.open(logo_path(strict=strict)).convert("RGBA")
    bbox = img.getchannel("A").getbbox()
    if bbox:
        img = img.crop(bbox)
    ratio = height / img.height
    return img.resize((max(1, round(img.width * ratio)), height), Image.LANCZOS)
