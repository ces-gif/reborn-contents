#!/usr/bin/env python3
"""하루치 콘텐츠 생성 CLI. 설정에 있는 매장을 순서대로 전부 돈다.

사용 예:
    python scripts/run_daily.py                    # 오늘(한국시간) 올라온 사진으로 생성 + 드라이브 업로드
    python scripts/run_daily.py --date 2026-08-21  # 특정 날짜분 다시 만들기
    python scripts/run_daily.py --dry-run          # 로컬에만 만들고 업로드/알림은 안 함
    python scripts/run_daily.py --reprocess        # 이미 처리한 사진도 다시 처리
    python scripts/run_daily.py --store fox-ils    # 그 매장만

한 매장이 실패해도 나머지 매장은 끝까지 돈다. 평택이 넘어졌다고 일산까지
공치면 안 된다. 실패한 매장이 하나라도 있으면 종료 코드는 1 이다.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from reborn.config import load_stores  # noqa: E402
from reborn.pipeline import print_summary, run, slugify  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="리본마켓 카드뉴스/블로그 자동 생성")
    parser.add_argument("--date", help="처리할 날짜 (YYYY-MM-DD, 한국시간 기준)")
    parser.add_argument("--dry-run", action="store_true", help="드라이브 업로드와 알림을 건너뛴다")
    parser.add_argument("--reprocess", action="store_true", help="이미 처리한 사진도 다시 처리한다")
    parser.add_argument("--out", default="out", help="로컬 출력 폴더 (기본 out)")
    parser.add_argument("--config", help="설정 파일 경로")
    parser.add_argument("--store", help="이 매장만 실행 (설정의 store id 또는 이름)")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )
    logging.getLogger("googleapiclient.discovery_cache").setLevel(logging.ERROR)

    if args.store:
        os.environ["ONLY_STORE"] = args.store
    stores = load_stores(args.config)
    target = date.fromisoformat(args.date) if args.date else None
    log = logging.getLogger("reborn")

    failed: list[str] = []
    results: dict = {}
    for settings in stores:
        if len(stores) > 1:
            print(f"\n━━━ {settings.store_name} ━━━")
        log.info("=== %s 시작 ===", settings.store_name)
        try:
            result = run(
                settings,
                day=target,
                out_root=Path(args.out) / slugify(settings.store_id),
                dry_run=args.dry_run,
                reprocess=args.reprocess,
            )
        except Exception as exc:
            # 한 매장이 넘어져도 나머지는 끝까지 돈다.
            log.exception("[%s] 실행 실패", settings.store_name)
            print(f"❌ {settings.store_name} 실패: {exc}", file=sys.stderr)
            failed.append(settings.store_name)
            continue
        results[settings.store_id] = result
        print_summary(result)

    _write_status(Path(args.out), stores, results, failed)

    if failed:
        print(f"\n❌ 실패한 매장: {', '.join(failed)}", file=sys.stderr)
        return 1
    return 0


def _write_status(out_root: Path, stores, results: dict, failed: list[str]) -> None:
    """실행 결과를 한 파일로 남긴다.

    깃허브 액션이 이걸 읽어서 뭔가 잘못됐으면 이슈를 연다 (이슈는 메일로 온다).
    "돌긴 돌았는데 사진이 있는데도 카드가 0장" 같은 조용한 실패를 놓치지 않으려는 것이다.
    """
    payload = {"failed": failed, "stores": []}
    for settings in stores:
        result = results.get(settings.store_id)
        payload["stores"].append(
            {
                "id": settings.store_id,
                "name": settings.store_name,
                "ok": result is not None,
                "photos": getattr(result, "photos_seen", 0) if result else 0,
                "cards": len(getattr(result, "cards", [])) if result else 0,
                "skipped": getattr(result, "skipped_reason", None) if result else "실행 실패",
                "problems": list(getattr(result, "step_failures", [])) if result else [],
            }
        )
    try:
        out_root.mkdir(parents=True, exist_ok=True)
        (out_root / "_status.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    except Exception as exc:  # 상태 파일 때문에 실행을 실패로 만들지는 않는다
        logging.getLogger("reborn").warning("상태 파일을 남기지 못했습니다: %s", exc)


if __name__ == "__main__":
    raise SystemExit(main())
