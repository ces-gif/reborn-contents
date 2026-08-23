"""설정 로딩.

config.yaml 의 {{PRIVATE:key}} 자리표시자를 data/private/company.yaml 값으로 채운다.
private 파일이 없어도 죽지 않는다 — 자리표시자가 '(비공개)' 로 바뀔 뿐이다.
"""
from __future__ import annotations

import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]      # .../SUMEX
PLACEHOLDER = re.compile(r"\{\{PRIVATE:([a-z_]+)\}\}")
MISSING = "(비공개)"


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def _flatten_private(private: dict[str, Any]) -> dict[str, str]:
    """{'company': {'ceo': 'x'}, 'rep': {'name': 'y'}} -> {'ceo': 'x', 'rep_name': 'y'}"""
    flat: dict[str, str] = {}
    for key, value in (private.get("company") or {}).items():
        flat[key] = str(value)
    for key, value in (private.get("rep") or {}).items():
        flat[f"rep_{key}"] = str(value)
    return flat


def _resolve(node: Any, values: dict[str, str]) -> Any:
    if isinstance(node, str):
        return PLACEHOLDER.sub(lambda m: values.get(m.group(1), MISSING), node)
    if isinstance(node, dict):
        return {k: _resolve(v, values) for k, v in node.items()}
    if isinstance(node, list):
        return [_resolve(v, values) for v in node]
    return node


@lru_cache(maxsize=1)
def load() -> dict[str, Any]:
    cfg = _load_yaml(ROOT / "config.yaml")
    private = _load_yaml(ROOT / "data" / "private" / "company.yaml")
    cfg = _resolve(cfg, _flatten_private(private))
    cfg["_root"] = str(ROOT)
    cfg["_has_private"] = bool(private)
    return cfg


def path(*parts: str) -> Path:
    return ROOT.joinpath(*parts)


def out_dir(sub: str = "") -> Path:
    target = ROOT / os.environ.get("SUMEX_OUT", "out")
    if sub:
        target = target / sub
    target.mkdir(parents=True, exist_ok=True)
    return target
