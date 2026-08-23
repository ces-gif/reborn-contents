"""무엇이 발행을 막고 무엇이 못 막는가.

은성님 지시: "찍어서 업로드한 모든 것들을 콘텐츠로 생성하라."
글자가 조금 흐리다는 이유로 카드를 통째로 버리면 안 된다.
다만 **틀린 가격이 찍히는 것**은 여전히 막는다.
"""

from __future__ import annotations

from reborn.vision import Product, sanity_check


def product(**kw) -> Product:
    base = dict(
        product_name="게이밍 의자",
        category="가구",
        tag_text="온라인가 86,900 / 리본가 43,500",
        condition_note="",
        original_price=86900,
        sale_price=43500,
        discount_pct=None,
        price_source="2번 사진 가격표",
        best_photo_index=1,
        photo_kinds=["product", "price_tag"],
        review_reason="",
        photo_paths=["a.jpg", "b.jpg"],
    )
    base.update(kw)
    return sanity_check(Product(**base))


def test_a_blurry_product_name_still_gets_a_card():
    p = product(review_reason="가격표 상품명 글자가 흐릿해 정확한 표기를 확신하기 어려움")
    assert p.publishable
    assert "흐릿" in p.cautions
    assert p.review_reason == ""


def test_a_rotated_photo_note_still_gets_a_card():
    p = product(review_reason="사진이 세로로 회전되어 있어 모델명 일부 판독이 어려움")
    assert p.publishable and p.cautions


def test_mismatched_product_and_tag_is_blocked():
    """가격표가 다른 물건 거면 틀린 가격이 찍힌다. 그건 막는다."""
    p = product(review_reason="1번 사진(책상)과 2번 사진(빨래바구니)의 상품이 서로 다릅니다")
    assert not p.publishable
    assert "서로 다릅니다" in p.review_reason


def test_missing_price_is_blocked():
    """가격은 절대 지어내지 않는다."""
    p = product(sale_price=None, original_price=None)
    assert not p.publishable
    assert "판매가를 읽지 못했" in p.review_reason


def test_price_tag_only_group_is_blocked():
    """가격표만 있으면 카드 배경으로 쓸 상품 사진이 없다."""
    p = product(photo_kinds=["price_tag"], photo_paths=["a.jpg"], best_photo_index=0)
    assert not p.publishable
    assert "상품이 보이는 사진이 없습니다" in p.review_reason


def test_absurd_discount_is_blocked():
    p = product(original_price=100000, sale_price=1000)
    assert not p.publishable
    assert "할인율" in p.review_reason


def test_a_caution_and_a_blocker_together_still_blocks():
    p = product(
        review_reason="상품이 서로 다릅니다",
        sale_price=None,
    )
    assert not p.publishable


def test_clean_product_has_neither(): 
    p = product()
    assert p.publishable
    assert not p.cautions and not p.review_reason
