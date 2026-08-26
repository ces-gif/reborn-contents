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


# ------------------------------------------------ 상품명에 상태가 또 들어간 경우


def test_상품명_끝의_괄호가_상태표기와_같으면_뗀다():
    from reborn.vision import _drop_repeated_condition as drop

    assert drop("라즈웰 트롤리 화이트 사각5단(까짐)", "까짐") == "라즈웰 트롤리 화이트 사각5단"
    assert drop("옷장 2단 (모서리 까짐)", "까짐") == "옷장 2단"
    assert drop("의자（사용감）", "사용감 있음") == "의자"


def test_상관없는_괄호는_그대로_둔다():
    from reborn.vision import _drop_repeated_condition as drop

    assert drop("찜기 냄비(33cm)", "까짐") == "찜기 냄비(33cm)"
    assert drop("이동장 케이지(화이트)", "찌그러짐") == "이동장 케이지(화이트)"


def test_상태표기가_없으면_건드리지_않는다():
    from reborn.vision import _drop_repeated_condition as drop

    assert drop("트롤리(까짐)", "") == "트롤리(까짐)"


def test_괄호를_떼면_이름이_없어지는_경우엔_그대로_둔다():
    from reborn.vision import _drop_repeated_condition as drop

    assert drop("(까짐)", "까짐") == "(까짐)"
