# -*- coding: utf-8 -*-
"""시상식 현수막 + 대형 상금 패널.

현수막 : 5000 x 900mm (옥외 게시대 표준)
상금 패널 : 900 x 600mm (사진 촬영용 대형 보드, 폼보드 출력)
"""
import base64, pathlib, subprocess

HERE = pathlib.Path(__file__).parent
LOGO = HERE / 'logo' if (HERE / 'logo').is_dir() else HERE.parent / 'logo'
CHROME = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
FONT = '/usr/share/fonts/truetype/nanum'

b64 = lambda p: base64.b64encode(pathlib.Path(p).read_bytes()).decode()
IMG = {k: f'data:image/png;base64,{b64(LOGO / f"{k}.png")}'
       for k in ('molab', 'hrdk', 'goyang', 'kdp')}

TITLE_SMALL = '2026 고양시'
TITLE = '바이브 코딩 창업경진대회'
CEREMONY = '시 상 식'
WHEN = '2026. 10. 22.(목)'          # ← 날짜가 다르면 이 한 줄만 고친다
WHERE = '한국항공대학교'
GIVER = '고양산업진흥원장'

# (상격, 수상자, 금액표기, 금액설명)
AWARDS = [
    ('대상',     ['유진수', '박준호'],                     '1,000,000', '금 일백만원정'),
    ('최우수상', ['김현수'],                               '500,000',   '금 오십만원정'),
    ('우수상',   ['하정묵'],                               '300,000',   '금 삼십만원정'),
    ('장려상',   ['권오규', '장보성'],                      '100,000',   '상품권 100,000원 상당'),
    ('장려상',   ['김승준'],                               '100,000',   '상품권 100,000원 상당'),
    ('장려상',   ['김효나', '주소민'],                      '100,000',   '상품권 100,000원 상당'),
    ('장려상',   ['곽세인', '강미주'],                      '100,000',   '상품권 100,000원 상당'),
    ('장려상',   ['김성훈', '김채원', '신재훈', '김수빈'],    '100,000',   '상품권 100,000원 상당'),
    ('장려상',   ['윤지성'],                               '100,000',   '상품권 100,000원 상당'),
]

FONTCSS = f'''
@font-face{{font-family:'NS';src:url('file://{FONT}/NanumSquareR.ttf');font-weight:400}}
@font-face{{font-family:'NS';src:url('file://{FONT}/NanumSquareB.ttf');font-weight:700}}
@font-face{{font-family:'MJ';src:url('file://{FONT}/NanumMyeongjo.ttf');font-weight:400}}
@font-face{{font-family:'MJ';src:url('file://{FONT}/NanumMyeongjoBold.ttf');font-weight:700}}
'''

NAVY_BG = 'linear-gradient(118deg,#04091C 0%,#0A1A42 38%,#123C86 68%,#061026 100%)'
GOLD, GOLD2, CYAN = '#E8C77A', '#C9A54E', '#6FE0FF'


def rays(w, h, n=26):
    """중앙에서 퍼지는 방사선 — 시상식 느낌."""
    cx, cy = w / 2, h * .46
    seg = []
    for i in range(n):
        a = i * (360 / n)
        import math
        x = cx + math.cos(math.radians(a)) * w
        y = cy + math.sin(math.radians(a)) * w
        seg.append(f'<line x1="{cx:.0f}" y1="{cy:.0f}" x2="{x:.0f}" y2="{y:.0f}"/>')
    return (f'<svg class="bgart" viewBox="0 0 {w} {h}" preserveAspectRatio="none">'
            f'<g stroke="{GOLD}" stroke-width="{min(w,h)*.0016:.2f}" opacity=".10">'
            f'{"".join(seg)}</g></svg>')


BAR = (f'<span class="lbl">주최</span><span class="logos">'
       f'<img class="l-molab" src="{IMG["molab"]}"><img class="l-hrdk" src="{IMG["hrdk"]}"></span>'
       f'<span class="lbl">주관</span><span class="logos">'
       f'<img class="l-goyang" src="{IMG["goyang"]}"><img class="l-kdp" src="{IMG["kdp"]}"></span>')


# ══════════════════════════════════════════ 시상식 현수막 5000 × 900mm
def banner():
    W, H = 5000, 900
    return f'''<!doctype html><meta charset="utf-8"><style>{FONTCSS}
@page{{size:{W}mm {H}mm;margin:0}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'NS',sans-serif;color:#fff;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
.wrap{{width:{W}mm;height:{H}mm;position:relative;overflow:hidden;background:{NAVY_BG}}}
.bgart{{position:absolute;inset:0;width:100%;height:100%}}
.glow{{position:absolute;left:46%;top:-55%;width:120%;height:210%;transform:translateX(-50%);
 background:radial-gradient(ellipse at 50% 50%,rgba(232,199,122,.22),transparent 60%)}}
.edge{{position:absolute;left:0;right:0;height:11mm;background:
 linear-gradient(90deg,{GOLD2},{GOLD},{GOLD2})}}
.edge.t{{top:0}} .edge.b{{bottom:0}}
.in{{position:relative;z-index:2;height:100%;padding:0 150mm;
 display:flex;align-items:center;gap:120mm}}
.left{{flex:0 0 auto}}
.eyebrow{{font-size:46mm;color:{GOLD};letter-spacing:11mm;margin-bottom:22mm}}
h1{{font-size:132mm;line-height:1.06;font-weight:700;letter-spacing:-2mm;white-space:nowrap}}
h1 em{{font-style:normal;color:{CYAN}}}
.mid{{flex:1;display:flex;justify-content:center}}
.cer{{border:4mm solid {GOLD};border-radius:16mm;padding:26mm 60mm;
 font-size:150mm;font-weight:700;letter-spacing:26mm;text-indent:26mm;color:{GOLD};
 line-height:1.05;white-space:nowrap;
 box-shadow:0 0 30mm rgba(232,199,122,.28) inset}}
.right{{flex:0 0 auto;text-align:right}}
.meta{{font-size:42mm;line-height:1.9;color:#DCE8FF;white-space:nowrap}}
.meta b{{color:#fff;font-weight:700}}
.bar{{margin-top:34mm;display:grid;grid-template-columns:auto auto;align-items:center;
 justify-content:end;column-gap:24mm;row-gap:13mm;background:#fff;border-radius:10mm;
 padding:17mm 24mm}}
.lbl{{font-size:20mm;font-weight:700;color:#4A5568;background:#EDF1F7;border-radius:5mm;
 padding:5mm 11mm;text-align:center}}
.logos{{display:flex;align-items:center;gap:26mm}}
.logos img{{display:block}}
.l-molab{{height:34mm}} .l-hrdk{{height:29mm}} .l-goyang{{height:39mm}} .l-kdp{{height:32mm}}
</style>
<div class="wrap">{rays(W, H)}<div class="glow"></div>
 <div class="edge t"></div><div class="edge b"></div>
 <div class="in">
  <div class="left">
   <div class="eyebrow">{TITLE_SMALL}</div>
   <h1><em>바이브 코딩</em> 창업경진대회</h1>
  </div>
  <div class="mid"><div class="cer">{CEREMONY}</div></div>
  <div class="right">
   <div class="meta">일시 &nbsp;<b>{WHEN}</b><br>장소 &nbsp;<b>{WHERE}</b></div>
   <div class="bar">{BAR}</div>
  </div>
 </div>
</div>'''


# ══════════════════════════════════════════ 대형 상금 패널 900 × 600mm
def panel(rank, names, amount, desc):
    W, H = 900, 600
    nm = ' · '.join(names)
    size = 56 if len(nm) <= 10 else (46 if len(nm) <= 20 else 34)
    return f'''<div class="pg">{rays(W, H, 22)}<div class="glow"></div>
 <div class="frame"></div>
 <div class="in">
  <div class="top">
   <div class="eyebrow">{TITLE_SMALL} {TITLE}</div>
   <div class="rank">{rank}</div>
  </div>
  <div class="who" style="font-size:{size}mm">{nm}</div>
  <div class="rule"></div>
  <div class="amt">
   <span class="won">￦</span><span class="num">{amount}</span>
  </div>
  <div class="desc">{desc}</div>
  <div class="foot">
   <div class="giver">{GIVER}</div>
   <div class="bar">{BAR}</div>
  </div>
 </div>
</div>'''


def panels():
    W, H = 900, 600
    pages = ''.join(panel(*a) for a in AWARDS)
    return f'''<!doctype html><meta charset="utf-8"><style>{FONTCSS}
@page{{size:{W}mm {H}mm;margin:0}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'NS',sans-serif;color:#fff;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
.pg{{width:{W}mm;height:{H}mm;position:relative;overflow:hidden;background:{NAVY_BG}}}
.pg+.pg{{page-break-before:always}}
.bgart{{position:absolute;inset:0;width:100%;height:100%}}
.glow{{position:absolute;left:50%;top:-30%;width:110%;height:120%;transform:translateX(-50%);
 background:radial-gradient(ellipse at 50% 50%,rgba(232,199,122,.22),transparent 62%)}}
.frame{{position:absolute;inset:22mm;border:2.4mm solid {GOLD};border-radius:8mm}}
.frame::after{{content:'';position:absolute;inset:4mm;border:.7mm solid rgba(232,199,122,.45);
 border-radius:5mm}}
.in{{position:relative;z-index:2;height:100%;padding:46mm 60mm 40mm;
 display:flex;flex-direction:column;align-items:center;text-align:center}}
.in>*{{flex:0 0 auto}}
.eyebrow{{font-size:15mm;color:#AFC8EA;letter-spacing:1.6mm}}
.rank{{margin-top:9mm;font-family:'MJ',serif;font-size:50mm;font-weight:700;
 color:{GOLD};letter-spacing:9mm;text-indent:9mm;line-height:1.1}}
.who{{margin-top:12mm;font-weight:700;line-height:1.2;letter-spacing:1mm}}
.rule{{margin-top:14mm;width:120mm;height:.9mm;background:{GOLD};opacity:.75}}
.amt{{margin-top:auto;display:flex;align-items:baseline;justify-content:center;gap:5mm;
 color:#fff}}
.won{{font-size:52mm;font-weight:700;color:{GOLD}}}
.num{{font-size:96mm;font-weight:700;letter-spacing:-1mm;
 text-shadow:0 0 6mm rgba(232,199,122,.45)}}
.desc{{margin-top:4mm;font-size:22mm;color:{GOLD}}}
.foot{{margin-top:auto;width:100%;display:flex;align-items:center;
 justify-content:space-between;gap:30mm}}
.giver{{font-family:'MJ',serif;font-size:24mm;font-weight:700;letter-spacing:2mm;
 white-space:nowrap}}
.bar{{display:grid;grid-template-columns:auto auto auto auto;align-items:center;
 column-gap:9mm;background:#fff;border-radius:5mm;padding:7mm 9mm}}
.lbl{{font-size:8mm;font-weight:700;color:#4A5568;background:#EDF1F7;border-radius:2mm;
 padding:2mm 4mm;text-align:center}}
.logos{{display:flex;align-items:center;gap:10mm}}
.logos img{{display:block}}
.l-molab{{height:13mm}} .l-hrdk{{height:11mm}} .l-goyang{{height:15mm}} .l-kdp{{height:12mm}}
</style>{pages}'''


def render(name, html):
    src = HERE / f'{name}.html'
    src.write_text(html, encoding='utf-8')
    out = HERE / f'{name}.pdf'
    subprocess.run([CHROME, '--headless', '--disable-gpu', '--no-sandbox',
                    '--allow-file-access-from-files', '--font-render-hinting=none',
                    f'--print-to-pdf={out}', '--no-pdf-header-footer',
                    f'file://{src}'], check=True, capture_output=True)
    print('   ', out.name)


def preview(name, page, width):
    """인쇄용 PDF 는 그대로 넘기고, 눈으로 확인할 미리보기 PNG 를 따로 뽑는다."""
    stem = HERE / f'{name}_미리보기'
    subprocess.run(['pdftoppm', '-png', '-singlefile', '-f', str(page), '-l', str(page),
                    '-scale-to-x', str(width), '-scale-to-y', '-1',
                    str(HERE / f'{name}.pdf'), str(stem)], check=True)
    print('   ', stem.name + '.png')


def main():
    render('시상식_현수막_5000x900', banner())
    render('상금패널_900x600', panels())
    print(f'    상금 패널 {len(AWARDS)}매')
    preview('시상식_현수막_5000x900', 1, 3000)
    preview('상금패널_900x600', 1, 1400)


if __name__ == '__main__':
    main()
