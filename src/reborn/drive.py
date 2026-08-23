"""Google Drive 읽기/쓰기.

인증은 세 가지를 지원한다 (환경변수로만 받는다, 저장소에 키를 두지 않는다).
앞에 있는 것부터 먼저 쓴다:

1. 서비스 계정 키 - GOOGLE_SERVICE_ACCOUNT_JSON (JSON 원문 또는 base64)
   → 가장 간단하지만, 조직 정책 iam.disableServiceAccountKeyCreation 이 켜져 있으면
     키를 아예 만들 수 없다. 그럴 땐 2번이나 3번을 쓴다.
2. 사용자 OAuth - GOOGLE_OAUTH_CLIENT_ID / GOOGLE_OAUTH_CLIENT_SECRET /
   GOOGLE_OAUTH_REFRESH_TOKEN
   → 은성님 계정 권한으로 동작한다. 서비스 계정 키를 못 만들 때 가장 빠른 우회로.
3. 키 없는 인증 (Workload Identity Federation / ADC)
   → 깃허브 액션에서 google-github-actions/auth 로 OIDC 인증을 하면
     GOOGLE_APPLICATION_CREDENTIALS 가 자동으로 잡힌다. 키 파일이 아예 없어서
     구글이 권장하는 방식이고, 위 조직 정책과도 충돌하지 않는다.
"""

from __future__ import annotations

import base64
import binascii
import io
import json
import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials as UserCredentials
from google.oauth2.service_account import Credentials as ServiceCredentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

log = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/drive"]
FOLDER_MIME = "application/vnd.google-apps.folder"
IMAGE_MIMES = ("image/jpeg", "image/png", "image/heic", "image/heif", "image/webp")


class DriveAuthError(RuntimeError):
    pass


@dataclass
class DriveFile:
    id: str
    name: str
    mime_type: str
    created_time: datetime
    modified_time: datetime
    size: int

    @property
    def is_image(self) -> bool:
        return self.mime_type in IMAGE_MIMES


def _parse_rfc3339(value: str | None) -> datetime:
    if not value:
        return datetime.fromtimestamp(0, tz=timezone.utc)
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _decode_service_account(raw: str) -> dict:
    raw = raw.strip()
    if raw.startswith("{"):
        return json.loads(raw)
    try:
        return json.loads(base64.b64decode(raw).decode("utf-8"))
    except (binascii.Error, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DriveAuthError(
            "GOOGLE_SERVICE_ACCOUNT_JSON 을 읽을 수 없습니다. JSON 원문이나 base64 인코딩 값을 넣어주세요."
        ) from exc


def build_credentials():
    sa_raw = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    if sa_raw:
        info = _decode_service_account(sa_raw)
        creds = ServiceCredentials.from_service_account_info(info, scopes=SCOPES)
        subject = os.environ.get("GOOGLE_IMPERSONATE_SUBJECT")
        if subject:  # Workspace 도메인 위임을 쓰는 경우
            creds = creds.with_subject(subject)
        return creds

    refresh = os.environ.get("GOOGLE_OAUTH_REFRESH_TOKEN")
    client_id = os.environ.get("GOOGLE_OAUTH_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")
    if refresh and client_id and client_secret:
        creds = UserCredentials(
            token=None,
            refresh_token=refresh,
            client_id=client_id,
            client_secret=client_secret,
            token_uri="https://oauth2.googleapis.com/token",
            scopes=SCOPES,
        )
        creds.refresh(Request())
        return creds

    # 3) 키 없는 인증 — 깃허브 액션의 OIDC(Workload Identity Federation) 등
    #    google-github-actions/auth 가 잡아준 자격증명을 그대로 쓴다.
    try:
        import google.auth

        creds, _ = google.auth.default(scopes=SCOPES)
        log.info("키 없는 기본 자격증명(ADC)으로 드라이브에 연결합니다")
        return creds
    except Exception as exc:
        log.debug("기본 자격증명 없음: %s", exc)

    raise DriveAuthError(
        "구글 드라이브 인증 정보가 없습니다. 아래 중 하나를 설정하세요 (docs/SETUP.md 참고):\n"
        "  1) GOOGLE_SERVICE_ACCOUNT_JSON — 서비스 계정 키 JSON\n"
        "  2) GOOGLE_OAUTH_CLIENT_ID / GOOGLE_OAUTH_CLIENT_SECRET / GOOGLE_OAUTH_REFRESH_TOKEN\n"
        "  3) 깃허브 액션에서 google-github-actions/auth 로 키 없는 OIDC 인증"
    )


class Drive:
    def __init__(self, service=None):
        self.service = service or build(
            "drive", "v3", credentials=build_credentials(), cache_discovery=False
        )

    # ------------------------------------------------------------------ read

    def list_children(
        self, folder_id: str, *, only_images: bool = False, page_size: int = 200
    ) -> list[DriveFile]:
        query = f"'{folder_id}' in parents and trashed = false"
        if only_images:
            mimes = " or ".join(f"mimeType = '{m}'" for m in IMAGE_MIMES)
            query += f" and ({mimes})"

        files: list[DriveFile] = []
        page_token = None
        while True:
            resp = self._retry(
                lambda: self.service.files()
                .list(
                    q=query,
                    fields="nextPageToken, files(id, name, mimeType, createdTime, modifiedTime, size)",
                    pageSize=page_size,
                    pageToken=page_token,
                    orderBy="createdTime",
                    supportsAllDrives=True,
                    includeItemsFromAllDrives=True,
                )
                .execute()
            )
            for item in resp.get("files", []):
                files.append(
                    DriveFile(
                        id=item["id"],
                        name=item["name"],
                        mime_type=item.get("mimeType", ""),
                        created_time=_parse_rfc3339(item.get("createdTime")),
                        modified_time=_parse_rfc3339(item.get("modifiedTime")),
                        size=int(item.get("size", 0) or 0),
                    )
                )
            page_token = resp.get("nextPageToken")
            if not page_token:
                break
        return files

    def download(self, file_id: str, dest: Path) -> Path:
        dest.parent.mkdir(parents=True, exist_ok=True)
        request = self.service.files().get_media(file_id=file_id, supportsAllDrives=True)
        buffer = io.BytesIO()
        downloader = MediaIoBaseDownload(buffer, request, chunksize=8 * 1024 * 1024)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        dest.write_bytes(buffer.getvalue())
        return dest

    def find_child(self, parent_id: str, name: str, *, mime_type: str | None = None) -> str | None:
        safe = name.replace("'", "\\'")
        query = f"'{parent_id}' in parents and name = '{safe}' and trashed = false"
        if mime_type:
            query += f" and mimeType = '{mime_type}'"
        resp = self._retry(
            lambda: self.service.files()
            .list(
                q=query,
                fields="files(id, name)",
                pageSize=1,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
            )
            .execute()
        )
        files = resp.get("files", [])
        return files[0]["id"] if files else None

    def get_parent(self, file_id: str) -> str | None:
        meta = self._retry(
            lambda: self.service.files()
            .get(fileId=file_id, fields="parents", supportsAllDrives=True)
            .execute()
        )
        parents = meta.get("parents") or []
        return parents[0] if parents else None

    # ----------------------------------------------------------------- write

    def ensure_folder(self, name: str, parent_id: str | None = None) -> str:
        if parent_id:
            existing = self.find_child(parent_id, name, mime_type=FOLDER_MIME)
            if existing:
                return existing
        body: dict = {"name": name, "mimeType": FOLDER_MIME}
        if parent_id:
            body["parents"] = [parent_id]
        folder = self._retry(
            lambda: self.service.files()
            .create(body=body, fields="id", supportsAllDrives=True)
            .execute()
        )
        log.info("드라이브 폴더 생성: %s (%s)", name, folder["id"])
        return folder["id"]

    def upload(
        self, path: Path, parent_id: str, *, mime_type: str | None = None, name: str | None = None
    ) -> str:
        name = name or path.name
        mime_type = mime_type or _guess_mime(path)
        media = MediaFileUpload(str(path), mimetype=mime_type, resumable=path.stat().st_size > 5_000_000)
        existing = self.find_child(parent_id, name)
        if existing:
            file = self._retry(
                lambda: self.service.files()
                .update(fileId=existing, media_body=media, fields="id", supportsAllDrives=True)
                .execute()
            )
        else:
            file = self._retry(
                lambda: self.service.files()
                .create(
                    body={"name": name, "parents": [parent_id]},
                    media_body=media,
                    fields="id",
                    supportsAllDrives=True,
                )
                .execute()
            )
        return file["id"]

    # ----------------------------------------------------------------- utils

    @staticmethod
    def _retry(call, *, attempts: int = 5):
        delay = 2.0
        last: Exception | None = None
        for attempt in range(attempts):
            try:
                return call()
            except HttpError as exc:  # 429/5xx 는 재시도한다
                status = getattr(exc.resp, "status", 0)
                if status not in (403, 429, 500, 502, 503, 504) or attempt == attempts - 1:
                    raise
                last = exc
                log.warning("드라이브 API %s, %.0f초 후 재시도 (%d/%d)", status, delay, attempt + 1, attempts)
                time.sleep(delay)
                delay *= 2
        raise last  # pragma: no cover


def _guess_mime(path: Path) -> str:
    suffix = path.suffix.lower()
    return {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".md": "text/markdown",
        ".html": "text/html",
        ".json": "application/json",
        ".txt": "text/plain",
    }.get(suffix, "application/octet-stream")


def upload_tree(drive: Drive, local_dir: Path, parent_id: str) -> dict[str, str]:
    """local_dir 안의 파일/폴더를 드라이브에 그대로 올린다. {상대경로: fileId}"""
    uploaded: dict[str, str] = {}
    for entry in sorted(local_dir.iterdir()):
        if entry.is_dir():
            child = drive.ensure_folder(entry.name, parent_id)
            for rel, fid in upload_tree(drive, entry, child).items():
                uploaded[f"{entry.name}/{rel}"] = fid
        else:
            uploaded[entry.name] = drive.upload(entry, parent_id)
    return uploaded


def iter_images(files: Iterable[DriveFile]) -> list[DriveFile]:
    return [f for f in files if f.is_image]
