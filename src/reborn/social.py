"""카드뉴스에 딸려 나가는 짧은 글: 카톡 공지 / 인스타 캡션 / 릴스 캡션.

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


# ---------------------------------------------------------------- 릴스 캡션
# 피드 캡션과 다르다. 릴스는 **첫 줄만 보이고** 나머지는 "더 보기"에 접힌다.
# 그래서 상품을 다 나열하지 않고 후킹 한 줄로 세운 뒤, 할인폭이 큰 셋만 보여준다.
# 매장 실제 릴스 게시물에는 해시태그가 없어서 붙이지 않는다.
HOOK_BY_CATEGORY = {
    "주방": "주방 새로 채우지 마세요!",
    "가구": "가구 새로 사지 마세요!",
    "생활": "생활용품 정가 주고 사지 마세요!",
    "가전": "가전 정가 주고 사지 마세요!",
    "유아": "육아템 새로 사지 마세요!",
}
DEFAULT_HOOK = "정가 주고 사지 마세요!"
REEL_HIGHLIGHTS = 3


def _hook(products: list[Product]) -> str:
    """가장 많이 나온 분류로 후킹을 고른다. 모르면 무난한 기본 문구."""
    counts: dict[str, int] = {}
    for p in products:
        key = (p.category or "").strip()
        if key:
            counts[key] = counts.get(key, 0) + 1
    for category in sorted(counts, key=lambda c: -counts[c]):
        for keyword, hook in HOOK_BY_CATEGORY.items():
            if keyword in category:
                return hook
    return DEFAULT_HOOK


def _biggest_savings(products: list[Product], count: int) -> list[Product]:
    """할인 **금액**이 큰 순서. 퍼센트가 아니라 아낀 돈이 눈에 들어온다."""
    priced = [p for p in products if p.original_price and p.original_price > p.sale_price]
    priced.sort(key=lambda p: p.original_price - p.sale_price, reverse=True)
    return priced[:count] or products[:count]


def reel_caption(
    products: list[Product],
    *,
    store_name: str,
    address: str = "",
    parking_note: str = "",
) -> str:
    """릴스에 붙일 캡션. 영상과 같은 폴더에 나란히 둔다."""
    lines = [_hook(products), f"{store_name}에 오면 반값에 득템 가능해요.", ""]

    for p in _biggest_savings(products, REEL_HIGHLIGHTS):
        if p.original_price:
            lines.append(f"{p.product_name} {p.sale_price:,}원 (원가 {p.original_price:,}원)")
        else:
            lines.append(f"{p.product_name} {p.sale_price:,}원")
    lines += [
        "",
        "✔ 포장만 뜯긴 리퍼 새상품만 (중고 절대 X)",
        "✔ 대표·직원이 1차·2차 직접 검수 완료",
        "✔ 교환·환불 OK",
        "",
    ]
    # 주소를 모르는 매장은 지어내지 않는다. 매장 이름만 남긴다.
    lines.append(f"📍 {address}" if address else f"📍 {store_name}")
    if parking_note:
        lines.append(parking_note)
    return "\n".join(lines).strip()
