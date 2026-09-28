#!/usr/bin/env python3
"""서류 평가 점수표 — 심사위원 배포용 A4 세로. 팀별 1장 + 총괄 집계표."""
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

CRITERIA = [
    ('1', '문제 정의 능력', 10,
     '해결하려는 문제가 명확하고 구체적인가. 문제의 존재를 근거로 보였는가.'),
    ('2', 'AI를 통한 솔루션의 적합성', 20,
     'AI(바이브 코딩)를 쓰는 것이 이 문제에 실제로 맞는 해법인가. 기술이 목적이 아니라 수단으로 쓰였는가.'),
    ('3', '시장 규모', 15,
     '목표 시장과 고객이 특정되어 있는가. 규모 추정에 근거가 있는가.'),
    ('4', '비즈니스 모델 타당성', 20,
     '누가 왜 돈을 내는지 설명되는가. 수익 구조와 비용 구조가 현실적인가.'),
    ('5', '아이템 구현에 대한 계획', 20,
     '최종 발표까지의 구현 범위와 일정이 구체적인가. 팀이 실제로 만들 수 있는 수준인가.'),
    ('6', '사업 의지', 15,
     '대회 이후로 이어갈 의지와 준비가 보이는가. 팀 구성과 역할이 분명한가.'),
]
TOTAL = sum(c[2] for c in CRITERIA)

BAR = (f'<span class="lbl">주최</span><span class="logos">'
       f'<img class="l-molab" src="{IMG["molab"]}"><img class="l-hrdk" src="{IMG["hrdk"]}"></span>'
       f'<span class="lbl">주관</span><span class="logos">'
       f'<img class="l-goyang" src="{IMG["goyang"]}"><img class="l-kdp" src="{IMG["kdp"]}"></span>')

CSS = f'''
@font-face{{font-family:'NS';src:url('file://{FONT}/NanumBarunGothic.ttf');font-weight:400}}
@font-face{{font-family:'NS';src:url('file://{FONT}/NanumBarunGothicBold.ttf');font-weight:700}}
@page{{size:210mm 297mm;margin:0}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'NS',sans-serif;color:#111;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
.pg{{width:210mm;height:297mm;padding:14mm 15mm 9mm;display:flex;flex-direction:column;
 overflow:hidden}}
.pg+.pg{{page-break-before:always}}
.pg>*{{flex:0 0 auto}}

h1{{font-size:7.4mm;text-align:center;letter-spacing:1mm;margin-bottom:1.4mm}}
.sub{{font-size:3.6mm;text-align:center;color:#444;margin-bottom:5mm}}

.meta{{width:100%;border-collapse:collapse;margin-bottom:4mm}}
.meta td{{border:.25mm solid #888;font-size:3.4mm;padding:2.2mm 3mm}}
.meta td.k{{background:#EFEFEF;font-weight:700;text-align:center;width:26mm}}

table.sc{{width:100%;border-collapse:collapse;table-layout:fixed}}
table.sc th{{background:#EFEFEF;border:.25mm solid #666;font-size:3.3mm;padding:2.2mm 1mm}}
table.sc td{{border:.25mm solid #999;font-size:3.4mm;padding:2.6mm 3mm;vertical-align:top}}
td.no{{text-align:center;font-weight:700;color:#555;width:11mm}}
td.it b{{font-size:3.6mm}}
td.it div{{font-size:3mm;color:#666;margin-top:1.2mm;line-height:1.45}}
td.mx{{text-align:center;width:18mm;font-weight:700;color:#1E4FA0}}
td.in{{width:24mm;background:#FCFCFC}}
tr.sum td{{background:#EFEFEF;font-weight:700;font-size:3.8mm;padding:3mm;text-align:center}}

.op{{margin-top:4mm;border:.25mm solid #999}}
.op .h{{background:#EFEFEF;border-bottom:.25mm solid #999;font-size:3.4mm;font-weight:700;
 padding:2mm 3mm}}
.op .b{{height:34mm}}

.sign{{margin-top:5mm;font-size:3.6mm;text-align:right;line-height:2.1}}
.note{{margin-top:4mm;font-size:2.9mm;color:#666;line-height:1.55}}

.bar{{margin-top:auto;padding-top:3mm;border-top:.25mm solid #CCC;
 display:flex;align-items:center;justify-content:center;gap:5mm}}
.lbl{{font-size:2.7mm;font-weight:700;color:#555;background:#F0F0F0;border-radius:.8mm;
 padding:.8mm 2mm}}
.logos{{display:flex;align-items:center;gap:5mm}}
.logos img{{display:block}}
.l-molab{{height:4.6mm}} .l-hrdk{{height:4mm}} .l-goyang{{height:5.2mm}} .l-kdp{{height:4.2mm}}

/* 총괄표 */
table.tot{{width:100%;border-collapse:collapse;table-layout:fixed}}
table.tot th{{background:#EFEFEF;border:.25mm solid #666;font-size:2.9mm;padding:2mm .5mm;
 line-height:1.2}}
table.tot td{{border:.25mm solid #999;height:7.4mm;font-size:3.1mm;padding:0 1.5mm}}
table.tot td.n{{text-align:center;color:#666}}
'''

def rows():
    out = ''
    for no, name, mx, desc in CRITERIA:
        out += (f'<tr><td class="no">{no}</td>'
                f'<td class="it"><b>{name}</b><div>{desc}</div></td>'
                f'<td class="mx">{mx}</td><td class="in"></td></tr>')
    out += f'<tr class="sum"><td colspan="2">합　계</td><td>{TOTAL}</td><td></td></tr>'
    return out

def sheet_page():
    return f'''<div class="pg">
 <h1>서 류 평 가 점 수 표</h1>
 <div class="sub">{TITLE} · 예선(서류) 심사</div>
 <table class="meta">
  <tr><td class="k">심사일</td><td>2026. 10.　　.</td>
      <td class="k">심사위원</td><td style="width:52mm">　　　　　　　　(서명)</td></tr>
  <tr><td class="k">팀　명</td><td colspan="3"></td></tr>
  <tr><td class="k">아이템</td><td colspan="3"></td></tr>
 </table>
 <table class="sc">
  <thead><tr><th style="width:11mm">번호</th><th>평　가　항　목</th>
   <th style="width:18mm">배점</th><th style="width:24mm">점수</th></tr></thead>
  <tbody>{rows()}</tbody>
 </table>
 <div class="op"><div class="h">종합 의견 · 보완이 필요한 부분</div><div class="b"></div></div>
 <div class="note">
  ※ 각 항목은 배점 범위 안에서 정수로 기재합니다. 합계는 100점 만점입니다.<br>
  ※ 예선은 제출된 사업계획서만으로 평가하며, 프로토타입은 최종 발표에서 평가합니다.<br>
  ※ 본 점수표에 기재된 내용과 제출 서류의 정보는 심사 목적 외에 사용하지 않으며, 외부로 유출하지 않습니다.
 </div>
 <div class="sign">심사위원 　　　　　　　　　 (서명 또는 인)</div>
 <div class="bar">{BAR}</div>
</div>'''

def total_page(nteams=20):
    heads = ''.join(f'<th>{no}<br>({mx})</th>' for no, _, mx, _ in CRITERIA)
    body = ''
    for i in range(1, nteams + 1):
        body += (f'<tr><td class="n">{i}</td><td></td><td></td>'
                 + '<td></td>' * len(CRITERIA)
                 + '<td></td><td></td><td></td></tr>')
    legend = ' ｜ '.join(f'{no}. {name}({mx})' for no, name, mx, _ in CRITERIA)
    return f'''<div class="pg">
 <h1>서류 평가 총괄표</h1>
 <div class="sub">{TITLE} · 예선(서류) 심사 집계</div>
 <table class="meta">
  <tr><td class="k">심사일</td><td>2026. 10.　　.</td>
      <td class="k">심사위원</td><td style="width:52mm">　　　　　　　　(서명)</td></tr>
 </table>
 <table class="tot">
  <thead><tr>
   <th style="width:9mm">연번</th><th style="width:26mm">팀　명</th><th style="width:20mm">대표자</th>
   {heads}
   <th style="width:14mm">합계<br>(100)</th><th style="width:12mm">순위</th>
   <th style="width:15mm">합격<br>여부</th>
  </tr></thead>
  <tbody>{body}</tbody>
 </table>
 <div class="note" style="margin-top:3mm">
  평가 항목 　{legend}<br>
  ※ 합계 100점 만점. 심사위원 2인의 평균 점수로 순위를 산출하고, 결승 진출 10개 팀을 선정합니다.<br>
  ※ 서류 합격자 발표 2026. 10. 12.(월) · 신청 시 기재한 이메일로 개별 통보
 </div>
 <div class="sign">심사위원 　　　　　　　　　 (서명 또는 인)</div>
 <div class="bar">{BAR}</div>
</div>'''

def main():
    for stem, pages in [
        ('서류평가_점수표_심사위원용', sheet_page() * 12),
        ('서류평가_총괄표', total_page()),
    ]:
        src = HERE / f'{stem}.html'
        src.write_text(f'<!doctype html><meta charset="utf-8"><style>{CSS}</style>{pages}',
                       encoding='utf-8')
        out = HERE / f'{stem}.pdf'
        subprocess.run([CHROME, '--headless', '--disable-gpu', '--no-sandbox',
                        '--allow-file-access-from-files', '--font-render-hinting=none',
                        f'--print-to-pdf={out}', '--no-pdf-header-footer',
                        f'file://{src}'], check=True, capture_output=True)
        print('  ', out.name)

if __name__ == '__main__':
    main()
