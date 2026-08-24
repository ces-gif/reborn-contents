"""BEST5 블로그 글 생성 (네이버 붙여넣기용 HTML 포함).

말투/구조는 reborn-pt-lifestyle-blog-post 스킬 규칙을 그대로 따른다:
- 공감형 인트로 → 문제 짚기 → "그래서 오늘은 ~" 전환
- 번호 매김 소제목, 절 단위 2~3줄 줄바꿈, 벽 텍스트 금지
- 비교표 넣고 표 아래에서 말로 다시 풀기
- "저는 ~하곤 해요" 1인칭 코멘트
- 마무리는 요약 + 따뜻한 응원
- "중고" 표현 절대 금지

HTML 은 모델이 쓰지 않고 우리가 조립한다. 그래야 네이버 규칙
(글자크기 19, 소제목 볼드, 번호는 '1)' 형식)이 매번 정확히 지켜진다.
"""

from __future__ import annotations

import html
import json
import logging
from dataclasses import dataclass
from datetime import date

from pydantic import BaseModel, Field, field_validator

from .llm import LLMClient, text_part
from .vision import Product

log = logging.getLogger(__name__)

class PostItem(BaseModel):
    heading: str = Field(description="번호 없는 소제목 텍스트. 번호는 우리가 붙인다.")
    body: list[list[str]] = Field(
        description="설명 문단들. 각 문단은 짧은 줄의 배열(한 줄 25자 내외)."
    )
    personal_note: str = Field(description="'저는 ~하곤 해요' 식 1인칭 코멘트 한 줄.")


def _flatten_lines(value):
    """줄 목록에 문단이 한 겹 더 씌워져 와도 받아준다.

    PostDraft 의 다른 칸(intro/body/closing)은 '문단들의 배열'이라 두 겹인데,
    table_wrapup 만 한 겹이다. 모델이 이걸 헷갈려 두 겹으로 보내면 예전에는
    글쓰기가 통째로 실패했다 — 카드뉴스를 다 만들어 놓고 발행이 날아갔다.
    모양이 조금 달라도 뜻은 분명하니 펴서 받는다.
    """
    if not isinstance(value, list):
        return value
    lines: list = []
    for item in value:
        if isinstance(item, list):
            lines.extend(str(x) for x in item)
        else:
            lines.append(item)
    return lines


class PostDraft(BaseModel):
    category_tag: str = Field(description="글 맨 위 카테고리 태그. 예: '오늘의 리본 특가'")
    title: str = Field(description="핵심 키워드가 들어간 제목.")
    intro: list[list[str]] = Field(description="공감형 인트로 문단들. 각 문단은 짧은 줄의 배열.")
    transition: list[str] = Field(description="'그래서 오늘은 ~' 전환 문단. 짧은 줄의 배열.")
    items: list[PostItem] = Field(
        description="BEST 상품별 섹션. 입력으로 준 순서 그대로, 개수도 그대로."
    )
    table_intro: str = Field(description="비교표 앞에 붙일 한 줄.")
    table_wrapup: list[str] = Field(description="표 아래에서 표 내용을 말로 다시 풀어주는 문단.")

    _flat = field_validator("table_wrapup", "tags", mode="before")(_flatten_lines)
    closing: list[list[str]] = Field(description="요약 + 따뜻한 응원 마무리 문단들.")
    tags: list[str] = Field(description="네이버 태그 8~12개. # 없이 단어만.")


SYSTEM = """당신은 리본마켓 평택점 점장 최은성입니다. 네이버 블로그에 '생활정보형' 포스트를 씁니다.

말투와 구조 (반드시 지킬 것):
- 존댓말, 이웃에게 말하듯 따뜻하고 담백하게. 과장 광고 금지.
- 계절/상황 공감으로 시작해서, 독자가 겪는 불편을 짚고, "그래서 오늘은 ~" 으로 전환합니다.
- 문단은 절 단위로 2~3줄씩 끊어 씁니다. 벽 텍스트 금지.
- 소제목은 단정형과 질문형을 섞습니다. 질문형 소제목 다음 문단은 "결론부터 말씀드리자면"으로 시작합니다.
- 상품 설명 중간에 "저는 ~하곤 해요" 같은 1인칭 경험 코멘트를 한 줄 넣습니다.
- 마무리는 오늘 내용 요약 + 따뜻한 응원 한 줄.

절대 규칙:
- "중고"라는 단어를 절대 쓰지 않습니다. 리본마켓은 리퍼브(검수를 마친 새 상품) 매장입니다.
- 주어진 상품 정보에 없는 스펙, 성능, 연식, 보증 조건을 지어내지 않습니다.
- 가격은 주어진 숫자를 그대로 씁니다. 바꾸거나 반올림하지 않습니다.
- **상품 상태를 지어내지 않습니다.** "미사용", "전시상품", "박스만 개봉", "새것 같은" 같은 표현은
  '가격표에적힌상태' 에 실제로 적혀 있을 때만 쓸 수 있습니다. "(가격표에 상태 표기 없음)" 이면
  상태에 대해 아무 말도 하지 않고, 제품 자체와 가격 이야기만 합니다.
- 제품 설명은 '제품설명(웹검색확인)' 과 '특징(웹검색확인)' 에 있는 내용만 씁니다.
  "(검색으로 확인 못 함)" 이면 제품 스펙을 언급하지 않고 상품명과 가격만으로 씁니다.
- 통계나 수치를 지어내지 않습니다.
- 마크다운 기호(#, **, - 등)를 본문에 쓰지 않습니다. 순수 문장으로만 씁니다.
- items 배열은 입력으로 받은 상품 순서와 개수를 정확히 그대로 지킵니다."""


@dataclass
class BlogPost:
    category_tag: str
    title: str
    intro: list[list[str]]
    transition: list[str]
    items: list[dict]
    table_intro: str
    table_wrapup: list[str]
    closing: list[list[str]]
    tags: list[str]
    products: list[Product]

    # ------------------------------------------------------------- markdown

    def to_markdown(self, store_name: str, footer_note: str) -> str:
        out: list[str] = [f"[{self.category_tag}]", f"# {self.title}", ""]
        for para in self.intro:
            out += ["  \n".join(para), ""]
        out += ["  \n".join(self.transition), ""]

        for i, (item, product) in enumerate(zip(self.items, self.products), start=1):
            out.append(f"{i}) {item['heading']}")
            out.append("")
            for para in item["body"]:
                out += ["  \n".join(para), ""]
            out.append(_price_line(product))
            out.append("")
            out.append(item["personal_note"])
            out.append("")

        out += [self.table_intro, ""]
        out += _markdown_table(self.products) + [""]
        out += ["  \n".join(self.table_wrapup), ""]
        for para in self.closing:
            out += ["  \n".join(para), ""]
        out += [f"📍 {store_name}", footer_note, ""]
        out.append(" ".join(f"#{t}" for t in self.tags))
        return "\n".join(out).strip() + "\n"

    # ----------------------------------------------------------------- html

    def to_naver_html(self, store_name: str, footer_note: str) -> str:
        """브라우저로 열고 전체 선택 → 복사 → 네이버 에디터에 그대로 붙여넣기."""
        e = html.escape
        parts: list[str] = [
            '<div style="font-size:19px; line-height:1.9; color:#222; '
            'font-family:\'Apple SD Gothic Neo\',\'Malgun Gothic\',sans-serif;">',
            f'<p style="font-size:15px; color:#888; margin:0 0 6px 0;">{e(self.category_tag)}</p>',
            f'<p style="font-size:24px; font-weight:bold; margin:0 0 24px 0;">{e(self.title)}</p>',
        ]
        for para in self.intro:
            parts.append(_p(para))
        parts.append(_p(self.transition))

        for i, (item, product) in enumerate(zip(self.items, self.products), start=1):
            # 번호는 반드시 '1)' 형식 — '1.' 은 네이버 에디터가 자동 목록으로 바꿔 번호가 깨진다.
            parts.append(
                f'<p style="margin:34px 0 10px 0;"><b>{i}) {e(item["heading"])}</b></p>'
            )
            for para in item["body"]:
                parts.append(_p(para))
            parts.append(
                '<p style="margin:14px 0;"><b>' + e(_price_line(product)) + "</b></p>"
            )
            parts.append(_p([item["personal_note"]]))

        parts.append(_p([self.table_intro]))
        parts.append(_html_table(self.products))
        parts.append(_p(self.table_wrapup))
        for para in self.closing:
            parts.append(_p(para))

        parts.append(
            f'<p style="margin:28px 0 6px 0;"><b>📍 {e(store_name)}</b></p>'
            f'<p style="margin:0 0 20px 0; font-size:17px; color:#666;">{e(footer_note)}</p>'
        )
        parts.append(
            '<p style="font-size:16px; color:#5b7cff;">'
            + " ".join(f"#{e(t)}" for t in self.tags)
            + "</p>"
        )
        parts.append("</div>")
        return (
            "<!doctype html>\n<html lang=\"ko\">\n<head>\n<meta charset=\"utf-8\">\n"
            f"<title>{e(self.title)}</title>\n</head>\n<body>\n" + "\n".join(parts) + "\n</body>\n</html>\n"
        )


def _p(lines: list[str]) -> str:
    body = "<br>".join(html.escape(line) for line in lines if line)
    return f'<p style="margin:0 0 20px 0;">{body}</p>'


def _price_line(p: Product) -> str:
    if p.original_price and p.computed_pct:
        return (
            f"온라인 판매가 {p.original_price:,}원 → 리본마켓 초특가 "
            f"{p.sale_price:,}원 ({p.computed_pct}% 할인)"
        )
    return f"리본마켓 초특가 {p.sale_price:,}원"


def _markdown_table(products: list[Product]) -> list[str]:
    rows = ["| 상품 | 온라인 판매가 | 리본마켓 초특가 | 할인율 |", "| --- | --- | --- | --- |"]
    for p in products:
        orig = f"{p.original_price:,}원" if p.original_price else "-"
        pct = f"{p.computed_pct}%" if p.computed_pct else "-"
        rows.append(f"| {p.product_name} | {orig} | {p.sale_price:,}원 | {pct} |")
    return rows


def _html_table(products: list[Product]) -> str:
    e = html.escape
    head = (
        '<table style="border-collapse:collapse; width:100%; font-size:17px; margin:10px 0 24px 0;">'
        "<tr>"
        + "".join(
            f'<th style="border:1px solid #ddd; padding:10px; background:#f7f7f9;"><b>{h}</b></th>'
            for h in ("상품", "온라인 판매가", "리본마켓 초특가", "할인율")
        )
        + "</tr>"
    )
    body = ""
    for p in products:
        orig = f"{p.original_price:,}원" if p.original_price else "-"
        pct = f"{p.computed_pct}%" if p.computed_pct else "-"
        body += (
            "<tr>"
            f'<td style="border:1px solid #ddd; padding:10px;">{e(p.product_name)}</td>'
            f'<td style="border:1px solid #ddd; padding:10px; color:#888;">{orig}</td>'
            f'<td style="border:1px solid #ddd; padding:10px;"><b>{p.sale_price:,}원</b></td>'
            f'<td style="border:1px solid #ddd; padding:10px; color:#FD6F23;"><b>{pct}</b></td>'
            "</tr>"
        )
    return head + body + "</table>"


def write_post(
    client: LLMClient,
    picks: list[tuple[Product, str]],
    *,
    model: str,
    store_name: str,
    day: date,
    footer_note: str,
) -> BlogPost:
    products = [p for p, _ in picks]
    brief = [
        {
            "순위": i,
            "상품명": p.product_name,
            "카테고리": p.category,
            "한줄소개": p.card_line,
            "가격표에적힌상태": p.condition_note or "(가격표에 상태 표기 없음)",
            "제품설명(웹검색확인)": p.description or "(검색으로 확인 못 함)",
            "특징(웹검색확인)": p.key_points,
            "온라인판매가": p.original_price,
            "리본마켓초특가": p.sale_price,
            "할인율": p.computed_pct,
            "선정이유": why,
        }
        for i, (p, why) in enumerate(picks, start=1)
    ]

    draft: PostDraft = client.structured(
        system=SYSTEM,
        parts=[
            text_part(
                f"오늘은 {day.strftime('%Y년 %m월 %d일')}, {store_name} 에 아래 상품들이 들어왔습니다.\n"
                f"이 {len(picks)}개를 순위 그대로 소개하는 블로그 글을 써주세요.\n"
                "독자가 복사해서 바로 올릴 수 있을 만큼 완성도 있게, 각 상품마다 2~3문단씩 채워주세요.\n\n"
                f"{json.dumps(brief, ensure_ascii=False, indent=2)}"
            )
        ],
        schema=PostDraft,
        max_tokens=16000,
        model=model,
    )

    items = [item.model_dump() for item in draft.items]
    if len(items) != len(products):
        log.warning("모델이 상품 %d개 중 %d개만 썼습니다. 개수를 맞춥니다.", len(products), len(items))
        n = min(len(items), len(products))
        items, products = items[:n], products[:n]

    return BlogPost(
        category_tag=draft.category_tag,
        title=draft.title,
        intro=draft.intro,
        transition=draft.transition,
        items=items,
        table_intro=draft.table_intro,
        table_wrapup=draft.table_wrapup,
        closing=draft.closing,
        tags=draft.tags,
        products=products,
    )
