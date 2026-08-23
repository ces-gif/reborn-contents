"""상품 사진에서 상품명 / 정가 / 할인가 / 한 줄 소개를 읽어낸다.

원칙 (기존 리본마켓 스킬의 규칙을 그대로 따른다):
- 가격은 사진 속 가격표에서 읽은 것만 쓴다. 안 보이면 지어내지 않고 needs_review 로 넘긴다.
- 사진에 안 보이는 스펙은 쓰지 않는다.
- "중고" 라는 표현은 절대 쓰지 않는다 (리퍼브 = 검수된 새 상품).
"""

from __future__ import annotations

import base64
import io
import json
import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path

from PIL import Image, ImageOps

log = logging.getLogger(__name__)

MAX_EDGE = 1568  # Claude 비전 입력 권장 최대 변
JPEG_QUALITY = 82

SYSTEM = """당신은 리본마켓 평택점의 콘텐츠 담당자입니다.
리본마켓은 리퍼브(검수를 마친 새 상품) 전문 매장입니다. "중고"라는 단어는 절대 쓰지 않습니다.

매장에서 찍은 상품 사진 여러 장(같은 상품을 여러 각도에서 찍은 것)을 보고,
카드뉴스에 쓸 정보를 뽑아냅니다.

절대 규칙:
1. 가격은 사진 속 가격표/POP에 실제로 적혀 있는 숫자만 씁니다. 추정·검색·상식으로 지어내지 않습니다.
2. 가격표에 정가(온라인 판매가)와 할인가가 둘 다 보이면 둘 다 적습니다.
   하나만 보이면 그 하나만 적고 나머지는 null 로 둡니다.
3. 가격을 하나도 읽을 수 없으면 needs_review 를 true 로 하고 review_reason 에 이유를 적습니다.
4. 한 줄 소개는 사진에서 실제로 확인되는 것(제품 종류, 색상, 구성품, 가격표에 적힌 문구)만 근거로 씁니다.
   보이지 않는 스펙(용량, 소비전력, 연식 등)은 사진이나 가격표에 적혀 있지 않으면 쓰지 않습니다.
5. 상품명은 가격표에 적힌 그대로를 우선합니다. 가격표에 없으면 사진 속 제품의 브랜드/로고/모델명으로 씁니다.
6. 상품이 아닌 사진(매장 전경, 간판, 영수증, 사람만 있는 사진 등)이면 is_product 를 false 로 합니다."""

USER_TEMPLATE = """아래는 같은 상품을 찍은 사진 {n}장입니다 (1번부터 순서대로).
가격표가 찍혀 있으면 거기 적힌 상품명과 가격을 그대로 읽어주세요.

extract_product 도구를 정확히 한 번 호출해서 결과를 주세요."""

TOOL = {
    "name": "extract_product",
    "description": "사진에서 읽어낸 상품 정보를 구조화해서 돌려준다.",
    "input_schema": {
        "type": "object",
        "properties": {
            "is_product": {
                "type": "boolean",
                "description": "판매 상품 사진이면 true. 매장 전경/간판/영수증 등이면 false.",
            },
            "product_name": {
                "type": "string",
                "description": "카드뉴스에 넣을 상품명. 가격표 표기 우선. 30자 이내 권장.",
            },
            "one_liner": {
                "type": "string",
                "description": "사진에서 확인되는 사실만 담은 한 줄 소개. 40자 이내. '중고' 금지.",
            },
            "category": {
                "type": "string",
                "description": "가전 / 가구 / 주방 / 홈리빙 / 육아 / 반려 / 기타 중 하나",
            },
            "original_price": {
                "type": ["integer", "null"],
                "description": "가격표에 적힌 할인 전 가격(정가·온라인 판매가). 없으면 null.",
            },
            "sale_price": {
                "type": ["integer", "null"],
                "description": "가격표에 적힌 리본마켓 판매가. 없으면 null.",
            },
            "discount_pct": {
                "type": ["integer", "null"],
                "description": "가격표에 할인율이 직접 적혀 있으면 그 숫자. 없으면 null (계산은 우리가 한다).",
            },
            "price_source": {
                "type": "string",
                "description": "가격을 어디서 읽었는지. 예: '3번 사진 가격표', '읽을 수 없음'",
            },
            "best_photo_index": {
                "type": "integer",
                "description": "카드뉴스에 쓸 가장 좋은 사진 번호(1부터). 상품이 크게, 배경이 깔끔한 것.",
            },
            "appeal": {
                "type": "string",
                "description": "이 상품이 잘 팔릴 만한 이유 한 문장 (블로그 BEST5 선정 근거로 쓴다).",
            },
            "needs_review": {
                "type": "boolean",
                "description": "가격을 못 읽었거나 확신이 없어 사람이 확인해야 하면 true.",
            },
            "review_reason": {
                "type": "string",
                "description": "needs_review 가 true 인 이유. 아니면 빈 문자열.",
            },
        },
        "required": [
            "is_product",
            "product_name",
            "one_liner",
            "category",
            "original_price",
            "sale_price",
            "discount_pct",
            "price_source",
            "best_photo_index",
            "appeal",
            "needs_review",
            "review_reason",
        ],
    },
}


@dataclass
class Product:
    is_product: bool
    product_name: str
    one_liner: str
    category: str
    original_price: int | None
    sale_price: int | None
    discount_pct: int | None
    price_source: str
    best_photo_index: int
    appeal: str
    needs_review: bool
    review_reason: str
    photo_paths: list[str] = field(default_factory=list)
    source_file_ids: list[str] = field(default_factory=list)
    group_index: int = 0

    @property
    def best_photo(self) -> Path:
        idx = max(1, min(self.best_photo_index, len(self.photo_paths)))
        return Path(self.photo_paths[idx - 1])

    @property
    def computed_pct(self) -> int | None:
        if self.discount_pct is not None:
            return self.discount_pct
        if self.original_price and self.sale_price and self.original_price > self.sale_price:
            return round((self.original_price - self.sale_price) / self.original_price * 100)
        return None

    @property
    def publishable(self) -> bool:
        """카드뉴스로 만들 수 있는 상태인가."""
        return bool(self.is_product and self.sale_price and not self.needs_review)

    def to_dict(self) -> dict:
        data = asdict(self)
        data["computed_pct"] = self.computed_pct
        data["publishable"] = self.publishable
        return data


def encode_image(path: Path) -> dict:
    img = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    img.thumbnail((MAX_EDGE, MAX_EDGE), Image.LANCZOS)
    buffer = io.BytesIO()
    img.save(buffer, "JPEG", quality=JPEG_QUALITY)
    return {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": "image/jpeg",
            "data": base64.standard_b64encode(buffer.getvalue()).decode("ascii"),
        },
    }


def extract_product(
    client, photo_paths: list[Path], *, model: str, group_index: int = 0, source_file_ids=None
) -> Product:
    content: list[dict] = []
    for i, path in enumerate(photo_paths, start=1):
        content.append({"type": "text", "text": f"[{i}번 사진]"})
        content.append(encode_image(path))
    content.append({"type": "text", "text": USER_TEMPLATE.format(n=len(photo_paths))})

    response = client.messages.create(
        model=model,
        max_tokens=1500,
        system=SYSTEM,
        tools=[TOOL],
        tool_choice={"type": "tool", "name": "extract_product"},
        messages=[{"role": "user", "content": content}],
    )

    payload = None
    for block in response.content:
        if block.type == "tool_use" and block.name == "extract_product":
            payload = block.input
            break
    if payload is None:  # pragma: no cover - tool_choice 로 강제되어 있다
        raise RuntimeError(f"비전 모델이 도구를 호출하지 않았습니다: {response}")

    product = Product(
        **{k: payload.get(k) for k in TOOL["input_schema"]["required"]},
        photo_paths=[str(p) for p in photo_paths],
        source_file_ids=list(source_file_ids or []),
        group_index=group_index,
    )
    return _sanity_check(product)


def _sanity_check(p: Product) -> Product:
    """모델이 실수했을 때 조용히 잘못된 가격이 카드에 찍히는 것을 막는다."""
    reasons: list[str] = []

    if p.sale_price is not None and p.sale_price <= 0:
        p.sale_price = None
    if p.original_price is not None and p.original_price <= 0:
        p.original_price = None

    if p.is_product and p.sale_price is None:
        reasons.append("가격표에서 판매가를 읽지 못했습니다")

    if p.original_price and p.sale_price and p.original_price <= p.sale_price:
        # 정가가 할인가보다 싸면 둘 중 하나를 잘못 읽은 것이다 → 정가를 버린다
        log.warning(
            "정가(%s)가 할인가(%s)보다 작거나 같아 정가를 버립니다: %s",
            p.original_price,
            p.sale_price,
            p.product_name,
        )
        p.original_price = None
        p.discount_pct = None

    pct = p.computed_pct
    if pct is not None and not (0 < pct < 95):
        reasons.append(f"할인율이 비정상입니다({pct}%)")

    if "중고" in (p.one_liner or "") or "중고" in (p.product_name or ""):
        p.one_liner = (p.one_liner or "").replace("중고", "리퍼브")
        p.product_name = (p.product_name or "").replace("중고", "리퍼브")

    if reasons:
        p.needs_review = True
        p.review_reason = "; ".join(filter(None, [p.review_reason, *reasons]))
    return p


def load_products(path: Path) -> list[Product]:
    data = json.loads(path.read_text(encoding="utf-8"))
    keys = set(TOOL["input_schema"]["required"]) | {
        "photo_paths",
        "source_file_ids",
        "group_index",
    }
    return [Product(**{k: v for k, v in item.items() if k in keys}) for item in data]


def save_products(products: list[Product], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps([p.to_dict() for p in products], ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return path
