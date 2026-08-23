"""스케줄 엔진 — 반복 규칙 해석, 마감일 계산, ICS."""
from datetime import date

import pytest

from sumex import schedule


@pytest.mark.parametrize("rule,day,expected", [
    ("매월 1~3일", date(2026, 9, 2), True),
    ("매월 1~3일", date(2026, 9, 4), False),
    ("매월 1일", date(2026, 9, 1), True),
    ("매월 1일", date(2026, 9, 2), False),
    ("매주 월요일", date(2026, 8, 24), True),      # 월
    ("매주 월요일", date(2026, 8, 25), False),
    ("매주 금요일", date(2026, 8, 28), True),
    ("매월 말", date(2026, 9, 30), True),
    ("매월 말", date(2026, 9, 15), False),
    ("2주 1회", date(2026, 9, 1), False),          # 해석 불가 → False
    ("", date(2026, 9, 1), False),
])
def test_recurring_rule(rule, day, expected):
    assert schedule._matches_recurring(rule, day) is expected


def test_workday_and_holidays():
    assert schedule.is_workday(date(2026, 8, 24))       # 월
    assert not schedule.is_workday(date(2026, 8, 23))   # 일
    assert not schedule.is_workday(date(2026, 8, 15))   # 광복절
    assert not schedule.is_workday(date(2026, 8, 17))   # 대체공휴일


def test_next_workday_skips_holiday_block():
    """8/14(금) 다음 영업일은 8/18(화) — 광복절+대체공휴일 연휴."""
    assert schedule.next_workday(date(2026, 8, 14)) == date(2026, 8, 18)


def test_dow_labels():
    assert schedule.dow(date(2026, 8, 24)) == "월"
    assert schedule.dow(date(2026, 8, 23)) == "일"


def test_closing_entries_land_on_workdays():
    entries = schedule.closing_entries(2026, 9)
    assert entries
    for e in entries:
        assert schedule.is_workday(e.when), f"{e.title} 이 휴무일 {e.when} 에 잡혔다"


def test_closing_includes_known_hospitals():
    titles = " ".join(e.title for e in schedule.closing_entries(2026, 9))
    for name in ("청담리온", "고대", "세종스포츠", "하늘", "노원을지"):
        assert name in titles, f"{name} 마감이 빠졌다"


def test_month_entries_sorted():
    entries = schedule.month_entries(2026, 9)
    assert entries == sorted(entries, key=schedule.Entry.sort_key)


def test_backlog_marks_overdue():
    entries = schedule.backlog_entries(date(2026, 8, 23))
    assert any(e.overdue for e in entries)


def test_backlog_excludes_done_by_default():
    ids_open = {e.task_id for e in schedule.backlog_entries()}
    ids_all = {e.task_id for e in schedule.backlog_entries(include_done=True)}
    assert ids_all > ids_open


def test_week_plan_has_seven_days():
    plan = schedule.week_plan(date(2026, 8, 24))
    assert len(plan) == 7
    assert min(plan) == date(2026, 8, 24)       # 월요일부터


def test_plan_visits_orders_time_windows_first():
    plan = schedule.plan_visits(["세종스포츠", "구리센트럴", "분당서울대"])
    assert plan["stops"][0]["hospital"].id == "snubh"      # 시간 창이 있는 곳
    assert plan["stops"][-1]["hospital"].id == "guri-central"  # 서울권 밖
    assert plan["total_copies"] == 4 + 4 + 3


def test_ics_is_wellformed():
    entries = schedule.month_entries(2026, 9)
    text = schedule.to_ics(entries)
    assert text.startswith("BEGIN:VCALENDAR")
    assert text.rstrip().endswith("END:VCALENDAR")
    assert text.count("BEGIN:VEVENT") == len(entries)
    assert text.count("BEGIN:VEVENT") == text.count("END:VEVENT")


def test_ics_escapes_separators():
    e = schedule.Entry(when=date(2026, 9, 1), kind="마감", title="a,b;c",
                       detail="첫 줄\n둘째 줄")
    text = schedule.to_ics([e])
    assert r"a\,b\;c" in text
    assert r"첫 줄\n둘째 줄" in text
