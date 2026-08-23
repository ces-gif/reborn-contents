#!/usr/bin/env python3
"""드라이브에 있는 리본마켓 로고를 assets/reborn_logo.png 로 받아 둔다.

카드뉴스는 반드시 이 실제 로고를 쓴다 (텍스트로 로고를 그리지 않는다).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from reborn.config import load_settings  # noqa: E402
from reborn.drive import Drive  # noqa: E402
from reborn.pipeline import ensure_logo  # noqa: E402


def main() -> int:
    settings = load_settings()
    path = ensure_logo(Drive(), settings)
    print(f"로고 준비 완료: {path} ({path.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
