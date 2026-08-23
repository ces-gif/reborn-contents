"""한글 줄바꿈 / 자동 크기 조절 유틸.

한글은 단어 사이 공백이 적어서 공백 기준 줄바꿈만으로는 긴 상품명이 안 접힌다.
그래서 공백 우선 → 안 되면 글자 단위로 접는다.
"""

from __future__ import annotations

from PIL import ImageDraw, ImageFont

_MEASURE = ImageDraw.Draw(__import__("PIL.Image", fromlist=["Image"]).new("RGB", (1, 1)))


def text_width(text: str, fnt: ImageFont.FreeTypeFont) -> int:
    if not text:
        return 0
    return int(_MEASURE.textlength(text, font=fnt))


def wrap(text: str, fnt: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    """공백 우선, 넘치면 글자 단위로 접는다."""
    words = text.split()
    lines: list[str] = []
    current = ""

    def flush() -> None:
        nonlocal current
        if current:
            lines.append(current)
            current = ""

    for word in words:
        candidate = f"{current} {word}".strip()
        if text_width(candidate, fnt) <= max_width:
            current = candidate
            continue
        flush()
        if text_width(word, fnt) <= max_width:
            current = word
            continue
        # 한 단어가 통째로 넘치면 글자 단위로 쪼갠다
        chunk = ""
        for ch in word:
            if text_width(chunk + ch, fnt) <= max_width:
                chunk += ch
            else:
                lines.append(chunk)
                chunk = ch
        current = chunk
    flush()
    return lines or [""]


def fit_lines(
    text: str,
    weight_font,
    max_width: int,
    max_lines: int,
    sizes: list[int],
) -> tuple[list[str], ImageFont.FreeTypeFont]:
    """max_lines 안에 들어가는 가장 큰 글자 크기를 고른다.

    weight_font: size -> FreeTypeFont 를 돌려주는 콜러블.
    """
    lines: list[str] = []
    fnt = weight_font(sizes[-1])
    for size in sizes:
        fnt = weight_font(size)
        lines = wrap(text, fnt, max_width)
        if len(lines) <= max_lines:
            return lines, fnt
    # 가장 작은 크기로도 안 들어가면 잘라내고 말줄임
    lines = lines[:max_lines]
    if lines:
        last = lines[-1]
        while last and text_width(last + "…", fnt) > max_width:
            last = last[:-1]
        lines[-1] = last + "…"
    return lines, fnt


def draw_centered(draw: ImageDraw.ImageDraw, lines, fnt, cx, top, line_gap, fill) -> int:
    y = top
    ascent, descent = fnt.getmetrics()
    line_height = ascent + descent
    for line in lines:
        w = text_width(line, fnt)
        draw.text((cx - w / 2, y), line, font=fnt, fill=fill)
        y += line_height + line_gap
    return y - line_gap if lines else top
