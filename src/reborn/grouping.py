"""같은 상품을 여러 장 찍은 사진을 하나의 '상품 묶음'으로 모은다.

매장에서 상품을 찍을 때는 한 상품을 몇 초 안에 2~4장 연속으로 찍고,
다음 상품으로 이동하면서 자연스럽게 시간 간격이 벌어진다.
그래서 촬영 시각의 간격으로 끊으면 상품 단위가 꽤 정확하게 나뉜다.

촬영 시각은 파일명(20260821_105013.jpg)에서 먼저 읽고,
없으면 드라이브 업로드 시각(createdTime)을 쓴다.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from .drive import DriveFile

# 20260821_105013.jpg / IMG_20260821_105013.jpg / 20260821105013.jpg
_PATTERNS = [
    re.compile(r"(?P<d>\d{8})[_\-]?(?P<t>\d{6})"),
    re.compile(r"(?P<d>\d{4}-\d{2}-\d{2})[ _T](?P<t>\d{2}-?\d{2}-?\d{2})"),
]


def capture_time(file: DriveFile, tz: str = "Asia/Seoul") -> datetime:
    """파일명에서 촬영 시각을 읽는다. 실패하면 드라이브 업로드 시각."""
    zone = ZoneInfo(tz)
    for pattern in _PATTERNS:
        match = pattern.search(file.name)
        if not match:
            continue
        date_part = match.group("d").replace("-", "")
        time_part = match.group("t").replace("-", "")
        try:
            naive = datetime.strptime(date_part + time_part, "%Y%m%d%H%M%S")
        except ValueError:
            continue
        return naive.replace(tzinfo=zone)
    return file.created_time.astimezone(zone)


@dataclass
class ProductGroup:
    """한 상품으로 추정되는 사진 묶음."""

    index: int
    files: list[DriveFile]
    times: list[datetime] = field(default_factory=list)

    @property
    def started_at(self) -> datetime:
        return min(self.times)

    @property
    def slug_time(self) -> str:
        return self.started_at.strftime("%H%M%S")

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self.files)


def group_photos(
    files: list[DriveFile],
    *,
    max_gap_seconds: int = 150,
    tz: str = "Asia/Seoul",
) -> list[ProductGroup]:
    dated = sorted(((f, capture_time(f, tz)) for f in files), key=lambda pair: pair[1])
    groups: list[ProductGroup] = []
    gap = timedelta(seconds=max_gap_seconds)

    for file, taken in dated:
        if groups and taken - groups[-1].times[-1] <= gap:
            groups[-1].files.append(file)
            groups[-1].times.append(taken)
        else:
            groups.append(ProductGroup(index=len(groups) + 1, files=[file], times=[taken]))
    return groups


def filter_for_day(
    files: list[DriveFile], day: datetime, *, tz: str = "Asia/Seoul"
) -> list[DriveFile]:
    """그날(현지 시간 기준 00:00~24:00)에 올라온 사진만 남긴다.

    기준은 '드라이브 업로드 시각'이다 — 은성님이 며칠 전에 찍어둔 사진을
    오늘 올렸다면 그건 오늘 콘텐츠다.
    """
    zone = ZoneInfo(tz)
    start = day.astimezone(zone).replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    return [f for f in files if start <= f.created_time.astimezone(zone) < end]


def utcnow() -> datetime:
    return datetime.now(timezone.utc)
