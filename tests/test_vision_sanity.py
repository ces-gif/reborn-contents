from reborn.vision import Product, sanity_check, strip_unevidenced_claims


def make(**kw):
    base = dict(
        product_name="테스트 상품", category="가전", tag_text="정가 100,000 리본가 50,000",
        condition_note="", original_price=100000, sale_price=50000, discount_pct=None,
        price_source="1번 사진 가격표", best_photo_index=2,
        photo_kinds=["price_tag", "product"], photo_paths=["tag.jpg", "item.jpg"],
    )
    base.update(kw)
    return Product(**base)


def test_computed_pct():
    assert make().computed_pct == 50


def test_explicit_pct_wins():
    assert make(discount_pct=45).computed_pct == 45


def test_missing_sale_price_needs_review():
    p = sanity_check(make(sale_price=None))
    assert p.needs_review and not p.publishable


def test_original_below_sale_is_dropped():
    p = sanity_check(make(original_price=40000, sale_price=50000))
    assert p.original_price is None and p.computed_pct is None


def test_absurd_discount_flagged():
    assert sanity_check(make(original_price=1000000, sale_price=10000)).needs_review


def test_junggo_word_is_replaced():
    p = sanity_check(make(product_name="중고 냉장고"))
    assert "중고" not in p.product_name


# ---- 은성님 지시: 가격표에 없는 상태 표현은 쓰지 않는다 ----

def test_condition_claim_without_tag_evidence_is_stripped():
    p = sanity_check(make(condition_note="박스만 개봉한 미사용품", tag_text="정가 100,000"))
    assert p.condition_note == ""


def test_condition_claim_with_tag_evidence_is_kept():
    p = sanity_check(make(condition_note="전시상품 입니다", tag_text="전시상품 / 정가 100,000"))
    assert "전시상품" in p.condition_note


def test_sentence_mixing_evidenced_and_invented_claims_is_dropped_whole():
    """단어만 오려내면 '박스만 개봉한 품' 같은 조각이 남는다. 문장째 버리는 게 안전하다."""
    assert strip_unevidenced_claims("박스만 개봉한 미사용품입니다", "정가 100,000") == ""
    assert strip_unevidenced_claims("전시상품, 미사용 새제품입니다", "전시상품 100,000원") == ""


def test_clean_sentences_survive_next_to_a_dropped_one():
    got = strip_unevidenced_claims(
        "12kg 인버터 드럼세탁기입니다. 미사용 새제품입니다.", "정가 100,000"
    )
    assert got == "12kg 인버터 드럼세탁기입니다."


def test_evidenced_claim_alone_is_kept():
    assert strip_unevidenced_claims("전시상품입니다.", "전시상품 100,000원") == "전시상품입니다."


# ---- 은성님 지시: 가격표만 찍힌 묶음은 카드뉴스를 만들지 않는다 ----

def test_price_tag_only_group_is_not_publishable():
    p = sanity_check(make(photo_kinds=["price_tag"], photo_paths=["tag.jpg"], best_photo_index=0))
    assert not p.has_product_photo
    assert not p.publishable
    assert "가격표만" in p.review_reason


def test_group_with_product_photo_is_publishable():
    assert sanity_check(make()).publishable


def test_single_photo_showing_both_is_publishable():
    p = sanity_check(make(photo_kinds=["both"], photo_paths=["both.jpg"], best_photo_index=1))
    assert p.publishable and p.best_photo.name == "both.jpg"


def test_best_photo_never_points_at_a_price_tag():
    """모델이 실수로 가격표 사진을 골라도 상품 사진으로 바로잡는다."""
    p = sanity_check(make(best_photo_index=1))  # 1번은 price_tag
    assert p.best_photo.name == "item.jpg"


def test_card_line_prefers_web_spec_over_tag_condition():
    p = make(condition_note="전시상품", spec_line="12kg 인버터 드럼세탁기")
    assert p.card_line == "12kg 인버터 드럼세탁기"


def test_card_line_does_not_borrow_the_tag_condition():
    # 상태 표기는 소개가 아니라 고지사항이다. 카드에서 자리가 다르다.
    p = make(condition_note="전시상품")
    assert p.card_line == ""
    assert p.card_condition == "전시상품"


def test_card_line_is_empty_when_nothing_is_known():
    assert make().card_line == ""
