"""통판독 — 사진 전부를 한 번에 보고 상품별로 정리한 결과를 옮기는 부분."""

from pathlib import Path

import pytest

from reborn import vision
from reborn.vision import PlannedPhoto, PlannedProduct, StorePlan, products_from_plan


def _paths(n: int) -> list[Path]:
    return [Path(f"/tmp/{i:03d}.jpg") for i in range(1, n + 1)]


def _plan(products, photos=None, n=4):
    photos = photos or [
        PlannedPhoto(index=i, kind="product", shows_product=True) for i in range(1, n + 1)
    ]
    return StorePlan(photos=photos, products=products)


def test_상품_사진과_가격표_사진이_한_상품으로_묶인다():
    plan = _plan(
        [
            PlannedProduct(
                photo_indexes=[1, 2],
                card_photo_index=1,
                product_name="쿠쿠 밥솥",
                original_price=200000,
                sale_price=100000,
            ),
            PlannedProduct(
                photo_indexes=[3, 4],
                card_photo_index=4,
                product_name="다이슨 청소기",
                sale_price=150000,
            ),
        ],
        photos=[
            PlannedPhoto(index=1, kind="product", shows_product=True),
            PlannedPhoto(index=2, kind="price_tag", shows_product=False),
            PlannedPhoto(index=3, kind="price_tag", shows_product=False),
            PlannedPhoto(index=4, kind="product", shows_product=True),
        ],
    )
    products = products_from_plan(plan, _paths(4), ["a", "b", "c", "d"])
    assert [p.product_name for p in products] == ["쿠쿠 밥솥", "다이슨 청소기"]
    assert products[0].photo_kinds == ["product", "price_tag"]
    assert products[0].best_photo.name == "001.jpg"
    assert products[1].best_photo.name == "004.jpg"
    assert products[1].source_file_ids == ["c", "d"]


def test_카드에_쓸_사진이_없으면_발행을_막는다():
    plan = _plan(
        [
            PlannedProduct(
                photo_indexes=[1],
                card_photo_index=0,
                product_name="정체불명",
                sale_price=10000,
            )
        ],
        photos=[PlannedPhoto(index=1, kind="price_tag", shows_product=False)],
        n=1,
    )
    (product,) = products_from_plan(plan, _paths(1), ["a"])
    assert not product.publishable
    assert "알아볼 수 있는 사진" in product.review_reason


def test_같은_사진을_두_상품이_가져가면_먼저_온_쪽만():
    plan = _plan(
        [
            PlannedProduct(photo_indexes=[1, 2], card_photo_index=1, product_name="가", sale_price=1000),
            PlannedProduct(photo_indexes=[2, 3], card_photo_index=3, product_name="나", sale_price=2000),
        ],
        n=3,
    )
    products = products_from_plan(plan, _paths(3), ["a", "b", "c"])
    assert [p.photo_paths for p in products] == [
        ["/tmp/001.jpg", "/tmp/002.jpg"],
        ["/tmp/003.jpg"],
    ]


def test_없는_사진_번호는_버린다():
    plan = _plan(
        [PlannedProduct(photo_indexes=[1, 99], card_photo_index=1, product_name="가", sale_price=1000)],
        n=2,
    )
    (product,) = products_from_plan(plan, _paths(2), ["a", "b"])
    assert product.photo_paths == ["/tmp/001.jpg"]


def test_카드로_고른_사진은_상품이_보이는_것으로_본다():
    """모델이 shows_product 를 빠뜨려도 카드로 고른 이상 상품 사진이다."""
    plan = _plan(
        [PlannedProduct(photo_indexes=[1], card_photo_index=1, product_name="가", sale_price=1000)],
        photos=[PlannedPhoto(index=1, kind="both", shows_product=False)],
        n=1,
    )
    (product,) = products_from_plan(plan, _paths(1), ["a"])
    assert product.publishable
    assert product.best_photo.name == "001.jpg"


def test_사진이_하나도_안_남는_상품은_통째로_뺀다():
    plan = _plan(
        [
            PlannedProduct(photo_indexes=[1], card_photo_index=1, product_name="가", sale_price=1000),
            PlannedProduct(photo_indexes=[1], card_photo_index=1, product_name="나", sale_price=2000),
        ],
        n=1,
    )
    products = products_from_plan(plan, _paths(1), ["a"])
    assert [p.product_name for p in products] == ["가"]


def test_상품_번호는_1부터_차례로():
    plan = _plan(
        [
            PlannedProduct(photo_indexes=[1], card_photo_index=1, product_name="가", sale_price=1000),
            PlannedProduct(photo_indexes=[2], card_photo_index=2, product_name="나", sale_price=2000),
        ],
        n=2,
    )
    products = products_from_plan(plan, _paths(2), ["a", "b"])
    assert [p.group_index for p in products] == [1, 2]


def test_종류를_이상하게_적어도_알아듣는다():
    p = PlannedPhoto(index=1, kind="PRICE TAG")
    assert p.kind == "price_tag"
    assert PlannedPhoto(index=2, kind="상품").kind == "product"


def test_사진_번호를_하나만_적어도_받는다():
    p = PlannedProduct(photo_indexes=3, card_photo_index=3, product_name="가")
    assert p.photo_indexes == [3]


def test_가격표에_없는_상태는_지운다():
    """통판독 결과에도 근거 없는 상태 표현 금지가 그대로 걸린다."""
    plan = _plan(
        [
            PlannedProduct(
                photo_indexes=[1],
                card_photo_index=1,
                product_name="가",
                tag_text="리본가 10,000",
                condition_note="미사용",
                sale_price=10000,
            )
        ],
        n=1,
    )
    (product,) = products_from_plan(plan, _paths(1), ["a"])
    assert product.condition_note == ""


# ------------------------------------------------ 가격표가 이 상품 것인가


def _one(**kw):
    base = dict(photo_indexes=[1], card_photo_index=1, product_name="스팀다리미", sale_price=10000)
    base.update(kw)
    return _plan([PlannedProduct(**base)], n=1)


def test_한_사진에_다른_물건이_같이_찍혔다는_설명만으로는_안_막는다():
    """08-27 사고: '다른 상품도 함께 찍혀 있으나 가격표는 이것으로 확인됨' 이
    '다른 상품' 이라는 말 때문에 발행이 막혔다."""
    plan = _one(
        review_reason="다른 상품(에어쿨러, 휴지통 등)도 함께 찍혀 있으나, 가격표는 이 스팀다리미 것으로 확인됨",
        price_tag_matches=True,
    )
    (product,) = products_from_plan(plan, _paths(1), ["a"])
    assert product.publishable
    assert "다른 상품" in product.cautions  # 리포트에는 남는다


def test_가격표가_다른_물건_것이면_막는다():
    plan = _one(review_reason="가격표가 옆 상품 것으로 보임", price_tag_matches=False)
    (product,) = products_from_plan(plan, _paths(1), ["a"])
    assert not product.publishable
    assert "가격표가 이 상품의 것이 아닐" in product.review_reason


def test_예전_방식은_사유_문장으로_판단한다():
    """통판독이 아닌 길(tag_matches 를 모름)에서는 예전대로 문장을 본다."""
    from reborn.vision import Product, sanity_check

    p = sanity_check(
        Product(
            product_name="가",
            category="기타",
            sale_price=1000,
            photo_paths=["a.jpg"],
            photo_kinds=["both"],
            photo_shows_product=[True],
            best_photo_index=1,
            review_reason="상품과 가격표가 서로 다른 물건입니다",
        )
    )
    assert not p.publishable
