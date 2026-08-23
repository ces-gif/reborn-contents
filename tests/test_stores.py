"""매장이 여럿일 때 설정이 섞이지 않는지."""

from __future__ import annotations

import textwrap

import pytest

from reborn.config import load_settings, load_stores

TWO_STORES = textwrap.dedent(
    """
    drive:
      publish_folder_name: "콘텐츠 발행"
    store:
      handle: "@shared"
      footer_note: "공통 문구"
    card:
      width: 1080
      orig_label: "온라인 판매가"
    stores:
      - id: "a-store"
        drive:
          sources:
            - {name: "리퍼", folder_id: "AAA", kind: "refurb"}
          logo_file_id: "LOGO-A"
        store: {id: "a-store", name: "가게 A", handle: "@a"}
        card: {sale_label: "A 초특가"}
      - id: "b-store"
        drive:
          sources:
            - {name: "리퍼", folder_id: "BBB", kind: "refurb"}
            - {name: "새상품", folder_id: "CCC", kind: "new"}
          logo_folder_id: "LOGOFOLDER-B"
          logo_wordmark: true
        store: {id: "b-store", name: "가게 B"}
        card: {sale_label: "B 초특가"}
    """
)


@pytest.fixture
def two_stores(tmp_path):
    path = tmp_path / "settings.yaml"
    path.write_text(TWO_STORES, encoding="utf-8")
    return path


def test_each_store_keeps_its_own_folders_and_logo(two_stores):
    a, b = load_stores(two_stores)
    assert [s.folder_id for s in a.sources] == ["AAA"]
    assert [s.folder_id for s in b.sources] == ["BBB", "CCC"]
    assert (a.logo_file_id, a.logo_folder_id) == ("LOGO-A", "")
    assert (b.logo_file_id, b.logo_folder_id) == ("", "LOGOFOLDER-B")


def test_a_stores_logo_never_leaks_into_the_other(two_stores):
    """한 매장 로고가 다른 매장 카드에 찍히면 브랜드 사고다."""
    a, b = load_stores(two_stores)
    assert a.logo_file_id != b.logo_file_id
    assert not b.logo_file_id
    assert b.logo_wordmark and not a.logo_wordmark


def test_shared_values_fall_through_to_every_store(two_stores):
    a, b = load_stores(two_stores)
    assert a.publish_folder_name == b.publish_folder_name == "콘텐츠 발행"
    assert a.footer_note == b.footer_note == "공통 문구"
    assert a.orig_label == b.orig_label == "온라인 판매가"
    assert (a.sale_label, b.sale_label) == ("A 초특가", "B 초특가")


def test_store_specific_values_win_over_shared(two_stores):
    a, b = load_stores(two_stores)
    assert a.store_handle == "@a"      # 매장이 덮어썼다
    assert b.store_handle == "@shared"  # 안 덮은 매장은 공통값


def test_only_store_runs_just_that_one(two_stores, monkeypatch):
    monkeypatch.setenv("ONLY_STORE", "b-store")
    picked = load_stores(two_stores)
    assert [s.store_id for s in picked] == ["b-store"]


def test_unknown_only_store_is_an_error_not_a_silent_skip(two_stores, monkeypatch):
    monkeypatch.setenv("ONLY_STORE", "없는가게")
    with pytest.raises(ValueError, match="없는가게"):
        load_stores(two_stores)


def test_load_settings_still_returns_the_first_store(two_stores):
    assert load_settings(two_stores).store_id == "a-store"


def test_the_real_config_has_both_shops_wired_to_different_folders():
    stores = load_stores()
    assert [s.store_id for s in stores] == ["reborn-pt", "fox-ils"]
    folders = [f for s in stores for f in s.source_folder_ids]
    assert len(folders) == len(set(folders)), "매장끼리 같은 사진 폴더를 보고 있습니다"
    publish = [s.publish_parent_id for s in stores]
    assert len(publish) == len(set(publish)), "매장끼리 같은 발행 폴더를 쓰고 있습니다"
