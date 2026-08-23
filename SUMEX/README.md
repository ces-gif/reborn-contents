# SUMEX 영업 자동화

의료기기 영업 담당자의 **교육자료 · 서류작업 · 업무 스케줄** 세 가지를 자동화한다.

전임자 인수인계 자료와 사내 교육자료를 학습해서, 병원마다 다른 납품 서류 규칙과
월 마감 일정을 코드가 알고 있게 만들었다. 서류를 몇 장 뽑아야 하는지, 도장을
어디에 찍는지, 이번 달 마감이 언제인지를 매번 기억해내지 않아도 된다.

```
교육자료   knowledge/         90일 온보딩 커리큘럼 · 강의안 · 자가점검
서류작업   sumex doc/quote/demo   거래명세서·가납서·선납서·견적서·데모인수증 xlsx
업무일정   sumex today/week/month  마감 · 방문 · 후속조치 · 구글 캘린더
```

---

## 빠른 시작

```bash
cd SUMEX
pip install -r requirements.txt
export PYTHONPATH=src

python3 -m sumex.cli today                  # 오늘 브리핑
python3 -m sumex.cli hospitals              # 거래처 23곳의 서류 규칙 한눈에
python3 -m sumex.cli checklist 세종스포츠     # 방문 전 체크리스트 (출력해서 차량 비치)
```

브라우저로 보려면:

```bash
node tools/node/bin/sumex-dash.mjs          # http://localhost:5173
```

휴대폰으로 열어 볼 수 있고, 그대로 인쇄하면 체크리스트가 된다.

---

## 이 도구가 아는 것

### 병원마다 다른 서류 규칙

| | |
|---|---|
| 매수 | 1장(신촌세브란스) ~ **5장(서울적십자)**. 기본은 4장인데 예외가 절반 |
| 도장 | 세종스포츠는 **3종**(수술실·재무팀·심사팀). 하나 빠지면 반려. 서울점프는 불필요 |
| 제출처 | 서울척은 수술실 14층 + 총무팀 B2. 세종스포츠 총무·심사는 **본원이 아니라 버거킹 옆 건물 3층** |
| 시간 | 분당서울대는 09:00~11:00 / 13:00~16:00. 냉장·냉동은 14:00 이전. 놓치면 그날 납품 불가 |
| 마감 | 청담리온 매월 1~3일. 노원을지는 **알림이 안 와서** 매월 1일 사이트를 직접 봐야 한다 |
| 하드룰 | 고대병원은 거래명세서 수량 총합 == 선납서 수량 총합이어야 마감이 통과된다 |

전부 `data/hospitals.yaml` 에 들어 있고, 고치면 체크리스트·방문계획·대시보드가
함께 바뀐다.

### 아직 모르는 것도 안다

```bash
python3 -m sumex.cli audit
```

인수인계 자료 두 부가 서로 다르게 말하거나 아예 비어 있는 항목 17건을 띄운다.
확정할 때마다 yaml 을 고치면 목록이 줄어든다.

---

## 명령

| 명령 | 하는 일 |
|---|---|
| `sumex today` | 오늘 브리핑 — 기한 지난 건, 마감 경고, 연휴 경고, 회신 지연 수리 건 |
| `sumex week` | 이번 주 계획 (요일별, 휴무 표시, 동선 메모) |
| `sumex month 2026-09` | 그 달 병원별 마감 일정을 실제 날짜로 |
| `sumex checklist 세종스포츠` | 납품 체크리스트 (`--md`, `-o` 로 파일 저장) |
| `sumex visit A B C` | 방문 순서 · 시간 제약 · **총 준비할 서류 매수** |
| `sumex hospitals` / `hospital <이름>` | 거래처 목록 / 상세 |
| `sumex doc <병원> --items "..."` | 거래명세서·가납서·선납서 xlsx |
| `sumex quote <병원> --spec q.yaml` | 견적서 xlsx |
| `sumex demo demo.yaml` | 데모인수증 + 데모 전 점검표 |
| `sumex task list\|done\|doing\|drop` | 인수인계 후속조치 관리 |
| `sumex repair open\|list\|update` | 장비 수리 접수 대장 |
| `sumex ics --month 2026-09` | 구글 캘린더용 .ics |
| `sumex product ICONIX` | 품목 정보 |
| `sumex casecover <병원>` | 관절경 케이스 커버 7축 점검표 |
| `sumex audit` | 데이터 결손·불일치 |
| `sumex export` | 대시보드용 JSON |

거래처는 약칭으로 찾는다: `세종스포츠` `서울척` `무척나은` `적십자` `고대`

### 예시

```bash
# 거래명세서 — 만들면 그 병원 체크리스트가 함께 나온다
python3 -m sumex.cli doc 세종스포츠 \
  --items "ICONIX 1.7T x 3 @ 320000; ICONIX 1 NEEDLES x 2 @ 33350" \
  --suffix 수술방

# 품목이 많으면 CSV (열: 코드,상품명,포장단위,수량,단가)
python3 -m sumex.cli doc 서울점프 --items items.csv

# 하루에 네 곳 도는 날
python3 -m sumex.cli visit 세종스포츠 무척나은 서울점프 구리센트럴
#   → 시간 창이 좁은 곳을 앞에, 서울권 밖을 뒤에 자동 배치
#   → 총 준비할 서류: 15장

# 수리 접수 (본사에 함께 물어야 할 3가지가 같이 나온다)
python3 -m sumex.cli repair open 서울적십자 "1788 CCU" "전원이 간헐적으로 꺼짐"
```

---

## 교육자료

`knowledge/` 가 신입 영업사원 온보딩 커리큘럼 전체다.

| 문서 | 내용 |
|---|---|
| [00 온보딩 로드맵](knowledge/00-온보딩-로드맵.md) | 90일 계획, 읽는 순서, 매일·매주 루틴 |
| [10 산업 기초](knowledge/10-산업-기초.md) | 산업 지도, 재료·고정 원리, 시장·경쟁 5사, 인허가·급여 |
| [20 어깨 해부학](knowledge/20-해부학-어깨.md) | 50분 강의안. 4관절 → 질환 → 수술 → 제품 매핑 |
| [30 제품 심층](knowledge/30-제품-심층.md) | 1788 · System 9 · CORE 2 · Zip · ICONIX · T7 |
| [40 서류 업무 총람](knowledge/40-서류-업무-총람.md) | **첫 주에 반드시.** 병원별 서류 규칙 전부 |
| [50 영업 플레이북](knowledge/50-영업-플레이북.md) | 의사결정 구조, 경쟁 대응 스크립트, 컴플라이언스 |
| [60 트러블슈팅](knowledge/60-트러블슈팅.md) | 에러코드, 증상 추적, 클레임 SOP 7단계 |
| [70 용어집](knowledge/70-용어집.md) · [80 자가점검](knowledge/80-자가점검.md) | 용어, 30/60/90일 문제은행 |

새 강의안을 만들 때는 `sumex-edu-material` 스킬을 쓴다.

---

## Claude 스킬

저장소 루트 `.claude/skills/` 에 6개가 들어 있다. Claude Code 에서 자동으로 잡힌다.

| 스킬 | 언제 |
|---|---|
| `sumex-delivery-doc` | "거래명세서 만들어줘", "가납서", "견적서" |
| `sumex-visit-brief` | "오늘 어디 가지", "방문 계획", "체크리스트 뽑아줘" |
| `sumex-schedule` | "오늘 뭐 해야 해", "이달 마감", "캘린더에 넣어줘" |
| `sumex-demo-request` | "데모 신청서", "데모 나가는데" |
| `sumex-edu-material` | "신입 교육자료 만들어줘", "제품 강의안" |
| `sumex-repair-ticket` | "장비 고장났대", "E05 떴는데", "수리 어떻게 됐지" |

---

## 개인정보 — 왜 두 겹으로 나눴나

이 저장소는 **공개**다. 인수인계 자료에는 교수·간호사·구매 담당자의 실명과
휴대폰·이메일이 들어 있어서, 그대로 올리면 안 된다.

```
data/                    ← 공개. 병원명 · 서류 규칙 · 마감일 · 품목
  hospitals.yaml            사람 이름 대신 역할로만 적는다 ("수술방 팀장")
  products.yaml
  doc_types.yaml
  tasks.yaml

data/private/            ← .gitignore. 절대 커밋되지 않는다
  company.yaml              사업자등록번호 · 대표자 · 주소 · 결제계좌
  contacts.yaml             담당자 실명 · 휴대폰 · 이메일
  accounts.yaml             계정별 매출 · 할인율 · 민감 메모
  repairs.json              수리 접수 대장
```

`data/private/` 가 없어도 전부 동작한다. 이름 자리에 `(비공개)` 가 들어갈 뿐이다.

```bash
python3 scripts/bootstrap_private_data.py            # 대화식
python3 scripts/bootstrap_private_data.py --skeleton # 빈 파일만
```

담당자 연락처는 구글 드라이브 인수인계 자료에 있다. Claude 에게
"드라이브 인수인계 자료에서 contacts.yaml 채워줘" 라고 하면 된다.

**회사 실양식 xlsx**(`templates/*.xlsx`)도 로고·계좌가 들어 있어 git 에서 제외했다.
없으면 코드가 같은 좌표로 새로 그린다. 실양식을 `templates/거래명세서.xlsx` 로
넣어두면 그 파일의 값만 채워서 서식이 그대로 유지된다.

---

## 구조

```
SUMEX/
├── knowledge/          교육자료 (마크다운 8편)
├── data/               거래처·품목·서류종류·할일 (yaml)
│   └── private/        개인정보 (git 제외)
├── src/sumex/          파이썬 엔진
│   ├── registry.py       yaml → 조회 가능한 객체
│   ├── checklist.py      납품 체크리스트 + 데이터 결손 점검
│   ├── docs.py           거래명세서·가납서·선납서·견적서 xlsx
│   ├── demo_form.py      데모인수증 (KQF-OPC-009-F)
│   ├── schedule.py       마감·반복·방문 계산 + ICS
│   ├── tasks.py          할 일 상태 (yaml 주석 보존하며 갱신)
│   ├── repair.py         수리 접수 대장
│   ├── brief.py          일일 브리핑
│   └── cli.py
├── tools/node/         대시보드 (의존성 없는 로컬 웹서버)
├── templates/          회사 실양식 xlsx (git 제외)
├── tests/              pytest 63건
└── out/                생성물 (git 제외)
```

## 테스트

```bash
python3 -m pytest tests -q                   # 63건
node tools/node/test/render.test.mjs         # 대시보드 렌더링
```

테스트에는 인수인계 자료에서 확인된 사실이 들어 있다 — 서울척은 3장,
서울적십자는 5장, 세종스포츠 도장 3종, 8/14 다음 영업일은 8/18.
데이터를 고칠 때 이 값이 깨지면 근거를 남기고 테스트를 함께 고친다.

---

## Hugging Face — 기계가 읽는 사본

깃허브는 사람이 읽고 고치는 곳이고, Hugging Face 는 기계가 읽는 곳으로 쓴다.
나중에 이 지식베이스로 RAG 를 붙이거나 신입 교육용 QA 를 만들 때 필요하다.

```bash
pip install huggingface_hub
python3 scripts/publish_hf.py --check        # 올리기 전 안전 점검만 (토큰 불필요)

export HF_TOKEN=hf_xxxxx                     # write 권한
python3 scripts/publish_hf.py                # 비공개 데이터셋으로 발행
```

올라가는 것: `knowledge/*.md` 8편 + `data/*.yaml` + 검색용 `sumex_kb.jsonl`
(교육자료를 섹션 단위로, 거래처·품목을 항목 단위로 쪼갠 150행).

**기본값이 비공개다.** 사내 교육용 대외비이고 거래처 이름이 들어 있어서,
`--public` 을 명시하고 확인 입력을 해야만 공개로 만들어진다.
발행 전에 연락처·이메일이 섞였는지 스스로 검사하고, 하나라도 걸리면 중단한다.
`data/private/`, `templates/`, `out/` 은 어떤 경우에도 올라가지 않는다.

> 토큰이 필요한 이유: Claude 의 Hugging Face 연결은 읽기 전용이라
> 저장소 생성·업로드를 대신 해줄 수 없다. 한 번만 실행하면 된다.

---

## 자료 출처

- 전임자 인수인계서 (거래처별 납품 프로세스·특이사항)
- SUMEX 거래처관리표 인수인계 (현장 확인, 서류 규칙·동선·후속조치 37건)
- SUMEX 의료기기 산업 학습보고서 Vol.1
- SUMEX 주력 품목 심층 매뉴얼 Vol.2
- 어깨복합체 해부학 신입강의
- 실제 거래명세서·견적서·데모인수증 (양식 좌표)
- Stryker 서비스 절차서 TSI10398 / TSI10413

교육자료는 **사내 교육용 대외비**다. 외부 공유·SNS 게시를 하지 않는다.
제품 사양·품번·가격은 개정되므로 견적·발주 전에 최신 자료로 재확인한다.
