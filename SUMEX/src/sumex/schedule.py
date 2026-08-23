"""업무 스케줄 엔진.

세 가지를 계산한다.
  1) 오늘/이번 주 해야 할 일   — backlog(기한) + recurring(주기) 를 날짜에 펼친다
  2) 월 마감 캘린더            — 병원별 마감 규칙을 실제 날짜로 환산
  3) 방문 계획                 — 시간 제약·동선 메모를 붙인 방문 순서

주기 규칙은 tasks.yaml 의 한국어 표현("매월 1~3일", "매주 월요일", "2주 1회")을
그대로 읽는다. 사람이 편집하는 파일이므로 코드가 사람 쪽에 맞춘다.
"""
from __future__ import annotations

import calendar
import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any, Iterable

from . import registry

WEEKDAYS = {"월": 0, "화": 1, "수": 2, "목": 3, "금": 4, "토": 5, "일": 6}
KOREAN_DOW = "월화수목금토일"

# 2026년 한국 공휴일 (필요 시 갱신)
HOLIDAYS_2026 = {
    date(2026, 1, 1), date(2026, 2, 16), date(2026, 2, 17), date(2026, 2, 18),
    date(2026, 3, 1), date(2026, 3, 2), date(2026, 5, 5), date(2026, 5, 24),
    date(2026, 5, 25), date(2026, 6, 6), date(2026, 8, 15), date(2026, 8, 17),
    date(2026, 9, 24), date(2026, 9, 25), date(2026, 9, 26),
    date(2026, 10, 3), date(2026, 10, 5), date(2026, 10, 9), date(2026, 12, 25),
}


def is_workday(day: date) -> bool:
    return day.weekday() < 5 and day not in HOLIDAYS_2026


def next_workday(day: date) -> date:
    nxt = day + timedelta(days=1)
    while not is_workday(nxt):
        nxt += timedelta(days=1)
    return nxt


def dow(day: date) -> str:
    return KOREAN_DOW[day.weekday()]


@dataclass
class Entry:
    when: date
    kind: str          # 마감 / 반복 / 후속 / 방문 / 회수
    title: str
    pri: str = "중"
    hospital: str | None = None
    detail: str = ""
    task_id: str | None = None
    overdue: bool = False

    def sort_key(self) -> tuple:
        rank = {"최상": 0, "상": 1, "중": 2}.get(self.pri, 3)
        return (self.when, rank, self.kind, self.title)


def _parse_due(value: Any) -> date | None:
    if isinstance(value, date):
        return value
    if not value:
        return None
    text = str(value).strip()
    if text in ("상시", "가능한 빨리", "수시"):
        return None
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%m/%d"):
        try:
            parsed = datetime.strptime(text, fmt).date()
            return parsed.replace(year=date.today().year) if fmt == "%m/%d" else parsed
        except ValueError:
            continue
    return None


def _hospital_label(hid: Any) -> str | None:
    if not hid:
        return None
    try:
        return registry.find(str(hid)).short
    except LookupError:
        return str(hid)


def backlog_entries(today: date | None = None, include_done: bool = False) -> list[Entry]:
    today = today or date.today()
    out: list[Entry] = []
    for task in registry.backlog():
        status = task.get("status", "todo")
        if status in ("done", "dropped") and not include_done:
            continue
        due = _parse_due(task.get("due"))
        out.append(Entry(
            when=due or today,
            kind="후속",
            title=str(task.get("title", "")),
            pri=str(task.get("pri", "중")),
            hospital=_hospital_label(task.get("hospital")),
            detail=str(task.get("note", "")),
            task_id=task.get("id"),
            overdue=bool(due and due < today and status != "done"),
        ))
    return out


def _matches_recurring(rule: str, day: date) -> bool:
    """'매월 1~3일', '매주 월요일', '매주 금요일', '매월 말' 등을 날짜에 대응."""
    rule = str(rule or "").strip()
    if not rule:
        return False

    m = re.search(r"매월\s*(\d+)\s*[~-]\s*(\d+)\s*일", rule)
    if m:
        return int(m.group(1)) <= day.day <= int(m.group(2))

    m = re.search(r"매월\s*(\d+)\s*일", rule)
    if m:
        return day.day == int(m.group(1))

    if "매월 말" in rule or "월말" in rule:
        last = calendar.monthrange(day.year, day.month)[1]
        return day.day >= last - 2

    if "월 초" in rule or "월초" in rule:
        return day.day <= 3

    m = re.search(r"매주\s*([월화수목금토일])", rule)
    if m:
        return day.weekday() == WEEKDAYS[m.group(1)]

    return False


def recurring_entries(day: date) -> list[Entry]:
    out: list[Entry] = []
    for rule in registry.recurring():
        when = rule.get("when")
        if not _matches_recurring(str(when), day):
            continue
        steps = rule.get("steps") or []
        out.append(Entry(
            when=day,
            kind="마감" if "마감" in str(rule.get("title", "")) else "반복",
            title=str(rule.get("title", "")),
            pri=str(rule.get("pri", "중")),
            detail="\n".join(f"- {s}" for s in steps)
                   + (f"\n★ {rule['hard_rule']}" if rule.get("hard_rule") else ""),
            task_id=rule.get("id"),
        ))
    return out


def closing_entries(year: int, month: int) -> list[Entry]:
    """그 달의 병원별 마감 일정을 실제 날짜로 계산한다."""
    out: list[Entry] = []
    first = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]

    for h in registry.hospitals():
        closing = h.closing
        if not closing:
            continue

        when = first
        detail_lines: list[str] = []

        rule = str(closing.get("rule", ""))
        if "1~3일" in rule or "월초" in rule or "매월 초" in rule:
            when = first
            while not is_workday(when):
                when = next_workday(when)
        elif "월말" in rule or closing.get("collection"):
            when = date(year, month, last_day)
            while not is_workday(when):
                when -= timedelta(days=1)

        if rule:
            detail_lines.append(rule)
        for key in ("how_to_find_deadline", "announced", "hard_rule", "time_limit", "after", "collection"):
            if closing.get(key):
                detail_lines.append(str(closing[key]).strip())
        for item in closing.get("bundle") or []:
            detail_lines.append(f"지참: {item}")
        if closing.get("order"):
            detail_lines.append("마감 순서: " + " → ".join(closing["order"]))

        out.append(Entry(
            when=when,
            kind="마감",
            title=f"{h.short} 월 마감",
            pri="최상",
            hospital=h.short,
            detail="\n".join(detail_lines),
        ))

    return sorted(out, key=Entry.sort_key)


def day_plan(day: date | None = None) -> list[Entry]:
    day = day or date.today()
    entries = recurring_entries(day)
    entries += [e for e in backlog_entries(day) if e.when <= day]
    return sorted(entries, key=Entry.sort_key)


def week_plan(start: date | None = None) -> dict[date, list[Entry]]:
    start = start or date.today()
    monday = start - timedelta(days=start.weekday())
    plan: dict[date, list[Entry]] = {}
    backlog = backlog_entries(start)
    for offset in range(7):
        day = monday + timedelta(days=offset)
        entries = recurring_entries(day)
        entries += [e for e in backlog if e.when == day or (e.overdue and day == start)]
        plan[day] = sorted(entries, key=Entry.sort_key)
    return plan


def visit_constraints(h: registry.Hospital) -> list[str]:
    """이 병원을 방문할 때 시간·요일 제약."""
    out: list[str] = []
    d = h.delivery
    if d.get("windows"):
        out.append("납품 가능 " + " / ".join(d["windows"]))
    if d.get("cold_chain_cutoff"):
        out.append(f"냉장·냉동 {d['cold_chain_cutoff']} 이전")
    if d.get("avoid"):
        out.append(f"자제: {d['avoid']}")
    if d.get("staff_window"):
        out.append(str(d["staff_window"]))
    if h.raw.get("parking"):
        out.append(f"주차 {h.raw['parking']}")
    closing = h.closing
    if closing.get("time_limit"):
        out.append(str(closing["time_limit"]))
    return out


def plan_visits(names: Iterable[str], day: date | None = None) -> dict[str, Any]:
    """방문 대상 목록을 받아 순서·제약·서류 준비량을 정리한다."""
    day = day or date.today()
    stops: list[dict[str, Any]] = []
    for name in names:
        h = registry.find(name)
        stops.append({
            "hospital": h,
            "copies": h.copies,
            "doc_type": h.doc_type,
            "constraints": visit_constraints(h),
            "region": h.raw.get("region", ""),
            "priority": h.priority,
        })

    # 시간 창이 좁은 곳을 앞으로, 서울권 밖을 뒤로
    def rank(stop: dict[str, Any]) -> tuple:
        h: registry.Hospital = stop["hospital"]
        has_window = bool(h.delivery.get("windows"))
        outside = 1 if not str(stop["region"]).startswith("서울") else 0
        pri = {"최상": 0, "상": 1, "중": 2}.get(stop["priority"], 3)
        return (0 if has_window else 1, outside, pri)

    stops.sort(key=rank)

    total_copies = sum(s["copies"] or 0 for s in stops)
    unknown = [s["hospital"].short for s in stops if s["copies"] is None]

    return {
        "date": day,
        "stops": stops,
        "total_copies": total_copies,
        "unknown_copies": unknown,
        "routing_notes": registry.routing_notes(),
    }


# ── ICS (구글 캘린더 가져오기용) ─────────────────────────────
def _ics_escape(text: str) -> str:
    return (str(text).replace("\\", "\\\\").replace(";", r"\;")
            .replace(",", r"\,").replace("\n", r"\n"))


def to_ics(entries: Iterable[Entry], name: str = "SUMEX 업무") -> str:
    lines = [
        "BEGIN:VCALENDAR", "VERSION:2.0",
        "PRODID:-//SUMEX//sales-automation//KO",
        "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
        f"X-WR-CALNAME:{_ics_escape(name)}",
        "X-WR-TIMEZONE:Asia/Seoul",
    ]
    stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    for idx, e in enumerate(entries):
        uid = f"sumex-{e.when:%Y%m%d}-{idx}-{(e.task_id or e.kind)}@sumex.local"
        summary = f"[{e.kind}] {e.title}"
        if e.hospital and e.hospital not in e.title:
            summary = f"[{e.kind}] {e.hospital} — {e.title}"
        lines += [
            "BEGIN:VEVENT",
            f"UID:{_ics_escape(uid)}",
            f"DTSTAMP:{stamp}",
            f"DTSTART;VALUE=DATE:{e.when:%Y%m%d}",
            f"DTEND;VALUE=DATE:{e.when + timedelta(days=1):%Y%m%d}",
            f"SUMMARY:{_ics_escape(summary)}",
        ]
        if e.detail:
            lines.append(f"DESCRIPTION:{_ics_escape(e.detail)}")
        if e.pri == "최상":
            lines += ["PRIORITY:1", "BEGIN:VALARM", "TRIGGER:-P1D",
                      "ACTION:DISPLAY", f"DESCRIPTION:{_ics_escape(summary)}", "END:VALARM"]
        lines.append("END:VEVENT")
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"


def month_entries(year: int, month: int) -> list[Entry]:
    """한 달치 전체 (마감 + 반복 + 기한 도래 후속조치)."""
    entries = closing_entries(year, month)
    last_day = calendar.monthrange(year, month)[1]
    for dayno in range(1, last_day + 1):
        day = date(year, month, dayno)
        entries += recurring_entries(day)
    for e in backlog_entries():
        if e.when.year == year and e.when.month == month:
            entries.append(e)
    return sorted(entries, key=Entry.sort_key)
