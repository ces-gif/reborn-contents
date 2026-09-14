# -*- coding: utf-8 -*-
"""2026 바이브 코딩 특강·경진대회 원가계산서(견적서).
2025년 원가계산서(3시트: 총괄표 / 인건비 / 일반경비)의 구성을 그대로 따른다."""
import sys
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter

TITLE = '2026 대학생과 고양시민의 AI 기술 창업을 위한 바이브 코딩 특강 및 경진대회'
NAVY, HEAD, GRAYF = '17365D', 'D9E2F3', 'F2F2F2'

thin = Side(style='thin', color='9AA5B1')
med  = Side(style='medium', color=NAVY)
BOX  = Border(left=thin, right=thin, top=thin, bottom=thin)
KO   = '맑은 고딕'

def F(sz=10, b=False, color='000000'):
    return Font(name=KO, size=sz, bold=b, color=color)

def put(ws, cell, val, *, sz=10, b=False, color='000000', fill=None,
        align='left', fmt=None, border=True, wrap=False):
    c = ws[cell]
    c.value = val
    c.font = F(sz, b, color)
    c.alignment = Alignment(horizontal=align, vertical='center', wrap_text=wrap)
    if fill:
        c.fill = PatternFill('solid', fgColor=fill)
    if border:
        c.border = BOX
    if fmt:
        c.number_format = fmt
    return c

def widths(ws, spec):
    for col, w in spec.items():
        ws.column_dimensions[col].width = w

WON = '#,##0'
PCT = '0.0%'

wb = Workbook()

# ─────────────────────────────────────────────────────────── 총괄표
ws = wb.active
ws.title = '총괄표'
widths(ws, {'A': 30, 'B': 16, 'C': 10, 'D': 8, 'E': 62})
ws.merge_cells('A1:E1')
put(ws, 'A1', f'{TITLE} 원가계산서', sz=13, b=True, align='center', border=False)
ws.row_dimensions[1].height = 30
put(ws, 'E2', '단위 : 원', align='right', border=False)

for col, head in zip('ABCDE', ['구 분', '금 액', '구성비', '비 고', '산출내용']):
    put(ws, f'{col}3', head, b=True, fill=HEAD, align='center')

인건비, 일반경비 = 3_250_000, 5_300_000
직접비 = 인건비 + 일반경비
총원가 = 9_090_909
일반관리비 = 256_500
이윤 = 총원가 - 직접비 - 일반관리비
부가세 = 909_091
합계 = 총원가 + 부가세
assert 합계 == 10_000_000, 합계

rows = [
    ('인건비(전문가 수당)', 인건비, '(1)', '창업 특강 강사료, 1:1 멘토링비, 예선 서류 평가료, 결승 심사수당'),
    ('일반경비(시상·실습·홍보·운영)', 일반경비, '(2)', '시상금 및 부상, AI 코딩 도구 이용료, 홍보·인쇄비, 행사 운영비'),
    ('일반관리비', 일반관리비, '(3)', '(3) = {(1) + (2)} × 3.0%   지방계약법 시행규칙 제8조제1항제14호(8% 이내)'),
    ('이윤', 이윤, '(4)', '(4) = {(1) + (2) + (3)} × 3.23%   지방계약법 시행규칙 제8조제2항제4호(10% 이내)'),
    ('총원가', 총원가, '(5)', '(5) = (1) + (2) + (3) + (4)'),
]
r = 4
for name, amt, tag, note in rows:
    bold = name == '총원가'
    put(ws, f'A{r}', name, b=bold, fill=GRAYF if bold else None)
    put(ws, f'B{r}', amt, align='right', fmt=WON, b=bold, fill=GRAYF if bold else None)
    put(ws, f'C{r}', amt / 총원가, align='center', fmt=PCT, b=bold, fill=GRAYF if bold else None)
    put(ws, f'D{r}', tag, align='center', b=bold, fill=GRAYF if bold else None)
    put(ws, f'E{r}', note, sz=9, b=bold, fill=GRAYF if bold else None, wrap=True)
    r += 1

put(ws, f'A{r}', '부가가치세', b=True)
put(ws, f'B{r}', 부가세, align='right', fmt=WON, b=True)
put(ws, f'C{r}', '-', align='center', b=True)
put(ws, f'D{r}', '(6)', align='center', b=True)
put(ws, f'E{r}', '(6) = (5) × 10%   총원가의 10%', sz=9, b=True)
r += 1
put(ws, f'A{r}', '합 계 금 액', b=True, color='FFFFFF', fill=NAVY, align='center')
put(ws, f'B{r}', 합계, align='right', fmt=WON, b=True, color='FFFFFF', fill=NAVY)
put(ws, f'C{r}', '', fill=NAVY)
put(ws, f'D{r}', '(7)', align='center', b=True, color='FFFFFF', fill=NAVY)
put(ws, f'E{r}', '(7) = (5) + (6)   금 일천만원정 (VAT 포함)', sz=9, b=True, color='FFFFFF', fill=NAVY)
note_r = r + 2
ws.merge_cells(f'A{note_r}:E{note_r}')
put(ws, f'A{note_r}',
    '※ 창업 특강 강사료는 발주처 「강사수당 지급기준」 나급을 적용하였다(강사수당 지급기준 시트 참조).  '
    '※ 2025년 원가계산서는 일반관리비 6% · 이윤 10%를 적용하였으나, 본 과업은 시상금(2,500,000원)과 '
    'AI 코딩 도구 이용료(1,500,000원) 등 실비성 지출 비중이 커 총액 10,000,000원 안에서는 위 요율을 '
    '적용할 수 없다. 2025년과 동일한 요율을 적용할 경우 필요한 총액은 11,036,880원이다. (참고 시트)',
    sz=9, wrap=True, border=False)
ws.row_dimensions[note_r].height = 42

# ─────────────────────────────────────────────── 인건비(전문가)
ws2 = wb.create_sheet('인건비(전문가)')
widths(ws2, {'A': 12, 'B': 30, 'C': 12, 'D': 8, 'E': 8, 'F': 14, 'G': 34})
ws2.merge_cells('A1:G1')
put(ws2, 'A1', '인건비 - 전문가 수당', sz=12, b=True, align='center', border=False)
put(ws2, 'G2', '단위 : 원', align='right', border=False)
for col, head in zip('ABCDEFG', ['구분', '세부항목', '단가', '인원', '회', '금액', '비고']):
    put(ws2, f'{col}3', head, b=True, fill=HEAD, align='center')

인건 = [
    ('강사',     '창업 특강 강사료 (나급)', 250_000,  1, 1, '9.28(월) 특강 2시간 — 최초 1h 170,000 + 초과 1h 80,000'),
    ('멘토',     '1:1 창업 멘토링비',            150_000, 10, 1, '10.8(목) 멘토링 대상 10개 팀'),
    ('심사위원', '예선 서류 평가료',             150_000,  2, 1, '10.15(목) 내/외부 위원 2인'),
    ('심사위원', '결승 심사수당',                400_000,  3, 1, '10.22(목) 현직 VC 3인'),
]
r = 4
for gu, item, unit, n, cnt, note in 인건:
    put(ws2, f'A{r}', gu, align='center')
    put(ws2, f'B{r}', item)
    put(ws2, f'C{r}', unit, align='right', fmt=WON)
    put(ws2, f'D{r}', n, align='center')
    put(ws2, f'E{r}', cnt, align='center')
    put(ws2, f'F{r}', f'=C{r}*D{r}*E{r}', align='right', fmt=WON)
    put(ws2, f'G{r}', note, sz=9)
    r += 1
put(ws2, f'A{r}', '합계', b=True, fill=GRAYF, align='center')
for col in 'BCDE':
    put(ws2, f'{col}{r}', '', fill=GRAYF)
put(ws2, f'F{r}', f'=SUM(F4:F{r-1})', align='right', fmt=WON, b=True, fill=GRAYF)
put(ws2, f'G{r}', '', fill=GRAYF)

# ─────────────────────────────────────────────── 일반경비
ws3 = wb.create_sheet('일반경비')
widths(ws3, {'A': 12, 'B': 32, 'C': 12, 'D': 10, 'E': 8, 'F': 14, 'G': 34})
ws3.merge_cells('A1:G1')
put(ws3, 'A1', '일반경비 - 시상·실습·홍보·운영', sz=12, b=True, align='center', border=False)
put(ws3, 'G2', '단위 : 원', align='right', border=False)
for col, head in zip('ABCDEFG', ['구분', '항목', '단가', '수량', '단위', '금액', '비고']):
    put(ws3, f'{col}3', head, b=True, fill=HEAD, align='center')

일반 = [
    ('시상', '대상 (1등)',                 1_000_000,  1, '팀', ''),
    ('시상', '최우수상 (2등)',               500_000,  1, '팀', ''),
    ('시상', '우수상 (3등)',                 300_000,  1, '팀', ''),
    ('시상', '장려상 (4~10등) 부상',          100_000,  7, '팀', '100,000원 상당 상품'),
    ('실습', 'AI 코딩 도구 이용료',            50_000, 30, '명', '멘토링 대상 10개 팀 · 팀당 3인 기준'),
    ('홍보', '포스터 제작·출력',               13_000, 20, '부', ''),
    ('홍보', '현수막·X배너',                  100_000,  2, '개', ''),
    ('인쇄', '결승 발표 심사 자료집',           12_000, 15, '부', '심사위원·운영진용'),
    ('인쇄', '상장 및 케이스',                  6_000, 10, '개', ''),
    ('운영', '특강 다과',                       3_000, 60, '명', '9.28 특강 정원 60명 기준'),
    ('운영', '결승 식대(도시락)',              12_000, 25, '명', '10.22 참가팀·심사위원·스태프'),
    ('운영', '소모품 및 현장 운영',            120_000,  1, '식', '명찰, 문구류, 현장 진행 물품'),
]
r = 4
for gu, item, unit, qty, u, note in 일반:
    put(ws3, f'A{r}', gu, align='center')
    put(ws3, f'B{r}', item)
    put(ws3, f'C{r}', unit, align='right', fmt=WON)
    put(ws3, f'D{r}', qty, align='center')
    put(ws3, f'E{r}', u, align='center')
    put(ws3, f'F{r}', f'=C{r}*D{r}', align='right', fmt=WON)
    put(ws3, f'G{r}', note, sz=9)
    r += 1
put(ws3, f'A{r}', '합계', b=True, fill=GRAYF, align='center')
for col in 'BCDE':
    put(ws3, f'{col}{r}', '', fill=GRAYF)
put(ws3, f'F{r}', f'=SUM(F4:F{r-1})', align='right', fmt=WON, b=True, fill=GRAYF)
put(ws3, f'G{r}', '', fill=GRAYF)

# ─────────────────────────────────────────────── 참고(증액 검토)
ws4 = wb.create_sheet('참고(증액 검토)')
widths(ws4, {'A': 30, 'B': 16, 'C': 16, 'D': 46})
ws4.merge_cells('A1:D1')
put(ws4, 'A1', '참고 — 2025년과 동일한 요율(일반관리비 6% · 이윤 10%)을 적용할 경우',
    sz=12, b=True, align='center', border=False)
for col, head in zip('ABCD', ['구 분', '본 견적 (10,000,000원)', '2025년 요율 적용 시', '비 고']):
    put(ws4, f'{col}3', head, b=True, fill=HEAD, align='center')

관리6 = round(직접비 * 0.06)
이윤10 = round((직접비 + 관리6) * 0.10)
총원가2 = 직접비 + 관리6 + 이윤10
부가세2 = round(총원가2 * 0.10)
합계2 = 총원가2 + 부가세2
comp = [
    ('인건비(전문가 수당)', 인건비, 인건비, '동일'),
    ('일반경비',           일반경비, 일반경비, '동일'),
    ('일반관리비',         일반관리비, 관리6, '3.0% → 6.0%'),
    ('이윤',               이윤, 이윤10, '3.23% → 10.0%'),
    ('총원가',             총원가, 총원가2, ''),
    ('부가가치세',         부가세, 부가세2, ''),
]
r = 4
for name, a, b_, note in comp:
    bold = name == '총원가'
    put(ws4, f'A{r}', name, b=bold, fill=GRAYF if bold else None)
    put(ws4, f'B{r}', a, align='right', fmt=WON, b=bold, fill=GRAYF if bold else None)
    put(ws4, f'C{r}', b_, align='right', fmt=WON, b=bold, fill=GRAYF if bold else None)
    put(ws4, f'D{r}', note, sz=9, b=bold, fill=GRAYF if bold else None)
    r += 1
put(ws4, f'A{r}', '합 계 금 액', b=True, color='FFFFFF', fill=NAVY, align='center')
put(ws4, f'B{r}', 합계, align='right', fmt=WON, b=True, color='FFFFFF', fill=NAVY)
put(ws4, f'C{r}', 합계2, align='right', fmt=WON, b=True, color='FFFFFF', fill=NAVY)
put(ws4, f'D{r}', f'차액 {합계2 - 합계:,}원', sz=9, b=True, color='FFFFFF', fill=NAVY)
r += 2
ws4.merge_cells(f'A{r}:D{r}')
put(ws4, f'A{r}',
    '※ 2025년 예산은 13,000,000원이었고 시상금이 없었다. 2026년은 총액이 10,000,000원으로 줄어든 대신 '
    '경진대회와 시상금 2,500,000원이 새로 들어갔다. 요율을 지키려면 총액 11,036,880원(천원 단위 절상 시 '
    '11,040,000원)이 필요하다.', sz=9, wrap=True, border=False)
ws4.row_dimensions[r].height = 40

# ─────────────────────────────────────────── 강사수당 지급기준 (발주처 기준표)
ws5 = wb.create_sheet('강사수당 지급기준')
widths(ws5, {'A': 10, 'B': 54, 'C': 13, 'D': 13, 'E': 17})
ws5.merge_cells('A1:E1')
put(ws5, 'A1', '강사수당 지급기준 — 가. 일반강의 강사수당', sz=12, b=True, align='center', border=False)
put(ws5, 'E2', '단위 : 원', align='right', border=False)
for col, head in zip('ABCDE', ['등급', '적용대상 (일반)', '최초 1시간', '초과 매시간', '2시간 환산']):
    put(ws5, f'{col}3', head, b=True, fill=HEAD, align='center')

등급표 = [
    ('특1급', '전직 장관(급) 및 광역자치단체장, 전직 국회의원, 전직 한국은행장, 전직 대학의 총장(이사장), 대기업 총수(부회장 이상)', 400_000, 300_000),
    ('특2급', '전직 차관(급) 및 기초자치단체장, 전직 공직유관단체장, 전직 전문대학 등의 총장(이사장), 대기업 임원·중견기업 대표', 300_000, 200_000),
    ('가급', '전직 4급 이상 공무원, 전직 대학의 교수(조교수 이상), 대기업 부장(급)·중견기업 임원·중소기업 대표, 전문직 3년 이상, 박사학위 취득 후 해당분야 3년 이상 실무경력자', 280_000, 120_000),
    ('나급', '전직 5급(상당) 공무원, 중견기업 부장(급)·중소기업 임원, 국가전문자격증 보유 3년 이상 실무경력자, 기타 전문자격 보유 5년 이상 실무경력자', 170_000, 80_000),
    ('다급', '전직 6급 이하 공무원, 외국어·전산 등 강사, 체육·레크리에이션 등 취미·소양 강사(해당분야 3년 이상 강의경력)', 100_000, 50_000),
    ('라급', '체육, 레크리에이션 등 취미·소양 강사', 80_000, 40_000),
    ('마급', '각종 교육운영(실기실습 등) 보조자', 60_000, 30_000),
]
r = 4
for 급, 대상, 최초, 초과 in 등급표:
    선택 = 급 == '나급'
    fill = 'FFF2CC' if 선택 else ('F4F7FB' if r % 2 == 0 else None)
    put(ws5, f'A{r}', 급, b=True, align='center', fill=fill)
    put(ws5, f'B{r}', 대상, sz=9, wrap=True, fill=fill)
    put(ws5, f'C{r}', 최초, align='right', fmt=WON, fill=fill)
    put(ws5, f'D{r}', 초과, align='right', fmt=WON, fill=fill)
    put(ws5, f'E{r}', f'=C{r}+D{r}', align='right', fmt=WON, b=선택, fill=fill)
    ws5.row_dimensions[r].height = 36
    r += 1
r += 1
ws5.merge_cells(f'A{r}:E{r}')
put(ws5, f'A{r}',
    '※ 본 과업의 창업 특강(2시간)은 나급을 적용하여 170,000 + 80,000 = 250,000원으로 계상하였다. '
    '2025년 원가계산서도 동일하게 나급을 적용하였다 (4시간 17+8+8+8 = 410,000원, 3시간 17+8+8 = 330,000원). '
    '강사가 중소기업 대표 등 가급 요건에 해당하면 2시간 400,000원까지 적용할 수 있다.',
    sz=9, wrap=True, border=False)
ws5.row_dimensions[r].height = 46

for s in wb.worksheets:
    s.sheet_view.showGridLines = False
    s.freeze_panes = 'A4'

wb.save(sys.argv[1])
print('wrote', sys.argv[1])
