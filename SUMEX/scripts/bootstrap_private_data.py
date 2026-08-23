#!/usr/bin/env python3
"""data/private/ 를 만든다 (git 에 올라가지 않는 개인정보 레이어).

세 가지 방법을 지원한다.

  1) 대화식 (기본)
        python scripts/bootstrap_private_data.py
  2) 예시 파일만 복사해 두고 나중에 손으로 채우기
        python scripts/bootstrap_private_data.py --skeleton
  3) 이미 정리해 둔 yaml/json 을 넣기
        python scripts/bootstrap_private_data.py --from /path/to/private.yaml

컨테이너나 PC 를 새로 잡을 때마다 다시 실행하면 된다.
이 폴더가 없어도 나머지 기능은 전부 동작한다 — 이름 자리에 '(비공개)' 가 들어갈 뿐이다.

※ 구글 드라이브의 인수인계 자료에서 담당자 정보를 옮기고 싶으면,
   Claude 에게 "드라이브 인수인계 자료에서 contacts.yaml 채워줘" 라고 하면 된다.
   이 스크립트는 드라이브에 직접 접근하지 않는다 (자격증명을 두지 않기 위해).
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / "data" / "private"

FIELDS = [
    ("company", "ceo", "대표자명"),
    ("company", "biz_no", "사업자등록번호 (예: 000-00-00000)"),
    ("company", "address", "회사 주소"),
    ("company", "bank_account", "결제계좌 (예: ○○은행 000-000-000000)"),
    ("rep", "name", "담당자 이름"),
    ("rep", "title", "직급 (예: 대리)"),
    ("rep", "phone", "휴대폰"),
    ("rep", "email", "이메일"),
]


def copy_skeletons() -> list[Path]:
    made: list[Path] = []
    PRIVATE.mkdir(parents=True, exist_ok=True)
    for example in sorted(PRIVATE.glob("*.example.yaml")):
        target = PRIVATE / example.name.replace(".example", "")
        if target.exists():
            print(f"  이미 있음, 건너뜀: {target.name}")
            continue
        shutil.copy(example, target)
        made.append(target)
        print(f"  만듦: {target.name}")
    return made


def interactive() -> dict:
    print("회사·담당자 정보를 입력합니다. 비워 두면 '(비공개)' 로 남습니다.\n")
    data: dict = {"company": {}, "rep": {}}
    for section, key, label in FIELDS:
        try:
            value = input(f"  {label}: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n중단했습니다.")
            sys.exit(1)
        if value:
            data[section][key] = value
    return {k: v for k, v in data.items() if v}


def load_source(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        return json.loads(text)
    return yaml.safe_load(text) or {}


def write_company(data: dict) -> Path:
    PRIVATE.mkdir(parents=True, exist_ok=True)
    target = PRIVATE / "company.yaml"
    if target.exists():
        existing = yaml.safe_load(target.read_text(encoding="utf-8")) or {}
        for section, values in data.items():
            existing.setdefault(section, {}).update(values)
        data = existing
    target.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return target


def verify() -> None:
    sys.path.insert(0, str(ROOT / "src"))
    from sumex import config  # noqa: E402

    config.load.cache_clear()
    cfg = config.load()
    company = cfg.get("company", {})
    missing = [k for k, v in company.items() if v == config.MISSING]
    print("\n확인:")
    print(f"  상호   : {company.get('name')}")
    print(f"  대표자 : {company.get('ceo')}")
    print(f"  담당자 : {cfg.get('rep', {}).get('name')}")
    if missing:
        print(f"\n  아직 비어 있음: {', '.join(missing)}")
        print(f"  → {PRIVATE / 'company.yaml'} 를 직접 편집하세요.")


def main() -> int:
    p = argparse.ArgumentParser(description="data/private 생성")
    p.add_argument("--skeleton", action="store_true", help="예시 파일만 복사한다")
    p.add_argument("--from", dest="source", help="이미 정리한 yaml/json 에서 가져온다")
    args = p.parse_args()

    print(f"대상 폴더: {PRIVATE}")
    print("이 폴더는 .gitignore 로 제외되어 있습니다 — 커밋되지 않습니다.\n")

    if args.skeleton:
        made = copy_skeletons()
        if not made:
            print("\n새로 만든 파일이 없습니다.")
        else:
            print(f"\n{len(made)}개 파일을 만들었습니다. 내용을 채우세요.")
        return 0

    if args.source:
        source = Path(args.source)
        if not source.exists():
            print(f"파일이 없습니다: {source}", file=sys.stderr)
            return 1
        target = write_company(load_source(source))
        print(f"  만듦: {target.name}")
    else:
        data = interactive()
        if not data:
            print("\n입력된 값이 없습니다. --skeleton 으로 빈 파일만 만들 수도 있습니다.")
            return 0
        target = write_company(data)
        print(f"\n  만듦: {target.name}")

    copy_skeletons()
    verify()
    print("\n담당자 연락처는 data/private/contacts.yaml 에 채우세요.")
    print("구글 드라이브 인수인계 자료를 참고하려면 Claude 에게 요청하면 됩니다.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
