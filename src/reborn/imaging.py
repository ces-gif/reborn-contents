"""아이폰 사진(HEIC)을 Pillow 가 열 수 있게 해 준다.

일산에서 올린 첫 사진 14장이 전부 IMG_7450.HEIC 같은 아이폰 기본 포맷이었다.
드라이브 목록에는 잡히는데 Pillow 가 HEIC 를 못 열어서, 사진을 다 받아놓고
판독 단계에서 한 장도 못 쓰고 카드뉴스가 0장이 됐다.

pillow-heif 를 한 번 등록해 두면 Image.open 이 HEIC 도 그냥 연다.
등록에 실패해도 파이프라인을 멈추지 않는다 — JPEG/PNG 는 그대로 처리된다.
"""

from __future__ import annotations

import logging

log = logging.getLogger(__name__)

_registered: bool | None = None


def register_heif() -> bool:
    """HEIC 지원을 붙인다. 여러 번 불러도 한 번만 등록한다."""
    global _registered
    if _registered is not None:
        return _registered
    try:
        import pillow_heif
    except ImportError:
        log.warning(
            "pillow-heif 가 없어 아이폰 HEIC 사진을 읽을 수 없습니다 "
            "(requirements.txt 확인). JPEG/PNG 는 그대로 처리됩니다."
        )
        _registered = False
        return False
    try:
        pillow_heif.register_heif_opener()
    except Exception as exc:  # pragma: no cover - 등록 자체가 실패하는 건 드물다
        log.warning("HEIC 지원 등록에 실패했습니다: %s", exc)
        _registered = False
        return False
    _registered = True
    return True


# ---------------------------------------------------------------- 촬영 시각


_EXIF_ORIGINAL = 36867  # DateTimeOriginal
_EXIF_DIGITIZED = 36868  # DateTimeDigitized
_EXIF_MODIFIED = 306  # DateTime


def exif_capture_time(path, tz: str = "Asia/Seoul"):
    """사진 파일 안에 적힌 촬영 시각. 못 읽으면 None.

    아이폰 사진은 파일명이 IMG_7499.HEIC 라 이름에서 시각을 알 수 없다.
    그럴 때 드라이브 업로드 시각으로 세우면 순서가 뒤죽박죽이 된다 —
    한 번에 20여 장을 올리면 업로드가 병렬로 끝나서 찍은 순서와 무관해진다.
    08-25 일산점이 딱 그랬다: 사진 23장이 상품 묶음 22개로 흩어져서
    상품 사진과 가격표 사진이 짝을 못 찾았다.

    그래서 파일 안의 EXIF 촬영 시각을 우선으로 본다.
    """
    from datetime import datetime
    from zoneinfo import ZoneInfo

    register_heif()
    try:
        from PIL import Image

        with Image.open(path) as img:
            exif = img.getexif()
    except Exception:  # pragma: no cover - 손상된 파일
        return None
    if not exif:
        return None
    # DateTimeOriginal 은 Exif 하위 IFD(0x8769) 에 들어 있다. 최상위만 보면 놓친다.
    try:
        sub = exif.get_ifd(0x8769) or {}
    except Exception:  # pragma: no cover
        sub = {}
    for tag in (_EXIF_ORIGINAL, _EXIF_DIGITIZED, _EXIF_MODIFIED):
        raw = sub.get(tag) or exif.get(tag)
        if not raw:
            continue
        text = str(raw).strip()
        for fmt in ("%Y:%m:%d %H:%M:%S", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(text[:19], fmt).replace(tzinfo=ZoneInfo(tz))
            except ValueError:
                continue
    return None
