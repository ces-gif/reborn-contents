# SUMEX 대시보드

의존성 없는 로컬 웹 서버. 파이썬이 만든 `out/export.json` 을 읽어 브라우저로 보여준다.

```bash
node bin/sumex-dash.mjs                    # http://127.0.0.1:5173
node bin/sumex-dash.mjs --port 8080
node bin/sumex-dash.mjs --host 0.0.0.0     # 같은 와이파이의 휴대폰에서 보려면
node bin/sumex-dash.mjs --no-refresh       # 데이터 갱신 없이 기존 json 으로
```

시작할 때 `python3 -m sumex.cli export` 를 한 번 돌려 데이터를 최신화한다.
화면 우측 상단의 `↻ 갱신` 을 눌러도 된다.

## 페이지

| 경로 | 내용 |
|---|---|
| `/` | 오늘 브리핑 — 기한 지난 건, 오늘 일정, 동선 메모 |
| `/hospitals` | 거래처 23곳의 서류 종류·매수·도장·간납사 |
| `/h/<id>` | 납품 체크리스트. **인쇄용으로 만들었다** |
| `/month` | 이달 마감·반복 일정 |
| `/tasks` | 인수인계 후속조치 |
| `/audit` | 확인이 필요한 것 |
| `/case` | 케이스 커버 7축 |
| `/api/data` | 원본 JSON |

## 왜 노드인가

차 안에서 휴대폰으로 열어 볼 체크리스트가 필요하고, 브라우저 인쇄로 바로
뽑을 수 있어야 한다. 파이썬 CLI 는 서류를 만들고, 이쪽은 그걸 눈으로 보고 인쇄한다.

라이트/다크 모드를 따르고, 인쇄 시에는 헤더가 빠지고 카드가 페이지 중간에서
잘리지 않는다.

## 테스트

```bash
npm test        # 또는 node test/render.test.mjs
```

`out/export.json` 이 먼저 있어야 한다:
`PYTHONPATH=../../src python3 -m sumex.cli export`
