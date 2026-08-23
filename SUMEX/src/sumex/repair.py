"""장비 수리 접수 대장.

인수인계 항목 T-013. 병원은 "빨리 고쳐달라", 본사는 "부품이 없다" 사이에서
영업 담당이 압박받는 구조라, 접수일·증상·회신·예상 완료일을 남기는 것이
유일한 방어 수단이다.

저장 위치는 data/private/repairs.json (git 제외 — 병원·장비 정보가 들어간다).
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

from . import config, registry

STATUSES = ("접수", "본사확인중", "부품대기", "수리중", "완료", "수리불가")


@dataclass
class Ticket:
    id: str
    hospital: str
    device: str
    symptom: str
    received: str                      # 접수일 YYYY-MM-DD
    status: str = "접수"
    vendor_reply: str = ""             # 스트라이커 회신
    eta: str = ""                      # 예상 완료일
    completed: str = ""                # 실제 완료일
    loaner: str = ""                   # 대체 장비 대여 여부
    parts_in_stock: str = ""           # 부품 재고 유무
    notes: list[str] = field(default_factory=list)

    @property
    def open(self) -> bool:
        return self.status not in ("완료", "수리불가")


def _path() -> Path:
    return config.path("data", "private", "repairs.json")


def load() -> list[Ticket]:
    p = _path()
    if not p.exists():
        return []
    rows = json.loads(p.read_text(encoding="utf-8"))
    return [Ticket(**row) for row in rows]


def save(tickets: list[Ticket]) -> None:
    p = _path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps([asdict(t) for t in tickets], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _next_id(tickets: list[Ticket]) -> str:
    year = date.today().year % 100
    seq = sum(1 for t in tickets if t.id.startswith(f"R{year}")) + 1
    return f"R{year}-{seq:03d}"


def open_ticket(hospital: str, device: str, symptom: str,
                received: date | None = None) -> Ticket:
    h = registry.find(hospital)
    tickets = load()
    ticket = Ticket(
        id=_next_id(tickets),
        hospital=h.short,
        device=device,
        symptom=symptom,
        received=(received or date.today()).isoformat(),
    )
    tickets.append(ticket)
    save(tickets)
    return ticket


def update(ticket_id: str, **fields: Any) -> Ticket:
    tickets = load()
    for t in tickets:
        if t.id == ticket_id:
            for key, value in fields.items():
                if key == "notes":
                    t.notes.append(str(value))
                elif hasattr(t, key):
                    setattr(t, key, str(value))
                else:
                    raise ValueError(f"'{key}' 는 대장에 없는 항목입니다.")
            if "status" in fields and fields["status"] not in STATUSES:
                raise ValueError(f"상태는 {', '.join(STATUSES)} 중 하나여야 합니다.")
            save(tickets)
            return t
    raise LookupError(f"{ticket_id} 라는 접수 건이 없습니다.")


def intake_questions() -> list[str]:
    """접수할 때 스트라이커에 반드시 함께 물어야 하는 것 (인수인계 사항)."""
    for s in registry.suppliers():
        if s.get("id") == "stryker-korea":
            return list(s.get("repair_playbook") or [])
    return []


def stale(days: int = 3) -> list[Ticket]:
    """회신이 없는 채로 오래된 건 — 병원이 묻기 전에 먼저 연락해야 하는 대상."""
    today = date.today()
    out = []
    for t in load():
        if not t.open:
            continue
        received = date.fromisoformat(t.received)
        if (today - received).days >= days and not t.vendor_reply:
            out.append(t)
    return out
