from datetime import datetime, timezone

from reborn.drive import DriveFile
from reborn.grouping import capture_time, filter_for_day, group_by_content, group_photos


def f(name, created="2026-08-21T09:07:22Z"):
    dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
    return DriveFile(id=name, name=name, mime_type="image/jpeg", created_time=dt, modified_time=dt, size=1)


def test_capture_time_from_filename():
    got = capture_time(f("20260821_105013.jpg"))
    assert (got.year, got.month, got.day, got.hour, got.minute, got.second) == (2026, 8, 21, 10, 50, 13)


def test_capture_time_falls_back_to_upload_time():
    got = capture_time(f("scan.jpg", "2026-08-21T00:07:22Z"))
    assert got.hour == 9  # UTC 00:07 -> KST 09:07


def test_groups_split_on_time_gap():
    files = [
        f("20260821_104712.jpg"),
        f("20260821_104733.jpg"),  # 21초 뒤 → 같은 상품
        f("20260821_105013.jpg"),  # 2분 40초 뒤 → 다른 상품
        f("20260821_105018.jpg"),
    ]
    groups = group_photos(files, max_gap_seconds=150)
    assert [len(g) for g in groups] == [2, 2]
    assert groups[0].files[0].name == "20260821_104712.jpg"


def test_filter_for_day_uses_upload_time_in_kst():
    files = [
        f("a.jpg", "2026-08-22T14:59:00Z"),  # KST 08-22 23:59
        f("b.jpg", "2026-08-22T15:01:00Z"),  # KST 08-23 00:01
    ]
    day = datetime(2026, 8, 23, tzinfo=timezone.utc)
    kept = filter_for_day(files, day)
    assert [x.name for x in kept] == ["b.jpg"]


# ---------------------------------------------------------------- 내용 기반 묶기


def _kinds(groups):
    return [g.kinds for g in groups]


def _files(n):
    return [f(f"{i:02d}-20260823_16{i:02d}00.jpg") for i in range(1, n + 1)]


def test_both_photo_starts_a_new_product():
    files = _files(4)
    groups = group_by_content(files, ["both", "price_tag", "both", "price_tag"])
    assert _kinds(groups) == [["both", "price_tag"], ["both", "price_tag"]]


def test_product_then_tag_pairs_up():
    files = _files(4)
    groups = group_by_content(files, ["product", "price_tag", "product", "price_tag"])
    assert _kinds(groups) == [["product", "price_tag"], ["product", "price_tag"]]


def test_tag_first_then_product_pairs_up():
    files = _files(4)
    groups = group_by_content(files, ["price_tag", "product", "price_tag", "product"])
    assert _kinds(groups) == [["price_tag", "product"], ["price_tag", "product"]]


def test_two_product_photos_before_the_tag_stay_together():
    files = _files(6)
    groups = group_by_content(
        files, ["product", "product", "price_tag", "product", "product", "price_tag"]
    )
    assert _kinds(groups) == [
        ["product", "product", "price_tag"],
        ["product", "product", "price_tag"],
    ]


def test_only_both_photos_split_one_per_product():
    files = _files(3)
    groups = group_by_content(files, ["both", "both", "both"])
    assert _kinds(groups) == [["both"], ["both"], ["both"]]


def test_other_photos_are_dropped():
    files = _files(5)
    groups = group_by_content(files, ["product", "price_tag", "other", "product", "price_tag"])
    assert _kinds(groups) == [["product", "price_tag"], ["product", "price_tag"]]
    assert all(g.files[0].name != files[2].name for g in groups)


def test_missing_tag_does_not_swallow_everything():
    files = _files(10)
    groups = group_by_content(files, ["product"] * 10, max_size=6)
    assert [len(g) for g in groups] == [6, 4]


def test_group_indexes_are_renumbered():
    files = _files(4)
    groups = group_by_content(files, ["both", "other", "both", "price_tag"])
    assert [g.index for g in groups] == [1, 2]


def test_31_photos_do_not_collapse_into_two_products():
    """실제로 겪은 사고: 31장이 2묶음이 되고 27장이 버려졌다."""
    kinds = (["both", "price_tag"] * 15) + ["both"]
    files = _files(31)
    groups = group_by_content(files, kinds)
    assert len(groups) == 16
    assert sum(len(g) for g in groups) == 31
