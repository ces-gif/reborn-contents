"""인스타그램 스토리(1080x1920) 카드뉴스 렌더러.

기존 카톡 가격비교 카드의 톤앤매너를 그대로 스토리 비율로 옮겼다.
- 시그니처 오렌지(#FD6F23) 통짜 가격 바, 대각선 절단 없음
- 할인율은 회청색(#72788E) 알약 뱃지에 오렌지 글씨
- 로고는 반드시 실제 로고 PNG (텍스트로 그리지 않는다)
- 상하좌우 여백 없이 꽉 차게 (오렌지 상단 바 / 오렌지 가격 바 / 어두운 하단 바가 화면 끝까지)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

from . import branding as B
from .textkit import draw_centered, fit_lines, text_width, wrap

log = logging.getLogger(__name__)

W, H = 1080, 1920
MARGIN = 72
CONTENT_W = W - MARGIN * 2

# 세로 배치 (인스타 스토리 상/하단 UI 안전영역을 고려해 핵심 정보는 180~1790 사이)
Y_ACCENT_BAR = 14
Y_LOGO = 176
LOGO_H = 78
# 로고는 높이가 아니라 **넓이**로 맞춘다. 모양(가로로 긴 워드마크 / 정사각형
# 마스코트)이 달라도 눈에 보이는 크기가 비슷해야 한다.
LOGO_AREA = 312 * LOGO_H
LOGO_MAX_W = 360
LOGO_MAX_H = 170
Y_NAME_BOTTOM = 592  # 상품명 블록의 아랫변(1줄이든 2줄이든 소개 문구 위치가 흔들리지 않게)
Y_DESC = 614
Y_PHOTO = 700
PHOTO_H = 720
Y_PRICE = 1470
PRICE_H = 350
Y_FOOTER = 1820

# 헤더 덩어리(눈썹·상품명·소개)를 쌓을 때 쓰는 최소 여백.
DESC_PHOTO_GAP = 18  # 소개 문구 아랫변과 사진 윗변 사이
NAME_DESC_GAP = 22  # 상품명 아랫변과 소개 문구 윗변 사이
LOGO_CLEAR = 16  # 로고 아랫변과 눈썹 문구 사이
EYEBROW_GAP = 18  # 눈썹 문구와 상품명 사이

NAME_SIZES = [76, 68, 60, 54, 48, 42]
DESC_SIZES = [38, 34, 30]


@dataclass
class CardData:
    product_name: str
    one_liner: str
    sale_price: int
    condition_note: str = ""  # 가격표에 직원이 적어 둔 상태 (까짐·사용감·기스 등)
    original_price: int | None = None
    discount_pct: int | None = None
    number: int | None = None   # 손님이 이 번호로 예약한다
    eyebrow: str = "오늘의 리본 특가"
    date_label: str = ""
    footer: str = "리본마켓 평택점 · 매장에서 직접 보고 구매하세요"
    orig_label: str = "온라인 판매가"
    sale_label: str = "리본마켓 초특가"

    @property
    def computed_pct(self) -> int | None:
        if self.discount_pct is not None:
            return self.discount_pct
        if self.original_price and self.sale_price and self.original_price > self.sale_price:
            return round((self.original_price - self.sale_price) / self.original_price * 100)
        return None


def won(value: int) -> str:
    return f"{value:,}원"


def _cover(img: Image.Image, box_w: int, box_h: int) -> Image.Image:
    """비율 유지하며 박스를 꽉 채우도록 잘라낸다."""
    img = ImageOps.exif_transpose(img).convert("RGB")
    return ImageOps.fit(img, (box_w, box_h), Image.LANCZOS, centering=(0.5, 0.5))


def _rounded(img: Image.Image, radius: int) -> Image.Image:
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, img.size[0] - 1, img.size[1] - 1], radius, fill=255)
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    out.paste(img, (0, 0), mask)
    return out


def _pill(draw: ImageDraw.ImageDraw, cx: int, cy: int, text: str, *, bg, fg, size: int) -> None:
    fnt = B.font("extrabold", size)
    tw = text_width(text, fnt)
    ascent, descent = fnt.getmetrics()
    th = ascent + descent
    pad_x, pad_y = int(size * 0.55), int(size * 0.30)
    w, h = tw + pad_x * 2, th + pad_y * 2
    box = [cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2]
    draw.rounded_rectangle(box, radius=h // 2, fill=bg)
    draw.text((cx - tw / 2, cy - th / 2), text, font=fnt, fill=fg)


def _strikethrough(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, fnt, fill) -> None:
    draw.text((x, y), text, font=fnt, fill=fill)
    ascent, _ = fnt.getmetrics()
    tw = text_width(text, fnt)
    line_y = y + int(ascent * 0.60)
    draw.line([(x - 4, line_y), (x + tw + 4, line_y)], fill=fill, width=max(3, fnt.size // 18))


def _logo_image(logo, strict_logo: bool) -> Image.Image:
    """카드 좌상단에 얹을 로고 이미지."""
    if isinstance(logo, Image.Image):  # 글자 로고(신규 매장) 등 이미 만들어진 것
        img = logo
    else:
        img = B.trim_margins(Image.open(logo)) if logo else B.trim_margins(
            Image.open(B.logo_path(strict=strict_logo))
        )
    return B.fit_logo(img, area=LOGO_AREA, max_w=LOGO_MAX_W, max_h=LOGO_MAX_H)



# 사진 위 왼쪽 아래에 붙는 상태 고지. 가격표에 직원이 적어 둔 말(까짐·사용감·
# 기스 등)을 그대로 옮긴다. 리퍼브 매장에서 이건 숨길 것이 아니라 먼저 알릴
# 것이다. 다만 상품 **소개** 자리에 들어가면 "까짐" 한 단어짜리 카드가 되므로
# 자리를 따로 준다.
COND_PAD_X = 26
COND_PAD_Y = 14
COND_INSET = 24
COND_BG = (27, 30, 38, 235)


# 번호 뱃지 — 손님이 카드 번호를 보고 매장에 예약을 건다. 사진 위 왼쪽 모서리에
# 올려서 어떤 상품 얘기인지 한눈에 붙게 한다 (상태 뱃지는 사진 아래라 안 겹친다).
NUM_D = 132                  # 지름
NUM_INSET = 18               # 사진 모서리에서 띄우는 거리


def _draw_number(canvas: Image.Image, number: int | None) -> None:
    if not number:
        return
    x0 = MARGIN + NUM_INSET
    y0 = Y_PHOTO + NUM_INSET
    badge = Image.new("RGBA", (NUM_D, NUM_D), (0, 0, 0, 0))
    d = ImageDraw.Draw(badge)
    # 흰 테두리를 둘러 어두운 사진에서도 동그라미가 살아 있게 한다
    d.ellipse([0, 0, NUM_D - 1, NUM_D - 1], fill=(255, 255, 255, 235))
    d.ellipse([6, 6, NUM_D - 7, NUM_D - 7], fill=B.ORANGE + (255,))

    label = str(number)
    for size in (74, 66, 58, 50):       # 두 자리, 세 자리도 안 넘치게
        font = B.font("extrabold", size)
        if text_width(label, font) <= NUM_D - 34:
            break
    tw = text_width(label, font)
    ascent, descent = font.getmetrics()
    # 숫자는 baseline 기준이라 시각 중심이 살짝 위다. descent 를 빼서 눈으로 맞춘다.
    ty = (NUM_D - (ascent + descent)) // 2 - 2
    d.text(((NUM_D - tw) // 2, ty), label, font=font, fill=(255, 255, 255))
    canvas.paste(badge, (x0, y0), badge)


def _draw_condition(draw: ImageDraw.ImageDraw, note: str) -> None:
    note = (note or "").strip()
    if not note:
        return
    font = B.font("bold", 30)
    label = f"상태 · {note}"
    # 사진 폭을 넘지 않게 자른다
    while text_width(label, font) > CONTENT_W - COND_INSET * 2 - COND_PAD_X * 2 and len(label) > 6:
        note = note[:-1]
        label = f"상태 · {note}…"
    tw = text_width(label, font)
    ascent, descent = font.getmetrics()
    th = ascent + descent
    x0 = MARGIN + COND_INSET
    y1 = Y_PHOTO + PHOTO_H - COND_INSET
    y0 = y1 - th - COND_PAD_Y * 2
    draw.rounded_rectangle(
        [x0, y0, x0 + tw + COND_PAD_X * 2, y1], radius=(th + COND_PAD_Y * 2) // 2, fill=COND_BG
    )
    draw.text((x0 + COND_PAD_X, y0 + COND_PAD_Y), label, font=font, fill=(255, 255, 255))

def _block_height(lines: list[str], fnt, gap: int) -> int:
    ascent, descent = fnt.getmetrics()
    return len(lines) * (ascent + descent) + max(0, len(lines) - 1) * gap


def _fit_desc(text: str) -> tuple[list[str], object, int]:
    """한 줄 소개. 두 줄이 되면 사진을 밀어내지 않게 글자를 한 단계 줄인다."""
    if not text.strip():
        return [], B.font("medium", DESC_SIZES[0]), 0
    lines, fnt = fit_lines(text, lambda s: B.font("medium", s), CONTENT_W, 2, DESC_SIZES)
    return lines, fnt, _block_height(lines, fnt, 6)


def _fit_name(text: str, bottom: int, ceiling: int) -> tuple[list[str], object, int]:
    """상품명 블록. 아랫변을 bottom 에 맞추되 윗변이 ceiling 위로 올라가지 않게 한다.

    ceiling 은 로고와 눈썹 문구가 차지한 자리다. 긴 상품명이 두 줄이 되고 소개까지
    두 줄이면 헤더가 위로 밀려 로고를 덮는데, 그때는 상품명을 줄여서 막는다.
    """
    for size in NAME_SIZES:
        fnt = B.font("extrabold", size)
        lines = wrap(text, fnt, CONTENT_W)
        if len(lines) > 2:
            continue
        height = _block_height(lines, fnt, 8)
        if bottom - height >= ceiling:
            return lines, fnt, height
    # 가장 작은 크기로도 안 들어가면 두 줄로 자르고 말줄임표를 붙인다
    lines, fnt = fit_lines(
        text, lambda s: B.font("extrabold", s), CONTENT_W, 2, [NAME_SIZES[-1]]
    )
    return lines, fnt, _block_height(lines, fnt, 8)


@dataclass
class HeaderLayout:
    """눈썹 문구 · 상품명 · 한 줄 소개를 어디에 어떤 크기로 그릴지."""

    eyebrow_top: int
    name_lines: list[str]
    name_font: object
    name_top: int
    desc_lines: list[str]
    desc_font: object
    desc_top: int
    desc_bottom: int


def plan_header(product_name: str, one_liner: str, logo_height: int) -> HeaderLayout:
    """헤더를 **아래에서 위로** 쌓는다.

    예전에는 소개 문구를 고정 위치(Y_DESC)에 그려서, 설명이 두 줄이 되면 사진을
    파고들어 둘째 줄이 잘렸다 (09-26 스탠리 머그 카드가 그랬다). 이제는 소개 문구의
    아랫변을 사진 바로 위에 맞추고 상품명을 그 위에 올린다. 자리가 모자라면
    글자 크기를 한 단계씩 줄여서라도 겹치지 않게 한다.
    """
    desc_lines, desc_font, desc_h = _fit_desc(one_liner)
    desc_top = Y_PHOTO - DESC_PHOTO_GAP - desc_h if desc_lines else Y_DESC

    eyebrow_font = B.font("bold", 36)
    ea, ed = eyebrow_font.getmetrics()
    name_bottom = min(Y_NAME_BOTTOM, desc_top - NAME_DESC_GAP) if desc_lines else Y_NAME_BOTTOM
    ceiling = Y_LOGO + logo_height + LOGO_CLEAR + (ea + ed) + EYEBROW_GAP

    name_lines, name_font, name_h = _fit_name(product_name, name_bottom, ceiling)
    name_top = name_bottom - name_h

    return HeaderLayout(
        eyebrow_top=name_top - EYEBROW_GAP - (ea + ed),
        name_lines=name_lines,
        name_font=name_font,
        name_top=name_top,
        desc_lines=desc_lines,
        desc_font=desc_font,
        desc_top=desc_top,
        desc_bottom=desc_top + desc_h,
    )


def render_card(
    data: CardData,
    photo_path: Path,
    out_path: Path,
    *,
    strict_logo: bool = True,
    logo: Path | str | Image.Image | None = None,
) -> Path:
    """카드뉴스 한 장. logo 를 주면 그 로고를 쓴다 (매장마다 로고가 다르다)."""
    canvas = Image.new("RGB", (W, H), B.BG)
    draw = ImageDraw.Draw(canvas)

    # 1) 상단 오렌지 액센트 바 (꽉 참)
    draw.rectangle([0, 0, W, Y_ACCENT_BAR], fill=B.ORANGE)

    # 2) 로고. 로고가 없으면 여기서 예외 → 있는 매장의 로고를 멋대로 글자로 대체하지 않는다.
    mark = _logo_image(logo, strict_logo)
    canvas.paste(mark, (MARGIN, Y_LOGO), mark)
    logo_mid = Y_LOGO + mark.height // 2

    # 3) 날짜 뱃지 (우상단)
    if data.date_label:
        fnt = B.font("semibold", 34)
        tw = text_width(data.date_label, fnt)
        pad_x, pad_y = 26, 14
        ascent, descent = fnt.getmetrics()
        th = ascent + descent
        x1 = W - MARGIN
        x0 = x1 - (tw + pad_x * 2)
        cy = logo_mid
        y0, y1 = cy - (th + pad_y * 2) // 2, cy + (th + pad_y * 2) // 2
        draw.rounded_rectangle([x0, y0, x1, y1], radius=(y1 - y0) // 2, fill=(244, 245, 248))
        draw.text((x0 + pad_x, y0 + pad_y), data.date_label, font=fnt, fill=B.SLATE)

    # 4~6) 눈썹 문구 + 상품명 + 한 줄 소개 (아래에서 위로 쌓는다 — plan_header 참고)
    head = plan_header(data.product_name, data.one_liner, mark.height)
    eyebrow_font = B.font("bold", 36)
    draw_centered(draw, [data.eyebrow], eyebrow_font, W // 2, head.eyebrow_top, 0, B.ORANGE)
    draw_centered(draw, head.name_lines, head.name_font, W // 2, head.name_top, 8, B.INK)
    if head.desc_lines:
        draw_centered(draw, head.desc_lines, head.desc_font, W // 2, head.desc_top, 6, B.SLATE)

    # 7) 상품 사진 — 둥근 모서리, 좌우 여백 균일. 흰 상품이 흰 배경에 묻히지 않게 얇은 테두리.
    photo = _cover(Image.open(photo_path), CONTENT_W, PHOTO_H)
    rounded = _rounded(photo, 40)
    canvas.paste(rounded, (MARGIN, Y_PHOTO), rounded)
    draw.rounded_rectangle(
        [MARGIN, Y_PHOTO, MARGIN + CONTENT_W - 1, Y_PHOTO + PHOTO_H - 1],
        radius=40,
        outline=(231, 233, 238),
        width=2,
    )
    _draw_number(canvas, data.number)
    _draw_condition(draw, data.condition_note)

    # 8) 가격 바 — 오렌지 통짜, 화면 끝까지
    draw.rectangle([0, Y_PRICE, W, Y_PRICE + PRICE_H], fill=B.ORANGE)
    _draw_prices(draw, data)

    # 9) 하단 바 — 매장 안내
    draw.rectangle([0, Y_FOOTER, W, H], fill=B.FOOTER_BG)
    foot_font = B.font("medium", 32)
    fw = text_width(data.footer, foot_font)
    fa, fd = foot_font.getmetrics()
    draw.text(
        ((W - fw) / 2, Y_FOOTER + (H - Y_FOOTER - (fa + fd)) / 2),
        data.footer,
        font=foot_font,
        fill=(214, 218, 228),
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path, "PNG", optimize=True)
    log.info("카드뉴스 생성: %s", out_path)
    return out_path


def _draw_prices(draw: ImageDraw.ImageDraw, data: CardData) -> None:
    x = MARGIN - 8
    pct = data.computed_pct
    has_orig = bool(data.original_price and data.original_price > data.sale_price)

    # 할인율 알약 뱃지 (우측, 세로 중앙)
    if pct:
        _pill(
            draw,
            W - MARGIN - 96,
            Y_PRICE + PRICE_H // 2,
            f"{pct}%↓",
            bg=B.SLATE,
            fg=B.ORANGE,
            size=62,
        )
        right_limit = W - MARGIN - 230
    else:
        right_limit = W - MARGIN

    if has_orig:
        label_font = B.font("medium", 34)
        draw.text((x, Y_PRICE + 44), data.orig_label, font=label_font, fill=(255, 226, 209))
        orig_font = B.font("semibold", 54)
        _strikethrough(
            draw, x, Y_PRICE + 88, won(data.original_price), orig_font, (255, 242, 234)
        )
        sale_label_y = Y_PRICE + 176
        sale_price_y = Y_PRICE + 218
    else:
        sale_label_y = Y_PRICE + 88
        sale_price_y = Y_PRICE + 136

    draw.text((x, sale_label_y), data.sale_label, font=B.font("bold", 38), fill=B.WHITE)

    # 판매가는 뱃지를 침범하지 않도록 자동 축소
    price_text = won(data.sale_price)
    for size in (100, 94, 86, 78, 70):
        price_font = B.font("extrabold", size)
        if x + text_width(price_text, price_font) <= right_limit:
            break
    draw.text((x, sale_price_y), price_text, font=price_font, fill=B.WHITE)


# ================================================================ 릴스 표지
# 릴스는 세로 9:16 — 우리 카드와 같은 규격이라 상품 카드는 그대로 쓴다.
# 맨 앞에 붙일 표지 한 장만 따로 그린다.
def render_cover(
    out_path: Path,
    *,
    date_label: str,
    store_name: str,
    headline: str = "오늘의 추천템",
    item_count: int | None = None,
    strict_logo: bool = True,
    logo: Path | str | Image.Image | None = None,
) -> Path:
    """릴스 맨 앞장(표지). 날짜 · 매장 · 오늘의 추천템. 상품 카드와 같은 1080x1920."""
    canvas = Image.new("RGB", (W, H), B.BG)
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([0, 0, W, Y_ACCENT_BAR], fill=B.ORANGE)

    mark = _logo_image(logo, strict_logo)
    canvas.paste(mark, ((W - mark.width) // 2, 540), mark)

    y = 540 + mark.height + 104
    if date_label:
        f = B.font("bold", 58)
        draw.text(((W - text_width(date_label, f)) / 2, y), date_label, font=f, fill=B.MUTED)
        y += 108

    f = B.font("bold", 64)
    draw.text(((W - text_width(store_name, f)) / 2, y), store_name, font=f, fill=B.INK)
    y += 132

    # 제목은 폭에 맞춰 자동 축소 — 문구가 길어져도 넘치지 않는다
    for size in (150, 136, 122, 108, 96):
        title_font = B.font("extrabold", size)
        if text_width(headline, title_font) <= CONTENT_W:
            break
    draw.text(((W - text_width(headline, title_font)) / 2, y), headline,
              font=title_font, fill=B.INK)
    y += title_font.size + 74

    draw.rounded_rectangle([(W - 200) // 2, y, (W + 200) // 2, y + 12], radius=6, fill=B.ORANGE)
    y += 108

    if item_count:
        _pill(draw, W // 2, y + 40, f"총 {item_count}개", bg=B.SLATE, fg=B.WHITE, size=48)

    draw.rectangle([0, Y_FOOTER, W, H], fill=B.FOOTER_BG)
    f = B.font("semibold", 36)
    note = "매장에서 직접 보고 구매하세요"
    draw.text(((W - text_width(note, f)) / 2, Y_FOOTER + 30), note, font=f, fill=(226, 229, 238))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path, "PNG")
    return out_path
