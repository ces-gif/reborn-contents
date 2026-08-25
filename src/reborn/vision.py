"""상품 사진에서 상품명 / 정가 / 할인가를 읽어낸다.

은성님 촬영 방식에 맞춘 설계:
  - 가격표 사진 1장 + 상품 사진 1장  (연속 촬영이라 하나로 묶인다)
  - 또는 가격표와 상품이 한 장에 같이 나온 사진 1장

원칙 (기존 리본마켓 스킬 규칙 + 2026-08-23 은성님 지시):
- 가격은 사진 속 가격표에서 읽은 것만 쓴다. 안 보이면 지어내지 않고 needs_review 로 넘긴다.
- **상태 표현("미사용", "전시상품", "박스 개봉" 등)은 가격표에 적혀 있을 때만 쓴다.**
  사진만 보고 상태를 추측해서 적지 않는다.
- 카드뉴스에 쓸 사진은 반드시 '상품이 보이는 사진'이어야 한다.
  묶음에 가격표 사진밖에 없으면 그건 정보 전달용이므로 카드뉴스를 만들지 않는다.
- "중고" 라는 표현은 절대 쓰지 않는다 (리퍼브 = 검수된 새 상품).
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from .llm import LLMClient, image_part, text_part

log = logging.getLogger(__name__)

PhotoKind = Literal["price_tag", "product", "both", "other"]

# 가격표에 근거 없이 쓰면 안 되는 상태 표현들 (은성님 지시: "정보가 없으면 함부로 적지마").
# 같은 패턴이 가격표 원문(tag_text)에서도 잡히면 근거가 있는 것으로 보고 남긴다.
CLAIM_PATTERNS = [
    re.compile(pattern)
    for pattern in (
        r"미사용",
        r"새\s?(제품|상품|것)",
        r"미개봉",
        r"(박스|단순|포장)?\s?개봉",
        r"전시\s?(상품|품)?",
        r"반품",
        r"리퍼(브)?",
        r"[A-Sa-s]\s?급",
        r"스크래치",
        r"흠집",
        r"파손",
        r"사용감",
        r"정품",
        r"보증",
        r"무상\s?A/?S",
    )
]

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?。])\s+|\n+")

# 카드가 **틀리게** 나가는 사유만 발행을 막는다.
# "가격표 글자가 조금 흐릿하다" 같은 건 카드를 만들고 리포트에만 적는다 —
# 이름이 조금 덜 정확한 카드가, 카드가 아예 없는 것보다 낫다.
MISMATCH_PATTERNS = [
    re.compile(pattern)
    for pattern in (
        r"서로 다릅니다",
        r"서로 다른",
        r"일치하지 않",
        r"불일치",
        r"다른 상품",
        r"상품이 바뀌",
    )
]


def _blocks_publishing(reason: str) -> bool:
    """이 사유 때문에 카드를 만들면 안 되는가.

    상품과 가격표가 서로 다른 물건이면 **틀린 가격**이 카드에 찍힌다. 그건 막는다.
    글자가 흐리다거나 모델명이 애매하다는 건 막지 않는다.
    """
    return any(pattern.search(reason) for pattern in MISMATCH_PATTERNS)


class PhotoRead(BaseModel):
    index: int = Field(description="사진 번호 (1부터)")
    kind: PhotoKind = Field(
        description=(
            "price_tag=가격표가 주인공, product=상품만 찍힘, "
            "both=상품 생김새가 보이면서 가격표도 같이 찍힘, other=둘 다 아님"
        )
    )
    product_visible: bool = Field(
        default=False,
        description=(
            "이 사진만 보고 **무슨 물건인지 알아볼 수 있으면** true. "
            "가격표가 화면 대부분을 차지하거나, 흰 상자면·벽·천처럼 무엇인지 알 수 없는 면만 "
            "보이면 false. 카드뉴스 배경으로 쓸 수 있는 사진인지를 정하는 값이라 엄격하게 판단한다."
        ),
    )


class PhotoClass(BaseModel):
    index: int = Field(description="사진 번호 (1부터, 준 순서대로)")
    kind: PhotoKind = Field(
        description=(
            "price_tag=가격표만 찍힘, product=상품만 찍힘, "
            "both=상품과 가격표가 한 장에 같이 찍힘, other=상품 사진이 아님(매장 전경 등)"
        )
    )
    product_visible: bool = Field(
        default=False,
        description=(
            "이 사진만 보고 무슨 물건인지 알아볼 수 있으면 true. "
            "가격표가 화면 대부분이거나 흰 면만 보이면 false."
        ),
    )
    item: str = Field(
        description=(
            "이 사진의 상품이 무엇인지 짧게. "
            "가격표 사진이면 가격표에 적힌 상품명, 상품 사진이면 눈에 보이는 물건 이름. "
            "예: '1인용 공부 책상', '2단 빨래바구니', '게이밍 의자'. 모르겠으면 빈 문자열."
        )
    )


class PhotoBatch(BaseModel):
    photos: list[PhotoClass] = Field(description="준 사진 수와 정확히 같은 개수로 답한다.")


CLASSIFY_SYSTEM = """당신은 리본마켓 평택점의 콘텐츠 담당자입니다.
매장에서 찍은 사진들을 한 장씩 분류합니다. 오직 분류만 하고 가격은 읽지 않습니다.

- price_tag : 가격표(POP)가 주인공인 사진. 종이/스티커에 상품명과 가격이 적힌 것.
- product   : 상품만 찍힌 사진. 가격표가 없거나 알아볼 수 없게 작게 나온 것.
- both      : 한 장에 **상품의 생김새를 알아볼 수 있게** 나오고 가격표도 같이 보이는 사진.
- other     : 매장 전경, 간판, 영수증, 사람만 나온 사진 등 상품 사진이 아닌 것.

**both 와 price_tag 를 가르는 기준 (가장 자주 틀리는 곳입니다)**
가격표가 상품 위에 붙어 있어도, 사진에 보이는 것이 흰 상자면·벽·천 같은
"무엇인지 알 수 없는 면" 뿐이라면 그건 **price_tag** 입니다.
"이 사진만 보고 무슨 물건인지 남에게 설명할 수 있는가?" 로 판단하세요.
설명할 수 없으면 both 가 아닙니다. 애매하면 price_tag 로 두세요 —
가격표 사진이 카드뉴스 배경으로 나가는 것이 가장 나쁜 결과입니다.

item 에는 **그 사진의 상품이 무엇인지**를 짧게 적습니다. 이걸로 같은 상품끼리 묶습니다.
가격표 사진이라면 가격표에 적힌 상품명을 그대로 적습니다 — 가장 중요합니다.
상품 사진이라면 눈에 보이는 물건 이름을 적습니다. 가격은 적지 않습니다.
반드시 준 사진 수와 같은 개수로, 준 순서 그대로 답합니다."""


class ProductRead(BaseModel):
    """비전 모델이 사진에서 읽어내는 것 — 사진에 실제로 보이는 것만."""

    photos: list[PhotoRead] = Field(description="사진마다 무엇이 찍혔는지. 준 사진 수와 같아야 한다.")
    product_name: str = Field(description="가격표에 적힌 상품명 그대로. 없으면 제품의 브랜드/모델명.")
    tag_text: str = Field(
        description=(
            "가격표에 적힌 글자를 보이는 대로 옮겨 적은 것. 상태 표기(전시상품 등)도 있으면 포함. "
            "가격표가 없으면 빈 문자열."
        )
    )
    condition_note: str = Field(
        description=(
            "가격표에 상품 상태가 적혀 있으면 그 표현만 그대로. "
            "가격표에 상태 표기가 없으면 반드시 빈 문자열. 사진만 보고 추측해서 쓰지 말 것."
        )
    )
    category: str = Field(description="가전 / 가구 / 주방 / 홈리빙 / 육아 / 반려 / 기타 중 하나")
    original_price: int | None = Field(description="가격표에 적힌 할인 전 가격(정가·온라인가). 없으면 null.")
    sale_price: int | None = Field(description="가격표에 적힌 리본마켓 판매가. 없으면 null.")
    discount_pct: int | None = Field(description="가격표에 할인율이 직접 적혀 있으면 그 숫자. 없으면 null.")
    price_source: str = Field(description="가격을 어디서 읽었는지. 예: '2번 사진 가격표', '읽을 수 없음'")
    best_photo_index: int = Field(
        description=(
            "카드뉴스에 쓸 사진 번호(1부터). 반드시 kind 가 product 또는 both 인 사진 중에서 고른다. "
            "상품이 보이는 사진이 하나도 없으면 0."
        )
    )
    needs_review: int | None = Field(
        default=None, description="사용하지 않음 (호환용). review_reason 으로 판단한다."
    )
    review_reason: str = Field(
        description="사람이 확인해야 할 이유가 있으면 적는다. 없으면 빈 문자열."
    )


SYSTEM = """당신은 리본마켓 평택점의 콘텐츠 담당자입니다.
리본마켓은 리퍼브(검수를 마친 새 상품) 전문 매장입니다. "중고"라는 단어는 절대 쓰지 않습니다.

매장에서 찍은 사진을 보고 카드뉴스에 쓸 정보를 뽑아냅니다.
사진은 보통 이렇게 들어옵니다:
  - 가격표 사진 1장 + 상품 사진 1장
  - 또는 가격표와 상품이 한 장에 같이 나온 사진 1장

절대 규칙:
1. 가격은 사진 속 가격표/POP 에 실제로 적혀 있는 숫자만 씁니다. 추정·검색·상식으로 지어내지 않습니다.
2. 가격표에 정가와 할인가가 둘 다 보이면 둘 다 적습니다. 하나만 보이면 그 하나만 적고 나머지는 null 로 둡니다.
3. 가격을 하나도 읽을 수 없으면 review_reason 에 이유를 적습니다.
4. **상품 상태를 지어내지 않습니다.** "미사용", "전시상품", "박스만 개봉", "새것 같은" 같은 표현은
   가격표에 그렇게 적혀 있을 때만 condition_note 에 그대로 옮겨 적습니다.
   가격표에 상태 표기가 없으면 condition_note 는 반드시 빈 문자열입니다.
   사진에 박스가 보인다거나 깨끗해 보인다는 이유로 상태를 단정하지 않습니다.
5. tag_text 에는 가격표에서 읽은 글자를 보이는 대로 옮겨 적습니다 (나중에 근거 확인용).
6. best_photo_index 는 상품이 보이는 사진(kind 가 product 또는 both) 중에서 고릅니다.
   가격표만 찍힌 사진은 카드뉴스 배경으로 쓰지 않습니다.
   상품이 보이는 사진이 하나도 없으면 0 을 넣습니다.
7. 상품명은 가격표 표기를 우선합니다. 가격표에 없으면 사진 속 제품의 브랜드/로고/모델명으로 씁니다."""

USER_TEMPLATE = """아래는 같은 상품을 찍은 사진 {n}장입니다 (1번부터 순서대로).
{source_note}
사진마다 가격표인지 상품인지 구분하고, 가격표에 적힌 상품명과 가격을 그대로 읽어주세요.
가격표에 없는 상품 상태는 적지 마세요."""

SOURCE_NOTES = {
    "refurb": (
        "이 상품은 '리퍼' 코너 상품입니다 — 검수를 마친 리퍼브 상품입니다.\n"
        "상품 상태(전시상품, 단순 개봉 등)는 가격표에 적혀 있을 때만 옮겨 적으세요."
    ),
    "new": (
        "이 상품은 '새상품' 코너 상품입니다 — 제조사와 직접 거래해 들여온 "
        "미개봉 새 제품을 초저가로 파는 코너입니다.\n"
        "따라서 '새상품'이라는 사실은 근거가 있습니다. 다만 그 외의 상태 표현"
        "(전시, 반품, 스크래치 등)은 가격표에 적혀 있을 때만 쓰세요."
    ),
}


@dataclass
class Product:
    """파이프라인이 실제로 들고 다니는 상품 정보."""

    product_name: str
    category: str
    tag_text: str = ""
    condition_note: str = ""
    original_price: int | None = None
    sale_price: int | None = None
    discount_pct: int | None = None
    price_source: str = ""
    best_photo_index: int = 0
    photo_kinds: list[str] = field(default_factory=list)
    needs_review: bool = False
    photo_shows_product: list[bool] = field(default_factory=list)
    review_reason: str = ""      # 발행을 막는 사유
    cautions: str = ""           # 카드는 만들되 사람이 한 번 볼 만한 것

    # 웹 검색으로 채워지는 부분 (research.py)
    spec_line: str = ""
    description: str = ""
    key_points: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    research_matched: bool = False

    photo_paths: list[str] = field(default_factory=list)
    source_file_ids: list[str] = field(default_factory=list)
    group_index: int = 0

    # 어느 폴더에서 온 상품인가 (리퍼 / 새상품)
    source_name: str = "상품"
    source_kind: str = "refurb"
    eyebrow: str = "오늘의 리본 특가"

    # ------------------------------------------------------------------ 파생

    @property
    def is_new_goods(self) -> bool:
        """제조사와 직거래한 미개봉 새상품 폴더에서 온 상품인가."""
        return self.source_kind == "new"

    @property
    def evidence_text(self) -> str:
        """상태 표현을 써도 되는지 판단할 때 쓰는 근거 텍스트.

        새상품 폴더는 폴더 자체가 '제조사 직거래 미개봉 새상품'이라는 근거다.
        리퍼 폴더는 가격표에 적힌 것만 근거가 된다.
        """
        if self.is_new_goods:
            return f"{self.tag_text} 새상품 새 제품 미개봉 정품"
        return self.tag_text

    @property
    def has_product_photo(self) -> bool:
        return bool(self._card_candidates())

    def _card_candidates(self) -> list[int]:
        """카드뉴스 배경으로 쓸 수 있는 사진 번호들 (1부터).

        종류가 product/both 인 것만으로는 부족하다. 흰 상자면에 가격표만 붙은 사진을
        모델이 both 로 부른 적이 있고, 그게 그대로 카드에 실렸다.
        그래서 '이 사진만 보고 무슨 물건인지 알아볼 수 있는가'(shows_product)를
        따로 묻고, 그 답이 참인 사진만 후보로 둔다.
        """
        shows = self.photo_shows_product or []
        return [
            i
            for i, kind in enumerate(self.photo_kinds, start=1)
            if kind in ("product", "both") and (i - 1 >= len(shows) or shows[i - 1])
        ]

    @property
    def best_photo(self) -> Path:
        """카드뉴스 배경으로 쓸 사진. 반드시 상품을 알아볼 수 있는 사진."""
        candidates = self._card_candidates()
        idx = self.best_photo_index
        if idx not in candidates:
            idx = candidates[0] if candidates else 0
        if not idx:
            raise ValueError(f"상품을 알아볼 수 있는 사진이 없습니다: {self.product_name}")
        return Path(self.photo_paths[idx - 1])

    @property
    def computed_pct(self) -> int | None:
        if self.discount_pct is not None:
            return self.discount_pct
        if self.original_price and self.sale_price and self.original_price > self.sale_price:
            return round((self.original_price - self.sale_price) / self.original_price * 100)
        return None

    @property
    def card_line(self) -> str:
        """카드뉴스 한 줄 소개 — 웹에서 확인된 상품 설명만.

        예전에는 설명이 없으면 가격표의 상태 표기를 여기에 넣었다. 그래서
        카드에 "까짐" 한 단어만 뜬 적이 있다. 상태 표기는 직원이 적어 둔
        **고지사항**(사용감·기스 등)이지 상품 소개가 아니다. 자리를 나눈다.
        상태 표기는 card_condition 으로 사진 위에 따로 붙는다.
        """
        return self.spec_line.strip()

    @property
    def card_condition(self) -> str:
        """카드 사진 위에 붙일 상태 고지. 가격표에 적힌 그대로만."""
        return self.condition_note.strip()

    @property
    def publishable(self) -> bool:
        """카드뉴스로 만들 수 있는 상태인가.

        needs_review 는 이제 **발행을 막는 사유**만 담는다. 글자가 흐리다는
        정도의 지적(cautions)은 카드를 만들고 리포트에만 적는다.
        """
        return bool(self.has_product_photo and self.sale_price and not self.needs_review)

    def to_dict(self) -> dict:
        data = asdict(self)
        data["cautions"] = self.cautions
        data["computed_pct"] = self.computed_pct
        data["publishable"] = self.publishable
        data["has_product_photo"] = self.has_product_photo
        data["card_line"] = self.card_line
        return data


def classify_photos(
    client: LLMClient, photo_paths: list[Path], *, model: str, batch_size: int = 16
) -> list[PhotoClass]:
    """사진마다 가격표인지 상품인지 먼저 분류한다.

    이걸 먼저 해야 같은 상품끼리 제대로 묶을 수 있다. 촬영 시각만으로 묶으면
    연달아 찍은 여러 상품이 한 덩어리가 되어버린다(실제로 그렇게 됐다).
    사진을 여러 장씩 묶어 한 번에 물어봐서 호출 수를 줄인다.
    """
    result: list[PhotoClass] = []
    for start in range(0, len(photo_paths), batch_size):
        chunk = photo_paths[start : start + batch_size]
        parts: list[dict] = []
        for i, path in enumerate(chunk, start=1):
            parts.append(text_part(f"[{i}번 사진]"))
            parts.append(image_part(path))
        parts.append(
            text_part(f"사진 {len(chunk)}장입니다. 각각 무엇이 찍혔는지 순서대로 분류해 주세요.")
        )
        try:
            batch: PhotoBatch = client.structured(
                system=CLASSIFY_SYSTEM,
                parts=parts,
                schema=PhotoBatch,
                max_tokens=2000,
                model=model,
            )
            got = {p.index: p for p in batch.photos}
        except Exception as exc:
            log.warning("사진 분류 실패(%d~%d번), 상품 사진으로 간주합니다: %s", start + 1, start + len(chunk), exc)
            got = {}

        for i in range(1, len(chunk) + 1):
            found = got.get(i)
            result.append(
                found.model_copy(update={"index": start + i})
                if found
                else PhotoClass(index=start + i, kind="product", item="")
            )
    return result


def extract_product(
    client: LLMClient,
    photo_paths: list[Path],
    *,
    model: str,
    group_index: int = 0,
    source_file_ids=None,
    source_name: str = "상품",
    source_kind: str = "refurb",
    eyebrow: str = "오늘의 리본 특가",
    known_kinds: list[str] | None = None,
    known_shows: list[bool] | None = None,
) -> Product:
    parts: list[dict] = []
    for i, path in enumerate(photo_paths, start=1):
        parts.append(text_part(f"[{i}번 사진]"))
        parts.append(image_part(path))
    parts.append(
        text_part(
            USER_TEMPLATE.format(
                n=len(photo_paths),
                source_note=SOURCE_NOTES.get(source_kind, SOURCE_NOTES["refurb"]),
            )
        )
    )

    read: ProductRead = client.structured(
        system=SYSTEM, parts=parts, schema=ProductRead, max_tokens=4000, model=model
    )

    kinds = [""] * len(photo_paths)
    shows = [False] * len(photo_paths)
    for photo in read.photos:
        if 1 <= photo.index <= len(kinds):
            kinds[photo.index - 1] = photo.kind
            shows[photo.index - 1] = bool(photo.product_visible)

    # 1차 판독도 "상품이 보인다" 고 한 사진은 그 판단을 살려 준다.
    for i, known in enumerate(known_shows or []):
        if i < len(shows) and known:
            shows[i] = True

    # 1차 판독에서 "가격표"로 본 사진은 카드 배경으로 쓰지 않는다.
    # 사진 한 장만 놓고 본 1차 판독이 더 보수적이라, 가격표가 카드에 실리는 사고를 막아준다.
    # 다만 **그렇게 해서 상품 사진이 하나도 안 남는다면 적용하지 않는다** —
    # 1차 판독이 틀렸을 때 멀쩡한 상품을 통째로 못 만들게 되기 때문이다.
    forced = list(kinds)
    for i, known in enumerate(known_kinds or []):
        if i < len(forced) and known == "price_tag":
            forced[i] = "price_tag"
    if any(k in ("product", "both") for k in forced):
        kinds = forced

    product = Product(
        product_name=read.product_name,
        category=read.category,
        tag_text=read.tag_text or "",
        condition_note=read.condition_note or "",
        original_price=read.original_price,
        sale_price=read.sale_price,
        discount_pct=read.discount_pct,
        price_source=read.price_source or "",
        best_photo_index=read.best_photo_index or 0,
        photo_kinds=kinds,
        photo_shows_product=shows,
        review_reason=read.review_reason or "",
        photo_paths=[str(p) for p in photo_paths],
        source_file_ids=list(source_file_ids or []),
        group_index=group_index,
        source_name=source_name,
        source_kind=source_kind,
        eyebrow=eyebrow,
    )
    return sanity_check(product)


def _unevidenced(text: str, tag_text: str) -> bool:
    """가격표에 근거가 없는 상태 표현이 이 문장에 들어 있는가."""
    return any(
        pattern.search(text) and not pattern.search(tag_text) for pattern in CLAIM_PATTERNS
    )


def strip_unevidenced_claims(text: str, tag_text: str) -> str:
    """가격표에 근거가 없는 상태 표현이 든 문장을 통째로 걷어낸다.

    단어만 오려내면 "박스만 개봉한 품" 같은 조각이 남는다. 문장 단위로 버리는 편이 안전하다.
    한 문장짜리 문구라면 통째로 비게 되는데, 그게 의도한 동작이다 —
    근거 없는 상태 표현을 붙이느니 아무 말도 안 하는 게 낫다.
    """
    if not text:
        return ""
    tag = tag_text or ""
    kept = [
        part.strip()
        for part in _SENTENCE_SPLIT.split(text)
        if part.strip() and not _unevidenced(part, tag)
    ]
    return " ".join(kept).strip(" ,·-–—")


def sanity_check(p: Product) -> Product:
    """모델이 실수했을 때 잘못된 값이 조용히 카드에 찍히는 것을 막는다.

    막는 것과 알려주기만 하는 것을 나눈다.
      · 막는다  — 카드가 틀리게 나가는 경우 (가격을 못 읽음, 상품 사진 없음,
                  상품과 가격표가 서로 다른 물건, 할인율이 말이 안 됨)
      · 알린다  — 이름 표기가 조금 애매한 정도. 카드는 만들고 리포트에 적는다.
    """
    reasons: list[str] = []
    cautions: list[str] = []
    if p.review_reason:
        (reasons if _blocks_publishing(p.review_reason) else cautions).append(p.review_reason)

    if p.sale_price is not None and p.sale_price <= 0:
        p.sale_price = None
    if p.original_price is not None and p.original_price <= 0:
        p.original_price = None

    if not p.has_product_photo:
        reasons.append("상품을 알아볼 수 있는 사진이 없습니다 (가격표만 찍힌 사진)")

    if p.sale_price is None:
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

    # 가격표에 근거 없는 상태 표현은 걷어낸다
    p.condition_note = strip_unevidenced_claims(p.condition_note, p.evidence_text)

    for attr in ("product_name", "condition_note", "spec_line", "description"):
        value = getattr(p, attr) or ""
        if "중고" in value:
            setattr(p, attr, value.replace("중고", "리퍼브"))

    p.needs_review = bool(reasons)
    p.review_reason = "; ".join(dict.fromkeys(r for r in reasons if r))
    p.cautions = "; ".join(dict.fromkeys(c for c in cautions if c))
    return p


_FIELDS = {f for f in Product.__dataclass_fields__}


def load_products(path: Path) -> list[Product]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [Product(**{k: v for k, v in item.items() if k in _FIELDS}) for item in data]


def save_products(products: list[Product], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps([p.to_dict() for p in products], ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return path



# ------------------------------------------------ 한 번에 다 보고 판단하기 (통판독)
#
# 은성님: "클로드 코워크에서 했던 거에 비해 너무 형편없어."
#
# 맞는 지적이었다. 코워크에서는 사진 스무 장을 **한꺼번에 펼쳐놓고** 사람처럼
# 봤다 — "이 가격표는 저 물건 거네, 이건 흐리니 옆 사진 쓰자". 자동화하면서
# 그걸 좁은 질문 네 개로 쪼갰다:
#   ① 사진마다 종류만 묻기 → ② 그 답으로 규칙 코드가 짝짓기 →
#   ③ 묶음별로 이름·가격 묻기 → ④ 사진 한 장씩 다시 검문
# 매 단계는 앞 단계가 버린 것을 되살릴 수 없다. ②에서 짝이 어긋나면
# ③④가 아무리 잘해도 못 고친다(08-25 일산: 23장 → 묶음 22개).
#
# 그래서 코워크가 하던 대로 되돌린다. 한 매장의 그날 사진을 **전부 한 번에**
# 보여주고, 묶기·이름·가격·카드에 쓸 사진까지 한 번에 결정하게 한다.
# 실패하면 예전 4단계 방식으로 물러난다 — 새 방식이 안 되는 날에도 카드는 나와야 한다.

PLAN_SYSTEM = """당신은 리퍼브 매장의 콘텐츠 담당자입니다.
오늘 매장에서 찍은 사진을 **전부 한 번에** 받았습니다.
이 사진들을 상품별로 정리해서 카드뉴스에 쓸 정보를 만들어 주세요.

이 매장은 리퍼브(검수를 마친 새 상품) 전문점입니다. "중고"라는 단어는 절대 쓰지 않습니다.

## 사진이 찍힌 방식
직원이 상품 하나를 처리할 때 보통 이렇게 찍습니다.
  · 상품 사진 1장 + 그 상품의 가격표 사진 1장 (순서는 그때그때 다릅니다)
  · 또는 상품과 가격표가 한 장에 같이 나온 사진 1장
  · 가끔 각도를 바꿔 2~3장 더 찍습니다
사진은 **찍은 순서대로** 드립니다. 그래서 대개 이웃한 사진이 같은 상품입니다.
하지만 순서만 믿지 마세요. **가격표에 적힌 상품명과 사진 속 물건이 같은지**
직접 보고 판단하세요. 실제로 가격표를 찍은 뒤 다음 상품을 먼저 찍는 일이 잦습니다.

## 해야 할 일
1. 사진 한 장 한 장이 무엇인지 적습니다 (kind, shows_product).
2. 같은 상품의 사진끼리 묶습니다.
3. 묶음마다 가격표를 읽어 상품명·가격을 적습니다.
4. 묶음마다 **카드뉴스 배경으로 쓸 사진 한 장**을 고릅니다.

## 절대 규칙
1. 가격은 사진 속 가격표·POP 에 **실제로 적혀 있는 숫자**만 씁니다.
   추정하거나 검색하거나 상식으로 지어내지 않습니다.
   정가와 할인가가 둘 다 보이면 둘 다, 하나만 보이면 그 하나만 적고 나머지는 null.
   가격을 하나도 못 읽으면 review_reason 에 적습니다.
2. **상품 상태를 지어내지 않습니다.** "미사용", "전시상품", "박스만 개봉",
   "새것 같은" 같은 표현은 **가격표에 그렇게 적혀 있을 때만** condition_note 에
   그대로 옮겨 적습니다. 없으면 반드시 빈 문자열입니다.
   박스가 보인다거나 깨끗해 보인다는 이유로 상태를 단정하지 않습니다.
3. 상품명은 가격표 표기를 우선합니다. 가격표에 없으면 사진 속 브랜드·로고·모델명으로.
4. tag_text 에는 가격표에서 읽은 글자를 보이는 대로 옮겨 적습니다 (나중에 근거 확인용).

## 카드에 쓸 사진 고르기 (가장 중요합니다)
카드뉴스 배경은 손님이 보고 "아, 저 물건이구나" 하고 알아볼 수 있어야 합니다.
가격표 사진이 배경으로 나가면 광고가 아니라 사고입니다. 실제로 그런 사고가 났습니다.

고르는 법: 사진에서 **가격표를 손으로 가린다고 상상**하고, 남는 것을 봅니다.
그 남은 것을 보고 물건 이름을 댈 수 있으면 그 사진을 쓸 수 있습니다.

기준은 "물건 전체가 다 나왔는가"가 **아니라** "무슨 물건인지 알 수 있는가"입니다.
매장 사진은 가까이서 찍혀 물건이 화면 밖으로 잘리는 일이 흔합니다. 잘렸어도
"노란 아기욕조", "검은 카시트", "접이식 쇼핑카트"처럼 이름을 댈 수 있으면 씁니다.

쓸 수 없는 사진은 이런 것뿐입니다:
  · 가격표가 사진의 주인공이다 (가격표를 찍은 사진이다)
  · 가격표를 가리면 흰 상자면·벽·바닥·천처럼 정체를 알 수 없는 면만 남는다
후보가 여러 장이면 상품이 가장 잘 보이는 사진을 고릅니다.
쓸 수 있는 사진이 하나도 없으면 card_photo_index 를 0 으로 두세요.

## 사진을 빠뜨리지 마세요
받은 사진은 **한 장도 빠짐없이** photos 에 나와야 합니다.
매장 전경처럼 상품과 무관한 사진은 kind="other" 로 두고 어느 묶음에도 넣지 않습니다.
그 외의 사진은 반드시 어느 한 상품의 photo_indexes 에 들어가야 합니다.
상품 하나가 통째로 빠지면 그날 팔 물건 하나를 못 알리는 것입니다."""


class PlannedPhoto(BaseModel):
    """사진 한 장에 대한 판단."""

    index: int = Field(description="사진 번호 (1부터)")
    kind: str = Field(description="product / price_tag / both / other 중 하나")
    shows_product: bool = Field(
        default=False,
        description="가격표를 가려도 무슨 물건인지 알 수 있으면 true",
    )
    note: str = Field(default="", description="사진에 보이는 것을 짧게. 예: '노란 아기욕조 근접'")

    @field_validator("kind", mode="before")
    @classmethod
    def _kind(cls, value):
        text = str(value or "").strip().lower()
        if text in ("product", "price_tag", "both", "other"):
            return text
        if "tag" in text or "price" in text:
            return "price_tag"
        if "both" in text:
            return "both"
        if "other" in text:
            return "other"
        return "product"


class PlannedProduct(BaseModel):
    """상품 하나 — 어떤 사진들이 이 상품이고, 가격표에 뭐라고 적혀 있는지."""

    photo_indexes: list[int] = Field(description="이 상품의 사진 번호들 (1부터)")
    card_photo_index: int = Field(
        description="카드뉴스 배경으로 쓸 사진 번호. 쓸 만한 사진이 없으면 0."
    )
    product_name: str = Field(description="가격표에 적힌 상품명 그대로. 없으면 브랜드/모델명.")
    tag_text: str = Field(default="", description="가격표에서 읽은 글자 그대로")
    condition_note: str = Field(
        default="", description="가격표에 적힌 상태 표기만 그대로. 없으면 빈 문자열."
    )
    category: str = Field(
        default="기타", description="가전 / 가구 / 주방 / 홈리빙 / 육아 / 반려 / 기타"
    )
    original_price: int | None = Field(default=None, description="가격표의 할인 전 가격. 없으면 null.")
    sale_price: int | None = Field(default=None, description="가격표의 판매가. 없으면 null.")
    discount_pct: int | None = Field(default=None, description="가격표에 적힌 할인율. 없으면 null.")
    price_source: str = Field(default="", description="가격을 어느 사진에서 읽었는지")
    review_reason: str = Field(default="", description="사람이 봐야 할 이유. 없으면 빈 문자열.")

    @field_validator("photo_indexes", mode="before")
    @classmethod
    def _indexes(cls, value):
        if value is None:
            return []
        if isinstance(value, int):
            return [value]
        out = []
        for item in value:
            try:
                out.append(int(item))
            except (TypeError, ValueError):
                continue
        return out


class StorePlan(BaseModel):
    photos: list[PlannedPhoto] = Field(description="받은 사진 전부. 빠뜨리지 말 것.")
    products: list[PlannedProduct] = Field(description="정리한 상품들. 찍은 순서대로.")


def plan_store_photos(
    client: LLMClient,
    photo_paths: list[Path],
    *,
    model: str,
    source_kind: str = "refurb",
    store_name: str = "",
) -> StorePlan:
    """사진 전부를 한 번에 보여주고 상품별로 정리하게 한다."""
    parts: list[dict] = []
    for i, path in enumerate(photo_paths, start=1):
        parts.append(text_part(f"[{i}번 사진]"))
        parts.append(image_part(path))
    note = SOURCE_NOTES.get(source_kind, SOURCE_NOTES["refurb"])
    where = f"{store_name} " if store_name else ""
    parts.append(
        text_part(
            f"{where}오늘 올라온 사진 {len(photo_paths)}장입니다 (찍은 순서).\n"
            f"{note}\n"
            "사진을 전부 훑어본 뒤 상품별로 정리해 주세요. "
            "한 장도 빠뜨리지 말고, 카드에 쓸 사진은 가격표를 가려도 "
            "무슨 물건인지 알 수 있는 사진으로 골라 주세요."
        )
    )
    return client.structured(
        system=PLAN_SYSTEM,
        parts=parts,
        schema=StorePlan,
        max_tokens=16000,
        model=model,
    )


def products_from_plan(
    plan: StorePlan,
    photo_paths: list[Path],
    file_ids: list[str],
    *,
    source_name: str = "상품",
    source_kind: str = "refurb",
    eyebrow: str = "오늘의 리본 특가",
    start_index: int = 1,
) -> list[Product]:
    """통판독 결과를 파이프라인이 쓰는 Product 로 옮긴다."""
    n = len(photo_paths)
    kinds = {p.index: p.kind for p in plan.photos if 1 <= p.index <= n}
    shows = {p.index: bool(p.shows_product) for p in plan.photos if 1 <= p.index <= n}

    products: list[Product] = []
    used: set[int] = set()
    for offset, planned in enumerate(plan.products):
        indexes = [i for i in planned.photo_indexes if 1 <= i <= n and i not in used]
        if not indexes:
            continue
        used.update(indexes)
        local_paths = [photo_paths[i - 1] for i in indexes]
        local_kinds = [kinds.get(i, "product") for i in indexes]
        local_shows = [shows.get(i, False) for i in indexes]

        card = 0
        if planned.card_photo_index in indexes:
            card = indexes.index(planned.card_photo_index) + 1
            local_shows[card - 1] = True  # 카드로 고른 사진은 상품이 보인다는 뜻이다

        product = Product(
            product_name=planned.product_name,
            category=planned.category or "기타",
            tag_text=planned.tag_text or "",
            condition_note=planned.condition_note or "",
            original_price=planned.original_price,
            sale_price=planned.sale_price,
            discount_pct=planned.discount_pct,
            price_source=planned.price_source or "",
            best_photo_index=card,
            photo_kinds=local_kinds,
            photo_shows_product=local_shows,
            review_reason=planned.review_reason or "",
            photo_paths=[str(p) for p in local_paths],
            source_file_ids=[file_ids[i - 1] for i in indexes] if file_ids else [],
            group_index=start_index + offset,
            source_name=source_name,
            source_kind=source_kind,
            eyebrow=eyebrow,
        )
        if card == 0:
            product.review_reason = "; ".join(
                filter(None, [product.review_reason, "상품을 알아볼 수 있는 사진이 없습니다"])
            )
        products.append(sanity_check(product))

    missed = [
        i
        for i in range(1, n + 1)
        if i not in used and kinds.get(i, "product") != "other"
    ]
    if missed:
        log.warning("통판독이 사진 %s번을 어느 상품에도 넣지 않았습니다", ", ".join(map(str, missed)))
    return products

# ------------------------------------------------ 카드에 쓸 사진 검문 (마지막 관문)

SCREEN_SYSTEM = """당신은 리본마켓 카드뉴스의 마지막 검수자입니다.
사진 한 장을 보고, **이 사진을 카드뉴스 배경으로 써도 되는지**만 판정합니다.

카드뉴스 배경은 손님이 보고 "아, 저 물건이구나" 하고 알아볼 수 있어야 합니다.
가격표 사진이 배경으로 나가면 광고가 아니라 사고입니다.

이렇게 판단하세요.
1. 사진에서 가격표(종이·스티커·POP)를 손으로 가린다고 상상합니다.
2. 그러고도 남는 것이 무엇인지 봅니다.
3. **그 남은 것을 보고 물건 이름을 댈 수 있으면 ok=true 입니다.**

판정 기준은 "물건 전체가 다 나왔는가"가 **아니라** "무슨 물건인지 알 수 있는가"입니다.
매장 사진은 가까이서 찍혀 물건이 화면 밖으로 잘리는 일이 흔합니다.
잘렸어도 "노란 아기욕조", "검은 카시트", "접이식 쇼핑카트"처럼 이름을 댈 수 있으면
통과입니다. 색·재질·형태가 보이면 손님은 알아봅니다.

ok=false 로 두어야 하는 경우는 이것뿐입니다:
- 가격표가 사진의 주인공이다 (가격표를 찍은 사진이다)
- 가격표를 가리면 흰 상자면·벽·바닥·천처럼 **정체를 알 수 없는 면**만 남는다
- 남은 것을 보고도 무슨 물건인지 이름을 댈 수 없다

이름을 댈 수 있으면 통과시키세요. 알아볼 수 있는 사진을 떨어뜨리면
멀쩡한 상품이 카드뉴스에서 통째로 빠집니다."""


class CardPhotoScreen(BaseModel):
    visible_besides_tag: str = Field(
        description="가격표를 가렸을 때 사진에 남는 것을 그대로 묘사. 예: '검은 사무용 의자 전체', '흰 상자면뿐'"
    )
    tag_dominates: bool = Field(
        description=(
            "가격표가 사진의 주인공이면 true. 상품 옆에 가격표가 같이 찍힌 정도는 false — "
            "상품보다 가격표가 크게, 화면 한가운데를 차지할 때만 true."
        )
    )
    ok: bool = Field(
        description=(
            "가격표를 가린 뒤 남는 것으로 물건 이름을 댈 수 있으면 true. "
            "잘리거나 가까이 찍힌 것은 이유가 되지 않는다."
        )
    )


def screen_card_photo(
    client: LLMClient, path: Path, *, product_name: str, model: str
) -> CardPhotoScreen:
    """카드 배경 후보 사진 한 장을 놓고 다시 판정한다.

    분류(classify)와 판독(extract)은 여러 장을 한꺼번에 보면서 상품명·가격까지
    같이 처리하느라 '이 사진에 물건이 보이는가'를 자주 놓친다. 실제로 흰 상자에
    가격표만 붙은 사진이 '상품 사진'으로 분류돼 카드에 실렸다.
    그래서 카드에 쓰기 직전에 **그 사진 한 장만** 놓고 이것만 묻는다.
    """
    parts = [
        image_part(path),
        text_part(
            f"이 사진을 '{product_name}' 카드뉴스의 배경으로 써도 될까요?\n"
            "가격표를 가렸을 때 무엇이 남는지 먼저 적고, 그 다음에 판정하세요.\n"
            "물건이 잘려 보여도 무슨 물건인지 알 수 있으면 통과입니다."
        ),
    ]
    return client.structured(
        system=SCREEN_SYSTEM, parts=parts, schema=CardPhotoScreen, max_tokens=1000, model=model
    )


def pick_card_photo(client: LLMClient, product: "Product", *, model: str) -> None:
    """카드에 쓸 사진을 검문해서 정하고, 쓸 사진이 없으면 발행을 막는다.

    후보를 앞에서부터 검문하다가 통과하는 첫 사진을 쓴다.
    전부 떨어지면 카드를 만들지 않는다 — 가격표 사진을 내보내느니 안 만든다.
    """
    if not product.publishable:
        return
    candidates = product._card_candidates()
    rejected: list[str] = []
    for index in candidates:
        path = Path(product.photo_paths[index - 1])
        try:
            verdict = screen_card_photo(client, path, product_name=product.product_name, model=model)
        except Exception as exc:  # 검문에 실패하면 원래 판단을 믿는다 (발행을 막지는 않는다)
            log.warning("[%s] 사진 검문 실패, 그대로 진행합니다: %s", product.product_name, exc)
            product.best_photo_index = index
            return
        if verdict.ok and not verdict.tag_dominates:
            product.best_photo_index = index
            return
        rejected.append(f"{path.name}({verdict.visible_besides_tag})")
        product.photo_shows_product[index - 1] = False

    reason = "카드에 쓸 상품 사진이 없습니다 — 가격표만 크게 찍혔습니다"
    if rejected:
        reason += f" · 검토한 사진: {', '.join(rejected)}"
    log.info("[%s] %s", product.product_name, reason)
    product.review_reason = "; ".join(filter(None, [product.review_reason, reason]))
    product.needs_review = True
