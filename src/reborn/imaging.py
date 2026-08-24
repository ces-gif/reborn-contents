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
