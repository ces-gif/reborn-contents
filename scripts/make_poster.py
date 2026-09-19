#!/usr/bin/env python3
"""A4 매장 안내 포스터 렌더러 (인쇄용 300dpi PNG + PDF).

카드뉴스와 같은 톤앤매너를 A4 세로로 옮긴 것이다.
- 시그니처 오렌지(#FD6F23) 통짜 배너, 대각선 절단 없음
- 회청색(#72788E) 알약 뱃지
- 어두운(#22252E) 하단 바가 종이 끝까지 닿는 풀블리드
- 로고 PNG 가 있으면 그걸 쓰고, 없으면 자리를 비우지 않고 매장 이름으로 대신한다
  (카드뉴스와 달리 포스터는 매장에서 직접 붙이는 종이라 멈추지 않고 만든다.
   진짜 로고를 넣으려면 assets/reborn_logo.png 를 두거나 REBORN_LOGO_PATH 를 준다)

사용:
    python scripts/make_poster.py                 # 기본 문구로 posters/ 에 생성
    python scripts/make_poster.py --out 경로.png  # 다른 이름으로
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from reborn import branding as B  # noqa: E402
from reborn.textkit import text_width  # noqa: E402

# --- A4 300dpi ---
DPI = 300
W, H = 2480, 3508          # 210 x 297mm
MARGIN = 190               # 약 16mm — 가정용 프린터 여백 안쪽

# --- 포스터 문구 (여기만 고치면 다른 포스터가 된다) ---
EYEBROW = "리본마켓 냉동식품 특가"
BRAND_LINE = "오뚜기 · 하림"
TITLE_LINE = "냉동식품"
BANNER_LINE = "전국 최저가"
LEAD = "마트에서 담던 그 제품, 리본마켓 평택점에서 더 싸게 담아가세요."

POINTS = [
    ("전국 최저가", "오뚜기 · 하림 냉동식품을 전국에서 가장 싼 값으로 드립니다"),
    ("매장에서 바로", "진열된 상품을 직접 보고 고르실 수 있습니다"),
    ("한정 수량", "매장 재고는 한정 수량, 소진 시 조기 종료됩니다"),
]

CTA = "리본마켓 평택점 · 매장에서 직접 보고 구매하세요"

STORE_NAME = "리본마켓 평택점"
STORE_HANDLE = "@reborn.mk"
STORE_ADDRESS = "경기 평택시 이충로 49-29 103호 리본마켓"
PARKING_NOTE = "*건물 건너편 무료 공영주차장 있음!"


def _pill(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, *, bg, fg, size: int) -> int:
    """왼쪽 위 좌표 기준 알약 뱃지. 아랫변 y 를 돌려준다."""
    fnt = B.font("extrabold", size)
    tw = text_width(text, fnt)
    ascent, descent = fnt.getmetrics()
    th = ascent + descent
    pad_x, pad_y = int(size * 0.70), int(size * 0.34)
    box = [x, y, x + tw + pad_x * 2, y + th + pad_y * 2]
    draw.rounded_rectangle(box, radius=(th + pad_y * 2) // 2, fill=bg)
    draw.text((x + pad_x, y + pad_y), text, font=fnt, fill=fg)
    return box[3]


def _line(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, *, weight: str, size: int, fill) -> int:
    fnt = B.font(weight, size)
    draw.text((x, y), text, font=fnt, fill=fill)
    ascent, descent = fnt.getmetrics()
    return y + ascent + descent


def _header_logo(canvas: Image.Image, y: int) -> int:
    """좌상단 로고. 파일이 없으면 매장 이름을 글자로 넣는다(포스터 한정)."""
    try:
        img = B.trim_margins(Image.open(B.logo_path(strict=True)))
        img = B.fit_logo(img, area=700 * 170, max_w=820, max_h=320)
    except B.LogoMissing:
        # 실제 로고가 들어오면 그때 다시 뽑는 게 좋다. 조용히 넘기지 않고 알린다.
        print(
            "⚠ 실제 로고 PNG 를 못 찾아 매장 이름을 글자로 넣었습니다.\n"
            "  assets/reborn_logo.png 를 두거나 REBORN_LOGO_PATH 를 주고 다시 실행하면\n"
            "  진짜 로고가 박힌 포스터가 나옵니다.",
            file=sys.stderr,
        )
        img = B.wordmark(STORE_NAME, 132)
    canvas.paste(img, (MARGIN, y), img)
    return y + img.height


def render() -> Image.Image:
    canvas = Image.new("RGB", (W, H), B.BG)
    draw = ImageDraw.Draw(canvas)

    # 상단 오렌지 액센트 바 (풀블리드)
    draw.rectangle([0, 0, W, 34], fill=B.ORANGE)

    # 머리말 — 로고 / 인스타 핸들
    logo_top = 210
    logo_bottom = _header_logo(canvas, logo_top)
    handle_fnt = B.font("semibold", 58)
    draw.text(
        (W - MARGIN - text_width(STORE_HANDLE, handle_fnt), logo_top + 30),
        STORE_HANDLE,
        font=handle_fnt,
        fill=B.MUTED,
    )

    # 눈썹 뱃지
    y = _pill(draw, MARGIN, logo_bottom + 110, EYEBROW, bg=B.SLATE, fg=B.WHITE, size=62)

    # 제목
    y = _line(draw, MARGIN, y + 90, BRAND_LINE, weight="extrabold", size=202, fill=B.INK)
    y = _line(draw, MARGIN, y + 4, TITLE_LINE, weight="extrabold", size=202, fill=B.INK)

    # 오렌지 통짜 배너 (풀블리드) — 이 포스터의 한 줄
    banner_fnt = B.font("extrabold", 252)
    ascent, descent = banner_fnt.getmetrics()
    banner_top = y + 70
    banner_h = ascent + descent + 130
    draw.rectangle([0, banner_top, W, banner_top + banner_h], fill=B.ORANGE)
    draw.text(
        ((W - text_width(BANNER_LINE, banner_fnt)) // 2, banner_top + 65),
        BANNER_LINE,
        font=banner_fnt,
        fill=B.WHITE,
    )
    y = banner_top + banner_h

    # 리드 문장
    y = _line(draw, MARGIN, y + 106, LEAD, weight="medium", size=64, fill=B.INK)

    # 안내 항목 — 오렌지 번호 사각형 + 제목/설명
    y += 88
    num_size = 118
    for i, (head, body) in enumerate(POINTS, start=1):
        draw.rounded_rectangle([MARGIN, y, MARGIN + num_size, y + num_size], radius=26, fill=B.ORANGE)
        nf = B.font("extrabold", 64)
        na, nd = nf.getmetrics()
        draw.text(
            (MARGIN + (num_size - text_width(str(i), nf)) // 2, y + (num_size - na - nd) // 2),
            str(i),
            font=nf,
            fill=B.WHITE,
        )
        tx = MARGIN + num_size + 46
        ty = _line(draw, tx, y - 6, head, weight="extrabold", size=80, fill=B.INK)
        ty = _line(draw, tx, ty + 4, body, weight="medium", size=56, fill=B.SLATE)
        y = max(ty, y + num_size) + 74

    # 하단 어두운 바 (풀블리드) — 매장 안내
    footer_h = 470
    ft = H - footer_h

    # 매장 방문 유도 — 가는 선 위 한 줄. 하단 바에 붙여 아래 여백이 뜨지 않게 한다.
    cta_fnt = B.font("bold", 68)
    ca, cd = cta_fnt.getmetrics()
    cta_y = ft - 150 - (ca + cd)
    draw.line([(MARGIN, cta_y - 110), (W - MARGIN, cta_y - 110)], fill=(232, 234, 240), width=4)
    draw.text(((W - text_width(CTA, cta_fnt)) // 2, cta_y), CTA, font=cta_fnt, fill=B.ORANGE)
    if y > cta_y - 150:  # 문구가 길어져 겹치면 알려준다 (인쇄물이라 조용히 넘기지 않는다)
        raise SystemExit(f"문구가 A4 한 장을 넘칩니다 (본문 끝 {y}px > 허용 {cta_y - 150}px). 문구를 줄여주세요.")

    draw.rectangle([0, ft, W, H], fill=B.FOOTER_BG)
    fy = _line(draw, MARGIN, ft + 96, STORE_NAME, weight="extrabold", size=82, fill=B.WHITE)
    fy = _line(draw, MARGIN, fy + 14, STORE_ADDRESS, weight="medium", size=56, fill=(206, 210, 222))
    _line(draw, MARGIN, fy + 8, PARKING_NOTE, weight="semibold", size=52, fill=B.ORANGE)

    hf = B.font("bold", 60)
    draw.text(
        (W - MARGIN - text_width(STORE_HANDLE, hf), ft + 110),
        STORE_HANDLE,
        font=hf,
        fill=(206, 210, 222),
    )
    return canvas


def main() -> None:
    ap = argparse.ArgumentParser(description="A4 안내 포스터를 만든다")
    ap.add_argument(
        "--out",
        default=str(REPO_ROOT / "posters" / "2026-09-19-frozen-lowest-price-a4.png"),
        help="PNG 저장 경로 (같은 이름의 PDF 도 같이 만든다)",
    )
    args = ap.parse_args()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    img = render()
    img.save(out, dpi=(DPI, DPI))
    pdf = out.with_suffix(".pdf")
    img.save(pdf, "PDF", resolution=DPI)
    print(f"만들었습니다: {out}\n            {pdf}")


if __name__ == "__main__":
    main()
