"""카드 한 줄 소개가 "까짐" 한 단어로 나가지 않게."""

from reborn.vision import Product


def _product(**kw) -> Product:
    base = dict(
        group_index=1,
        source_kind="refurb",
        photo_paths=["a.jpg"],
        photo_kinds=["both"],
        product_name="테스트 상품",
        category="주방",
    )
    base.update(kw)
    return Product(**base)


def test_웹설명이_있으면_그대로_쓴다():
    p = _product(spec_line="스테인리스 보온병 355ml", condition_note="까짐")
    assert p.card_line == "스테인리스 보온병 355ml"


def test_상태표기는_소개_자리에_들어가지_않는다():
    """\"까짐\" 은 직원이 적어 둔 고지사항이지 상품 소개가 아니다."""
    p = _product(condition_note="까짐")
    assert p.card_line == ""
    assert p.card_condition == "까짐"


def test_설명과_상태표기는_따로_나간다():
    p = _product(spec_line="6인용 IH 압력밥솥", condition_note="사용감 있음")
    assert p.card_line == "6인용 IH 압력밥솥"
    assert p.card_condition == "사용감 있음"


def test_아무것도_없으면_빈_줄():
    assert _product().card_line == ""


def test_공백만_있는_설명은_설명이_아니다():
    p = _product(spec_line="   ", condition_note="찍힘")
    assert p.card_line == ""
    assert p.card_condition == "찍힘"
