"""카드뉴스에 딸려 나가는 짧은 글: 카톡 오픈채팅 공지 / 인스타 캡션.

모델을 부르지 않고 템플릿으로 만든다 (기존 스킬의 표기 습관을 그대로 반영).
- 구조용 이모지만 사용 (✔ 📍 ✨)
- 마크다운 금지
- "중고" 금지
- CTA 는 하나
"""

from __future__ import annotations

from datetime import date

from .vision import Product


def _price_block(p: Product) -> str:
    if p.original_price and p.computed_pct:
        return (
            f"온라인 판매가 {p.original_price:,}원\n"
            f"→ 리본마켓 초특가 {p.sale_price:,}원 ({p.computed_pct}%↓)"
        )
    return f"리본마켓 초특가 {p.sale_price:,}원"


def kakao_notice(products: list[Product], *, day: date, store_name: str, footer_note: str) -> str:
    """오픈채팅방 공지 텍스트. 카드뉴스 이미지와 함께 올린다."""
    lines = [
        f"✨ {day.strftime('%m월 %d일')} {store_name} 오늘의 특가",
        "",
        "회원님, 오늘 매장에 새로 들어온 상품 안내드립니다.",
        "",
    ]
    for i, p in enumerate(products, start=1):
        lines.append(f"{i}. {p.product_name}")
        if p.card_line:
            lines.append(f"   {p.card_line}")
        lines.append("   " + _price_block(p).replace("\n", "\n   "))
        lines.append("")
    lines += [
        "✔ 리본마켓은 검수를 마친 리퍼브 상품만 취급합니다",
        "✔ 매장에서 직접 보고 구매하실 수 있습니다",
        "",
        f"📍 {store_name}",
        footer_note,
    ]
    return "\n".join(lines).strip()


def instagram_caption(
    products: list[Product], *, day: date, store_name: str, handle: str
) -> str:
    top = products[0] if products else None
    lines = [f"{day.strftime('%m.%d')} 오늘의 리본 특가 🧡", ""]
    if top:
        lines += [
            f"{top.product_name}",
            _price_block(top),
            "",
        ]
    if len(products) > 1:
        lines.append("오늘 함께 들어온 상품")
        for p in products[1:]:
            pct = f" ({p.computed_pct}%↓)" if p.computed_pct else ""
            lines.append(f"✔ {p.product_name} {p.sale_price:,}원{pct}")
        lines.append("")
    lines += [
        "리본마켓은 검수를 마친 리퍼브 상품만 취급합니다.",
        "재고는 한정 수량이라 매장에서 먼저 나가는 편이에요.",
        "",
        f"📍 {store_name}",
        "지금 매장에 오시면 실물로 확인하실 수 있어요 🙂",
        "",
        _hashtags(products, handle),
    ]
    return "\n".join(lines).strip()


def _hashtags(products: list[Product], handle: str) -> str:
    tags = ["리본마켓", "평택리퍼브", "평택가전", "리퍼브가전", "평택중고아닌리퍼브"]
    for p in products[:5]:
        head = (p.product_name or "").split()
        if head:
            tags.append(head[0].replace("#", ""))
        if p.category:
            tags.append(f"리퍼브{p.category}")
    seen: list[str] = []
    for t in tags:
        t = t.strip()
        if t and t not in seen:
            seen.append(t)
    return " ".join(f"#{t}" for t in seen) + f" {handle}"
