#!/usr/bin/env python3
"""SUMEX 지식베이스를 Hugging Face 데이터셋으로 발행한다.

무엇을 올리나
    knowledge/*.md      교육자료 8편
    data/*.yaml         거래처 서류 규칙 · 품목 · 서류 양식 · 할 일
    (JSONL 로 변환한 검색용 사본도 함께)

무엇을 올리지 않나
    data/private/**     담당자 실명·연락처·계좌·매출 — 절대
    templates/*.xlsx    회사 실양식 (로고·계좌 포함)
    out/**              생성물

왜 Hugging Face 인가
    깃허브는 사람이 읽고 고치는 곳이고, 여기는 기계가 읽는 곳이다.
    나중에 이 지식베이스로 RAG 를 붙이거나, 신입 교육용 QA 를 만들거나,
    다른 도구에서 데이터셋으로 불러 쓸 때 쓴다.

기본값은 비공개(private) 다
    이 자료는 사내 교육용 대외비이고 거래처 이름이 들어 있다.
    `--public` 을 명시하지 않으면 절대 공개로 만들지 않는다.

사용법
    pip install huggingface_hub
    export HF_TOKEN=hf_xxxxx          # write 권한 필요
    python scripts/publish_hf.py --check            # 올리기 전 안전 점검만
    python scripts/publish_hf.py                    # 비공개 데이터셋으로 발행
    python scripts/publish_hf.py --repo 내계정/이름   # 저장소 이름 지정
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_NAME = "sumex-sales-kb"

# 절대 올리지 않는 것
FORBIDDEN = ("data/private", "templates", "out", "__pycache__", ".venv", "node_modules")

# 연락처가 섞여 들어가지 않았는지 마지막으로 확인하는 패턴
PHONE = re.compile(r"01[0-9][- ]?[0-9]{3,4}[- ]?[0-9]{4}")
EMAIL = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")


class Unsafe(RuntimeError):
    pass


def collect() -> list[Path]:
    files = sorted(ROOT.glob("knowledge/*.md"))
    files += sorted(p for p in ROOT.glob("data/*.yaml"))
    files.append(ROOT / "README.md")
    return [p for p in files if p.exists()]


def safety_check(files: list[Path]) -> list[str]:
    """연락처·비공개 경로가 섞였는지 본다. 하나라도 걸리면 발행하지 않는다."""
    problems: list[str] = []
    for path in files:
        rel = path.relative_to(ROOT).as_posix()
        if any(rel.startswith(bad) for bad in FORBIDDEN):
            problems.append(f"{rel}: 발행 대상이 아닌 경로")
            continue
        if ".example." in rel:
            continue
        text = path.read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), start=1):
            if PHONE.search(line):
                problems.append(f"{rel}:{lineno}: 휴대폰 번호로 보이는 문자열")
            if EMAIL.search(line) and "example.com" not in line:
                problems.append(f"{rel}:{lineno}: 이메일 주소")
    return problems


def build_jsonl(staging: Path) -> int:
    """기계가 읽기 좋은 형태로 한 번 더 뽑는다.

    knowledge 는 `##` 헤딩 단위로 쪼개고, hospitals 는 거래처 한 곳이 한 줄이 된다.
    """
    rows: list[dict] = []

    for md in sorted(ROOT.glob("knowledge/*.md")):
        doc = md.stem
        chunks = re.split(r"^## ", md.read_text(encoding="utf-8"), flags=re.MULTILINE)
        for idx, chunk in enumerate(chunks):
            body = chunk.strip()
            if not body:
                continue
            title = body.splitlines()[0].lstrip("# ").strip()
            rows.append({
                "source": f"knowledge/{md.name}",
                "kind": "교육자료",
                "doc": doc,
                "section": title,
                "text": body,
            })

    hospitals = yaml.safe_load((ROOT / "data" / "hospitals.yaml").read_text(encoding="utf-8"))
    for section in ("hospitals", "prospects"):
        for row in hospitals.get(section) or []:
            rows.append({
                "source": "data/hospitals.yaml",
                "kind": "거래처",
                "doc": row["id"],
                "section": row["name"],
                "text": yaml.safe_dump(row, allow_unicode=True, sort_keys=False),
            })

    products = yaml.safe_load((ROOT / "data" / "products.yaml").read_text(encoding="utf-8"))
    for cat in products.get("categories") or []:
        for item in cat.get("items") or []:
            rows.append({
                "source": "data/products.yaml",
                "kind": "품목",
                "doc": item.get("id", ""),
                "section": item.get("name", ""),
                "text": yaml.safe_dump(item, allow_unicode=True, sort_keys=False),
            })

    target = staging / "sumex_kb.jsonl"
    with target.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    return len(rows)


CARD = """---
license: other
license_name: internal-confidential
license_link: LICENSE
language: [ko]
tags: [medical-device, sales-enablement, korean, knowledge-base, onboarding]
pretty_name: SUMEX 영업 지식베이스
configs:
  - config_name: default
    data_files: sumex_kb.jsonl
---

# SUMEX 영업 지식베이스

의료기기 영업 담당자의 **교육자료 · 서류작업 규칙 · 품목 정보**를 담은 한국어
지식베이스다. 코드와 도구는 깃허브에 있고, 여기에는 기계가 읽을 데이터만 둔다.

> **대외비.** 사내 교육용 자료이며 거래처 이름과 업무 절차가 들어 있다.
> 외부 공유·재배포를 하지 않는다. 담당자 실명·연락처·계좌·매출은
> 이 데이터셋에 포함되지 않는다 (별도 비공개 레이어에서 관리).

## 구성

| 파일 | 내용 |
|---|---|
| `sumex_kb.jsonl` | 검색·RAG 용. 교육자료를 섹션 단위로, 거래처·품목을 항목 단위로 쪼갠 것 |
| `knowledge/*.md` | 교육자료 원본 8편 |
| `data/*.yaml` | 거래처 서류 규칙 · 품목 · 서류 양식 좌표 · 할 일 |

### `sumex_kb.jsonl` 필드

| 필드 | 뜻 |
|---|---|
| `source` | 원본 파일 경로 |
| `kind` | `교육자료` / `거래처` / `품목` |
| `doc` | 문서 또는 항목 id |
| `section` | 섹션 제목 또는 항목 이름 |
| `text` | 본문 (마크다운 또는 yaml) |

## 무엇이 들어 있나

**교육자료** — 90일 온보딩 커리큘럼, 의료기기 산업 기초(재료·고정 원리·시장·
경쟁 5사·인허가), 어깨 복합체 50분 강의안, 제품 심층(영상 플랫폼·파워툴·
고속드릴·피부봉합·앵커·서지컬 헬멧), 병원별 서류 업무 총람, 영업 플레이북,
트러블슈팅과 클레임 SOP, 용어집, 자가점검 문제은행.

**거래처 서류 규칙** — 병원 23곳의 서류 종류·매수·도장 유무·배부처·납품 절차·
시간 제약·월 마감 규칙. 출처가 둘이고 서로 다르게 말하는 항목은 `conflicts`
로 남겨 두었다.

**품목** — 취급 제품의 임상 적응증, 공학적 구조, 품번, 영업 논리.

## 쓰는 법

```python
from datasets import load_dataset

ds = load_dataset("{repo_id}", split="train")
edu = ds.filter(lambda r: r["kind"] == "교육자료")
```

## 주의

- 제품 사양·품번·가격은 개정된다. 견적·발주 전에 최신 자료로 재확인할 것.
- 시장 수치는 조사기관별 정의가 달라 편차가 있다. 인용 시 출처와 기준연도를 함께.
- 제품 적응증은 반드시 최신 허가사항과 사용설명서를 확인할 것.
- 의학적 조언이 아니다.
"""

LICENSE = """SUMEX 사내 교육용 대외비 자료

이 저장소의 내용은 사내 교육 목적으로만 사용한다.
외부 공유, 재배포, 공개 게시를 금지한다.
"""


def main() -> int:
    p = argparse.ArgumentParser(description="SUMEX 지식베이스를 Hugging Face 에 발행")
    p.add_argument("--repo", help="대상 저장소 (예: 내계정/sumex-sales-kb)")
    p.add_argument("--public", action="store_true",
                   help="공개로 만든다. 기본은 비공개 — 대외비 자료이므로 신중히")
    p.add_argument("--check", action="store_true", help="안전 점검만 하고 끝낸다")
    args = p.parse_args()

    files = collect()
    print(f"발행 대상 {len(files)}개 파일")
    for f in files:
        print(f"  · {f.relative_to(ROOT)}")

    problems = safety_check(files)
    if problems:
        print("\n발행을 중단합니다. 아래 항목을 data/private/ 로 옮기세요.\n", file=sys.stderr)
        for msg in problems:
            print(f"  ! {msg}", file=sys.stderr)
        return 1
    print("\n안전 점검 통과 — 공개 파일에 연락처 없음")

    if args.check:
        print("--check 이므로 여기서 끝냅니다.")
        return 0

    if args.public:
        print("\n경고: --public 이 지정되었습니다.")
        print("이 자료는 사내 교육용 대외비이고 거래처 이름이 들어 있습니다.")
        try:
            answer = input("정말 공개로 만들까요? 'yes' 를 입력하세요: ").strip()
        except (EOFError, KeyboardInterrupt):
            answer = ""
        if answer != "yes":
            print("취소했습니다.")
            return 1

    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
    if not token:
        print("\nHF_TOKEN 환경변수가 필요합니다 (write 권한).", file=sys.stderr)
        print("  https://huggingface.co/settings/tokens 에서 만든 뒤", file=sys.stderr)
        print("  export HF_TOKEN=hf_xxxxx", file=sys.stderr)
        return 2

    try:
        from huggingface_hub import HfApi
    except ImportError:
        print("\npip install huggingface_hub 가 필요합니다.", file=sys.stderr)
        return 2

    api = HfApi(token=token)
    repo_id = args.repo
    if not repo_id:
        who = api.whoami()
        repo_id = f"{who['name']}/{DEFAULT_NAME}"
    print(f"\n대상: {repo_id}  ({'공개' if args.public else '비공개'})")

    with tempfile.TemporaryDirectory() as tmp:
        staging = Path(tmp)
        count = build_jsonl(staging)
        print(f"  sumex_kb.jsonl — {count}행")

        for src in files:
            rel = src.relative_to(ROOT)
            dst = staging / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(src, dst)

        (staging / "README.md").write_text(CARD.format(repo_id=repo_id), encoding="utf-8")
        (staging / "LICENSE").write_text(LICENSE, encoding="utf-8")

        api.create_repo(repo_id=repo_id, repo_type="dataset",
                        private=not args.public, exist_ok=True)
        api.upload_folder(
            repo_id=repo_id,
            repo_type="dataset",
            folder_path=str(staging),
            commit_message="SUMEX 지식베이스 갱신",
        )

    print(f"\n완료: https://huggingface.co/datasets/{repo_id}")
    if not args.public:
        print("비공개 저장소입니다. 본인 계정으로 로그인해야 보입니다.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
