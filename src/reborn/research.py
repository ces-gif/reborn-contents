"""가격표에서 읽은 상품명으로 인터넷을 찾아 짧은 설명을 붙인다.

은성님 지시(2026-08-23): "해당 상품을 인터넷에서 찾아서 거기에 맞는 약간의 설명을 더해주면 좋겠어."

Claude API 의 서버 도구 web_search 를 쓴다 (별도 검색 API 키가 필요 없다).
검색으로 그 모델이 확인되지 않으면 matched=False 로 두고 **아무 설명도 붙이지 않는다** —
없는 스펙을 지어내느니 비워두는 편이 낫다.
"""

from __future__ import annotations

import logging

from pydantic import BaseModel, Field

from .llm import LLMClient, LLMError, LLMQuotaError, text_part
from .vision import Product, strip_unevidenced_claims

log = logging.getLogger(__name__)

class Research(BaseModel):
    matched: bool = Field(
        description=(
            "검색으로 이 제품(또는 같은 라인의 제품)이 확인되면 true. "
            "확인이 안 되면 false — 이 경우 나머지 항목은 모두 비운다."
        )
    )
    official_name: str = Field(description="검색으로 확인된 정식 제품명. 확인 안 되면 빈 문자열.")
    spec_line: str = Field(
        description=(
            "카드뉴스에 넣을 한 줄 설명. 40자 이내. 제품이 무엇이고 핵심 기능이 뭔지만. "
            "예: '12kg 인버터 드럼세탁기, 스팀 살균 코스'. "
            "가격·할인·재고·상품 상태는 넣지 않는다. 확인 안 되면 빈 문자열."
        )
    )
    description: str = Field(
        description=(
            "블로그에 넣을 설명 2~3문장. 어떤 제품이고 어떤 사람에게 맞는지. "
            "검색으로 확인된 사실만. 확인 안 되면 빈 문자열."
        )
    )
    key_points: list[str] = Field(
        description="검색으로 확인된 특징 최대 3개. 각 20자 이내. 확인 안 되면 빈 배열."
    )
    sources: list[str] = Field(description="근거로 삼은 페이지 URL 최대 3개.")


SYSTEM = """당신은 리본마켓 평택점의 콘텐츠 담당자입니다.
매장 가격표에서 읽은 상품명을 받아, 그 제품이 무엇인지 인터넷에서 확인하고
카드뉴스와 블로그에 넣을 짧은 설명을 만듭니다.

절대 규칙:
1. 검색해서 확인된 내용만 씁니다. 기억이나 추측으로 스펙을 쓰지 않습니다.
2. 검색해도 그 제품을 특정할 수 없으면 matched=false 로 두고 나머지를 전부 비웁니다.
   틀린 설명을 붙이는 것보다 설명이 없는 편이 낫습니다.
3. **상품의 상태를 쓰지 않습니다.** "미사용", "전시상품", "박스 개봉", "새것 같은" 같은 말은
   매장 가격표에 적힌 내용이지 인터넷에서 알 수 있는 게 아닙니다. 절대 넣지 마세요.
4. 가격, 할인율, 재고, 구매처를 쓰지 않습니다. 가격은 매장 가격표가 유일한 근거입니다.
5. "중고"라는 단어를 쓰지 않습니다. 리본마켓은 리퍼브(검수를 마친 새 상품) 매장입니다.
6. 광고 문구를 쓰지 않습니다. "최고", "강력 추천" 같은 표현 대신 사실만 담백하게 씁니다.
7. 모델명이 일부만 일치하는 다른 제품을 그 제품인 양 설명하지 않습니다.
   확실하지 않으면 matched=false 입니다."""


def research_product(client: LLMClient, product: Product, *, model: str) -> Product:
    """상품에 spec_line / description / key_points / sources 를 채워 넣는다.

    검색이 실패하거나 제품을 특정하지 못하면 아무것도 채우지 않고 그대로 돌려준다.
    """
    prompt = (
        f"매장 가격표에서 읽은 상품명: {product.product_name}\n"
        f"분류: {product.category}\n"
        f"가격표 원문: {product.tag_text or '(없음)'}\n\n"
        "이 제품을 인터넷에서 찾아서 어떤 제품인지 확인해 주세요.\n"
        "확인되면 카드뉴스용 한 줄(spec_line)과 블로그용 설명(description)을 만들어 주세요.\n"
        "특정할 수 없으면 matched 를 false 로 두세요."
    )

    try:
        result: Research = client.structured(
            system=SYSTEM,
            parts=[text_part(prompt)],
            schema=Research,
            max_tokens=8000,
            search=True,
            model=model,
        )
    except LLMQuotaError:
        raise
    except (LLMError, Exception) as exc:  # 검색 실패로 하루치 발행을 멈추지 않는다
        log.warning("'%s' 웹 검색 실패(설명 없이 진행): %s", product.product_name, exc)
        return product

    if not result.matched:
        log.info("'%s' 은(는) 검색으로 특정하지 못해 설명을 붙이지 않습니다", product.product_name)
        return product

    # 검색 결과에도 상태 표현이 섞여 들어올 수 있으니 한 번 더 걷어낸다.
    product.spec_line = strip_unevidenced_claims(result.spec_line.strip(), product.evidence_text)[:60]
    product.description = strip_unevidenced_claims(result.description.strip(), product.evidence_text)
    product.key_points = [
        strip_unevidenced_claims(p.strip(), product.evidence_text) for p in result.key_points[:3]
    ]
    product.key_points = [p for p in product.key_points if p]
    product.sources = [s for s in result.sources[:3] if s.startswith("http")]
    product.research_matched = True
    log.info("  ↳ 검색 확인: %s | %s", result.official_name or product.product_name, product.spec_line)
    return product


def research_all(client: LLMClient, products: list[Product], *, model: str) -> list[Product]:
    for product in products:
        if not product.publishable:
            continue
        try:
            research_product(client, product, model=model)
        except LLMQuotaError as exc:
            # 한도를 다 썼으면 나머지도 전부 같은 오류다. 설명 없이 발행은 계속한다.
            log.warning("하루 요청 한도를 다 써서 상품 설명 붙이기를 여기서 멈춥니다: %s", exc)
            break
    return products
