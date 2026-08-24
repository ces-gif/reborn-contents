"""아이폰 사진(HEIC)이 파이프라인을 통과하는지.

일산 첫 업로드 14장이 전부 IMG_7450.HEIC 같은 아이폰 기본 포맷이었다.
드라이브 목록에는 잡히는데 Pillow 가 못 열어서 카드뉴스가 0장이 됐다.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

import reborn  # noqa: F401  — import 만으로 HEIC 지원이 등록된다
from reborn.cardnews import CardData, render_card
from reborn.drive import IMAGE_MIMES, DriveFile
from reborn.imaging import register_heif
from reborn.llm import _encode_jpeg

pillow_heif = pytest.importorskip("pillow_heif")


@pytest.fixture
def heic(tmp_path) -> Path:
    path = tmp_path / "IMG_7450.HEIC"
    pillow_heif.from_pillow(Image.new("RGB", (1200, 900), (240, 120, 30))).save(
        str(path), quality=70
    )
    return path


def test_importing_reborn_registers_heic():
    assert ".heic" in Image.registered_extensions()


def test_register_is_idempotent():
    assert register_heif() and register_heif()


def test_drive_lists_iphone_photos_as_images():
    from datetime import datetime, timezone

    dt = datetime(2026, 8, 24, tzinfo=timezone.utc)
    photo = DriveFile(
        id="x", name="IMG_7450.HEIC", mime_type="image/heif",
        created_time=dt, modified_time=dt, size=2143169,
    )
    assert photo.is_image
    assert "image/heic" in IMAGE_MIMES and "image/heif" in IMAGE_MIMES


def test_heic_survives_the_vision_encoder(heic):
    """판독 경로. 여기서 터지면 상품을 하나도 못 읽는다."""
    data = _encode_jpeg(str(heic))
    assert data[:2] == b"\xff\xd8"  # JPEG 시작 표식


def test_a_card_renders_from_an_iphone_photo(heic, tmp_path, monkeypatch):
    """카드 렌더링 경로."""
    logo = tmp_path / "logo.png"
    img = Image.new("RGBA", (600, 200), (0, 0, 0, 0))
    img.paste((255, 90, 0, 255), (50, 40, 550, 160))
    img.save(logo)

    out = tmp_path / "card.png"
    render_card(
        CardData(
            product_name="아이폰 사진 상품",
            one_liner="",
            sale_price=19000,
            original_price=39000,
            date_label="2026.08.24",
        ),
        heic,
        out,
        logo=logo,
    )
    with Image.open(out) as card:
        assert card.size == (1080, 1920)
