"""거래처·품목·서류종류 레지스트리.

data/*.yaml 을 읽어서 조회 가능한 객체로 만든다.
개인정보가 필요한 자리는 data/private/ 이 있으면 채우고, 없으면 비워둔다.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any, Iterable

import yaml

from . import config


def _read(name: str) -> dict[str, Any]:
    p = config.path("data", name)
    if not p.exists():
        return {}
    with p.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def _read_private(name: str) -> dict[str, Any]:
    p = config.path("data", "private", name)
    if not p.exists():
        return {}
    with p.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


@dataclass
class Hospital:
    id: str
    name: str
    raw: dict[str, Any] = field(repr=False, default_factory=dict)

    # ── 편의 접근자 ─────────────────────────────────────────
    @property
    def short(self) -> str:
        return self.raw.get("short") or self.name

    @property
    def consignment(self) -> str | None:
        """간납사. 없으면 None (직거래)."""
        value = self.raw.get("consignment")
        return value if value not in (None, "", "X", "x") else None

    @property
    def doc_type(self) -> str:
        return self.raw.get("doc_type", "거래명세서")

    @property
    def doc(self) -> dict[str, Any]:
        return self.raw.get("doc") or {}

    @property
    def copies(self) -> int | None:
        """준비해야 할 서류 매수. 규칙이 없으면 None → 기본값 사용."""
        explicit = self.doc.get("copies")
        if explicit is not None:
            return explicit
        variants = self.raw.get("doc_variants")
        if variants:
            return max(v.get("copies", 0) for v in variants)
        return None

    @property
    def stamp(self) -> bool | None:
        return self.doc.get("stamp")

    @property
    def distribution(self) -> list[dict[str, Any]]:
        return self.doc.get("distribution") or []

    @property
    def priority(self) -> str:
        return self.raw.get("priority", "중")

    @property
    def conflicts(self) -> list[dict[str, Any]]:
        return self.raw.get("conflicts") or []

    @property
    def open_items(self) -> list[str]:
        return self.raw.get("open") or []

    @property
    def cautions(self) -> list[str]:
        return self.raw.get("cautions") or []

    @property
    def watch(self) -> list[str]:
        return self.raw.get("watch") or []

    @property
    def closing(self) -> dict[str, Any]:
        return self.raw.get("closing") or {}

    @property
    def delivery(self) -> dict[str, Any]:
        return self.raw.get("delivery") or {}

    def contacts(self) -> list[dict[str, Any]]:
        rows = _read_private("contacts.yaml").get("contacts") or []
        return [c for c in rows if c.get("hospital") == self.id]


@lru_cache(maxsize=1)
def _hospital_doc() -> dict[str, Any]:
    return _read("hospitals.yaml")


@lru_cache(maxsize=1)
def hospitals() -> list[Hospital]:
    doc = _hospital_doc()
    out: list[Hospital] = []
    for section in ("hospitals", "prospects"):
        for row in doc.get(section) or []:
            out.append(Hospital(id=row["id"], name=row["name"], raw=row))
    return out


def meta() -> dict[str, Any]:
    return _hospital_doc().get("meta") or {}


def suppliers() -> list[dict[str, Any]]:
    return _hospital_doc().get("suppliers") or []


def consignors() -> list[dict[str, Any]]:
    return _hospital_doc().get("consignors") or []


class NotFound(LookupError):
    """거래처를 찾지 못했을 때. 후보를 함께 담아 던진다."""

    def __init__(self, query: str, candidates: Iterable[Hospital]):
        self.query = query
        self.candidates = list(candidates)
        names = ", ".join(f"{h.short}({h.id})" for h in self.candidates[:8]) or "없음"
        super().__init__(f"'{query}' 에 해당하는 거래처를 찾지 못했습니다. 후보: {names}")


def find(query: str) -> Hospital:
    """id / 정식명 / 약칭 / 부분일치 순으로 찾는다."""
    q = query.strip()
    rows = hospitals()
    for h in rows:
        if h.id == q:
            return h
    for h in rows:
        if h.name == q or h.short == q:
            return h
    partial = [h for h in rows if q in h.name or q in h.short or q in h.id]
    if len(partial) == 1:
        return partial[0]
    if len(partial) > 1:
        raise NotFound(q, partial)
    raise NotFound(q, rows)


# ── 품목 ────────────────────────────────────────────────────
@lru_cache(maxsize=1)
def _product_doc() -> dict[str, Any]:
    return _read("products.yaml")


@lru_cache(maxsize=1)
def products() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for cat in _product_doc().get("categories") or []:
        for item in cat.get("items") or []:
            row = dict(item)
            row["category"] = cat.get("name")
            row["category_id"] = cat.get("id")
            out.append(row)
    return out


def find_product(query: str) -> dict[str, Any] | None:
    q = query.strip().lower()
    for p in products():
        names = [str(p.get("id", "")), str(p.get("name", ""))] + [str(a) for a in (p.get("aka") or [])]
        if any(q == n.lower() for n in names):
            return p
    for p in products():
        names = [str(p.get("id", "")), str(p.get("name", ""))] + [str(a) for a in (p.get("aka") or [])]
        if any(q in n.lower() for n in names):
            return p
    return None


def products_for(hospital_id: str) -> list[dict[str, Any]]:
    """이 병원에 들어가는 것으로 기록된 품목."""
    return [p for p in products() if hospital_id in (p.get("accounts") or [])]


def case_cover_axes() -> list[dict[str, Any]]:
    return _product_doc().get("case_cover_axes") or []


# ── 서류 종류 ───────────────────────────────────────────────
@lru_cache(maxsize=1)
def _doc_type_doc() -> dict[str, Any]:
    return _read("doc_types.yaml")


def doc_types() -> list[dict[str, Any]]:
    return _doc_type_doc().get("types") or []


def doc_type(name_or_id: str) -> dict[str, Any] | None:
    q = name_or_id.strip()
    for t in doc_types():
        if t.get("id") == q or t.get("name") == q:
            return t
    return None


def filename_pattern() -> str:
    return _doc_type_doc().get("filename_pattern", "SUMEX {doc_type}({subject})_{yymmdd}{suffix}.xlsx")


# ── 할 일 ───────────────────────────────────────────────────
@lru_cache(maxsize=1)
def _task_doc() -> dict[str, Any]:
    return _read("tasks.yaml")


def backlog() -> list[dict[str, Any]]:
    return _task_doc().get("backlog") or []


def recurring() -> list[dict[str, Any]]:
    return _task_doc().get("recurring") or []


def routing_notes() -> list[str]:
    return _task_doc().get("routing") or []


def reload() -> None:
    """yaml 을 다시 읽는다 (파일을 편집한 뒤 호출)."""
    for fn in (_hospital_doc, hospitals, _product_doc, products, _doc_type_doc, _task_doc):
        fn.cache_clear()
    config.load.cache_clear()
