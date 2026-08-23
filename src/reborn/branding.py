"""리본마켓 브랜드 토큰과 로고/폰트 로딩."""

from __future__ import annotations

import logging
import os
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont

from .config import ASSETS, FONTS, REPO_ROOT

log = logging.getLogger(__name__)

# --- 색 (기존 카톡 가격비교 카드에서 쓰던 값 그대로) ---
ORANGE = (253, 111, 35)  # #FD6F23  리본마켓 시그니처 (로고의 순환 화살표와 같은 색)
SLATE = (114, 120, 142)  # #72788E  회청색, 할인율 뱃지 배경
INK = (20, 22, 28)  # #14161C  본문 검정 (로고 워드마크와 같은 계열)
BG = (255, 255, 255)
FOOTER_BG = (34, 37, 46)  # #22252E
MUTED = (140, 146, 162)
WHITE = (255, 255, 255)

# 로고를 찾는 순서 (앞이 우선)
#   1. REBORN_LOGO_PATH 환경변수
#   2. assets/reborn_logo.(png|jpg|webp)  — 저장소에 직접 넣어둔 파일
#   3. .cache/reborn_logo.png             — 드라이브에서 받아 캐시한 파일
LOGO_ENV_PATH = "REBORN_LOGO_PATH"
LOGO_COMMITTED = ASSETS / "reborn_logo.png"
LOGO_CACHE = REPO_ROOT / ".cache" / "reborn_logo.png"
LOGO_SUFFIXES = (".png", ".webp", ".jpg", ".jpeg")

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


def _committed_logo() -> Path | None:
    for suffix in LOGO_SUFFIXES:
        candidate = LOGO_COMMITTED.with_suffix(suffix)
        if candidate.exists() and candidate.stat().st_size > 0:
            return candidate
    return None


def logo_path(strict: bool = True) -> Path:
    """실제 리본마켓 로고 파일 경로."""
    override = os.environ.get(LOGO_ENV_PATH)
    if override and Path(override).exists():
        return Path(override)
    committed = _committed_logo()
    if committed:
        return committed
    if LOGO_CACHE.exists() and LOGO_CACHE.stat().st_size > 0:
        return LOGO_CACHE
    if strict:
        raise LogoMissing(
            "리본마켓 로고 파일을 찾을 수 없습니다. 로고 없이 카드뉴스를 만들지 않습니다.\n"
            f"  1) 저장소에 직접 넣기: {LOGO_COMMITTED}\n"
            f"  2) 드라이브에서 받기: config/settings.yaml 의 drive.logo_file_id 확인\n"
            f"  3) 다른 경로 쓰기: {LOGO_ENV_PATH} 환경변수"
        )
    raise LogoMissing("로고 없음")


def trim_margins(img: Image.Image, *, tolerance: int = 12) -> Image.Image:
    """로고 주변 여백을 잘라낸다.

    투명 배경 PNG(드라이브의 1080x1080 로고)와 흰 배경 PNG(워드마크 파일) 둘 다 다뤄야 한다.
    투명 여백이 있으면 알파로 자르고, 없으면 네 모서리 색을 배경으로 보고 그 색 여백을 자른다.
    """
    img = img.convert("RGBA")
    alpha = img.getchannel("A")

    if alpha.getextrema()[0] < 250:  # 투명한 부분이 있다 → 알파 기준
        bbox = alpha.getbbox()
        return img.crop(bbox) if bbox else img

    rgb = img.convert("RGB")
    w, h = rgb.size
    corners = [rgb.getpixel(p) for p in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1))]
    if len({corners[0]} | set(corners)) != 1:  # 모서리 색이 제각각이면 배경이 아니다
        return img
    background = Image.new("RGB", rgb.size, corners[0])
    diff = ImageChops.difference(rgb, background).convert("L").point(
        lambda v: 255 if v > tolerance else 0
    )
    bbox = diff.getbbox()
    return img.crop(bbox) if bbox else img


def wordmark(text: str, height: int) -> Image.Image:
    """로고 파일이 아직 없는 매장을 위한 임시 글자 로고.

    **로고가 있는 매장에는 절대 쓰지 않는다.** 진짜 로고를 글자로 흉내내면
    브랜드가 망가진다. 새로 연 매장이 로고 파일을 올리기 전까지만,
    설정에서 logo_wordmark 를 켠 매장에 한해 쓴다.
    """
    fnt = font("extrabold", max(12, int(height * 0.86)))
    ascent, descent = fnt.getmetrics()
    canvas = Image.new("RGBA", (1, 1))
    width = int(ImageDraw.Draw(canvas).textlength(text, font=fnt))
    img = Image.new("RGBA", (width + 8, ascent + descent), (0, 0, 0, 0))
    ImageDraw.Draw(img).text((4, 0), text, font=fnt, fill=(*SLATE, 255))
    return img


def load_logo(
    height: int,
    *,
    max_width: int | None = None,
    strict: bool = True,
    path: Path | str | None = None,
) -> Image.Image:
    """여백을 잘라내고 원하는 높이로 맞춘 로고.

    path 를 주면 그 파일을 쓴다 (매장마다 로고가 다르다).
    가로로 긴 워드마크형 로고는 max_width 를 넘지 않도록 더 줄인다
    (카드뉴스 우상단 날짜 뱃지를 침범하지 않게).
    """
    img = trim_margins(Image.open(path if path else logo_path(strict=strict)))
    ratio = height / img.height
    width = max(1, round(img.width * ratio))
    if max_width and width > max_width:
        ratio = max_width / img.width
        width, height = max_width, max(1, round(img.height * ratio))
    return img.resize((width, height), Image.LANCZOS)
