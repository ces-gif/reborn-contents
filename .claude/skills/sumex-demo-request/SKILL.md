---
name: sumex-demo-request
description: "[SUMEX] 스트라이커 데모인수증(KQF-OPC-009-F Korea Demo Receipt Form) 작성 + 데모 전 점검표 + 회수 일정 등록. '데모 신청서', '데모인수증', '데모 나가는데', '장비 데모 서류' 요청 시 사용."
---

# SUMEX 데모인수증

데모 장비는 **한국스트라이커 자산**이다. 파손·분실 시 우리가 배상 책임을 진다.
서류를 대충 쓰면 안 되는 이유가 하나 더 있다 — 기재 사항이 의료기기법에 따라
**지출보고서에 포함되어 공개되거나 심평원 등에 제출될 수 있다.**

## 절차

### 1. 요청 내용을 yaml 로 정리한다

```yaml
# demo.yaml
hospital: 노원을지            # data/hospitals.yaml 의 id 또는 약칭
dept: 정형외과
doctor: 홍길동 교수님          # 서류에만 들어간다. 저장소 파일에 남기지 않는다
institution_no: "11101016"    # 요양기관번호
address: "서울특별시 노원구 한글비석로 68"
release_date: 2026-09-01      # 회수일은 기본 +30일
ship_method: 용달
items:
  - model: 1788010000i
    name: 1788 CAMERA CONTROL UNIT (CCU)
    qty: 1
    serial: ""                # 제조번호(Serial/Lot) — 출고 시 채운다
    license_no: 수신23-2838   # 허가번호
    category: 의료영상 처리장치
    maker: "미국, Stryker Endoscopy"
    is_device: O
```

허가번호를 모르는 소모품·액세서리는 `license_no: N/A`, `is_device: X`.

### 2. 만든다

```bash
cd SUMEX && export PYTHONPATH=src
python3 -m sumex.cli demo demo.yaml
```

- `templates/데모인수증.xlsx` (회사 배포 실양식)이 있으면 그 파일의 값만 채운다
- 없으면 같은 항목을 가진 작업용 시트를 만든다
- **빈 칸이 있으면 경고가 나온다** — 요양기관번호, 의사명, Serial/Lot,
  의료기기인데 허가번호가 비어 있는 품목

### 3. 데모 전 점검을 전달한다

명령이 함께 출력한다. 특히 이 두 가지:

- **백업 카메라 헤드와 광케이블 반드시 동행**
- 데모 종료 후 **24시간 내** 피드백 정리하여 서면 회신

### 4. 회수 일정을 캘린더에 등록한다

기본 회수일 = 출고일 + 30일. 등록하지 않으면 잊는다.
`data/tasks.yaml` 에 후속조치로 추가하거나 Google Calendar 에 직접 넣는다.

회수 주소: 서울 송파구 송파대로 55 A동 603-2호 스트라이커 CR팀

## 데모 요청 라인

- **데모 진행 요청·일정 조율** → 송파 Commercial Reporting Team
- **장비 고장·수리** → 강남 아셈타워 Technical Service

두 거점이 다르다. 용건에 따라 가는 곳이 다르다.
담당자 연락처는 `data/private/contacts.yaml`(git 제외)에서 본다.

## 놓치기 쉬운 약관

1. **출고일 포함 3일 안에** 제품·수량을 확인해야 한다. 3일 지나면 인수 완료 처리
2. 대여 물품은 평가용으로만, **요청 병원 외에는 사용할 수 없다**
3. 표시·기재사항을 제거하지 말 것
4. **환자에게 사용해도 그 비용을 별도로 청구할 수 없다**

## 개인정보

의사명·담당자 연락처는 생성된 xlsx 에만 들어간다.
`demo.yaml` 을 저장소에 커밋하지 않는다 (`out/` 또는 `data/private/` 에 둔다).
