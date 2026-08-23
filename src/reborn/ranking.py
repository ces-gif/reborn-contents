"""오늘 들어온 상품 중 '잘 팔릴 만한' BEST N 을 고른다.

1차로 규칙 기반 점수를 매기고(할인율·절약액·카테고리),
2차로 모델에게 순위를 다시 물어본다. 모델 호출이 실패해도 규칙 점수로 그대로 굴러간다.
"""

from __future__ import annotations

import json
import logging

from pydantic import BaseModel, Field

from .llm import LLMClient, text_part
from .vision import Product

log = logging.getLogger(__name__)

# 리본마켓에서 실제로 회전이 빠른 순서 (매장 판매 특성 반영)
CATEGORY_WEIGHT = {
    "가전": 1.00,
    "주방": 0.92,
    "가구": 0.88,
    "홈리빙": 0.84,
    "육아": 0.86,
    "반려": 0.80,
    "기타": 0.70,
}

class RankedItem(BaseModel):
    id: int = Field(description="상품 id")
    why: str = Field(description="이 순위인 이유 한 문장 (가격 대비 매력, 수요 등).")


class Ranking(BaseModel):
    ranking: list[RankedItem] = Field(description="잘 팔릴 것 같은 순서대로 나열한 상품 목록.")


def rule_score(product: Product) -> float:
    pct = product.computed_pct or 0
    saving = (product.original_price or 0) - (product.sale_price or 0)
    # 할인율(0~1) 60% + 절약액(로그 스케일) 40%, 카테고리 가중치
    pct_score = min(pct, 80) / 80
    saving_score = min(max(saving, 0), 1_500_000) / 1_500_000
    base = pct_score * 0.6 + saving_score * 0.4
    return round(base * CATEGORY_WEIGHT.get(product.category, 0.7), 4)


def pick_best(
    products: list[Product], *, count: int, client=None, model: str | None = None
) -> list[tuple[Product, str]]:
    """(상품, 선정 이유) 목록을 순위대로 돌려준다."""
    candidates = [p for p in products if p.publishable]
    if not candidates:
        return []

    ranked = sorted(candidates, key=rule_score, reverse=True)
    if len(candidates) <= count or client is None or model is None:
        return [(p, p.spec_line or "") for p in ranked[:count]]

    pool = ranked[: max(count * 3, 10)]
    listing = [
        {
            "id": i,
            "상품명": p.product_name,
            "카테고리": p.category,
            "한줄소개": p.card_line,
            "제품설명": p.description,
            "온라인판매가": p.original_price,
            "리본가": p.sale_price,
            "할인율": p.computed_pct,
        }
        for i, p in enumerate(pool)
    ]

    try:
        result: Ranking = client.structured(
            system=(
                "당신은 리본마켓 평택점 점장입니다. 리퍼브(검수 완료 새 상품) 매장을 운영합니다.\n"
                "오늘 매장에 들어온 상품 목록을 보고 '실제로 가장 잘 팔릴 것 같은' 순서대로 고릅니다.\n"
                "판단 기준: 할인 폭이 체감되는가, 평택 지역 손님(신혼·이사·자취·육아)이 찾는 물건인가, "
                "가격대가 즉시 결제 가능한 범위인가, 매장에 직접 보러 올 이유가 되는가."
            ),
            parts=[
                text_part(
                    f"오늘 상품 목록입니다.\n\n{json.dumps(listing, ensure_ascii=False, indent=2)}\n\n"
                    f"가장 잘 팔릴 것 같은 순서대로 상위 {count}개를 골라주세요."
                )
            ],
            schema=Ranking,
            max_tokens=4000,
            model=model,
        )
        picked: list[tuple[Product, str]] = []
        used: set[int] = set()
        for item in result.ranking:
            if 0 <= item.id < len(pool) and item.id not in used:
                used.add(item.id)
                picked.append((pool[item.id], item.why))
            if len(picked) == count:
                break
        if picked:
            return picked
    except Exception as exc:  # 순위 매기기는 실패해도 파이프라인을 멈추지 않는다
        log.warning("모델 순위 선정 실패, 규칙 점수로 대체합니다: %s", exc)

    return [(p, p.spec_line or "") for p in ranked[:count]]
