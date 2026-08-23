"""이미 처리한 사진을 기억해서 같은 상품을 두 번 만들지 않게 한다.

원장(ledger)은 드라이브의 '콘텐츠 발행' 폴더 안에 _ledger.json 으로 보관한다.
저장소가 아니라 드라이브에 두는 이유: 실행 환경(깃허브 액션 러너)은 매번 새로 뜨고
드라이브는 실제로 콘텐츠가 쌓이는 곳이기 때문이다.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

log = logging.getLogger(__name__)

LEDGER_NAME = "_ledger.json"


@dataclass
class Ledger:
    processed_file_ids: set[str] = field(default_factory=set)
    runs: list[dict] = field(default_factory=list)

    @classmethod
    def load(cls, path: Path) -> "Ledger":
        if not path.exists():
            return cls()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            log.warning("원장 파일이 깨져 있어 새로 시작합니다: %s", path)
            return cls()
        return cls(
            processed_file_ids=set(data.get("processed_file_ids", [])),
            runs=data.get("runs", []),
        )

    def save(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {
                    "processed_file_ids": sorted(self.processed_file_ids),
                    "runs": self.runs[-90:],  # 최근 90회만 보관
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        return path

    def seen(self, file_id: str) -> bool:
        return file_id in self.processed_file_ids

    def mark(self, file_ids: list[str]) -> None:
        self.processed_file_ids.update(file_ids)

    def record_run(self, entry: dict) -> None:
        self.runs.append(entry)
