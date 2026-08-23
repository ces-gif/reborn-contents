# SUMEX 폴더에서 일할 때

의료기기 영업 자동화. 교육자료 · 서류작업 · 업무 스케줄 세 가지를 다룬다.
사용법은 [README.md](README.md), 도메인 지식은 [knowledge/](knowledge/).

## 반드시 지킬 것

### 1. 개인정보를 `data/` 나 `knowledge/` 에 쓰지 않는다

이 저장소는 **공개**다. 인수인계 자료에는 교수·간호사·구매 담당자의 실명과
휴대폰·이메일이 있다.

- 공개 파일에는 **역할**로만 적는다 — "수술방 팀장", "담당 주임", "수간호사"
- 실명·연락처·개인 평가는 `data/private/`(gitignore) 에만
- 사업자등록번호·결제계좌도 `data/private/company.yaml`
- 커밋 전에 확인: `grep -rnE '01[0-9]-[0-9]{3,4}-[0-9]{4}' data knowledge`

### 2. 데이터를 고치면 근거를 남긴다

`data/hospitals.yaml` 의 각 항목에는 `source: [A, B]` 가 붙어 있다.

- A = 전임자 인수인계서
- B = 거래처관리표 (현장 확인)

두 출처가 다르면 지우지 말고 `conflicts:` 로 남긴다. 현장에서 확정한 뒤에만
한쪽으로 정리하고, 그때 `updated` 날짜를 갱신한다.

확인이 안 된 것은 **모른다고 적는다.** `copies: null` 이면 코드가 "기본 4장
준비하고 현장에서 확정" 이라고 안내한다. 추측한 숫자를 넣으면 현장에서 사고가 난다.

### 3. 테스트에 사실이 들어 있다

`tests/` 는 인수인계 자료에서 확인된 값을 고정한다 — 서울척 3장,
서울적십자 5장, 세종스포츠 도장 3종, 8/14 다음 영업일 8/18.
데이터를 바꿔서 이게 깨지면 **근거를 남기고 테스트를 함께 고친다.**

```bash
export PYTHONPATH=src
python3 -m pytest tests -q
node tools/node/test/render.test.mjs      # export.json 이 먼저 필요하다
```

### 4. 서류는 체크리스트와 함께 낸다

`sumex doc` 은 서류를 만든 뒤 그 병원 체크리스트를 함께 출력한다.
사용자에게 전달할 때 **매수 · 도장 · 배부처**를 빠뜨리지 않는다.
매수를 틀리면 다시 출력하러 나가야 하고, 도장이 빠지면 다음 달 마감으로 밀린다.

## 구조

```
data/*.yaml        사실 (사람이 편집, 코드가 읽음)
src/sumex/         엔진. registry → checklist/docs/schedule → cli
tools/node/        대시보드. 파이썬이 만든 out/export.json 을 읽는다
knowledge/*.md     교육자료
.claude/skills/    저장소 루트에 sumex-* 6개
```

한국어 파일이다. 새로 쓰는 문서·주석·에러 메시지도 한국어로 쓴다.

## yaml 을 편집할 때

`data/tasks.yaml` 의 상태값은 `sumex task done T-004` 로 바꾼다.
직접 편집해도 되지만, 코드가 해당 줄만 치환하므로 주석과 배치가 보존된다.

새 거래처를 넣을 때 필요한 최소 항목:

```yaml
  - id: some-hospital        # 영문 소문자-하이픈. 품목·할일이 이 id 를 참조한다
    name: 정식 병원명
    short: 약칭               # 사용자가 실제로 부르는 이름
    region: 서울 광진
    priority: 상              # 최상 / 상 / 중
    consignment: 간납사명      # 직거래면 null
    doc_type: 거래명세서       # 또는 선납서 / 가납서
    doc:
      copies: 4
      stamp: false
      distribution:           # 합계가 copies 와 같아야 한다 (테스트가 검사)
        - { to: 수술방, copies: 1 }
        - { to: 총무과, copies: 2 }
        - { to: 자사, copies: 1 }
    source: [A]
```

## 하지 말 것

- 확인 안 된 서류 규칙을 추측해서 채우기
- 실명·연락처를 공개 파일에 쓰기
- 회사 실양식 xlsx 를 커밋하기 (`templates/` 는 gitignore)
- 교육자료를 외부에 공개하기 (사내 대외비)
