#!/usr/bin/env python3
"""리본마켓 하루치 콘텐츠 생성 CLI.

사용 예:
    python scripts/run_daily.py                    # 오늘(한국시간) 올라온 사진으로 생성 + 드라이브 업로드
    python scripts/run_daily.py --date 2026-08-21  # 특정 날짜분 다시 만들기
    python scripts/run_daily.py --dry-run          # 로컬에만 만들고 업로드/알림은 안 함
    python scripts/run_daily.py --reprocess        # 이미 처리한 사진도 다시 처리
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from reborn.config import load_settings  # noqa: E402
from reborn.pipeline import print_summary, run  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="리본마켓 카드뉴스/블로그 자동 생성")
    parser.add_argument("--date", help="처리할 날짜 (YYYY-MM-DD, 한국시간 기준)")
    parser.add_argument("--dry-run", action="store_true", help="드라이브 업로드와 알림을 건너뛴다")
    parser.add_argument("--reprocess", action="store_true", help="이미 처리한 사진도 다시 처리한다")
    parser.add_argument("--out", default="out", help="로컬 출력 폴더 (기본 out)")
    parser.add_argument("--config", help="설정 파일 경로")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )
    logging.getLogger("googleapiclient.discovery_cache").setLevel(logging.ERROR)

    settings = load_settings(args.config)
    target = date.fromisoformat(args.date) if args.date else None

    try:
        result = run(
            settings,
            day=target,
            out_root=Path(args.out),
            dry_run=args.dry_run,
            reprocess=args.reprocess,
        )
    except Exception as exc:
        logging.getLogger("reborn").exception("실행 실패")
        print(f"❌ 실패: {exc}", file=sys.stderr)
        return 1

    print_summary(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
