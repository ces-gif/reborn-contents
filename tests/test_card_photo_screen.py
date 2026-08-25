"""카드에 쓸 사진을 한 장씩 다시 검문하는 마지막 관문.

실제 사고: 흰 상자에 가격표만 붙은 사진이 '상품 사진'으로 분류돼 카드에 실렸다.
분류 결과를 믿는 방식으로는 막을 수 없어서, 카드에 쓰기 직전에 그 사진 한 장만
놓고 "가격표를 가리면 무엇이 남는가" 를 다시 묻는다.
"""

from __future__ import annotations

from reborn.vision import CardPhotoScreen, Product, pick_card_photo


def product(paths, kinds, **kw) -> Product:
    base = dict(
        product_name="사무용 의자",
        category="가구",
        tag_text="온라인가 67,900 / 리본가 34,000",
        condition_note="",
        original_price=67900,
        sale_price=34000,
        discount_pct=None,
        price_source="가격표",
        best_photo_index=1,
        photo_kinds=list(kinds),
        photo_shows_product=[True] * len(kinds),
        review_reason="",
        photo_paths=list(paths),
    )
    base.update(kw)
    return Product(**base)


class Screener:
    """사진 이름으로 판정을 정해 두는 가짜 검수자."""

    vision_model = "m"

    def __init__(self, verdicts: dict):
        self.verdicts = verdicts
        self.asked: list[str] = []

    def structured(self, *, system, parts, schema, max_tokens=8000, search=False, model=None):
        path = next(p["path"] for p in parts if p["type"] == "image")
        name = path.rsplit("/", 1)[-1]
        self.asked.append(name)
        return self.verdicts[name]


def ok() -> CardPhotoScreen:
    return CardPhotoScreen(visible_besides_tag="검은 사무용 의자 전체", tag_dominates=False, ok=True)


def tag_only() -> CardPhotoScreen:
    return CardPhotoScreen(visible_besides_tag="흰 상자면뿐", tag_dominates=True, ok=False)


def test_a_tag_only_photo_is_rejected_and_the_card_is_dropped():
    p = product(["tag.jpg"], ["product"])
    client = Screener({"tag.jpg": tag_only()})
    pick_card_photo(client, p, model="m")
    assert not p.publishable
    assert "가격표만 크게 찍혔습니다" in p.review_reason


def test_it_moves_on_to_the_next_photo_that_passes():
    p = product(["tag.jpg", "chair.jpg"], ["product", "product"], best_photo_index=1)
    client = Screener({"tag.jpg": tag_only(), "chair.jpg": ok()})
    pick_card_photo(client, p, model="m")
    assert p.publishable
    assert p.best_photo.name == "chair.jpg"
    assert client.asked == ["tag.jpg", "chair.jpg"]


def test_a_good_photo_passes_on_the_first_try():
    p = product(["chair.jpg", "tag.jpg"], ["product", "price_tag"])
    client = Screener({"chair.jpg": ok()})
    pick_card_photo(client, p, model="m")
    assert p.publishable and p.best_photo.name == "chair.jpg"
    assert client.asked == ["chair.jpg"], "통과했으면 더 묻지 않는다"


def test_a_photo_where_the_tag_dominates_is_rejected_even_if_ok_is_true():
    """모델이 ok=true 라고 해도 가격표가 화면을 덮으면 쓰지 않는다."""
    p = product(["big-tag.jpg"], ["product"])
    client = Screener({
        "big-tag.jpg": CardPhotoScreen(
            visible_besides_tag="의자 등받이 일부", tag_dominates=True, ok=True
        )
    })
    pick_card_photo(client, p, model="m")
    assert not p.publishable


def test_a_screening_failure_does_not_block_publishing():
    """검문이 실패했다고 멀쩡한 카드를 막지는 않는다."""

    class Broken:
        vision_model = "m"

        def structured(self, **kw):
            raise RuntimeError("모델 응답 없음")

    p = product(["chair.jpg"], ["product"])
    pick_card_photo(Broken(), p, model="m")
    assert p.publishable


def test_products_already_blocked_are_left_alone():
    p = product(["tag.jpg"], ["price_tag"], sale_price=None)
    client = Screener({})
    pick_card_photo(client, p, model="m")
    assert client.asked == [], "이미 막힌 상품은 검문하지 않는다"
