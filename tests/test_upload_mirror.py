"""같은 날짜를 다시 돌렸을 때 예전 파일이 남지 않는지."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from reborn.drive import DriveFile, upload_tree


def folder_file(name: str) -> DriveFile:
    dt = datetime(2026, 8, 23, tzinfo=timezone.utc)
    return DriveFile(
        id=f"id-{name}",
        name=name,
        mime_type="application/vnd.google-apps.folder",
        created_time=dt,
        modified_time=dt,
        size=0,
    )


def plain_file(name: str) -> DriveFile:
    dt = datetime(2026, 8, 23, tzinfo=timezone.utc)
    return DriveFile(
        id=f"id-{name}", name=name, mime_type="image/png",
        created_time=dt, modified_time=dt, size=10,
    )


class FakeDrive:
    def __init__(self, existing: dict[str, list[DriveFile]] | None = None):
        self.existing = existing or {}
        self.trashed: list[str] = []
        self.uploaded: list[str] = []
        self.folders: dict[tuple[str, str], str] = {}

    def list_children(self, folder_id, only_images=False, page_size=200):
        return list(self.existing.get(folder_id, []))

    def ensure_folder(self, name, parent_id=None):
        return self.folders.setdefault((parent_id, name), f"{parent_id}/{name}")

    def upload(self, path: Path, parent_id, mime_type=None, name=None):
        self.uploaded.append(f"{parent_id}/{path.name}")
        return f"file-{path.name}"

    def trash(self, file_id):
        self.trashed.append(file_id)


def make_out(tmp_path: Path) -> Path:
    out = tmp_path / "out"
    (out / "카드뉴스").mkdir(parents=True)
    (out / "카드뉴스" / "01-새상품.png").write_bytes(b"x")
    (out / "리포트.md").write_text("ok", encoding="utf-8")
    return out


def test_old_run_files_are_cleared_out(tmp_path):
    """예전 실행의 03번과 새 실행의 03번이 한 폴더에 나란히 남으면 안 된다."""
    drive = FakeDrive({
        "DAY": [plain_file("리포트.md"), folder_file("카드뉴스")],
        "DAY/카드뉴스": [plain_file("01-새상품.png"), plain_file("03-예전상품.png")],
    })
    upload_tree(drive, make_out(tmp_path), "DAY")
    assert drive.trashed == ["id-03-예전상품.png"]


def test_folders_are_never_trashed(tmp_path):
    drive = FakeDrive({
        "DAY": [folder_file("카드뉴스"), folder_file("블로그")],
        "DAY/카드뉴스": [],
    })
    upload_tree(drive, make_out(tmp_path), "DAY")
    assert drive.trashed == []


def test_the_ledger_survives_cleanup(tmp_path):
    """원장을 지우면 어제 처리한 사진을 오늘 또 처리한다."""
    drive = FakeDrive({
        "DAY": [plain_file("_ledger.json"), folder_file("카드뉴스")],
        "DAY/카드뉴스": [],
    })
    upload_tree(drive, make_out(tmp_path), "DAY")
    assert drive.trashed == []


def test_mirror_can_be_turned_off(tmp_path):
    drive = FakeDrive({
        "DAY": [], "DAY/카드뉴스": [plain_file("03-예전상품.png")],
    })
    upload_tree(drive, make_out(tmp_path), "DAY", mirror=False)
    assert drive.trashed == []


def test_a_failed_cleanup_does_not_stop_publishing(tmp_path):
    """정리에 실패했다고 하루치 발행을 날리지 않는다."""
    class Grumpy(FakeDrive):
        def list_children(self, folder_id, only_images=False, page_size=200):
            raise RuntimeError("권한 없음")

    drive = Grumpy()
    uploaded = upload_tree(drive, make_out(tmp_path), "DAY")
    assert "카드뉴스/01-새상품.png" in uploaded
