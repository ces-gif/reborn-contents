#!/usr/bin/env python3
"""2026 바이브 코딩 창업경진대회 상장 — A4 가로, 1매 1쪽.

팀명·팀원은 카카오톡 대화 '본문'에 적힌 내용만 사용한다.
(발신자 저장이름은 잘못 저장되어 있어 쓰지 않는다.)
"""
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
FONT = '/usr/share/fonts/truetype/nanum'
CHROME = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'

TITLE = '2026 바이브 코딩 창업경진대회'
DATE = '2026년 10월 22일'
GIVER = '고 양 산 업 진 흥 원 장'
GIVER_NAME = '한 동 균'
UNKNOWN = '＊＊＊ 팀명 확인 필요 ＊＊＊'

BODY = {
    '대상': ('인공지능을 활용한 창의적인 아이디어와 뛰어난 사업화 역량을 선보였으며,',
             '심사 결과 참가 팀 중 가장 우수한 성적을 거두었으므로',
             '이에 그 성과를 높이 기려 이 상장을 수여합니다.'),
    '최우수상': ('해결하고자 하는 문제를 명확히 정의하고 탄탄한 비즈니스 모델을 제시하였으며,',
                 '심사 결과 그 우수성을 인정받았으므로',
                 '이에 그 노력을 기려 이 상장을 수여합니다.'),
    '우수상': ('인공지능을 활용한 실현 가능한 해결책과 구체적인 실행 계획을 제시하였으며,',
               '심사 결과 그 성과를 인정받았으므로',
               '이에 그 노력을 기려 이 상장을 수여합니다.'),
    '장려상': ('성실한 준비와 끝까지 포기하지 않는 열정으로 전 과정을 완주하였으며,',
               '창업에 대한 굳은 의지를 보여주었으므로',
               '이에 그 뜻을 기려 이 상장을 수여합니다.'),
}

# (번호, 상격, 팀명, 팀원)
AWARDS = [
    ('01', '대상',     '스펙연구소', ['유진수', '박준호']),
    ('02', '최우수상', None,         ['김현수']),
    ('03', '우수상',   '다시',       ['하정묵']),
    ('04', '장려상',   'ATED LAB',   ['권오규', '장보성']),
    ('05', '장려상',   '효도한스푼',  ['김승준']),
    ('06', '장려상',   '한접시',      ['김효나', '주소민']),
    ('07', '장려상',   '트렌드나비',  ['곽세인', '강미주']),
    ('08', '장려상',   'y3k',        ['김성훈', '김채원', '신재훈', '김수빈']),
    ('09', '장려상',   None,         ['윤지성']),
]

CSS = f'''
@font-face{{font-family:'MJ';src:url('file://{FONT}/NanumMyeongjo.ttf');font-weight:400}}
@font-face{{font-family:'MJ';src:url('file://{FONT}/NanumMyeongjoBold.ttf');font-weight:700}}
@font-face{{font-family:'NS';src:url('file://{FONT}/NanumBarunGothic.ttf');font-weight:400}}
@page{{size:297mm 210mm;margin:0}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'MJ',serif;color:#141A26;
 -webkit-print-color-adjust:exact;print-color-adjust:exact}}
.pg{{width:297mm;height:210mm;padding:14mm;position:relative;overflow:hidden;background:#fff}}
.pg+.pg{{page-break-before:always}}
.frame{{position:absolute;inset:14mm;border:2.4mm solid #17365D}}
.frame::after{{content:'';position:absolute;inset:2.4mm;border:.5mm solid #B99653}}
.in{{position:relative;height:100%;padding:13mm 24mm 17mm;display:flex;flex-direction:column;
 align-items:center;text-align:center}}
.no{{position:absolute;top:4mm;left:4mm;font-family:'NS';font-size:3.4mm;color:#6B7684}}
h1{{font-size:22mm;font-weight:700;letter-spacing:9mm;text-indent:9mm;
 color:#17365D;line-height:1}}
.rank{{margin-top:9mm;font-size:10mm;font-weight:700;letter-spacing:2.4mm;
 text-indent:2.4mm;color:#17365D}}
.who{{margin-top:8mm;font-size:6mm;line-height:2;letter-spacing:.3mm}}
.who b{{font-weight:700;letter-spacing:1.4mm}}
.who .un{{color:#C4372F;font-family:'NS';font-size:5mm;letter-spacing:0}}
.body{{margin-top:8mm;font-size:5.2mm;line-height:2}}
.date{{margin-top:auto;padding-top:9mm;font-size:5.8mm;letter-spacing:1mm}}
.sign{{margin-top:7mm;font-size:8mm;font-weight:700;letter-spacing:1.2mm;
 display:flex;align-items:center;justify-content:center;gap:7mm}}
.seal{{font-family:'NS';font-size:4mm;color:#8A94A6;letter-spacing:0}}
'''


def page(no, rank, team, members):
    t1, t2, t3 = BODY[rank]
    names = '，　'.join(members)
    if team:
        rows = (f'<div>팀　　명 ：　<b>{team}</b></div>'
                f'<div>팀　　원 ：　<b>{names}</b></div>')
        subject = '위 팀은'
    else:
        # 팀명을 아직 못 받았어도 수상자 이름은 반드시 찍는다
        rows = (f'<div>성　　명 ：　<b>{names}</b></div>'
                f'<div>팀　　명 ：　<span class="un">{UNKNOWN}</span></div>')
        subject = '위 사람은'
    return f'''<div class="pg"><div class="frame"></div>
 <div class="in">
  <div class="no">제 2026-{no}호</div>
  <h1>상 장</h1>
  <div class="rank">{rank}</div>
  <div class="who">{rows}</div>
  <div class="body">
   {subject} 「{TITLE}」에 참가하여<br>
   {t1}<br>{t2}<br>{t3}
  </div>
  <div class="date">{DATE}</div>
  <div class="sign">{GIVER}　　{GIVER_NAME}<span class="seal">(직인)</span></div>
 </div>
</div>'''


def main():
    pages = ''.join(page(*a) for a in AWARDS)
    src = HERE / '상장.html'
    src.write_text(f'<!doctype html><meta charset="utf-8"><style>{CSS}</style>{pages}',
                   encoding='utf-8')
    out = HERE / '상장_2026바이브코딩창업경진대회.pdf'
    subprocess.run([CHROME, '--headless', '--disable-gpu', '--no-sandbox',
                    '--allow-file-access-from-files', '--font-render-hinting=none',
                    f'--print-to-pdf={out}', '--no-pdf-header-footer',
                    f'file://{src}'], check=True, capture_output=True)
    print(f'   {out.name}  ({len(AWARDS)}매)')


if __name__ == '__main__':
    main()
