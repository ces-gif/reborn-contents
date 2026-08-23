"""일일 브리핑 — 아침에 이것만 보면 오늘 뭘 해야 하는지 알 수 있게."""
from __future__ import annotations

from datetime import date

from . import checklist, config, registry, repair, schedule, tasks


def build(day: date | None = None) -> str:
    day = day or date.today()
    w: list[str] = []
    bar = "═" * 60

    w.append(bar)
    w.append(f" SUMEX 업무 브리핑   {day:%Y-%m-%d} ({schedule.dow(day)})")
    w.append(bar)

    if not schedule.is_workday(day):
        w.append(" ※ 오늘은 휴무일입니다. 다음 영업일은 "
                 f"{schedule.next_workday(day):%Y-%m-%d} ({schedule.dow(schedule.next_workday(day))}) 입니다.")
        w.append("")

    # 연휴 예고
    nxt = schedule.next_workday(day)
    gap = (nxt - day).days
    if schedule.is_workday(day) and gap > 1:
        w.append(f" ★ 다음 영업일이 {nxt:%m/%d}({schedule.dow(nxt)}) 입니다. "
                 "오늘 안에 마감해야 할 납품·서류·세금계산서를 먼저 처리하세요.")
        w.append("")

    # 월 마감 창
    lo, hi = config.load().get("schedule", {}).get("closing_window", [1, 3])
    if lo <= day.day <= hi:
        w.append(f" ★★ 월 마감 기간입니다 (매월 {lo}~{hi}일). 마감을 넘기면 대금 지급이 밀립니다.")
        for entry in schedule.closing_entries(day.year, day.month):
            if entry.when.day <= hi:
                w.append(f"    · {entry.title}")
        w.append("")

    # 오늘 일정
    entries = schedule.day_plan(day)
    overdue = [e for e in entries if e.overdue]
    today_items = [e for e in entries if not e.overdue]

    if overdue:
        w.append(f"[기한 지남 {len(overdue)}건]")
        for e in sorted(overdue, key=lambda x: x.when):
            days_late = (day - e.when).days
            w.append(f"  ! ({e.pri}) {e.task_id or ''} {e.hospital or ''} {e.title}  — {days_late}일 지남")
        w.append("")

    if today_items:
        w.append("[오늘]")
        for e in today_items:
            head = f"  · [{e.kind}] "
            if e.hospital:
                head += f"{e.hospital} — "
            w.append(head + e.title)
            for line in str(e.detail).splitlines():
                if line.strip():
                    w.append(f"      {line.strip()}")
        w.append("")
    elif not overdue:
        w.append("[오늘] 예정된 반복 업무 없음\n")

    # 수리 대장
    stale = repair.stale()
    if stale:
        w.append(f"[수리 회신 지연 {len(stale)}건 — 병원이 묻기 전에 먼저 연락]")
        for t in stale:
            w.append(f"  ! {t.id} {t.hospital} / {t.device} / {t.symptom} (접수 {t.received})")
        w.append("")

    # 데이터 결손
    gaps = checklist.audit()
    blocking = [g for g in gaps if g["kind"] in ("매수 미확인", "배부처 미기재", "매수 불일치")]
    if blocking:
        w.append(f"[서류 규칙이 아직 비어 있는 거래처 {len(blocking)}곳]")
        for g in blocking[:6]:
            w.append(f"  ? {g['hospital']} — {g['detail']}")
        if len(blocking) > 6:
            w.append(f"    … 외 {len(blocking) - 6}건 (sumex audit)")
        w.append("")

    counts = tasks.counts()
    w.append(f"할 일: 미착수 {counts.get('todo', 0)} / 진행 {counts.get('doing', 0)} / 완료 {counts.get('done', 0)}")

    if not config.load().get("_has_private"):
        w.append("")
        w.append("※ data/private/ 가 없어 담당자·계좌 정보가 '(비공개)' 로 표시됩니다.")
        w.append("  python scripts/bootstrap_private_data.py 로 만들 수 있습니다.")

    return "\n".join(w).rstrip() + "\n"
