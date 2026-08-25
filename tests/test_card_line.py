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


def test_설명이_없으면_상태표기에_출처를_붙인다():
    p = _product(condition_note="까짐")
    assert p.card_line == "가격표 표기: 까짐"


def test_이미_가격표로_시작하면_덧붙이지_않는다():
    p = _product(condition_note="가격표 표기: 전시상품")
    assert p.card_line == "가격표 표기: 전시상품"


def test_아무것도_없으면_빈_줄():
    assert _product().card_line == ""


def test_공백만_있는_설명은_설명이_아니다():
    p = _product(spec_line="   ", condition_note="찍힘")
    assert p.card_line == "가격표 표기: 찍힘"
