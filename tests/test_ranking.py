from reborn.ranking import pick_best, rule_score
from reborn.vision import Product


def p(name, orig, sale, category="가전"):
    return Product(
        product_name=name, category=category, spec_line=f"{name} 설명",
        original_price=orig, sale_price=sale, price_source="가격표",
        best_photo_index=1, photo_kinds=["both"], photo_paths=["a.jpg"],
    )


def test_bigger_discount_scores_higher():
    assert rule_score(p("A", 200000, 100000)) > rule_score(p("B", 200000, 180000))


def test_pick_best_returns_at_most_count():
    items = [p(f"상품{i}", 200000, 200000 - i * 10000) for i in range(1, 9)]
    picked = pick_best(items, count=5)
    assert len(picked) == 5
    assert picked[0][0].product_name == "상품8"  # 할인 폭이 가장 큰 것


def test_unpublishable_items_are_excluded():
    good = p("좋은 상품", 200000, 100000)
    bad = p("가격 미상", None, None)
    bad.needs_review = True  # sanity_check 가 붙여주는 상태
    assert [x[0].product_name for x in pick_best([good, bad], count=5)] == ["좋은 상품"]
