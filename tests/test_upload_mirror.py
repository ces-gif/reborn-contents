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
        self.as_docs: dict[str, bool] = {}
        self.folders: dict[tuple[str, str], str] = {}

    def list_children(self, folder_id, only_images=False, page_size=200):
        return list(self.existing.get(folder_id, []))

    def ensure_folder(self, name, parent_id=None):
        return self.folders.setdefault((parent_id, name), f"{parent_id}/{name}")

    def upload(self, path: Path, parent_id, mime_type=None, name=None, as_doc=False):
        self.uploaded.append(f"{parent_id}/{name or path.name}")
        self.as_docs[name or path.name] = as_doc
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


# ------------------------------------------------ 캡션은 구글 문서로 올라간다


def doc_file(name: str) -> DriveFile:
    dt = datetime(2026, 8, 23, tzinfo=timezone.utc)
    return DriveFile(
        id=f"id-{name}", name=name, mime_type="application/vnd.google-apps.document",
        created_time=dt, modified_time=dt, size=10,
    )


def make_out_with_caption(tmp_path: Path) -> Path:
    out = make_out(tmp_path)
    (out / "카드뉴스" / "2026-09-05-릴스캡션.txt").write_text("후킹", encoding="utf-8")
    return out


def test_caption_txt_is_uploaded_as_a_google_doc(tmp_path):
    """폰 드라이브 앱에서 txt 는 잘 안 열린다. 문서여야 그 자리에서 복사한다."""
    drive = FakeDrive()
    upload_tree(drive, make_out_with_caption(tmp_path), "DAY")
    assert drive.as_docs["2026-09-05-릴스캡션"] is True
    assert drive.as_docs["01-새상품.png"] is False


def test_the_caption_doc_drops_the_txt_extension(tmp_path):
    """구글 문서가 된 뒤에는 .txt 가 아니다. 이름에 남겨두면 헷갈린다."""
    drive = FakeDrive()
    upload_tree(drive, make_out_with_caption(tmp_path), "DAY")
    assert "DAY/카드뉴스/2026-09-05-릴스캡션" in drive.uploaded
    assert "DAY/카드뉴스/2026-09-05-릴스캡션.txt" not in drive.uploaded


def test_yesterdays_caption_doc_is_not_trashed_by_todays_cleanup(tmp_path):
    """이름이 어긋나면 방금 올린 문서를 정리가 도로 버린다. 실제로 위험했던 부분."""
    drive = FakeDrive({
        "DAY": [folder_file("카드뉴스")],
        "DAY/카드뉴스": [doc_file("2026-09-05-릴스캡션"), plain_file("01-새상품.png")],
    })
    upload_tree(drive, make_out_with_caption(tmp_path), "DAY")
    assert drive.trashed == []


def test_a_leftover_txt_caption_is_cleaned_up(tmp_path):
    """문서로 바꾸기 전에 올라간 txt 는 다음 실행 때 치운다. 둘이 나란히 있으면 헷갈린다."""
    drive = FakeDrive({
        "DAY": [folder_file("카드뉴스")],
        "DAY/카드뉴스": [plain_file("2026-09-05-릴스캡션.txt")],
    })
    upload_tree(drive, make_out_with_caption(tmp_path), "DAY")
    assert drive.trashed == ["id-2026-09-05-릴스캡션.txt"]
