"""카드뉴스 PNG 를 공개 URL 로 올린다.

인스타그램 그래프 API 는 파일 업로드를 받지 않고 **공개된 이미지 URL** 만 받는다.
구글 드라이브 링크는 바이러스 검사 안내 페이지가 끼어들어서 인스타가 못 읽는 경우가 많다.
그래서 Cloudflare R2(S3 호환) 공개 버킷에 올려서 그 URL 을 쓴다.

R2 대신 다른 S3 호환 스토리지(AWS S3, MinIO 등)를 써도 그대로 동작한다 —
R2_ENDPOINT 와 R2_PUBLIC_BASE_URL 만 바꾸면 된다.

설정이 없으면 조용히 비활성 상태가 되고, 인스타 업로드 단계는 건너뛴다.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

log = logging.getLogger(__name__)


class NotConfigured(RuntimeError):
    pass


def is_configured() -> bool:
    return all(
        os.environ.get(key)
        for key in ("R2_ACCOUNT_ID", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY", "R2_BUCKET")
    ) or all(
        os.environ.get(key)
        for key in ("R2_ENDPOINT", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY", "R2_BUCKET")
    )


def _endpoint() -> str:
    explicit = os.environ.get("R2_ENDPOINT")
    if explicit:
        return explicit
    account = os.environ.get("R2_ACCOUNT_ID")
    return f"https://{account}.r2.cloudflarestorage.com"


def _public_base() -> str:
    base = os.environ.get("R2_PUBLIC_BASE_URL")
    if not base:
        raise NotConfigured(
            "R2_PUBLIC_BASE_URL 이 없습니다. R2 버킷의 공개 주소(예: https://pub-xxxx.r2.dev)를 "
            "설정하세요. 인스타그램은 공개 URL 만 받습니다."
        )
    return base.rstrip("/")


def _client():
    try:
        import boto3
        from botocore.config import Config
    except ImportError as exc:  # pragma: no cover
        raise NotConfigured("boto3 가 설치되어 있지 않습니다 (requirements.txt 확인)") from exc

    return boto3.client(
        "s3",
        endpoint_url=_endpoint(),
        aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
        region_name=os.environ.get("R2_REGION", "auto"),
        config=Config(signature_version="s3v4", retries={"max_attempts": 4, "mode": "standard"}),
    )


def upload_public(path: Path, key: str) -> str:
    """파일을 올리고 공개 URL 을 돌려준다."""
    if not is_configured():
        raise NotConfigured(
            "이미지 공개 호스팅이 설정되지 않았습니다. "
            "R2_ACCOUNT_ID / R2_ACCESS_KEY_ID / R2_SECRET_ACCESS_KEY / R2_BUCKET / "
            "R2_PUBLIC_BASE_URL 을 설정하세요. (docs/SETUP.md 참고)"
        )
    base = _public_base()
    client = _client()
    client.upload_file(
        str(path),
        os.environ["R2_BUCKET"],
        key,
        ExtraArgs={"ContentType": "image/png", "CacheControl": "public, max-age=86400"},
    )
    url = f"{base}/{key}"
    log.info("공개 URL 업로드: %s", url)
    return url
