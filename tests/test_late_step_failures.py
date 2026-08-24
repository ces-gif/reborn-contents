"""카드뉴스를 다 만든 뒤의 단계가 넘어져도 발행은 계속되는지.

실제 사고: 일산 사진 14장을 다 판독하고 카드뉴스 13장까지 만든 뒤,
블로그 글의 한 칸 형식이 어긋나 매장 전체가 죽었다. 13장이 통째로 사라졌다.
"""

from __future__ import annotations

import pytest

from reborn.blog import PostDraft


def draft(**kw) -> PostDraft:
    base = dict(
        category_tag="오늘의 특가",
        title="제목",
        intro=[["안녕하세요."]],
        transition=["그래서 준비했어요."],
        items=[],
        table_intro="한눈에 보시라고 정리했어요.",
        table_wrapup=["표에서 보시다시피 반값입니다."],
        closing=[["오늘도 좋은 하루 되세요."]],
        tags=["리본마켓"],
    )
    base.update(kw)
    return PostDraft(**base)


def test_a_paragraph_wrapped_line_list_is_accepted():
    """모델이 한 겹 더 씌워 보내도 글쓰기가 죽지 않는다."""
    got = draft(table_wrapup=[["아기욕조는 33,000원"], ["카시트는 159,500원입니다."]])
    assert got.table_wrapup == ["아기욕조는 33,000원", "카시트는 159,500원입니다."]


def test_a_plain_line_list_is_untouched():
    assert draft(table_wrapup=["한 줄", "두 줄"]).table_wrapup == ["한 줄", "두 줄"]


def test_nested_tags_are_flattened_too():
    assert draft(tags=[["리본마켓", "평택리퍼브"], ["여우마켓"]]).tags == [
        "리본마켓",
        "평택리퍼브",
        "여우마켓",
    ]


def test_mixed_shapes_survive():
    assert draft(table_wrapup=["평범한 줄", ["감싼 줄"]]).table_wrapup == ["평범한 줄", "감싼 줄"]


def test_a_truly_wrong_type_still_fails():
    """아무 모양이나 받아주면 안 된다 — 진짜 잘못된 건 걸러야 한다."""
    with pytest.raises(Exception):
        draft(table_wrapup=42)
