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


# ---------------------------------------------------------------- 상태 고지 뱃지


def _card(**kw):
    from reborn.cardnews import CardData

    base = dict(
        product_name="테스트 상품",
        one_liner="",
        sale_price=10000,
        original_price=20000,
        date_label="2026.08.25",
    )
    base.update(kw)
    return CardData(**base)


def test_상태표기가_있으면_사진_위에_뱃지가_그려진다(tmp_path, monkeypatch, photo, logo):
    from reborn import cardnews

    drawn: list[str] = []
    real = cardnews._draw_condition

    def spy(draw, note):
        drawn.append(note)
        return real(draw, note)

    monkeypatch.setattr(cardnews, "_draw_condition", spy)
    cardnews.render_card(_card(condition_note="까짐"), photo, tmp_path / "c.png")
    assert drawn == ["까짐"]


def test_상태표기가_없으면_아무것도_안_그린다(tmp_path, photo, logo):
    from PIL import Image

    from reborn import cardnews

    a = cardnews.render_card(_card(), photo, tmp_path / "a.png")
    b = cardnews.render_card(_card(condition_note="  "), photo, tmp_path / "b.png")
    assert Image.open(a).tobytes() == Image.open(b).tobytes()


def test_아주_긴_상태표기는_사진_밖으로_안_넘어간다(tmp_path, photo, logo):
    from reborn import cardnews

    note = "모서리 찌그러짐과 표면 까짐 그리고 사용감이 상당히 많이 있습니다 확인 바랍니다"
    out = cardnews.render_card(_card(condition_note=note), photo, tmp_path / "c.png")
    assert out.exists()


def test_cover_card_is_story_sized_and_holds_the_headline(tmp_path, logo):
    """릴스 표지는 상품 카드와 같은 1080x1920 이어야 이어 붙일 때 안 깨진다."""
    from reborn.cardnews import render_cover

    out = render_cover(
        tmp_path / "00-표지.png",
        date_label="2026.09.05",
        store_name="리본마켓 평택점",
        headline="오늘의 추천템",
        item_count=9,
    )
    with Image.open(out) as img:
        assert img.size == (1080, 1920)


def test_cover_shrinks_a_long_headline_instead_of_overflowing(tmp_path, logo):
    from reborn.cardnews import render_cover

    out = render_cover(
        tmp_path / "long.png",
        date_label="2026.09.05",
        store_name="여우마켓 일산점 리퍼브 전문 매장",
        headline="오늘의 아주 특별한 추천템 모음",
    )
    with Image.open(out) as img:
        assert img.size == (1080, 1920)


# ----------------------------------------------- 번호 뱃지 (손님이 예약하는 번호)


def _num_photo(tmp_path):
    """어두운 사진. 뱃지가 여기서도 보여야 한다."""
    p = tmp_path / "dark.png"
    Image.new("RGB", (900, 700), (58, 62, 70)).save(p)
    return p


def _badge_area(path):
    """번호 뱃지가 놓이는 사진 좌상단 영역을 잘라 온다."""
    from PIL import Image

    from reborn import cardnews as C

    with Image.open(path) as im:
        box = (C.MARGIN + C.NUM_INSET, C.Y_PHOTO + C.NUM_INSET)
        return im.convert("RGB").crop((box[0], box[1], box[0] + C.NUM_D, box[1] + C.NUM_D))


def test_number_badge_is_drawn_on_the_photo(tmp_path, logo):
    """손님이 번호를 보고 예약한다. 사진 위에 오렌지 동그라미로 찍혀야 한다."""
    from reborn import branding as B
    from reborn.cardnews import CardData, render_card

    out = tmp_path / "c.png"
    render_card(
        CardData(number=7, product_name="싱크선반", one_liner="설명", sale_price=1000),
        _num_photo(tmp_path), out, logo=logo,
    )
    colors = {c for _, c in _badge_area(out).getcolors(maxcolors=100000)}
    assert B.ORANGE in colors          # 동그라미
    assert (255, 255, 255) in colors   # 흰 숫자·테두리


def test_no_badge_when_the_card_has_no_number(tmp_path, logo):
    """번호를 안 주면 아무것도 안 그린다 — 예전 카드가 달라지지 않게."""
    from reborn import branding as B
    from reborn.cardnews import CardData, render_card

    out = tmp_path / "c.png"
    render_card(
        CardData(product_name="싱크선반", one_liner="설명", sale_price=1000),
        _num_photo(tmp_path), out, logo=logo,
    )
    assert B.ORANGE not in {c for _, c in _badge_area(out).getcolors(maxcolors=100000)}


def test_a_three_digit_number_still_fits(tmp_path, logo):
    """두 자리·세 자리도 동그라미를 넘치면 안 된다."""
    from reborn import cardnews as C

    for n in (9, 12, 108):
        label = str(n)
        for size in (74, 66, 58, 50):
            font = C.B.font("extrabold", size)
            if C.text_width(label, font) <= C.NUM_D - 34:
                break
        assert C.text_width(label, font) <= C.NUM_D - 34
