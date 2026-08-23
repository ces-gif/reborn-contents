#!/usr/bin/env python3
"""SUMEX 를 리본마켓 저장소에서 떼어내 독립 저장소로 만든다.

지금은 SUMEX 가 `ces-gif/reborn-contents` 안의 한 폴더로 들어가 있다.
리본마켓(중고가전 유통)과 SUMEX(의료기기 영업)는 완전히 다른 사업이므로
저장소를 나누는 것이 맞다. 이 스크립트가 그 분리를 자동으로 한다.

무엇을 하나
    1. SUMEX/ 안의 내용을 새 저장소의 최상위로 옮긴다
    2. .claude/skills/sumex-* 6개를 함께 가져온다
    3. CI 워크플로를 독립 저장소 기준으로 고쳐 쓴다 (working-directory 제거)
    4. 문서 안의 `cd SUMEX` 같은 경로 안내를 고친다
    5. git init → 커밋 (원하면 push 까지)

무엇을 가져가지 않나
    data/private/**      담당자 실명·연락처·계좌 (새 저장소에서 다시 만든다)
    templates/*.xlsx     회사 실양식
    out/**               생성물
    __pycache__, .venv, node_modules

사용법
    # 1) 먼저 GitHub 에서 빈 저장소를 하나 만든다 (비공개 권장)
    #    https://github.com/new  →  이름: sumex-auto, Private, 초기화 파일 없이

    # 2) 미리보기 — 어디에 뭐가 놓이는지만 확인
    python3 scripts/split_repo.py --dry-run

    # 3) 로컬에 만들어 본다
    python3 scripts/split_repo.py --out /tmp/sumex-auto

    # 4) 만들면서 바로 푸시
    python3 scripts/split_repo.py --out /tmp/sumex-auto \\
        --push https://github.com/ces-gif/sumex-auto.git

비공개로 만들 것
    교육자료는 사내 교육용 대외비이고 거래처 이름이 들어 있다.
    공개 저장소로 만들면 지금처럼 개인정보를 분리해도 거래처 목록 자체가 노출된다.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

SUMEX = Path(__file__).resolve().parents[1]        # .../SUMEX
REPO = SUMEX.parent                                # .../reborn-contents

EXCLUDE_DIRS = {"out", "__pycache__", ".venv", "node_modules", ".pytest_cache", ".git"}
EXCLUDE_SUFFIX = {".pyc", ".xlsx", ".xls"}          # templates 실양식 포함
KEEP_PRIVATE = {"README.md"}                        # data/private 에서 이것만 가져간다
EXCLUDE_FILES = {"scripts/split_repo.py"}           # 분리 스크립트 자신은 안 가져간다

# 새 저장소에서는 의미가 없어지는 문단 (제목 줄부터 다음 `---` 앞까지 통째로 뺀다)
DROP_SECTIONS = ["## 독립 저장소로 분리"]

WORKFLOW = """name: CI

# SUMEX 영업 자동화 — 파이썬 엔진과 노드 대시보드를 함께 검증한다.
# 테스트에는 인수인계 자료에서 확인된 사실이 고정되어 있다
# (서울척 3장 / 서울적십자 5장 / 세종스포츠 도장 3종 / 8-14 다음 영업일 8-18).
# 데이터를 고쳐서 이게 깨지면 근거를 남기고 테스트를 함께 고칠 것.

on:
  push:
    branches: ["**"]
  pull_request:
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
          cache-dependency-path: requirements-dev.txt

      - name: 의존성 설치
        run: pip install -r requirements-dev.txt

      - name: 파이썬 테스트
        env:
          PYTHONPATH: src
        run: python -m pytest tests -q

      - name: 개인정보가 공개 파일에 섞이지 않았는지
        run: |
          set -e
          # data/private/ 와 *.example.yaml 은 검사에서 뺀다 (자리표시자가 들어 있다)
          find data knowledge config.yaml -type f \\
               ! -path 'data/private/*' ! -name '*.example.*' -print0 > /tmp/targets
          if ! [ -s /tmp/targets ]; then echo "검사 대상 없음"; exit 0; fi
          if xargs -0 grep -nE '01[0-9][- ]?[0-9]{3,4}[- ]?[0-9]{4}' < /tmp/targets; then
            echo "::error::휴대폰 번호로 보이는 문자열이 있습니다. data/private/ 로 옮기세요."
            exit 1
          fi
          if xargs -0 grep -niE '[a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,}' < /tmp/targets; then
            echo "::error::이메일 주소가 있습니다. data/private/ 로 옮기세요."
            exit 1
          fi
          echo "확인 완료 — 연락처 없음"

      - name: 회사 실양식이 커밋되지 않았는지
        run: |
          if git ls-files --error-unmatch templates/*.xlsx 2>/dev/null; then
            echo "::error::templates/*.xlsx 는 커밋하지 않습니다 (로고·계좌 포함)."
            exit 1
          fi
          echo "확인 완료"

      - uses: actions/setup-node@v4
        with:
          node-version: "20"

      - name: 대시보드 데이터 생성
        env:
          PYTHONPATH: src
        run: python -m sumex.cli export

      - name: 노드 테스트
        run: node tools/node/test/render.test.mjs

      - name: CLI 스모크 테스트
        env:
          PYTHONPATH: src
        run: |
          set -e
          python -m sumex.cli today
          python -m sumex.cli hospitals
          python -m sumex.cli audit
          python -m sumex.cli month 2026-09
          python -m sumex.cli checklist 세종스포츠
          python -m sumex.cli visit 세종스포츠 무척나은 구리센트럴
          python -m sumex.cli doc 세종스포츠 --items "ICONIX 1.7T x 3 @ 320000"
          python -m sumex.cli ics --month 2026-09
          python -m sumex.cli casecover
"""

# 문서 안에서 고쳐야 하는 경로 안내 (SUMEX 가 최상위가 되므로).
# 순서가 중요하다 — 구조 다이어그램의 `SUMEX/` 를 먼저 처리한 뒤 일반 경로를 자른다.
REWRITES: list[tuple[str, str]] = [
    ("```\nSUMEX/\n├──", "```\n.\n├──"),
    ("cd SUMEX\npip install -r requirements.txt", "pip install -r requirements.txt"),
    ("cd SUMEX && export PYTHONPATH=src", "export PYTHONPATH=src"),
    ("저장소 루트 `.claude/skills/` 에 6개가 들어 있다.",
     "`.claude/skills/` 에 6개가 들어 있다."),
    ("`.claude/skills/    저장소 루트에 sumex-* 6개",
     "`.claude/skills/    sumex-* 6개"),
    # 새 저장소는 비공개로 만드는 것을 전제로 한다. 그래도 개인정보 분리는 유지한다 —
    # 비공개 저장소도 협업자에게 열리고, 허깅페이스 발행이 같은 파일을 읽는다.
    ("이 저장소는 **공개**다. 인수인계 자료에는 교수·간호사·구매 담당자의 실명과\n"
     "휴대폰·이메일이 들어 있어서, 그대로 올리면 안 된다.",
     "저장소를 비공개로 두더라도 개인정보는 분리해 둔다. 비공개 저장소도 협업자에게\n"
     "열리고, 허깅페이스 발행이 같은 파일을 읽기 때문이다."),
    ("이 저장소는 **공개**다. 인수인계 자료에는 교수·간호사·구매 담당자의 실명과\n"
     "휴대폰·이메일이 있다.",
     "저장소가 비공개여도 개인정보는 분리해 둔다. 인수인계 자료에는 교수·간호사·구매\n"
     "담당자의 실명과 휴대폰·이메일이 있다."),
    # 분리 안내는 새 저장소에서 의미가 없다 (이미 분리된 상태)
    ("리본마켓 저장소(`ces-gif/reborn-contents`) 안의 한 폴더로 들어가 있다",
     "리본마켓 저장소에서 분리되어 나온 독립 저장소다"),
    # 남은 것은 모두 폴더 접두사이므로 일괄로 자른다
    ("SUMEX/knowledge/", "knowledge/"),
    ("SUMEX/data/", "data/"),
    ("SUMEX/src/", "src/"),
    ("SUMEX/tests/", "tests/"),
    ("SUMEX/tools/", "tools/"),
    ("SUMEX/out/", "out/"),
    ("SUMEX/scripts/", "scripts/"),
    ("SUMEX/templates/", "templates/"),
]


def wanted(path: Path) -> bool:
    rel = path.relative_to(SUMEX)
    if rel.as_posix() in EXCLUDE_FILES:
        return False
    if any(part in EXCLUDE_DIRS for part in rel.parts):
        return False
    if path.suffix in EXCLUDE_SUFFIX:
        return False
    if rel.parts[:2] == ("data", "private") and path.name not in KEEP_PRIVATE:
        # 예시 파일은 가져간다. 실제 개인정보 파일은 두고 간다.
        if ".example." not in path.name:
            return False
    return True


def collect() -> list[Path]:
    return sorted(p for p in SUMEX.rglob("*") if p.is_file() and wanted(p))


def drop_sections(text: str) -> str:
    """제목 줄부터 다음 구분선(---) 직전까지 통째로 들어낸다."""
    for heading in DROP_SECTIONS:
        start = text.find(f"\n{heading}\n")
        if start == -1:
            continue
        end = text.find("\n---\n", start + 1)
        text = text[:start] + (text[end:] if end != -1 else "\n")
    return text


def rewrite(text: str) -> str:
    text = drop_sections(text)
    for old, new in REWRITES:
        text = text.replace(old, new)
    return text


def build(out: Path, dry_run: bool) -> tuple[int, list[str]]:
    files = collect()
    skills = sorted(REPO.glob(".claude/skills/sumex-*/SKILL.md"))
    plan: list[str] = []

    for src in files:
        plan.append(str(src.relative_to(SUMEX)))
    for src in skills:
        plan.append(str(src.relative_to(REPO)))
    plan.append(".github/workflows/ci.yml")

    if dry_run:
        return len(plan), plan

    if out.exists():
        if not (out / ".git").exists() and any(out.iterdir()):
            raise SystemExit(f"{out} 가 비어 있지 않고 git 저장소도 아닙니다. 다른 경로를 주세요.")
        shutil.rmtree(out)
    out.mkdir(parents=True)

    for src in files:
        dst = out / src.relative_to(SUMEX)
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.suffix in (".md", ".yaml", ".yml", ".py", ".mjs", ".json", ".txt"):
            dst.write_text(rewrite(src.read_text(encoding="utf-8")), encoding="utf-8")
        else:
            shutil.copy2(src, dst)

    for src in skills:
        dst = out / ".claude" / "skills" / src.parent.name / "SKILL.md"
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(rewrite(src.read_text(encoding="utf-8")), encoding="utf-8")

    wf = out / ".github" / "workflows" / "ci.yml"
    wf.parent.mkdir(parents=True, exist_ok=True)
    wf.write_text(WORKFLOW, encoding="utf-8")

    # 독립 저장소에서는 .gitignore 의 경로가 그대로 맞는다 (SUMEX/.gitignore 를 그대로 씀)
    return len(plan), plan


def git(out: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=out, check=True,
                          capture_output=True, text=True)


def commit_and_push(out: Path, remote: str | None) -> None:
    if not (out / ".git").exists():
        git(out, "init", "-q", "-b", "main")
    git(out, "add", "-A")
    try:
        git(out, "-c", "user.email=ces@rebornmarket.org", "-c", "user.name=SUMEX",
            "commit", "-q", "-m",
            "SUMEX 영업 자동화 — 교육자료 · 서류작업 · 업무 스케줄\n\n"
            "리본마켓 저장소(ces-gif/reborn-contents)에서 분리해 독립 저장소로 옮겼다.\n"
            "리본마켓은 중고가전 유통, SUMEX 는 의료기기 영업이라 성격이 완전히 다르다.\n\n"
            "담당자 실명·연락처·계좌는 data/private/(gitignore)에 두고 가져오지 않았다.\n"
            "새 환경에서 scripts/bootstrap_private_data.py 로 다시 만든다.")
    except subprocess.CalledProcessError as exc:
        if "nothing to commit" not in (exc.stdout or ""):
            raise
        print("변경 사항 없음 — 커밋 생략")

    if not remote:
        return

    existing = subprocess.run(["git", "remote"], cwd=out, capture_output=True, text=True)
    if "origin" in existing.stdout.split():
        git(out, "remote", "set-url", "origin", remote)
    else:
        git(out, "remote", "add", "origin", remote)

    print(f"\n푸시: {remote}")
    result = subprocess.run(["git", "push", "-u", "origin", "main"],
                            cwd=out, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr.strip(), file=sys.stderr)
        raise SystemExit(
            "\n푸시에 실패했습니다. 확인할 것:\n"
            "  · GitHub 에 그 이름의 빈 저장소가 실제로 있는가\n"
            "  · 이 환경에 그 저장소에 대한 푸시 권한이 있는가\n"
            "    (Claude 세션이면 add_repo 로 먼저 붙여야 합니다)\n"
        )
    print(result.stdout.strip() or "완료")


def main() -> int:
    p = argparse.ArgumentParser(description="SUMEX 를 독립 저장소로 분리")
    p.add_argument("--out", default="/tmp/sumex-auto", help="만들 위치")
    p.add_argument("--push", metavar="URL", help="만들면서 이 원격으로 푸시한다")
    p.add_argument("--dry-run", action="store_true", help="옮길 파일 목록만 본다")
    args = p.parse_args()

    out = Path(args.out).expanduser().resolve()
    count, plan = build(out, args.dry_run)

    if args.dry_run:
        print(f"옮길 파일 {count}개\n")
        for rel in plan:
            print(f"  {rel}")
        print(f"\n가져가지 않는 것: data/private 실제 파일, templates/*.xlsx, out/")
        return 0

    print(f"만들었습니다: {out}   (파일 {count}개)")
    commit_and_push(out, args.push)

    if not args.push:
        print("\n다음:")
        print("  1) https://github.com/new 에서 빈 저장소를 만든다 (Private 권장, 초기화 파일 없이)")
        print(f"  2) cd {out}")
        print("     git remote add origin https://github.com/<계정>/<이름>.git")
        print("     git push -u origin main")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:      # `| head` 처럼 중간에 끊길 때
        sys.stdout = None
        raise SystemExit(0)
