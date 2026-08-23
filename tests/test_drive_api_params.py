"""구글 API 를 부를 때 인자 이름을 실제 라이브러리 규칙대로 쓰는지 확인한다.

구글 discovery 클라이언트는 파라미터 이름이 camelCase(fileId)다. snake_case(file_id)로
부르면 'Got an unexpected keyword argument file_id' 라는 TypeError 가 난다.
가짜 드라이브로만 테스트하면 이 실수가 안 잡혀서, 실제 클라이언트처럼
모르는 인자를 거부하는 mock 으로 따로 확인한다.
"""

from __future__ import annotations

import inspect
import ssl

import pytest

from reborn import drive as drive_mod
from reborn.drive import Drive

# 구글 discovery 클라이언트가 실제로 받는 인자 이름 (files 리소스)
ALLOWED = {
    "get_media": {"fileId", "acknowledgeAbuse", "supportsAllDrives", "supportsTeamDrives"},
    "get": {"fileId", "fields", "supportsAllDrives", "supportsTeamDrives",
            "acknowledgeAbuse", "includeLabels", "includePermissionsForView"},
    "update": {"fileId", "body", "media_body", "fields", "addParents", "removeParents",
               "supportsAllDrives", "supportsTeamDrives", "keepRevisionForever",
               "ocrLanguage", "useContentAsIndexableText", "includeLabels",
               "includePermissionsForView"},
    "create": {"body", "media_body", "fields", "supportsAllDrives", "supportsTeamDrives",
               "ignoreDefaultVisibility", "keepRevisionForever", "ocrLanguage",
               "useContentAsIndexableText", "includeLabels", "includePermissionsForView"},
    "list": {"q", "fields", "pageSize", "pageToken", "orderBy", "spaces", "corpora",
             "driveId", "includeItemsFromAllDrives", "supportsAllDrives",
             "supportsTeamDrives", "includeLabels", "includePermissionsForView"},
}


class StrictMethod:
    """실제 discovery 클라이언트처럼, 모르는 인자를 받으면 TypeError 를 낸다."""

    def __init__(self, name, result):
        self.name = name
        self.result = result
        self.calls: list[dict] = []

    def __call__(self, **kwargs):
        for key in kwargs:
            if key not in ALLOWED[self.name]:
                raise TypeError(f"Got an unexpected keyword argument {key}")
        self.calls.append(kwargs)
        return _Executable(self.result)


class _Executable:
    def __init__(self, result):
        self.result = result

    def execute(self):
        return self.result


class StrictFiles:
    def __init__(self):
        self.get_media = StrictMethod("get_media", b"")
        self.get = StrictMethod("get", {"parents": ["PARENT"]})
        self.update = StrictMethod("update", {"id": "u"})
        self.create = StrictMethod("create", {"id": "c"})
        self.list = StrictMethod("list", {"files": []})


class StrictService:
    def __init__(self):
        self._files = StrictFiles()

    def files(self):
        return self._files


@pytest.fixture
def drive():
    return Drive(service=StrictService())


def test_get_parent_uses_camelcase_fileId(drive):
    assert drive.get_parent("abc") == "PARENT"
    assert drive.service.files().get.calls[0]["fileId"] == "abc"


def test_list_children_params_are_accepted(drive):
    assert drive.list_children("folder") == []
    call = drive.service.files().list.calls[0]
    assert call["supportsAllDrives"] is True
    assert call["includeItemsFromAllDrives"] is True


def test_download_calls_get_media_with_fileId(drive, monkeypatch, tmp_path):
    """다운로드가 fileId 로 불리는지 확인 — 여기서 file_id 오타가 났었다."""
    import reborn.drive as drive_module

    class FakeDownloader:
        def __init__(self, buffer, request, chunksize=None):
            self.buffer = buffer

        def next_chunk(self):
            self.buffer.write(b"hello")
            return None, True

    monkeypatch.setattr(drive_module, "MediaIoBaseDownload", FakeDownloader)
    dest = drive.download("abc", tmp_path / "x.jpg")
    assert dest.read_bytes() == b"hello"
    assert drive.service.files().get_media.calls[0]["fileId"] == "abc"


def test_every_google_call_in_drive_module_uses_camelcase():
    """소스에 snake_case 파라미터가 다시 새어 들어오지 않게 막는다."""
    source = inspect.getsource(__import__("reborn.drive", fromlist=["drive"]))
    assert "file_id=file_id" not in source
    assert "page_token=" not in source
    assert "page_size=" not in source


# --------------------------------------------------- 끊긴 연결에서 살아나기


def test_reconnects_and_retries_when_the_connection_drops(monkeypatch):
    """판독에 십수 분 걸리는 동안 구글 연결이 끊긴다.

    실제로 카드뉴스 11장을 다 만들어 놓고 마지막 업로드에서 SSLEOFError 로
    전부 날렸다. 끊긴 연결은 버리고 새로 붙어서 다시 해야 한다.
    """
    monkeypatch.setattr(drive_mod.time, "sleep", lambda s: None)
    client = drive_mod.Drive.__new__(drive_mod.Drive)
    client._owns_service = True
    client.service = "old"
    monkeypatch.setattr(drive_mod.Drive, "_build_service", staticmethod(lambda: "new"))

    calls = []

    def flaky():
        calls.append(client.service)
        if len(calls) < 3:
            raise ssl.SSLEOFError("EOF occurred in violation of protocol")
        return "ok"

    assert client._retry(flaky) == "ok"
    assert calls == ["old", "new", "new"]  # 끊길 때마다 새로 붙었다


def test_gives_up_after_the_last_attempt(monkeypatch):
    monkeypatch.setattr(drive_mod.time, "sleep", lambda s: None)
    client = drive_mod.Drive.__new__(drive_mod.Drive)
    client._owns_service = True
    client.service = "s"
    monkeypatch.setattr(drive_mod.Drive, "_build_service", staticmethod(lambda: "s"))

    def always_broken():
        raise ConnectionResetError("nope")

    with pytest.raises(ConnectionResetError):
        client._retry(always_broken, attempts=3)


def test_injected_service_is_never_rebuilt(monkeypatch):
    """테스트가 넣어준 가짜 서비스를 우리가 갈아치우면 안 된다."""
    monkeypatch.setattr(drive_mod.time, "sleep", lambda s: None)
    client = drive_mod.Drive.__new__(drive_mod.Drive)
    client._owns_service = False
    client.service = "fake"

    calls = []

    def flaky():
        calls.append(client.service)
        if len(calls) < 2:
            raise ssl.SSLEOFError("boom")
        return "ok"

    assert client._retry(flaky) == "ok"
    assert calls == ["fake", "fake"]
