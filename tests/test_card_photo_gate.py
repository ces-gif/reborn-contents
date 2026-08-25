"""카드뉴스 배경에 가격표 사진이 실리지 않는지.

실제 사고 (2026-08-25, 리퍼 04 지오리스 등받이):
흰 상자면에 가격표만 붙은 사진을 모델이 both(상품+가격표)로 분류했고,
그게 그대로 카드뉴스 배경으로 나갔다. 상품은 한 조각도 안 보였다.
"""

from __future__ import annotations

import pytest

from reborn.vision import Product


def product(kinds, shows, **kw) -> Product:
    base = dict(
        product_name="지오리스 등받이 의자",
        category="가구",
        tag_text="온라인가 67,900 / 리본가 34,000",
        condition_note="",
        original_price=67900,
        sale_price=34000,
        discount_pct=None,
        price_source="가격표",
        best_photo_index=1,
        photo_kinds=list(kinds),
        photo_shows_product=list(shows),
        review_reason="",
        photo_paths=[f"{i}.jpg" for i in range(1, len(kinds) + 1)],
    )
    base.update(kw)
    return Product(**base)


def test_a_tag_on_a_blank_surface_is_not_a_card_photo():
    """모델이 both 라고 해도, 상품을 못 알아보면 카드 배경으로 쓰지 않는다."""
    p = product(["both"], [False])
    assert not p.has_product_photo
    with pytest.raises(ValueError, match="알아볼 수 있는 사진이 없습니다"):
        _ = p.best_photo


def test_it_falls_back_to_a_photo_that_does_show_the_product():
    """모델이 1번을 골랐어도 거기 상품이 안 보이면 2번으로 넘어간다."""
    p = product(["both", "product"], [False, True], best_photo_index=1)
    assert p.best_photo.name == "2.jpg"


def test_the_chosen_photo_is_kept_when_it_really_shows_the_product():
    p = product(["product", "price_tag"], [True, False], best_photo_index=1)
    assert p.best_photo.name == "1.jpg"


def test_a_price_tag_is_never_chosen_even_if_it_somehow_shows_something():
    p = product(["price_tag", "product"], [True, True], best_photo_index=1)
    assert p.best_photo.name == "2.jpg"


def test_old_records_without_the_flag_still_work():
    """예전에 만든 products.json 에는 이 항목이 없다. 그때 방식대로 동작해야 한다."""
    p = product(["product", "price_tag"], [])
    assert p.has_product_photo and p.best_photo.name == "1.jpg"


def test_blocked_when_every_photo_is_just_the_tag():
    p = product(["both", "price_tag"], [False, False])
    assert not p.publishable
