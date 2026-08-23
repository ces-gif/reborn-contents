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


MAX_GROUP_SIZE = 6  # 안전장치: 가격표를 빠뜨려도 한 묶음이 무한정 커지지 않게


@dataclass
class ProductGroup:
    """한 상품으로 추정되는 사진 묶음."""

    index: int
    files: list[DriveFile]
    times: list[datetime] = field(default_factory=list)
    kinds: list[str] = field(default_factory=list)

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


# ---------------------------------------------------------------- 내용 기반 묶기


def _new_group(index: int, file: DriveFile, kind: str, taken: datetime) -> ProductGroup:
    group = ProductGroup(index=index, files=[file], times=[taken])
    group.kinds = [kind]
    return group


def group_by_content(
    files: list[DriveFile],
    kinds: list[str],
    *,
    tz: str = "Asia/Seoul",
    max_size: int = MAX_GROUP_SIZE,
) -> list[ProductGroup]:
    """사진 내용으로 같은 상품끼리 묶는다.

    은성님 촬영 방식은 상품 하나당
      · 상품 사진 1장 + 가격표 사진 1장 (순서는 상관없음), 또는
      · 상품과 가격표가 같이 나온 사진 1장 (+ 가격표 근접 사진 1장)
    이다. 그래서 **가격표가 상품의 경계**가 된다.

    촬영 시각으로 묶던 예전 방식은 연달아 찍으면 전부 한 덩어리가 됐다
    (31장이 2덩어리가 되고 뒤 27장이 버려졌다). 시계 대신 내용을 본다.

    규칙:
      · 새 상품 사진(both)이 오면 앞 묶음을 닫는다.
      · 가격표는 한 묶음에 하나까지. 두 번째 가격표가 오면 새 상품이다.
      · 이미 상품과 가격표가 다 있는 묶음에 상품 사진이 오면 새 상품이다.
        (가격표만 있는 묶음에 오는 상품 사진은 그 가격표의 상품이다)
      · other(매장 전경 등)는 버린다.
    """
    groups: list[ProductGroup] = []
    current: ProductGroup | None = None

    def close() -> None:
        nonlocal current
        if current is not None:
            groups.append(current)
            current = None

    for file, kind in zip(files, kinds):
        taken = capture_time(file, tz)

        if kind == "other":
            close()
            continue

        if current is not None:
            tags = sum(1 for k in current.kinds if k == "price_tag")
            products = sum(1 for k in current.kinds if k in ("product", "both"))
            has_both = "both" in current.kinds

            starts_new = (
                kind == "both"
                or (kind == "price_tag" and tags >= 1)
                or (kind == "product" and (has_both or (tags >= 1 and products >= 1)))
                or len(current.files) >= max_size
            )
            if starts_new:
                close()

        if current is None:
            current = _new_group(len(groups) + 1, file, kind, taken)
        else:
            current.files.append(file)
            current.times.append(taken)
            current.kinds.append(kind)

    close()
    for i, group in enumerate(groups, start=1):
        group.index = i
    return groups
