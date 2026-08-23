from datetime import date

from reborn.blog import BlogPost
from reborn.vision import Product


def product(name, orig, sale):
    return Product(
        is_product=True, product_name=name, one_liner="설명", category="가전",
        original_price=orig, sale_price=sale, discount_pct=None, price_source="가격표",
        best_photo_index=1, appeal="", needs_review=False, review_reason="",
    )


def make_post(n=2):
    products = [product(f"상품{i}", 200000, 100000) for i in range(1, n + 1)]
    return BlogPost(
        category_tag="오늘의 리본 특가",
        title="평택 리퍼브 가전 BEST",
        intro=[["안녕하세요.", "리본마켓입니다."]],
        transition=["그래서 오늘은 준비했어요."],
        items=[{"heading": f"소제목{i}", "body": [["본문 한 줄", "본문 두 줄"]],
                "personal_note": "저는 이렇게 쓰곤 해요."} for i in range(1, n + 1)],
        table_intro="한눈에 보시라고 정리했어요.",
        table_wrapup=["표에서 보시다시피 반값입니다."],
        closing=[["오늘도 좋은 하루 되세요."]],
        tags=["리본마켓", "평택리퍼브"],
        products=products,
    )


def test_html_uses_paren_numbering_not_period():
    """네이버 에디터는 '1.' 을 자동 목록으로 바꿔 번호를 전부 1로 만든다. 반드시 '1)' 이어야 한다."""
    html = make_post(3).to_naver_html("리본마켓 평택점", "재고 소진 시 종료")
    assert "<b>1) 소제목1</b>" in html
    assert "<b>2) 소제목2</b>" in html
    assert "<b>3) 소제목3</b>" in html
    assert "<b>1. " not in html


def test_html_body_font_size_is_19():
    html = make_post().to_naver_html("리본마켓 평택점", "재고 소진 시 종료")
    assert "font-size:19px" in html


def test_html_has_comparison_table_with_both_prices():
    html = make_post().to_naver_html("리본마켓 평택점", "재고 소진 시 종료")
    assert "온라인 판매가" in html and "리본마켓 초특가" in html
    assert "200,000원" in html and "100,000원" in html and "50%" in html


def test_markdown_has_both_prices_per_item():
    md = make_post().to_markdown("리본마켓 평택점", "재고 소진 시 종료")
    assert "온라인 판매가 200,000원 → 리본마켓 초특가 100,000원 (50% 할인)" in md
    assert "중고" not in md
