# -*- coding: utf-8 -*-
"""2026 바이브 코딩 특강·창업 경진대회 현수막 / X배너.
현수막 5000x900mm, X배너 600x1800mm — 국내에서 가장 널리 쓰는 규격.
로고 4종(고용노동부·한국산업인력공단·고양산업진흥원·K-하이테크 플랫폼)을 모두 노출한다."""
import base64, pathlib, subprocess, sys

HERE = pathlib.Path(__file__).parent
LOGO = HERE.parent / 'logo'
CHROME = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
FONT = '/usr/share/fonts/truetype/nanum'

b64 = lambda p: base64.b64encode(pathlib.Path(p).read_bytes()).decode()
IMG = {k: f'data:image/png;base64,{b64(LOGO / f"{k}.png")}' for k in ('molab', 'hrdk', 'goyang', 'kdp')}

# 행사 정보 — 과업지시서·계획(안)과 같은 값
TITLE_SMALL = '2026 대학생과 고양시민의 AI 기술 창업을 위한'
TITLE_1 = '바이브 코딩'
TITLE_2 = '특강 &amp; 창업 경진대회'
SLOGAN = '코딩을 몰라도, 2시간 만에 내 서비스를 만든다'
LECTURE = '2026. 9. 28.(월) 13:00'
PLACE = '한국항공대학교 대강당'

CSS_FONT = f'''
@font-face {{ font-family:'NS'; src:url('file://{FONT}/NanumSquareR.ttf'); font-weight:400; }}
@font-face {{ font-family:'NS'; src:url('file://{FONT}/NanumSquareB.ttf'); font-weight:700; }}
@font-face {{ font-family:'NSR'; src:url('file://{FONT}/NanumSquareRoundB.ttf'); font-weight:700; }}
'''

# 배경 — 남색 그라데이션 위에 은은한 노드 네트워크. AI 행사물의 관용적 표현.
def nodes(w, h, seed=7):
    import random
    r = random.Random(seed)
    pts = [(r.uniform(0, w), r.uniform(0, h)) for _ in range(46)]
    seg = []
    for i, (x1, y1) in enumerate(pts):
        for x2, y2 in pts[i + 1:]:
            d = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** .5
            if d < min(w, h) * 0.34:
                seg.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/>')
    dot = ''.join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r.uniform(1.6,4.2):.1f}"/>' for x, y in pts)
    return (f'<svg class="net" viewBox="0 0 {w} {h}" preserveAspectRatio="none">'
            f'<g stroke="#5FD3FF" stroke-width="0.7" fill="none" opacity=".18">{"".join(seg)}</g>'
            f'<g fill="#7CF7C4" opacity=".40">{dot}</g></svg>')

LOGOBAR = '''
<div class="bar">
  <div class="grp"><span class="lbl">주최</span>
    <img class="l-molab" src="{molab}"><img class="l-hrdk" src="{hrdk}"></div>
  <div class="sep"></div>
  <div class="grp"><span class="lbl">주관</span>
    <img class="l-goyang" src="{goyang}"><img class="l-kdp" src="{kdp}"></div>
</div>'''.format(**IMG)

# ─────────────────────────────────────────────────────────── 현수막 5000x900
HYUN = f'''<!doctype html><meta charset="utf-8"><style>
{CSS_FONT}
@page {{ size:5000mm 900mm; margin:0; }}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:5000mm;height:900mm;font-family:'NS';overflow:hidden;
 background:linear-gradient(115deg,#071331 0%,#0E2A63 42%,#123C86 72%,#0B1F46 100%)}}
.wrap{{position:relative;width:5000mm;height:900mm;display:flex;flex-direction:column;overflow:hidden}}
.net{{position:absolute;inset:0;width:100%;height:100%}}
.glow{{position:absolute;right:-6%;top:-40%;width:52%;height:180%;border-radius:50%;
 background:radial-gradient(circle,rgba(63,169,245,.38) 0%,rgba(63,169,245,0) 62%)}}
.main{{position:relative;flex:1;display:flex;align-items:center;padding:0 150mm}}
.left{{flex:1}}
.eyebrow{{font-size:52mm;color:#7CF7C4;letter-spacing:.02em;margin-bottom:22mm;font-weight:700}}
h1{{font-family:'NSR';font-size:150mm;line-height:1.02;color:#fff;letter-spacing:-.02em}}
h1 .hl{{background:linear-gradient(90deg,#5FD3FF,#7CF7C4);-webkit-background-clip:text;
 -webkit-text-fill-color:transparent}}
.slogan{{margin-top:26mm;font-size:54mm;color:#CFE4FF}}
.right{{flex:0 0 900mm;text-align:right}}
.dbox{{display:inline-block;border-left:8mm solid #7CF7C4;padding:14mm 0 14mm 30mm;text-align:left}}
.dbox .d{{font-size:66mm;font-weight:700;color:#fff;line-height:1.25}}
.dbox .p{{font-size:46mm;color:#9FC4F0;margin-top:8mm}}
.bar{{position:relative;z-index:2;flex:0 0 155mm;width:5000mm;background:#fff;display:flex;
 align-items:center;justify-content:center;gap:80mm;padding:0 100mm}}
.grp{{display:flex;align-items:center;gap:46mm}}
.lbl{{font-size:42mm;font-weight:700;color:#0E2A63;background:#E8F0FB;
 padding:11mm 22mm;border-radius:7mm;white-space:nowrap}}
.bar img{{object-fit:contain}}
.bar .l-molab{{height:80mm}} .bar .l-hrdk{{height:50mm}}
.bar .l-goyang{{height:82mm}} .bar .l-kdp{{height:58mm}}
.sep{{width:1.5mm;height:80mm;background:#D5DEEA}}
</style>
<div class="wrap">
  {nodes(5000, 900)}
  <div class="glow"></div>
  <div class="main">
    <div class="left">
      <div class="eyebrow">{TITLE_SMALL}</div>
      <h1><span class="hl">{TITLE_1}</span> {TITLE_2}</h1>
      <div class="slogan">{SLOGAN}</div>
    </div>
    <div class="right"><div class="dbox">
      <div class="d">{LECTURE}</div>
      <div class="p">{PLACE}</div>
    </div></div>
  </div>
  {LOGOBAR}
</div>'''

# ─────────────────────────────────────────────────────────── X배너 600x1800
STEPS = [('①', '창업 특강', '9. 28.(월)', '바이브 코딩 실습 2시간'),
         ('②', '1:1 멘토링', '10. 8.(목)', '신청 10개 팀 · 팀당 60분'),
         ('③', '예선 심사', '10. 15.(목)', '사업계획서 서류평가'),
         ('④', '결승 &amp; 시상', '10. 22.(목)', '현직 VC 심사 · 라이브 데모')]
step_html = ''.join(
    f'<div class="st"><div class="no">{n}</div><div class="tx"><div class="nm">{t}</div>'
    f'<div class="sub">{s}</div></div><div class="dt">{d}</div></div>' for n, t, d, s in STEPS)

XB = f'''<!doctype html><meta charset="utf-8"><style>
{CSS_FONT}
@page {{ size:600mm 1800mm; margin:0; }}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:600mm;height:1800mm;font-family:'NS';overflow:hidden;
 background:linear-gradient(170deg,#071331 0%,#0E2A63 40%,#123C86 68%,#08152F 100%)}}
.wrap{{position:relative;width:600mm;height:1800mm;display:flex;flex-direction:column;overflow:hidden}}
.body{{position:relative;z-index:2;flex:1;display:flex;flex-direction:column;justify-content:space-evenly;padding:70mm 0 40mm}}
.net{{position:absolute;inset:0;width:100%;height:100%}}
.glow{{position:absolute;left:-30%;top:4%;width:160%;height:36%;border-radius:50%;
 background:radial-gradient(circle,rgba(63,169,245,.34) 0%,rgba(63,169,245,0) 62%)}}
.top{{position:relative;padding:0 52mm}}
.eyebrow{{font-size:22mm;color:#7CF7C4;font-weight:700;line-height:1.5;margin-bottom:16mm}}
h1{{font-family:'NSR';font-size:86mm;line-height:1.04;letter-spacing:-.03em;
 background:linear-gradient(90deg,#5FD3FF,#7CF7C4);-webkit-background-clip:text;
 -webkit-text-fill-color:transparent}}
h2{{font-family:'NSR';font-size:48mm;line-height:1.16;color:#fff;letter-spacing:-.02em;margin-top:10mm}}
.slogan{{margin-top:24mm;font-size:26mm;color:#CFE4FF;line-height:1.45}}
.rule{{margin:0 52mm;height:1.2mm;background:linear-gradient(90deg,#5FD3FF,rgba(95,211,255,0))}}
.steps{{position:relative;padding:0 52mm;display:flex;flex-direction:column;gap:15mm}}
.st{{display:flex;align-items:center;gap:16mm;background:rgba(255,255,255,.07);
 border:.8mm solid rgba(124,247,196,.30);border-radius:9mm;padding:16mm 20mm}}
.no{{font-size:30mm;font-weight:700;color:#7CF7C4;flex:0 0 auto}}
.tx{{flex:1}}
.nm{{font-size:27mm;font-weight:700;color:#fff;line-height:1.2}}
.sub{{font-size:17mm;color:#9FC4F0;margin-top:4mm}}
.dt{{font-size:23mm;font-weight:700;color:#fff;white-space:nowrap}}
.prize{{position:relative;margin:0 52mm;border-radius:10mm;padding:26mm 20mm;text-align:center;
 background:linear-gradient(120deg,rgba(124,247,196,.16),rgba(95,211,255,.16));
 border:1mm solid rgba(124,247,196,.45)}}
.prize .k{{font-size:21mm;color:#7CF7C4;font-weight:700}}
.prize .v{{font-size:52mm;font-weight:700;color:#fff;margin-top:8mm;font-family:'NSR'}}
.prize .d{{font-size:17mm;color:#9FC4F0;margin-top:9mm;line-height:1.5}}
.info{{position:relative;margin:0 52mm;font-size:20mm;color:#CFE4FF;line-height:1.75}}
.info b{{color:#fff;font-weight:700}}
.bar{{position:relative;z-index:2;flex:0 0 190mm;width:600mm;background:#fff;
 display:flex;flex-direction:column;align-items:center;justify-content:center;gap:18mm}}
.grp{{display:flex;align-items:center;gap:26mm}}
.lbl{{font-size:16mm;font-weight:700;color:#0E2A63;background:#E8F0FB;
 padding:5mm 11mm;border-radius:4mm;white-space:nowrap}}
.bar img{{object-fit:contain}}
.bar .l-molab{{height:28mm}} .bar .l-hrdk{{height:18mm}}
.bar .l-goyang{{height:29mm}} .bar .l-kdp{{height:21mm}}
.sep{{display:none}}
</style>
<div class="wrap">
  {nodes(600, 1800, 11)}
  <div class="glow"></div>
  <div class="body">
  <div class="top">
    <div class="eyebrow">{TITLE_SMALL}</div>
    <h1>{TITLE_1}</h1>
    <h2>{TITLE_2}</h2>
    <div class="slogan">{SLOGAN}</div>
  </div>
  <div class="rule"></div>
  <div class="steps">{step_html}</div>
  <div class="prize">
    <div class="k">총 시상 규모</div>
    <div class="v">2,500,000원</div>
    <div class="d">대상 100만 · 최우수 50만 · 우수 30만 · 장려 10만 × 7팀</div>
  </div>
  <div class="info">
    <b>참가대상</b>  한국항공대학교 재학생 및 고양시민 (1~4인 팀)<br>
    <b>장　　소</b>  한국항공대학교 대강당 · 스타트업 라운지<br>
    <b>참가문의</b>  (주)리본마켓 010-5843-0627
  </div>
  </div>
  {LOGOBAR}
</div>'''

def render(html, stem, w_mm, h_mm):
    src = HERE / f'{stem}.html'
    src.write_text(html, encoding='utf-8')
    pdf = HERE / f'{stem}.pdf'
    subprocess.run([CHROME, '--headless', '--disable-gpu', '--no-sandbox',
                    '--allow-file-access-from-files', '--font-render-hinting=none',
                    f'--print-to-pdf={pdf}', '--no-pdf-header-footer',
                    f'file://{src}'], check=True, capture_output=True)
    print(f'  {pdf.name}  {w_mm}x{h_mm}mm')

render(HYUN, '현수막_5000x900', 5000, 900)
render(XB, 'X배너_600x1800', 600, 1800)
