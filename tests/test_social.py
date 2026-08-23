from datetime import date

from reborn.social import instagram_caption, kakao_notice
from reborn.vision import Product


def p(name, orig, sale):
    return Product(
        product_name=name, category="가전", spec_line="6인용 IH 압력밥솥",
        original_price=orig, sale_price=sale, price_source="가격표",
        best_photo_index=1, photo_kinds=["both"], photo_paths=["a.jpg"],
    )


def test_kakao_notice_shows_both_prices():
    text = kakao_notice([p("쿠쿠 밥솥", 169000, 89000)], day=date(2026, 8, 23),
                        store_name="리본마켓 평택점", footer_note="재고 소진 시 종료")
    assert "온라인 판매가 169,000원" in text
    assert "리본마켓 초특가 89,000원 (47%↓)" in text
    assert "중고" not in text


def test_instagram_caption_has_store_block_and_tags():
    text = instagram_caption([p("쿠쿠 밥솥", 169000, 89000)], day=date(2026, 8, 23),
                             store_name="리본마켓 평택점", handle="@reborn.mk")
    assert "📍 리본마켓 평택점" in text
    assert "#리본마켓" in text and "@reborn.mk" in text
