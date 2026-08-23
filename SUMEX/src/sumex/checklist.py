"""납품 체크리스트 — "이 병원에 갈 때 뭘 몇 장 들고 어디에 두고 오나".

병원마다 규칙이 전부 다르고 헷갈리기 쉬운 부분이라, 출력해서 차량에 비치할
용도로 만든다. 서류 매수를 잘못 준비하면 다시 출력하러 나가야 한다.
"""
from __future__ import annotations

from datetime import date
from typing import Any

from . import registry
from .registry import Hospital


def build(h: Hospital, when: date | None = None) -> dict[str, Any]:
    """체크리스트를 구조체로 만든다. 렌더링은 render_text/render_md 가 한다."""
    when = when or date.today()
    meta = registry.meta()
    copies = h.copies
    fallback = copies is None

    steps: list[str] = []

    # 1. 서류 준비
    doc_type = h.doc_type
    if fallback:
        steps.append(
            f"{doc_type} 준비 — 이 병원의 매수 규칙이 아직 확인되지 않았다. "
            f"기본 {meta.get('doc_default_copies', 4)}장 준비하고 현장에서 확정할 것"
        )
    else:
        steps.append(f"{doc_type} {copies}장 출력")

    src = h.doc.get("source_system")
    if src:
        steps.append(f"서류 출처: {src}")
    author = h.doc.get("author")
    if author:
        steps.append(f"서류 작성 주체: {author}")

    granularity = h.doc.get("granularity")
    if granularity:
        steps.append(f"★ 작성 단위: {granularity}")

    required = h.doc.get("fields_required")
    if required:
        steps.append(f"필수 기입 항목: {', '.join(required)}")

    # 2. 도장
    if h.stamp is True:
        kinds = h.doc.get("stamp_kinds")
        if kinds:
            steps.append(f"★ 도장 {len(kinds)}종 필요 — {' / '.join(kinds)} (하나라도 빠지면 서류 반려)")
        else:
            steps.append("★ 병원 도장 필요")
    elif h.stamp is False:
        steps.append("도장 불필요 — 제출만 하면 된다 (도장 찾다 시간 낭비하지 말 것)")

    # 3. 배부처
    for row in h.distribution:
        steps.append(f"→ {row.get('to')} : {row.get('copies')}장")
    note = h.doc.get("note")
    if note:
        steps.append(f"※ {note}")

    # 품목별로 서류가 다른 병원
    for variant in h.raw.get("doc_variants") or []:
        label = variant.get("product")
        if variant.get("copies") == 0:
            steps.append(f"[{label}] 병원 서류 처리 불필요 — {variant.get('note')}")
        else:
            dist = ", ".join(f"{d['to']} {d['copies']}장" for d in variant.get("distribution") or [])
            steps.append(f"[{label}] {variant.get('copies')}장 — {dist}")

    # 4. 납품 절차
    delivery = h.delivery
    order: list[str] = []
    if delivery.get("process"):
        order = [ln.strip() for ln in str(delivery["process"]).strip().splitlines() if ln.strip()]
    route = h.doc.get("route_order")
    if route:
        order.append("제출 순서: " + " → ".join(route))

    # 5. 하드 룰 (어기면 그날 일이 무산되는 것)
    hard: list[str] = []
    if delivery.get("windows"):
        hard.append("납품 가능 시간: " + " / ".join(delivery["windows"]))
    if delivery.get("cold_chain_cutoff"):
        hard.append(f"냉장·냉동 품목은 {delivery['cold_chain_cutoff']} 이전만 가능")
    if delivery.get("hard_rule"):
        hard.append(str(delivery["hard_rule"]))
    if delivery.get("packaging"):
        hard.append(str(delivery["packaging"]))
    if delivery.get("avoid"):
        hard.append(f"방문 자제: {delivery['avoid']}")
    if delivery.get("staff_window"):
        hard.append(str(delivery["staff_window"]))
    if h.raw.get("parking"):
        hard.append(f"주차장 운영: {h.raw['parking']}")

    # 6. 마감
    closing = h.closing
    closing_lines: list[str] = []
    if closing:
        if closing.get("rule"):
            closing_lines.append(str(closing["rule"]))
        if closing.get("how_to_find_deadline"):
            closing_lines.append(str(closing["how_to_find_deadline"]).strip())
        if closing.get("announced"):
            closing_lines.append(str(closing["announced"]))
        for item in closing.get("bundle") or []:
            closing_lines.append(f"지참: {item}")
        if closing.get("hard_rule"):
            closing_lines.append("★ " + str(closing["hard_rule"]).strip())
        if closing.get("time_limit"):
            closing_lines.append(str(closing["time_limit"]))
        if closing.get("order"):
            closing_lines.append("마감 순서: " + " → ".join(closing["order"]))
        if closing.get("collection"):
            closing_lines.append(f"수금: {closing['collection']}")
        if closing.get("after"):
            closing_lines.append(str(closing["after"]))

    return {
        "hospital": h,
        "date": when,
        "doc_type": doc_type,
        "copies": copies,
        "copies_unconfirmed": fallback,
        "steps": steps,
        "order": order,
        "hard": hard,
        "closing": closing_lines,
        "cautions": h.cautions,
        "watch": h.watch,
        "open": h.open_items,
        "conflicts": h.conflicts,
        "consignment": h.consignment,
        "products": [p["name"] for p in registry.products_for(h.id)],
        "contacts": h.contacts(),
    }


def render_text(data: dict[str, Any]) -> str:
    h: Hospital = data["hospital"]
    w: list[str] = []
    bar = "─" * 58

    w.append(bar)
    w.append(f" {h.name}  납품 체크리스트   ({data['date']:%Y-%m-%d})")
    w.append(bar)
    w.append(f" 서류종류 : {data['doc_type']}")
    w.append(f" 매수     : {data['copies'] if data['copies'] is not None else '미확인'}"
             + ("   ← 현장에서 확정 필요" if data["copies_unconfirmed"] else ""))
    w.append(f" 간납사   : {data['consignment'] or '없음 (직거래)'}")
    if data["products"]:
        w.append(f" 주요품목 : {', '.join(data['products'])}")
    w.append("")

    def block(title: str, lines: list[str], bullet: str = "·") -> None:
        if not lines:
            return
        w.append(f"[{title}]")
        for ln in lines:
            for i, part in enumerate(str(ln).splitlines()):
                w.append(f"  {bullet} {part}" if i == 0 else f"    {part}")
        w.append("")

    block("서류", data["steps"])
    block("절차", data["order"], bullet="›")
    block("반드시 지킬 것", data["hard"], bullet="★")
    block("월 마감", data["closing"])
    block("주의", data["cautions"], bullet="!")
    block("진행 중인 건", data["watch"])
    block("확인 필요", data["open"], bullet="?")

    if data["conflicts"]:
        w.append("[출처 불일치 — 현장에서 확정할 것]")
        for c in data["conflicts"]:
            w.append(f"  ? {c.get('field')}")
            w.append(f"      인수인계서: {c.get('A')}")
            w.append(f"      현장확인:   {c.get('B')}")
            w.append(f"      → {c.get('action')}")
        w.append("")

    if data["contacts"]:
        w.append("[담당자]")
        for c in data["contacts"]:
            bits = [c.get("name"), c.get("role"), c.get("dept"), c.get("phone")]
            w.append("  · " + " / ".join(str(b) for b in bits if b))
        w.append("")

    return "\n".join(w).rstrip() + "\n"


def render_md(data: dict[str, Any]) -> str:
    h: Hospital = data["hospital"]
    w: list[str] = [f"# {h.name} 납품 체크리스트", ""]
    w.append(f"- **서류**: {data['doc_type']} "
             f"{data['copies'] if data['copies'] is not None else '(매수 미확인)'}장")
    w.append(f"- **간납사**: {data['consignment'] or '없음 (직거래)'}")
    w.append(f"- **작성일**: {data['date']:%Y-%m-%d}")
    w.append("")

    def block(title: str, lines: list[str]) -> None:
        if not lines:
            return
        w.append(f"## {title}")
        for ln in lines:
            w.append(f"- {str(ln).replace(chr(10), ' ')}")
        w.append("")

    block("서류 준비·배부", data["steps"])
    block("납품 절차", data["order"])
    block("반드시 지킬 것", data["hard"])
    block("월 마감", data["closing"])
    block("주의", data["cautions"])
    block("진행 중인 건", data["watch"])
    block("확인 필요", data["open"])
    return "\n".join(w).rstrip() + "\n"


def audit() -> list[dict[str, Any]]:
    """전 거래처의 데이터 결손·불일치를 훑는다. 무엇을 먼저 확인해야 하는지 알려준다."""
    findings: list[dict[str, Any]] = []
    for h in registry.hospitals():
        if h.raw.get("kind"):        # 협력사·공급사는 제외
            continue
        if h.copies is None and not h.raw.get("doc_variants"):
            findings.append({"hospital": h.name, "kind": "매수 미확인",
                             "detail": "서류를 몇 장 준비해야 하는지 모른다"})
        if h.copies is not None and h.distribution:
            total = sum(d.get("copies", 0) for d in h.distribution)
            if total != h.copies:
                findings.append({"hospital": h.name, "kind": "매수 불일치",
                                 "detail": f"총 {h.copies}장인데 배부처 합계는 {total}장"})
        if h.copies is not None and not h.distribution and not h.raw.get("doc_variants"):
            findings.append({"hospital": h.name, "kind": "배부처 미기재",
                             "detail": f"{h.copies}장을 어디에 두고 오는지 모른다"})
        for c in h.conflicts:
            findings.append({"hospital": h.name, "kind": "출처 불일치",
                             "detail": f"{c.get('field')} — {c.get('action')}"})
        for o in h.open_items:
            findings.append({"hospital": h.name, "kind": "확인 필요", "detail": o})
    return findings
