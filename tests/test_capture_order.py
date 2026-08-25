"""아이폰 사진을 찍은 순서대로 세우는지."""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from PIL import Image

from reborn.drive import DriveFile
from reborn.grouping import capture_time
from reborn.imaging import exif_capture_time

KST = ZoneInfo("Asia/Seoul")


def _photo(path, *, taken: str | None = None, dated: str | None = None):
    img = Image.new("RGB", (24, 24), "white")
    if taken is None and dated is None:
        img.save(path)
        return path
    exif = Image.Exif()
    if dated:
        exif[306] = dated
    if taken:
        exif[0x8769] = {36867: taken}
    img.save(path, exif=exif)
    return path


def test_촬영시각을_파일_안에서_읽는다(tmp_path):
    p = _photo(tmp_path / "IMG_7499.jpg", taken="2026:08:25 10:18:22")
    assert exif_capture_time(p) == datetime(2026, 8, 25, 10, 18, 22, tzinfo=KST)


def test_DateTimeOriginal_이_DateTime_보다_우선(tmp_path):
    p = _photo(tmp_path / "IMG_7500.jpg", taken="2026:08:25 09:00:00", dated="2026:08:25 23:59:59")
    assert exif_capture_time(p).hour == 9


def test_EXIF_가_없으면_None(tmp_path):
    assert exif_capture_time(_photo(tmp_path / "plain.png")) is None


def test_아이폰_업로드_순서가_뒤섞여도_찍은_순서로_선다(tmp_path):
    """드라이브 업로드 시각은 뒤죽박죽인데 EXIF 로는 제대로 서야 한다."""
    shots = {
        "IMG_7499.jpg": "2026:08:25 10:00:00",  # 상품
        "IMG_7500.jpg": "2026:08:25 10:00:20",  # 그 가격표
        "IMG_7501.jpg": "2026:08:25 10:03:00",  # 다음 상품
    }
    paths = {n: _photo(tmp_path / n, taken=t) for n, t in shots.items()}
    # 업로드가 병렬로 끝나 순서가 뒤집힌 상황
    uploaded = ["IMG_7501.jpg", "IMG_7499.jpg", "IMG_7500.jpg"]
    files = [
        DriveFile(
            id=f"id-{i}",
            name=name,
            mime_type="image/jpeg",
            created_time=datetime(2026, 8, 25, 3, 0, i, tzinfo=timezone.utc),
            modified_time=datetime(2026, 8, 25, 3, 0, i, tzinfo=timezone.utc),
            size=1,
        )
        for i, name in enumerate(uploaded)
    ]

    by_name = {f.name: f for f in files}
    files.sort(key=lambda f: exif_capture_time(paths[f.name]) or capture_time(f))
    assert [f.name for f in files] == ["IMG_7499.jpg", "IMG_7500.jpg", "IMG_7501.jpg"]
    assert by_name  # 이름으로 되짚을 수 있어야 리포트에 적을 수 있다


def test_EXIF_가_없으면_업로드_시각으로_돌아간다(tmp_path):
    p = _photo(tmp_path / "plain.jpg")
    f = DriveFile(
        id="id-x",
        name="plain.jpg",
        mime_type="image/jpeg",
        created_time=datetime(2026, 8, 25, 3, 0, 0, tzinfo=timezone.utc),
        modified_time=datetime(2026, 8, 25, 3, 0, 0, tzinfo=timezone.utc),
        size=1,
    )
    assert (exif_capture_time(p) or capture_time(f)).hour == 12
