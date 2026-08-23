#!/usr/bin/env python3
"""카드뉴스 디자인만 빠르게 확인해 보는 미리보기 스크립트 (모델·드라이브 호출 없음).

    python scripts/preview_card.py --photo 사진.jpg --name "상품명" \
        --desc "한 줄 소개" --orig 548000 --sale 259000 --out card.png
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from reborn.cardnews import CardData, render_card  # noqa: E402
from reborn.config import load_settings  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--photo", required=True)
    p.add_argument("--name", required=True)
    p.add_argument("--desc", default="")
    p.add_argument("--orig", type=int)
    p.add_argument("--sale", type=int, required=True)
    p.add_argument("--pct", type=int)
    p.add_argument("--out", default="card.png")
    p.add_argument("--date", default=date.today().isoformat())
    args = p.parse_args()

    s = load_settings()
    render_card(
        CardData(
            product_name=args.name,
            one_liner=args.desc,
            sale_price=args.sale,
            original_price=args.orig,
            discount_pct=args.pct,
            date_label=date.fromisoformat(args.date).strftime("%Y.%m.%d"),
            footer=s.visit_line,
            orig_label=s.orig_label,
            sale_label=s.sale_label,
        ),
        Path(args.photo),
        Path(args.out),
    )
    print(f"저장: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
