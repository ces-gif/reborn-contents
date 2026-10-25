#!/usr/bin/env python3
"""경영컨설팅 견적서 템플릿 — 수식 연동 (단가표 → 견적서).

단가표에서 품목을 고르면 단위·단가가 자동으로 들어오고,
수량만 적으면 공급가액·소계·부가세·합계·한글금액까지 전부 계산된다.
"""
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

OUT = Path(__file__).resolve().parent / '견적서_템플릿_경영컨설팅.xlsx'

F = '맑은 고딕'
NAVY, HEAD, SOFT, LINE = '17365D', 'DCE6F1', 'F4F7FC', 'B4BDC7'
WARN, DIM = 'C4372F', '767676'
thin = Side(style='thin', color=LINE)
med = Side(style='medium', color=NAVY)
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
MONEY = '#,##0'
DATE = 'yyyy"."mm"."dd'

# 견적 항목 행 범위
R0, R1 = 24, 41          # 품목 입력 시작/끝 행
NROW = R1 - R0 + 1

wb = Workbook()

# ══════════════════════════════════════════════════ 단가표
pr = wb.create_sheet('단가표')
PRICES = [
    ('정부지원사업', '사업계획서 작성 대행', '건', 3000000),
    ('정부지원사업', '지원사업 발굴 · 매칭 자문', '건', 1000000),
    ('정부지원사업', '선정 후 사후관리 · 정산 지원', '건', 1500000),
    ('인증 · 등록',  '벤처기업 확인 컨설팅', '건', 2000000),
    ('인증 · 등록',  '기업부설연구소 설립 컨설팅', '건', 2500000),
    ('인증 · 등록',  '이노비즈 · 메인비즈 컨설팅', '건', 3000000),
    ('창업 지원',    '법인 설립 대행', '건', 500000),
    ('창업 지원',    '사업 타당성 분석', '건', 4000000),
    ('창업 지원',    '비즈니스 모델 설계 워크숍', '회', 1500000),
    ('교육 · 특강',  '창업 교육 프로그램 운영', '회', 2000000),
    ('교육 · 특강',  '전문가 특강', '시간', 300000),
    ('교육 · 특강',  '1:1 멘토링', '회', 150000),
    ('IR · 투자',    'IR 자료(피치덱) 제작', '건', 3000000),
    ('IR · 투자',    'IR 피칭 코칭', '회', 500000),
    ('IR · 투자',    '투자 유치 자문', '건', 5000000),
    ('경영 자문',    '경영 진단 · 조직 진단', '건', 5000000),
    ('경영 자문',    '월 정기 자문 (리테이너)', '월', 1500000),
    ('기타',        '기타 (직접 입력)', '식', 0),
]
pr['A1'] = '서비스 단가표'
pr['A1'].font = Font(name=F, bold=True, size=14, color=NAVY)
pr['A2'] = '※ 아래 단가는 예시입니다. 반드시 회사 기준 단가로 교체해 주세요.'
pr['A2'].font = Font(name=F, size=10, color=WARN)
for i, h in enumerate(['구분', '품목 · 서비스', '단위', '단가', '비고'], 1):
    c = pr.cell(row=4, column=i, value=h)
    c.font = Font(name=F, bold=True, size=11, color='FFFFFF')
    c.fill = PatternFill('solid', fgColor=NAVY)
    c.alignment = Alignment(horizontal='center', vertical='center')
    c.border = BOX
for r, (g, nm, unit, price) in enumerate(PRICES, 5):
    for i, v in enumerate([g, nm, unit, price, ''], 1):
        c = pr.cell(row=r, column=i, value=v)
        c.font = Font(name=F, size=10)
        c.border = BOX
        c.alignment = Alignment(
            horizontal='center' if i in (1, 3) else ('right' if i == 4 else 'left'),
            vertical='center')
        if i == 4:
            c.number_format = MONEY
    pr.row_dimensions[r].height = 19
for col, w in zip('ABCDE', (16, 34, 8, 14, 20)):
    pr.column_dimensions[col].width = w
pr.freeze_panes = 'A5'
LAST = 4 + len(PRICES)

# ══════════════════════════════════════════════════ 견적서
q = wb.create_sheet('견적서', 0)
for col, w in zip('ABCDEFGHI', (4.5, 11, 23, 22, 6.5, 7, 12.5, 14, 11)):
    q.column_dimensions[col].width = w


def put(ref, val, *, bold=False, size=11, color='000000', fill=None,
        align='left', fmt=None, border=True, wrap=False):
    c = q[ref]
    c.value = val
    c.font = Font(name=F, bold=bold, size=size, color=color)
    c.alignment = Alignment(horizontal=align, vertical='center', wrap_text=wrap)
    if fill:
        c.fill = PatternFill('solid', fgColor=fill)
    if border:
        c.border = BOX
    if fmt:
        c.number_format = fmt
    return c


def lbl(ref, text):
    return put(ref, text, bold=True, size=10, fill=HEAD, align='center')


# 제목
q.merge_cells('A1:I2')
put('A1', '견     적     서', bold=True, size=26, color=NAVY, align='center', border=False)
q.row_dimensions[1].height = 26
q.row_dimensions[2].height = 20

# 견적 정보
q.merge_cells('F4:G4'); lbl('F4', '견적번호')
put('H4', '=TEXT($H$5,"yyyymmdd")&"-01"', align='center')
q.merge_cells('H4:I4')
q.merge_cells('F5:G5'); lbl('F5', '견적일자')
put('H5', '=TODAY()', align='center', fmt=DATE)
q.merge_cells('H5:I5')
q.merge_cells('F6:G6'); lbl('F6', '유효기간')
put('H6', '=$H$5+30', align='center', fmt=DATE)
q.merge_cells('H6:I6')
put('A4', '아래와 같이 견적서를 제출합니다.', size=11, border=False)

def pair(row, left_label, left_val, right_label, right_val, size=10):
    """왼쪽(공급받는자) 라벨 A:B / 값 C:D, 오른쪽(공급자) 라벨 E:F / 값 G:I."""
    q.merge_cells(f'A{row}:B{row}'); lbl(f'A{row}', left_label)
    q.merge_cells(f'C{row}:D{row}'); put(f'C{row}', left_val, size=size)
    q.merge_cells(f'E{row}:F{row}'); lbl(f'E{row}', right_label)
    q.merge_cells(f'G{row}:I{row}'); put(f'G{row}', right_val, size=size)

# 공급받는자 / 공급자
put('A8', '■ 공급받는자', bold=True, size=11, color=NAVY, border=False)
put('E8', '■ 공급자', bold=True, size=11, color=NAVY, border=False)
pair(9,  '상　　호',  None, '상　　호',    '주식회사 리본마켓')
pair(10, '프로젝트명', None, '사업자번호',  '209-88-03446')
pair(11, '담 당 자',  None, '대 표 자',    '김기훈')
pair(12, '연 락 처',  None, '업태 / 종목', '서비스 / 경영컨설팅업')
pair(13, '이 메 일',  None, '주　　소',    '경기도 평택시 이충로 49-29, 103호', size=9)
pair(14, '주　　소',  None, '담당 · 연락처', '최은성  010-5843-0627 / ces@rebornmarket.org', size=9)

# 합계 금액 (한글)
q.merge_cells('A16:B16'); lbl('A16', '합계금액')
q.merge_cells('C16:I16')
put('C16', '="금 "&TEXT($H$46,"#,##0")&"원정   (부가세 포함)"',
    bold=True, size=14, color=NAVY, align='center')
q.row_dimensions[16].height = 30

# 항목 표
put('A18', '■ 견적 내역', bold=True, size=11, color=NAVY, border=False)
put('A19', '※ 품목을 목록에서 고르면 단위·단가가 자동으로 들어옵니다. 수량만 입력하세요.',
    size=9, color=DIM, border=False)

HDRS = ['No', '구분', '품목 · 서비스', '상세 내용', '단위', '수량', '단가', '공급가액', '비고']
for i, h in enumerate(HDRS, 1):
    c = q.cell(row=R0 - 1, column=i, value=h)
    c.font = Font(name=F, bold=True, size=10, color='FFFFFF')
    c.fill = PatternFill('solid', fgColor=NAVY)
    c.alignment = Alignment(horizontal='center', vertical='center')
    c.border = Border(left=thin, right=thin, top=med, bottom=thin)
q.row_dimensions[R0 - 1].height = 24

TBL = f"'단가표'!$B${5}:$D${LAST}"
for n, r in enumerate(range(R0, R1 + 1), 1):
    q.cell(row=r, column=1, value=n)
    q.cell(row=r, column=2,
           value=f'=IFERROR(INDEX(\'단가표\'!$A${5}:$A${LAST},'
                 f'MATCH($C{r},\'단가표\'!$B${5}:$B${LAST},0)),"")')
    q.cell(row=r, column=3, value=None)
    q.cell(row=r, column=4, value=None)
    q.cell(row=r, column=5, value=f'=IFERROR(VLOOKUP($C{r},{TBL},2,0),"")')
    q.cell(row=r, column=6, value=None)
    q.cell(row=r, column=7, value=f'=IFERROR(VLOOKUP($C{r},{TBL},3,0),"")')
    q.cell(row=r, column=8, value=f'=IF($C{r}="","",IFERROR(ROUND($F{r}*$G{r},0),""))')
    q.cell(row=r, column=9, value=None)
    for i in range(1, 10):
        c = q.cell(row=r, column=i)
        c.font = Font(name=F, size=10)
        c.border = BOX
        c.alignment = Alignment(
            horizontal={1: 'center', 2: 'center', 5: 'center', 6: 'center'}.get(i)
            or ('right' if i in (7, 8) else 'left'), vertical='center')
        if i in (6, 7, 8):
            c.number_format = MONEY
        if i in (3, 4, 6, 9):
            c.fill = PatternFill('solid', fgColor=SOFT)
    q.row_dimensions[r].height = 20

# 품목 드롭다운
dv = DataValidation(type='list',
                    formula1=f"='단가표'!$B${5}:$B${LAST}", allow_blank=True)
q.add_data_validation(dv)
dv.add(f'C{R0}:C{R1}')

# 집계
TOT = [
    ('소　　계', f'=SUM($H${R0}:$H${R1})', False),
    ('할　　인', 0, True),
    ('공급가액', f'=$H${R1+1}-$H${R1+2}', False),
    ('부가세 (10%)', f'=ROUND($H${R1+3}*0.1,0)', False),
    ('합　　계', f'=$H${R1+3}+$H${R1+4}', False),
]
for i, (name, val, editable) in enumerate(TOT):
    r = R1 + 1 + i
    q.merge_cells(f'A{r}:G{r}')
    last = (i == len(TOT) - 1)
    put(f'A{r}', name, bold=True, size=11 if not last else 12,
        fill=HEAD if not last else NAVY,
        color='000000' if not last else 'FFFFFF', align='right')
    c = put(f'H{r}', val, bold=True, size=11 if not last else 13,
            align='right', fmt=MONEY,
            fill=SOFT if editable else (NAVY if last else None),
            color='FFFFFF' if last else '000000')
    put(f'I{r}', '입력' if editable else None, size=9, color=WARN, align='center')
    q.row_dimensions[r].height = 22 if not last else 28

# 특기사항
r = R1 + 7
put(f'A{r}', '■ 특기사항', bold=True, size=11, color=NAVY, border=False)
NOTES = [
    '1. 본 견적의 유효기간은 견적일로부터 30일입니다.',
    '2. 상기 금액은 부가가치세 10%가 포함된 금액입니다.',
    '3. 대금 지급 조건 : 계약 시 50%, 완료 시 50% (협의 가능)',
    '4. 과업 범위 변경 시 견적 금액은 재산정될 수 있습니다.',
    '5. 출장비 · 인쇄비 등 실비는 별도 청구될 수 있습니다.',
]
for i, t in enumerate(NOTES):
    rr = r + 1 + i
    q.merge_cells(f'A{rr}:I{rr}')
    put(f'A{rr}', t, size=10, border=False)

# 인쇄 설정
q.sheet_properties.pageSetUpPr.fitToPage = True
q.page_setup.orientation = 'portrait'
q.page_setup.paperSize = q.PAPERSIZE_A4
q.page_setup.fitToWidth = 1
q.page_setup.fitToHeight = 0
q.print_area = f'A1:I{r + len(NOTES)}'
q.sheet_view.showGridLines = False

# ══════════════════════════════════════════════════ 안내
g = wb.create_sheet('안내')
g.column_dimensions['A'].width = 3
g.column_dimensions['B'].width = 100
GUIDE = [
    ('t', '경영컨설팅 견적서 템플릿 — 사용법'),
    ('', ''),
    ('h', '쓰는 순서'),
    ('p', '① [단가표] 시트의 단가를 회사 기준으로 바꿉니다.  ← 가장 먼저'),
    ('p', '② [견적서] 시트에서 공급받는자 정보를 채웁니다. (상호·프로젝트명·담당자·연락처)'),
    ('p', '③ 「품목 · 서비스」 칸을 클릭하면 드롭다운이 뜹니다. 품목을 고르세요.'),
    ('p', '④ 「수량」만 입력하면 끝입니다. 나머지는 자동 계산됩니다.'),
    ('', ''),
    ('h', '자동으로 계산되는 것'),
    ('p', '· 구분 · 단위 · 단가  →  단가표에서 자동으로 가져옵니다'),
    ('p', '· 공급가액  =  수량 × 단가'),
    ('p', '· 소계  =  공급가액 전체 합'),
    ('p', '· 공급가액 계  =  소계 − 할인'),
    ('p', '· 부가세  =  공급가액 계 × 10%  (원 단위 반올림)'),
    ('p', '· 합계  =  공급가액 계 + 부가세'),
    ('p', '· 상단 「합계금액」의 한글 표기  →  합계에서 자동 생성'),
    ('p', '· 견적번호  =  견적일자 기준 자동 (예: 20261025-01)'),
    ('p', '· 유효기간  =  견적일자 + 30일'),
    ('', ''),
    ('h', '직접 입력하는 칸  (연한 파란색 배경)'),
    ('p', '상세 내용 · 수량 · 비고 · 할인'),
    ('', ''),
    ('h', '주의'),
    ('w', '· 단가표의 단가는 모두 예시입니다. 반드시 실제 단가로 교체하세요.'),
    ('p', '· 목록에 없는 품목은 단가표에 행을 추가하면 드롭다운에 바로 나타납니다.'),
    ('p', '· 특정 건만 단가를 다르게 쓰려면 해당 칸의 수식을 지우고 금액을 직접 적으세요.'),
    ('p', '  (그 칸만 수식이 사라지고 나머지 계산은 그대로 동작합니다)'),
    ('p', '· 행이 모자라면 견적 내역의 마지막 행을 복사해 아래로 늘리세요.'),
    ('p', f'  다만 소계 수식의 범위(H{R0}:H{R1})는 같이 넓혀야 합니다.'),
    ('', ''),
    ('h', '인쇄'),
    ('p', '· A4 세로 · 가로 1페이지에 맞춤으로 설정되어 있습니다.'),
    ('p', '· 눈금선은 숨겨 두었습니다. 그대로 인쇄하면 됩니다.'),
    ('p', '· 직인은 출력 후 공급자 「상호」 옆에 날인하세요.'),
]
r = 2
for kind, text in GUIDE:
    if kind == 't':
        g.cell(row=r, column=2, value=text).font = Font(name=F, bold=True, size=15, color=NAVY)
        g.row_dimensions[r].height = 28
    elif kind == 'h':
        g.cell(row=r, column=2, value=text).font = Font(name=F, bold=True, size=11.5, color=NAVY)
        g.row_dimensions[r].height = 22
    elif kind == 'w':
        g.cell(row=r, column=2, value=text).font = Font(name=F, size=10.5, bold=True, color=WARN)
    elif kind == 'p':
        g.cell(row=r, column=2, value=text).font = Font(name=F, size=10.5)
    r += 1
g.sheet_view.showGridLines = False

wb.remove(wb['Sheet'])
wb.move_sheet('견적서', offset=-wb.sheetnames.index('견적서'))
wb.save(OUT)
print('  ', OUT.name)
print('   시트:', ' / '.join(wb.sheetnames))
print(f'   품목 행: {R0}~{R1} ({NROW}행) · 단가표 품목 {len(PRICES)}종')
