"""sumex 명령줄 도구.

  sumex today                       오늘 브리핑
  sumex week                        이번 주 계획
  sumex month 2026-09               그 달 마감·반복 일정
  sumex checklist 세종스포츠         납품 체크리스트 (차량 비치용)
  sumex hospitals                   거래처 목록
  sumex hospital 서울척              거래처 전체 정보
  sumex doc 세종스포츠 --items "..."  거래명세서/가납서/선납서 xlsx 생성
  sumex quote 호수병원 --spec q.yaml  견적서 생성
  sumex demo demo.yaml              데모인수증 + 데모 전 점검표
  sumex visit 세종스포츠 무척나은      방문 계획 (순서·서류 총매수·제약)
  sumex task list|done|doing|drop    할 일 관리
  sumex repair open|list|update      장비 수리 접수 대장
  sumex ics --month 2026-09 -o x.ics 구글 캘린더용 파일
  sumex audit                       데이터 결손·불일치 점검
  sumex product ICONIX              품목 정보
  sumex casecover                   케이스 커버 7축 점검표
"""
from __future__ import annotations

import argparse
import sys
from datetime import date, datetime
from pathlib import Path

import yaml

from . import brief, checklist, config, demo_form, docs, registry, repair, schedule, tasks


def _date(text: str | None) -> date:
    if not text:
        return date.today()
    return datetime.strptime(text, "%Y-%m-%d").date()


def _month(text: str | None) -> tuple[int, int]:
    if not text:
        today = date.today()
        return today.year, today.month
    parsed = datetime.strptime(text, "%Y-%m")
    return parsed.year, parsed.month


# ── 명령 구현 ───────────────────────────────────────────────
def cmd_today(args: argparse.Namespace) -> int:
    print(brief.build(_date(args.date)))
    return 0


def cmd_week(args: argparse.Namespace) -> int:
    plan = schedule.week_plan(_date(args.date))
    for day, entries in plan.items():
        mark = "" if schedule.is_workday(day) else "  (휴무)"
        print(f"\n── {day:%m/%d} ({schedule.dow(day)}){mark} " + "─" * 30)
        if not entries:
            print("   -")
        for e in entries:
            flag = "!" if e.overdue else "·"
            label = f"{e.hospital} — " if e.hospital else ""
            print(f"   {flag} [{e.kind}] {label}{e.title}")
    print()
    for note in registry.routing_notes():
        print(f"동선: {note}")
    return 0


def cmd_month(args: argparse.Namespace) -> int:
    year, month = _month(args.month)
    entries = schedule.month_entries(year, month)
    print(f"{year}년 {month}월 업무 일정  ({len(entries)}건)\n")
    current: date | None = None
    for e in entries:
        if e.when != current:
            current = e.when
            print(f"\n{e.when:%m/%d} ({schedule.dow(e.when)})")
        label = f"{e.hospital} — " if e.hospital else ""
        print(f"  [{e.pri}] [{e.kind}] {label}{e.title}")
        for line in str(e.detail).splitlines():
            if line.strip():
                print(f"       {line.strip()}")
    return 0


def cmd_checklist(args: argparse.Namespace) -> int:
    h = registry.find(args.hospital)
    data = checklist.build(h, _date(args.date))
    text = checklist.render_md(data) if args.md else checklist.render_text(data)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"저장: {args.out}")
    else:
        print(text)
    return 0


def cmd_hospitals(args: argparse.Namespace) -> int:
    rows = registry.hospitals()
    if args.priority:
        rows = [h for h in rows if h.priority == args.priority]
    print(f"{'id':<24} {'거래처':<20} {'서류':<8} {'매수':>4}  {'도장':<6} {'간납사':<16} 우선")
    print("─" * 100)
    for h in rows:
        copies = h.copies
        stamp = {True: "필요", False: "불필요", None: "-"}[h.stamp]
        print(f"{h.id:<24} {h.short:<20} {h.doc_type:<8} "
              f"{(copies if copies is not None else '?'):>4}  {stamp:<6} "
              f"{(h.consignment or '-'):<16} {h.priority}")
    print(f"\n총 {len(rows)}곳")
    return 0


def cmd_hospital(args: argparse.Namespace) -> int:
    h = registry.find(args.hospital)
    print(yaml.safe_dump(h.raw, allow_unicode=True, sort_keys=False, width=100))
    products = registry.products_for(h.id)
    if products:
        print("취급 품목:")
        for p in products:
            print(f"  · {p['name']}  ({p['category']})")
    return 0


def cmd_doc(args: argparse.Namespace) -> int:
    h = registry.find(args.hospital)
    items = docs.parse_items(args.items)
    path = docs.build_statement(
        h, items,
        doc_type=args.type,
        when=_date(args.date),
        subject=args.subject,
        suffix=args.suffix or "",
    )
    total = docs.summarize(items)
    print(f"생성: {path}")
    print(f"합계 {total['total']:,.0f}원  (공급가액 {total['supply']:,.0f} / 부가세 {total['vat']:,.0f})")
    print()
    print(checklist.render_text(checklist.build(h, _date(args.date))))
    return 0


def cmd_quote(args: argparse.Namespace) -> int:
    h = registry.find(args.hospital)
    spec = yaml.safe_load(Path(args.spec).read_text(encoding="utf-8")) or {}
    groups = [(g.get("group", ""), docs.parse_items(g.get("items") or []))
              for g in (spec.get("groups") or [])]
    if not groups:
        print("spec 파일에 groups 가 없습니다. 형식은 README 를 보세요.", file=sys.stderr)
        return 2
    path = docs.build_quotation(h, groups, when=_date(args.date), subject=spec.get("subject"))
    print(f"생성: {path}")
    return 0


def cmd_demo(args: argparse.Namespace) -> int:
    req = demo_form.load_request(args.spec)
    path = demo_form.build(req)
    print(f"생성: {path}")
    print(f"출고 {req.release_date:%Y-%m-%d} → 회수 {req.return_date:%Y-%m-%d}\n")
    print("[데모 전 점검]")
    for line in demo_form.checklist(req):
        print(f"  · {line}")
    return 0


def cmd_visit(args: argparse.Namespace) -> int:
    plan = schedule.plan_visits(args.hospitals, _date(args.date))
    print(f"방문 계획  {plan['date']:%Y-%m-%d} ({schedule.dow(plan['date'])})\n")
    for idx, stop in enumerate(plan["stops"], start=1):
        h = stop["hospital"]
        copies = stop["copies"]
        print(f"{idx}. {h.name}  [{stop['region']}]")
        print(f"   {stop['doc_type']} {copies if copies is not None else '?'}장"
              + ("   ← 매수 미확인" if copies is None else ""))
        for c in stop["constraints"]:
            print(f"   ★ {c}")
        print()
    print(f"총 준비할 서류: {plan['total_copies']}장"
          + (f"  (+ 미확인 {', '.join(plan['unknown_copies'])})" if plan["unknown_copies"] else ""))
    print()
    for note in plan["routing_notes"]:
        print(f"동선: {note}")
    return 0


def cmd_task(args: argparse.Namespace) -> int:
    if args.action == "list":
        rows = tasks.filtered(status=args.status, hospital=args.hospital, pri=args.pri)
        for t in rows:
            hid = t.get("hospital")
            label = registry.find(hid).short if hid else "-"
            print(f"{t['id']:<8} {t.get('status', 'todo'):<7} {t.get('pri', '중'):<3} "
                  f"{str(t.get('due', '')):<12} {label:<12} {t.get('title', '')}")
        print(f"\n{len(rows)}건   " + " / ".join(f"{k} {v}" for k, v in tasks.counts().items() if v))
        return 0

    status = {"done": "done", "doing": "doing", "drop": "dropped", "todo": "todo"}[args.action]
    task = tasks.set_status(args.id, status)
    print(f"{task['id']} → {status}   {task.get('title')}")
    return 0


def cmd_repair(args: argparse.Namespace) -> int:
    if args.action == "open":
        t = repair.open_ticket(args.hospital, args.device, args.symptom)
        print(f"접수: {t.id}  {t.hospital} / {t.device}")
        print("\n[접수 시 본사에 반드시 함께 확인할 것]")
        for line in repair.intake_questions():
            print(f"  · {line}")
        return 0

    if args.action == "update":
        fields = dict(pair.split("=", 1) for pair in args.set)
        t = repair.update(args.id, **fields)
        print(f"{t.id}  상태 {t.status}  회신 {t.vendor_reply or '-'}  예상완료 {t.eta or '-'}")
        return 0

    tickets = repair.load()
    if not tickets:
        print("접수된 건이 없습니다.  sumex repair open <병원> <장비> <증상>")
        return 0
    print(f"{'ID':<9} {'병원':<12} {'장비':<20} {'상태':<10} {'접수':<11} {'예상완료':<11} 증상")
    print("─" * 110)
    for t in tickets:
        if args.open_only and not t.open:
            continue
        print(f"{t.id:<9} {t.hospital:<12} {t.device:<20} {t.status:<10} "
              f"{t.received:<11} {t.eta or '-':<11} {t.symptom}")
    return 0


def cmd_ics(args: argparse.Namespace) -> int:
    if args.month:
        year, month = _month(args.month)
        entries = schedule.month_entries(year, month)
        name = f"SUMEX {year}-{month:02d}"
    else:
        entries = schedule.backlog_entries()
        name = "SUMEX 후속조치"
    text = schedule.to_ics(entries, name)
    out = Path(args.out or config.out_dir() / f"{name}.ics")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(f"생성: {out}  ({len(entries)}건)")
    print("구글 캘린더 → 설정 → 가져오기 및 내보내기 → 가져오기 에서 이 파일을 올리세요.")
    return 0


def cmd_audit(args: argparse.Namespace) -> int:
    findings = checklist.audit()
    if not findings:
        print("결손 항목 없음.")
        return 0
    by_kind: dict[str, list[dict]] = {}
    for f in findings:
        by_kind.setdefault(f["kind"], []).append(f)
    for kind, rows in by_kind.items():
        print(f"\n[{kind}] {len(rows)}건")
        for r in rows:
            print(f"  · {r['hospital']}: {r['detail']}")
    print(f"\n총 {len(findings)}건")
    return 0


def cmd_product(args: argparse.Namespace) -> int:
    if not args.name:
        for p in registry.products():
            print(f"{p['id']:<14} {p['name']:<40} {p['category']}")
        return 0
    p = registry.find_product(args.name)
    if not p:
        print(f"'{args.name}' 품목을 찾지 못했습니다.", file=sys.stderr)
        return 1
    print(yaml.safe_dump(p, allow_unicode=True, sort_keys=False, width=100))
    for hid in p.get("accounts") or []:
        try:
            print(f"  납품처: {registry.find(hid).name}")
        except LookupError:
            pass
    return 0


def cmd_casecover(args: argparse.Namespace) -> int:
    print("관절경 케이스 커버 7축 — 하나라도 비면 수술이 멈춘다\n")
    for axis in registry.case_cover_axes():
        print(f"[{axis['axis']}]")
        for item in axis.get("items") or []:
            print(f"  □ {item}")
        if axis.get("spare"):
            print(f"  ★ {axis['spare']}")
        print()
    if args.hospital:
        h = registry.find(args.hospital)
        products = registry.products_for(h.id)
        if products:
            print(f"[{h.short} 에 들어가는 것으로 기록된 품목]")
            for p in products:
                print(f"  □ {p['name']}")
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    """대시보드(tools/node)와 외부 도구가 읽을 JSON 을 만든다.

    개인정보는 담지 않는다 — 공개 데이터 + 계산된 일정만 나간다.
    """
    import json

    day = _date(args.date)
    payload = {
        "generated": day.isoformat(),
        "meta": registry.meta(),
        "hospitals": [
            {
                "id": h.id,
                "name": h.name,
                "short": h.short,
                "region": h.raw.get("region", ""),
                "priority": h.priority,
                "consignment": h.consignment,
                "docType": h.doc_type,
                "copies": h.copies,
                "stamp": h.stamp,
                "distribution": h.distribution,
                "checklist": checklist.build(h, day)["steps"],
                "hard": checklist.build(h, day)["hard"],
                "closing": checklist.build(h, day)["closing"],
                "cautions": h.cautions,
                "watch": h.watch,
                "open": h.open_items,
                "products": [p["name"] for p in registry.products_for(h.id)],
            }
            for h in registry.hospitals()
        ],
        "today": [
            {"kind": e.kind, "title": e.title, "pri": e.pri, "hospital": e.hospital,
             "detail": e.detail, "taskId": e.task_id, "overdue": e.overdue,
             "when": e.when.isoformat()}
            for e in schedule.day_plan(day)
        ],
        "month": [
            {"kind": e.kind, "title": e.title, "pri": e.pri, "hospital": e.hospital,
             "detail": e.detail, "when": e.when.isoformat()}
            for e in schedule.month_entries(day.year, day.month)
        ],
        "tasks": [
            {k: (str(v) if k == "due" else v) for k, v in t.items()}
            for t in registry.backlog()
        ],
        "audit": checklist.audit(),
        "caseCover": registry.case_cover_axes(),
        "products": [
            {"id": p.get("id"), "name": p.get("name"), "category": p.get("category"),
             "aka": p.get("aka") or [], "accounts": p.get("accounts") or []}
            for p in registry.products()
        ],
        "routing": registry.routing_notes(),
    }
    out = Path(args.out or config.out_dir() / "export.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(f"생성: {out}  (거래처 {len(payload['hospitals'])} / 이달 일정 {len(payload['month'])})")
    return 0


# ── 파서 ────────────────────────────────────────────────────
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="sumex", description="SUMEX 영업 자동화")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("today", help="오늘 브리핑")
    s.add_argument("--date")
    s.set_defaults(func=cmd_today)

    s = sub.add_parser("week", help="이번 주 계획")
    s.add_argument("--date")
    s.set_defaults(func=cmd_week)

    s = sub.add_parser("month", help="월 마감·반복 일정")
    s.add_argument("month", nargs="?", help="YYYY-MM")
    s.set_defaults(func=cmd_month)

    s = sub.add_parser("checklist", help="납품 체크리스트")
    s.add_argument("hospital")
    s.add_argument("--date")
    s.add_argument("--md", action="store_true")
    s.add_argument("-o", "--out")
    s.set_defaults(func=cmd_checklist)

    s = sub.add_parser("hospitals", help="거래처 목록")
    s.add_argument("--priority", choices=["최상", "상", "중"])
    s.set_defaults(func=cmd_hospitals)

    s = sub.add_parser("hospital", help="거래처 상세")
    s.add_argument("hospital")
    s.set_defaults(func=cmd_hospital)

    s = sub.add_parser("doc", help="거래명세서·가납서·선납서 생성")
    s.add_argument("hospital")
    s.add_argument("--items", required=True,
                   help="'품목 x 수량 @ 단가; ...' 또는 csv/json 파일 경로")
    s.add_argument("--type", default="거래명세서",
                   choices=["거래명세서", "가납서", "선납서"])
    s.add_argument("--date")
    s.add_argument("--subject")
    s.add_argument("--suffix", help="파일명 뒤에 붙일 말 (예: 수술방, 간납사명)")
    s.set_defaults(func=cmd_doc)

    s = sub.add_parser("quote", help="견적서 생성")
    s.add_argument("hospital")
    s.add_argument("--spec", required=True, help="견적 항목 yaml")
    s.add_argument("--date")
    s.set_defaults(func=cmd_quote)

    s = sub.add_parser("demo", help="데모인수증 생성")
    s.add_argument("spec", help="데모 요청 yaml")
    s.set_defaults(func=cmd_demo)

    s = sub.add_parser("visit", help="방문 계획")
    s.add_argument("hospitals", nargs="+")
    s.add_argument("--date")
    s.set_defaults(func=cmd_visit)

    s = sub.add_parser("task", help="할 일 관리")
    s.add_argument("action", choices=["list", "done", "doing", "drop", "todo"])
    s.add_argument("id", nargs="?")
    s.add_argument("--status", choices=list(tasks.VALID))
    s.add_argument("--hospital")
    s.add_argument("--pri", choices=["최상", "상", "중"])
    s.set_defaults(func=cmd_task)

    s = sub.add_parser("repair", help="장비 수리 접수 대장")
    s.add_argument("action", choices=["list", "open", "update"])
    s.add_argument("hospital", nargs="?")
    s.add_argument("device", nargs="?")
    s.add_argument("symptom", nargs="?")
    s.add_argument("--id")
    s.add_argument("--set", nargs="*", default=[], metavar="키=값")
    s.add_argument("--open-only", action="store_true")
    s.set_defaults(func=cmd_repair)

    s = sub.add_parser("ics", help="구글 캘린더용 ics 생성")
    s.add_argument("--month", help="YYYY-MM")
    s.add_argument("-o", "--out")
    s.set_defaults(func=cmd_ics)

    s = sub.add_parser("audit", help="데이터 결손·불일치 점검")
    s.set_defaults(func=cmd_audit)

    s = sub.add_parser("product", help="품목 정보")
    s.add_argument("name", nargs="?")
    s.set_defaults(func=cmd_product)

    s = sub.add_parser("casecover", help="케이스 커버 7축 점검표")
    s.add_argument("hospital", nargs="?")
    s.set_defaults(func=cmd_casecover)

    s = sub.add_parser("export", help="대시보드용 JSON 내보내기")
    s.add_argument("--date")
    s.add_argument("-o", "--out")
    s.set_defaults(func=cmd_export)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except registry.NotFound as exc:
        print(f"오류: {exc}", file=sys.stderr)
        return 2
    except (LookupError, ValueError) as exc:
        print(f"오류: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
