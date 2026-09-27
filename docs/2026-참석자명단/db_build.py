#!/usr/bin/env python3
"""참가자 DB — 과업지시서 Ⅲ-가 '참가자 DB(소속·학번·연락처·팀 구성 여부)' 대응."""
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

HERE = Path(__file__).resolve().parent
OUT = HERE / '참가자DB_및_참석자명단.xlsx'

NAVY, HEAD, ZEBRA = '17365D', 'DCE6F1', 'F7F9FC'
F = '맑은 고딕'
thin = Side(style='thin', color='B4BDC7')
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)

def style_header(ws, ncols, row=1):
    for c in range(1, ncols + 1):
        cell = ws.cell(row=row, column=c)
        cell.font = Font(name=F, bold=True, size=10, color='FFFFFF')
        cell.fill = PatternFill('solid', fgColor=NAVY)
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        cell.border = BOX
    ws.row_dimensions[row].height = 30
    ws.freeze_panes = ws.cell(row=row + 1, column=1)

def sheet(wb, name, cols, nrows=60, note=None):
    """cols : [(제목, 폭)] — 1행 머리글, nrows 개 빈 행에 테두리·연번."""
    ws = wb.create_sheet(name)
    top = 1
    if note:
        ws['A1'] = note
        ws['A1'].font = Font(name=F, size=9, color='9C2A2A')
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(cols))
        ws.row_dimensions[1].height = 18
        top = 2
    for i, (t, w) in enumerate(cols, 1):
        ws.cell(row=top, column=i, value=t)
        ws.column_dimensions[get_column_letter(i)].width = w
    style_header(ws, len(cols), top)
    for r in range(top + 1, top + 1 + nrows):
        for c in range(1, len(cols) + 1):
            cell = ws.cell(row=r, column=c)
            cell.border = BOX
            cell.font = Font(name=F, size=10)
            cell.alignment = Alignment(vertical='center',
                                       horizontal='center' if c == 1 else 'left')
            if (r - top) % 2 == 0:
                cell.fill = PatternFill('solid', fgColor=ZEBRA)
        ws.cell(row=r, column=1, value=r - top)
        ws.row_dimensions[r].height = 19
    return ws, top

def yn(ws, col, top, nrows, values):
    """드롭다운. values 는 콤마로 묶인 목록."""
    dv = DataValidation(type='list', formula1=f'"{values}"', allow_blank=True)
    ws.add_data_validation(dv)
    dv.add(f'{col}{top+1}:{col}{top+nrows}')

wb = Workbook()
wb.remove(wb.active)

# ── 0. 안내 ────────────────────────────────────────────────────────────────
ws = wb.create_sheet('안내')
ws.column_dimensions['A'].width = 4
ws.column_dimensions['B'].width = 104
GUIDE = [
    ('t', '2026년 고양시 바이브 코딩 창업경진대회 — 참가자 DB 및 참석자 명단'),
    ('', ''),
    ('h', '이 파일의 용도'),
    ('p', '과업지시서 Ⅲ-가의 「참가자 DB(소속·학번·연락처·팀 구성 여부) 구축」과'),
    ('p', '결과보고·정산 시 제출하는 행사별 참석자 명단을 하나로 관리하는 대장입니다.'),
    ('', ''),
    ('h', '시트 구성'),
    ('p', '① 창업특강_참석  9. 28.(월) 특강 참석자 — 현장 서명부를 받아 옮겨 적는 시트'),
    ('p', '② 참가팀_명단    서류 접수 팀 전체 — 구글폼 응답을 붙여넣어 관리'),
    ('p', '③ 서류심사_결과  예선 평가 점수와 합격 여부'),
    ('p', '④ 온라인멘토링   10. 13.(화)~10. 18.(일) 팀별 멘토링 진행 기록'),
    ('p', '⑤ 최종발표_참석  10. 22.(목) 발표 평가 및 시상 참석'),
    ('p', '⑥ 집계          위 시트를 자동 집계 (수식이 들어 있으니 덮어쓰지 마세요)'),
    ('', ''),
    ('h', '쓰는 법'),
    ('p', '· 구글폼 응답 시트를 열어 필요한 열만 복사해 「참가팀_명단」에 값 붙여넣기 하세요.'),
    ('p', '· 회색 드롭다운이 걸린 칸은 목록에서 고르시면 집계가 자동으로 맞습니다.'),
    ('p', '· 행이 모자라면 마지막 행을 복사해 아래로 늘리세요. 연번과 테두리가 같이 따라옵니다.'),
    ('', ''),
    ('h', '개인정보 취급'),
    ('p', '· 수집 목적(참석 확인·결과보고·정산) 외의 용도로 쓰지 않습니다.'),
    ('p', '· 사업 종료 및 정산 완료 후 6개월 이내에 파기합니다.'),
    ('p', '· 파일을 외부로 보낼 때는 연락처·이메일 열을 지우거나 가린 사본을 쓰세요.'),
]
r = 2
for kind, text in GUIDE:
    if kind == 't':
        ws.cell(row=r, column=2, value=text).font = Font(name=F, bold=True, size=14, color=NAVY)
        ws.row_dimensions[r].height = 26
    elif kind == 'h':
        ws.cell(row=r, column=2, value=text).font = Font(name=F, bold=True, size=11, color=NAVY)
    elif kind == 'p':
        ws.cell(row=r, column=2, value=text).font = Font(name=F, size=10)
    r += 1

# ── 1. 창업특강 참석 ───────────────────────────────────────────────────────
ws, top = sheet(wb, '창업특강_참석', [
    ('연번', 6), ('성명', 11), ('소속 대학', 20), ('학과', 20), ('학년', 8),
    ('학번', 14), ('연락처', 16), ('이메일', 26),
    ('개인정보\n동의', 10), ('서명\n확인', 8), ('비고', 20),
], nrows=90, note='※ 9. 28.(월) 현장 서명부(창업특강_참석자명단.pdf)를 받아 이곳에 옮겨 적습니다.')
yn(ws, 'I', top, 90, 'Y,N'); yn(ws, 'J', top, 90, 'Y,N')

# ── 2. 참가팀 명단 ─────────────────────────────────────────────────────────
ws, top = sheet(wb, '참가팀_명단', [
    ('연번', 6), ('팀명', 16), ('참가\n형태', 9), ('대표자', 10), ('소속 대학', 18),
    ('학과 / 학년', 18), ('연락처', 16), ('이메일', 26), ('아이템 한 줄 소개', 40),
    ('팀원 2', 22), ('팀원 3', 22), ('팀원 4', 22),
    ('사업계획서\n제출', 11), ('특강\n참석', 9), ('멘토링 가능\n시간대', 20), ('비고', 18),
], nrows=60, note='※ 구글폼 응답 시트에서 값만 복사해 붙여넣으세요. 접수 마감 10. 9.(금) 18:00')
yn(ws, 'C', top, 60, '개인,2인,3인,4인')
yn(ws, 'M', top, 60, 'Y,N'); yn(ws, 'N', top, 60, 'Y,N')

# ── 3. 서류심사 결과 ───────────────────────────────────────────────────────
ws, top = sheet(wb, '서류심사_결과', [
    ('연번', 6), ('팀명', 16), ('대표자', 10),
    ('심사위원 1\n점수', 13), ('심사위원 2\n점수', 13), ('평균', 10),
    ('순위', 8), ('합격\n여부', 9), ('통보일', 12), ('심사 의견', 44),
], nrows=60, note='※ 서류 합격자 발표 10. 12.(월) · 합격 팀에 이메일 개별 통보')
yn(ws, 'H', top, 60, '합격,불합격')
for r in range(top + 1, top + 61):
    ws.cell(row=r, column=6, value=f'=IF(COUNT(D{r}:E{r})=0,"",ROUND(AVERAGE(D{r}:E{r}),1))')

# ── 4. 온라인 멘토링 ───────────────────────────────────────────────────────
ws, top = sheet(wb, '온라인멘토링', [
    ('연번', 6), ('팀명', 16), ('멘토링\n일자', 12), ('시작', 9), ('종료', 9),
    ('멘토명', 12), ('소속', 18), ('참석\n인원', 8), ('진행\n방식', 11),
    ('멘토링 결과 요약 (개선 과제)', 50), ('비고', 16),
], nrows=30, note='※ 10. 13.(화) ~ 10. 18.(일) · 서류 합격 팀 대상 · 팀당 1회')
yn(ws, 'I', top, 30, 'Zoom,Google Meet,기타')

# ── 5. 최종발표 참석 ───────────────────────────────────────────────────────
ws, top = sheet(wb, '최종발표_참석', [
    ('연번', 6), ('구분', 11), ('팀명 / 소속', 20), ('성명', 11),
    ('연락처', 16), ('이메일', 24), ('발표\n순서', 8),
    ('참석\n확인', 9), ('수상', 14), ('비고', 20),
], nrows=60, note='※ 10. 22.(목) · 학생·심사위원·스태프를 구분해 함께 기록합니다.')
yn(ws, 'B', top, 60, '참가학생,심사위원,스태프,내빈')
yn(ws, 'H', top, 60, 'Y,N')
yn(ws, 'I', top, 60, '대상,최우수상,우수상,장려상')

# ── 6. 집계 ────────────────────────────────────────────────────────────────
ws = wb.create_sheet('집계')
ws.column_dimensions['A'].width = 4
ws.column_dimensions['B'].width = 30
ws.column_dimensions['C'].width = 16
ws.column_dimensions['D'].width = 46
ws['B2'] = '집계'
ws['B2'].font = Font(name=F, bold=True, size=14, color=NAVY)
ROWS = [
    ('창업 특강 참석자', '=COUNTA(창업특강_참석!B3:B92)', '명 · 9. 28.(월)'),
    ('개인정보 동의 확인', '=COUNTIF(창업특강_참석!I3:I92,"Y")', '명'),
    ('', '', ''),
    ('서류 접수 팀', '=COUNTA(참가팀_명단!B3:B62)', '팀 · 마감 10. 9.(금)'),
    ('사업계획서 제출 완료', '=COUNTIF(참가팀_명단!M3:M62,"Y")', '팀'),
    ('참가 인원 (팀원 포함)', '=COUNTA(참가팀_명단!D3:D62)+COUNTA(참가팀_명단!J3:J62)'
                          '+COUNTA(참가팀_명단!K3:K62)+COUNTA(참가팀_명단!L3:L62)', '명'),
    ('', '', ''),
    ('서류 합격 팀', '=COUNTIF(서류심사_결과!H3:H62,"합격")', '팀 · 발표 10. 12.(월)'),
    ('멘토링 완료 팀', '=COUNTA(온라인멘토링!B3:B32)', '팀 · 10. 13. ~ 10. 18.'),
    ('', '', ''),
    ('최종발표 참석 (전체)', '=COUNTIF(최종발표_참석!H3:H62,"Y")', '명 · 10. 22.(목)'),
    ('  ├ 참가 학생', '=COUNTIFS(최종발표_참석!B3:B62,"참가학생",최종발표_참석!H3:H62,"Y")', '명'),
    ('  ├ 심사위원', '=COUNTIFS(최종발표_참석!B3:B62,"심사위원",최종발표_참석!H3:H62,"Y")', '명'),
    ('  └ 스태프', '=COUNTIFS(최종발표_참석!B3:B62,"스태프",최종발표_참석!H3:H62,"Y")', '명'),
    ('', '', ''),
    ('수상 팀', '=COUNTA(최종발표_참석!I3:I62)', '팀 · 총 10팀 예정'),
]
r = 4
for label, formula, unit in ROWS:
    if not label:
        r += 1
        continue
    ws.cell(row=r, column=2, value=label).font = Font(name=F, size=11,
        bold=not label.startswith(' '))
    c = ws.cell(row=r, column=3, value=formula)
    c.font = Font(name=F, size=11, bold=True, color=NAVY)
    c.alignment = Alignment(horizontal='center')
    c.fill = PatternFill('solid', fgColor=HEAD)
    c.border = BOX
    ws.cell(row=r, column=4, value=unit).font = Font(name=F, size=10, color='767676')
    ws.row_dimensions[r].height = 20
    r += 1

wb.save(OUT)
print('  ', OUT.name, '—', len(wb.sheetnames), '시트:', ' / '.join(wb.sheetnames))
