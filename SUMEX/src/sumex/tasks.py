"""할 일 상태 관리.

data/tasks.yaml 을 사람이 읽는 형태 그대로 두고, 상태 값만 안전하게 바꾼다.
yaml 을 통째로 다시 쓰면 주석과 배치가 날아가므로 해당 줄만 치환한다.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from . import config, registry

VALID = ("todo", "doing", "done", "dropped")
_PATH = lambda: config.path("data", "tasks.yaml")  # noqa: E731


class UnknownTask(LookupError):
    pass


def get(task_id: str) -> dict[str, Any]:
    for task in registry.backlog():
        if str(task.get("id")) == task_id:
            return task
    raise UnknownTask(f"{task_id} 라는 할 일이 없습니다.")


def set_status(task_id: str, status: str) -> dict[str, Any]:
    if status not in VALID:
        raise ValueError(f"상태는 {', '.join(VALID)} 중 하나여야 합니다. (받은 값: {status})")
    task = get(task_id)

    path: Path = _PATH()
    text = path.read_text(encoding="utf-8")

    # `id: T-004` 가 들어 있는 블록 안의 `status: xxx` 하나만 바꾼다.
    pattern = re.compile(
        rf"(\{{\s*id:\s*{re.escape(task_id)}\b.*?status:\s*)(todo|doing|done|dropped)",
        re.DOTALL,
    )
    new_text, count = pattern.subn(rf"\g<1>{status}", text, count=1)
    if count != 1:
        raise UnknownTask(
            f"{task_id} 의 status 를 찾지 못했습니다. data/tasks.yaml 을 직접 편집하세요."
        )
    path.write_text(new_text, encoding="utf-8")
    registry.reload()
    task = get(task_id)
    return task


def counts() -> dict[str, int]:
    out = {k: 0 for k in VALID}
    for task in registry.backlog():
        out[str(task.get("status", "todo"))] = out.get(str(task.get("status", "todo")), 0) + 1
    return out


def filtered(*, status: str | None = None, hospital: str | None = None,
             pri: str | None = None) -> list[dict[str, Any]]:
    rows = registry.backlog()
    if status:
        rows = [t for t in rows if t.get("status", "todo") == status]
    if pri:
        rows = [t for t in rows if t.get("pri") == pri]
    if hospital:
        try:
            hid = registry.find(hospital).id
        except LookupError:
            hid = hospital
        rows = [t for t in rows if t.get("hospital") == hid]
    return rows
