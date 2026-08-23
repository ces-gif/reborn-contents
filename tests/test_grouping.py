from datetime import datetime, timezone

from reborn.drive import DriveFile
from reborn.grouping import capture_time, filter_for_day, group_photos


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
