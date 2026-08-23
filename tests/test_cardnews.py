from pathlib import Path

import pytest
from PIL import Image

from reborn import branding
from reborn.cardnews import CardData, render_card, won


@pytest.fixture
def logo(tmp_path, monkeypatch):
    path = tmp_path / "logo.png"
    Image.new("RGBA", (600, 160), (253, 111, 35, 255)).save(path)
    monkeypatch.setenv(branding.LOGO_ENV_PATH, str(path))
    return path


@pytest.fixture
def photo(tmp_path):
    path = tmp_path / "photo.jpg"
    Image.new("RGB", (1600, 1200), (230, 232, 238)).save(path)
    return path


def test_won_formatting():
    assert won(1290000) == "1,290,000원"


def test_card_is_instagram_story_size(tmp_path, logo, photo):
    out = render_card(
        CardData(product_name="쿠쿠 6인용 밥솥", one_liner="박스만 개봉한 미사용품",
                 sale_price=89000, original_price=169000, date_label="2026.08.23"),
        photo, tmp_path / "card.png",
    )
    with Image.open(out) as img:
        assert img.size == (1080, 1920)


def test_card_is_full_bleed_at_top_and_bottom(tmp_path, logo, photo):
    """스토리 화면을 꽉 채우도록 상단 오렌지 바와 하단 바가 좌우 끝까지 닿아 있어야 한다."""
    out = render_card(
        CardData(product_name="테스트", one_liner="설명", sale_price=10000, original_price=20000),
        photo, tmp_path / "card.png",
    )
    with Image.open(out) as img:
        assert img.getpixel((0, 3)) == branding.ORANGE
        assert img.getpixel((1079, 3)) == branding.ORANGE
        assert img.getpixel((0, 1919)) == branding.FOOTER_BG
        assert img.getpixel((1079, 1919)) == branding.FOOTER_BG
        # 가격 바도 좌우 끝까지
        assert img.getpixel((0, 1500)) == branding.ORANGE
        assert img.getpixel((1079, 1500)) == branding.ORANGE


def test_missing_logo_raises_instead_of_drawing_text(tmp_path, photo, monkeypatch):
    monkeypatch.delenv(branding.LOGO_ENV_PATH, raising=False)
    monkeypatch.setattr(branding, "LOGO_CACHE", tmp_path / "nope.png")
    with pytest.raises(branding.LogoMissing):
        render_card(
            CardData(product_name="테스트", one_liner="설명", sale_price=10000),
            photo, tmp_path / "card.png",
        )


def test_single_price_variant_renders(tmp_path, logo, photo):
    out = render_card(
        CardData(product_name="정가만 있는 상품", one_liner="설명", sale_price=39000),
        photo, tmp_path / "card.png",
    )
    assert Path(out).exists()


def test_very_long_product_name_still_fits(tmp_path, logo, photo):
    out = render_card(
        CardData(
            product_name="삼성전자 비스포크 그랑데 AI 세탁기 건조기 세트 25kg 새틴 베이지 전시상품",
            one_liner="전시 상품, 외관 미세 스크래치 외 기능 이상 없습니다",
            sale_price=1890000, original_price=3290000,
        ),
        photo, tmp_path / "card.png",
    )
    with Image.open(out) as img:
        assert img.size == (1080, 1920)
