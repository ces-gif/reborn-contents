from reborn.vision import Product, _sanity_check


def make(**kw):
    base = dict(
        is_product=True, product_name="테스트 상품", one_liner="설명", category="가전",
        original_price=100000, sale_price=50000, discount_pct=None,
        price_source="1번 사진 가격표", best_photo_index=1, appeal="", needs_review=False,
        review_reason="",
    )
    base.update(kw)
    return Product(**base)


def test_computed_pct():
    assert make().computed_pct == 50


def test_explicit_pct_wins():
    assert make(discount_pct=45).computed_pct == 45


def test_missing_sale_price_needs_review():
    p = _sanity_check(make(sale_price=None))
    assert p.needs_review and not p.publishable


def test_original_below_sale_is_dropped():
    p = _sanity_check(make(original_price=40000, sale_price=50000))
    assert p.original_price is None and p.computed_pct is None


def test_absurd_discount_flagged():
    p = _sanity_check(make(original_price=1000000, sale_price=10000))
    assert p.needs_review


def test_junggo_word_is_replaced():
    p = _sanity_check(make(one_liner="깨끗한 중고 제품"))
    assert "중고" not in p.one_liner


def test_non_product_is_not_publishable():
    assert not _sanity_check(make(is_product=False, sale_price=None)).publishable
