#!/usr/bin/env python3
"""행사별 참석자 명단(서명부) — A4 가로, 현장 출력용."""
import base64, subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOGO = HERE.parent / '2026-홍보물' / 'logo'
FONT = '/usr/share/fonts/truetype/nanum'
CHROME = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'

def b64(p):
    return 'data:image/png;base64,' + base64.b64encode(Path(p).read_bytes()).decode()

IMG = {k: b64(LOGO / f'{k}.png') for k in ('molab', 'hrdk', 'goyang', 'kdp')}

TITLE = '2026년 고양시 바이브 코딩 창업경진대회'
ROWS_PER_PAGE = 20

# (파일명, 행사명, 일시, 장소, 쪽수)
EVENTS = [
    ('창업특강_참석자명단', '창업 특강',
     '2026. 9. 28.(월) 14:00 ~ 16:00', '한국항공대학교 대강당', 10),
    ('최종발표_참석자명단', '최종 발표 평가 및 시상',
     '2026. 10. 22.(목)', '한국항공대학교 스타트업 라운지', 3),
]

PRIVACY = (
    '개인정보 수집·이용 안내 ｜ 수집 항목 : 성명, 소속, 학년 ｜ '
    '수집 목적 : 행사 참석 확인, 사업 결과보고 및 정산 ｜ 보유 기간 : 사업 종료 및 정산 완료 후 6개월 이내 파기 ｜ '
    '동의를 거부하실 수 있으나 이 경우 행사 참석 확인이 제한됩니다.'
)

COLS = [
    ('연번', '15mm'), ('성 명', '45mm'), ('소속', '105mm'), ('학년', '24mm'),
    ('개인정보<br>동의', '26mm'), ('서 명', '58mm'),
]

CSS = f'''
@font-face{{font-family:'NS';src:url('file://{FONT}/NanumBarunGothic.ttf');font-weight:400}}
@font-face{{font-family:'NS';src:url('file://{FONT}/NanumBarunGothicBold.ttf');font-weight:700}}
@page{{size:297mm 210mm;margin:0}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'NS',sans-serif;color:#111;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
.pg{{width:297mm;height:210mm;padding:10mm 12mm 7mm;display:flex;flex-direction:column;
 overflow:hidden}}
.pg+.pg{{page-break-before:always}}
.pg>*{{flex:0 0 auto}}

.doc{{font-size:3mm;color:#666;text-align:right;margin-bottom:1.5mm}}
h1{{font-size:6mm;text-align:center;letter-spacing:.6mm;margin-bottom:.8mm}}
.sub{{font-size:3.2mm;text-align:center;color:#444;margin-bottom:2.4mm}}

.meta{{width:100%;border-collapse:collapse;margin-bottom:2mm}}
.meta td{{border:.25mm solid #888;font-size:3.1mm;padding:1.1mm 2.5mm}}
.meta td.k{{background:#EFEFEF;font-weight:700;text-align:center;width:22mm}}

table.sign{{width:100%;border-collapse:collapse;table-layout:fixed}}
table.sign th{{background:#EFEFEF;border:.25mm solid #666;font-size:3.1mm;
 padding:1.1mm 1mm;line-height:1.2}}
table.sign td{{border:.25mm solid #999;height:6.5mm;font-size:3.1mm;padding:0 2mm}}
td.n{{text-align:center;color:#666}}
td.c{{text-align:center}}

.foot{{margin-top:2.4mm}}
.pv{{font-size:2.7mm;color:#555;line-height:1.5}}

.bar{{margin-top:auto;padding-top:2mm;border-top:.25mm solid #CCC;
 display:flex;align-items:center;justify-content:center;gap:5mm}}
.lbl{{font-size:2.7mm;font-weight:700;color:#555;background:#F0F0F0;border-radius:.8mm;
 padding:.8mm 2mm}}
.logos{{display:flex;align-items:center;gap:5mm}}
.logos img{{display:block}}
.l-molab{{height:4.6mm}} .l-hrdk{{height:4mm}} .l-goyang{{height:5.2mm}} .l-kdp{{height:4.2mm}}
'''

def page(ev, when, place, pno, total):
    head = ''.join(f'<th style="width:{w}">{h}</th>' for h, w in COLS)
    body = ''
    for i in range(ROWS_PER_PAGE):
        n = (pno - 1) * ROWS_PER_PAGE + i + 1
        body += (f'<tr><td class="n">{n}</td>' + '<td></td>' * 3 +
                 '<td class="c">□</td><td></td></tr>')
    return f'''<div class="pg">
 <div class="doc">{pno} / {total} 쪽</div>
 <h1>참 석 자 명 단</h1>
 <div class="sub">{TITLE}</div>
 <table class="meta">
  <tr><td class="k">행사명</td><td>{ev}</td>
      <td class="k">일 시</td><td style="width:62mm">{when}</td></tr>
  <tr><td class="k">장 소</td><td>{place}</td>
      <td class="k">주 관</td><td>고양산업진흥원</td></tr>
 </table>
 <table class="sign"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>
 <div class="foot"><div class="pv">※ {PRIVACY}</div></div>
 <div class="bar">
  <span class="lbl">주최</span>
  <span class="logos"><img class="l-molab" src="{IMG['molab']}"><img class="l-hrdk" src="{IMG['hrdk']}"></span>
  <span class="lbl">주관</span>
  <span class="logos"><img class="l-goyang" src="{IMG['goyang']}"><img class="l-kdp" src="{IMG['kdp']}"></span>
 </div>
</div>'''

def main():
    for stem, ev, when, place, n in EVENTS:
        pages = ''.join(page(ev, when, place, i + 1, n) for i in range(n))
        src = HERE / f'{stem}.html'
        src.write_text(f'<!doctype html><meta charset="utf-8"><style>{CSS}</style>{pages}',
                       encoding='utf-8')
        out = HERE / f'{stem}.pdf'
        subprocess.run([CHROME, '--headless', '--disable-gpu', '--no-sandbox',
                        '--allow-file-access-from-files', '--font-render-hinting=none',
                        f'--print-to-pdf={out}', '--no-pdf-header-footer',
                        f'file://{src}'], check=True, capture_output=True)
        print(f'   {out.name}  ({n}쪽 · {n * ROWS_PER_PAGE}명)')

if __name__ == '__main__':
    main()
