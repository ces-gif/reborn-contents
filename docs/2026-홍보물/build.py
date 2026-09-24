# -*- coding: utf-8 -*-
"""2026 바이브 코딩 특강·창업 경진대회 현수막 / X배너.

규격 : 현수막 5000x900mm(옥외 게시대 표준), X배너 600x1800mm(표준 거치대)
테마 : A 기본형(남색+노드망) / B 미래형(딥스페이스+네온 원근 그리드)
로고 : 고용노동부·한국산업인력공단·고양산업진흥원·K-하이테크 플랫폼 4종 전부 노출

인쇄 주의 — .wrap 크기는 반드시 mm로 못박는다. height:100%는 인쇄 뷰포트 기준으로
잡혀 하단 로고 바가 바닥에 붙지 않고 폭도 잘린다.
"""
import base64, pathlib, random, subprocess

HERE = pathlib.Path(__file__).parent
# 로고는 이 폴더 안(배포본) 또는 상위 폴더(작업본) 어느 쪽에나 있을 수 있다
LOGO = HERE / 'logo' if (HERE / 'logo').is_dir() else HERE.parent / 'logo'
CHROME = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
FONT = '/usr/share/fonts/truetype/nanum'

b64 = lambda p: base64.b64encode(pathlib.Path(p).read_bytes()).decode()
IMG = {k: f'data:image/png;base64,{b64(LOGO / f"{k}.png")}' for k in ('molab', 'hrdk', 'goyang', 'kdp')}

TITLE_SMALL = '2026 대학생과 고양시민의 AI 기술 창업을 위한'
TITLE_1, TITLE_2 = '바이브 코딩', '특강 &amp; 창업 경진대회'
SLOGAN = '코딩을 몰라도, 2시간 만에 내 서비스를 만든다'
LECTURE, PLACE = '2026. 9. 28.(월) 13:00', '한국항공대학교 대강당'
STEPS = [('01', '창업 특강', '9. 28.(월)', '바이브 코딩 실습 2시간'),
         ('02', '1:1 멘토링', '10. 8.(목)', '신청 10개 팀 · 팀당 60분'),
         ('03', '예선 심사', '10. 15.(목)', '사업계획서 서류평가'),
         ('04', '결승 &amp; 시상', '10. 22.(목)', '현직 VC 심사 · 라이브 데모')]

FONTCSS = f'''
@font-face{{font-family:'NS';src:url('file://{FONT}/NanumSquareR.ttf');font-weight:400}}
@font-face{{font-family:'NS';src:url('file://{FONT}/NanumSquareB.ttf');font-weight:700}}
@font-face{{font-family:'NSR';src:url('file://{FONT}/NanumSquareRoundB.ttf');font-weight:700}}
'''

# ── 테마 ──────────────────────────────────────────────────────────────────
THEMES = {
    'A': dict(bg_h='linear-gradient(115deg,#071331 0%,#0E2A63 42%,#123C86 72%,#0B1F46 100%)',
              bg_x='linear-gradient(170deg,#071331 0%,#0E2A63 40%,#123C86 68%,#08152F 100%)',
              c1='#5FD3FF', c2='#7CF7C4', dim='#9FC4F0', body='#CFE4FF',
              card='rgba(255,255,255,.07)', cardline='rgba(124,247,196,.30)', glowtxt='none'),
    'B': dict(bg_h='linear-gradient(115deg,#01030A 0%,#050B1E 38%,#0A1436 68%,#02040C 100%)',
              bg_x='linear-gradient(175deg,#01030A 0%,#060D22 36%,#0B1740 66%,#01030A 100%)',
              c1='#22E6FF', c2='#9B7CFF', dim='#7E8FC7', body='#C6D6FF',
              card='rgba(34,230,255,.05)', cardline='rgba(34,230,255,.38)',
              glowtxt='0 0 .18em rgba(34,230,255,.55),0 0 .5em rgba(155,124,255,.35)'),
}

def net(w, h, seed, t, op=1.0):
    """A안 배경 — 노드 네트워크.

    선 굵기와 점 크기는 뷰박스 크기에 비례시킨다. 고정값을 쓰면 뷰박스가 작은
    포스터에서만 선이 굵게 나와 글자를 덮는다. op로 판형별 농도를 조절한다.
    """
    r = random.Random(seed)
    k = min(w, h)
    sw, r0, r1 = k * .0009, k * .0030, k * .0068
    pts = [(r.uniform(0, w), r.uniform(0, h)) for _ in range(46)]
    seg = [f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/>'
           for i, (x1, y1) in enumerate(pts) for x2, y2 in pts[i + 1:]
           if ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** .5 < k * .34]
    dot = ''.join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r.uniform(r0,r1):.2f}"/>' for x, y in pts)
    return (f'<svg class="bgart" viewBox="0 0 {w} {h}" preserveAspectRatio="none">'
            f'<g stroke="{t["c1"]}" stroke-width="{sw:.2f}" fill="none" opacity="{.18*op:.3f}">{"".join(seg)}</g>'
            f'<g fill="{t["c2"]}" opacity="{.40*op:.3f}">{dot}</g></svg>')

def grid(w, h, t, horizon=.52):
    """B안 배경 — 소실점으로 모이는 원근 그리드와 지평선 발광."""
    hy = h * horizon
    vx, vy = w / 2, hy
    lines = []
    for i in range(-26, 27):
        x = vx + i * (w / 16)
        lines.append(f'<line x1="{vx:.1f}" y1="{vy:.1f}" x2="{x:.1f}" y2="{h}"/>')
    y, step = hy, h * .012
    while y < h:
        lines.append(f'<line x1="0" y1="{y:.1f}" x2="{w}" y2="{y:.1f}"/>')
        y += step; step *= 1.34
    return (f'<svg class="bgart" viewBox="0 0 {w} {h}" preserveAspectRatio="none">'
            f'<defs><linearGradient id="gf" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{t["c1"]}" stop-opacity="0"/>'
            f'<stop offset=".45" stop-color="{t["c1"]}" stop-opacity=".55"/>'
            f'<stop offset="1" stop-color="{t["c2"]}" stop-opacity=".18"/></linearGradient></defs>'
            f'<g stroke="url(#gf)" stroke-width=".9" fill="none">{"".join(lines)}</g>'
            f'<ellipse cx="{vx:.1f}" cy="{hy:.1f}" rx="{w*.42:.1f}" ry="{h*.05:.1f}" '
            f'fill="{t["c1"]}" opacity=".22" style="filter:blur({h*.02:.1f}px)"/></svg>')

# ── 로고 바 : 라벨을 한 열에 고정해 주최/주관 줄을 맞춘다 ──────────────────
BAR_ROWS = f'''
  <span class="lbl">주최</span>
  <span class="logos"><img class="l-molab" src="{IMG['molab']}"><img class="l-hrdk" src="{IMG['hrdk']}"></span>
  <span class="lbl">주관</span>
  <span class="logos"><img class="l-goyang" src="{IMG['goyang']}"><img class="l-kdp" src="{IMG['kdp']}"></span>'''

def bar_css(one_row, lbl, gap, pad, hm, hh, hg, hk):
    """one_row=True면 [주최][로고][주관][로고]를 한 줄로, False면 두 줄로 쌓는다.
    어느 쪽이든 라벨이 같은 열에 놓여 줄이 맞는다."""
    cols = 'auto auto auto auto' if one_row else 'auto auto'
    return f'''
.bar{{position:relative;z-index:3;background:#fff;display:grid;
 grid-template-columns:{cols};align-items:center;align-content:center;
 justify-content:center;column-gap:{gap};row-gap:{pad}}}
.lbl{{font-size:{lbl};font-weight:700;color:#0E2A63;background:#EAF1FB;
 border-radius:.28em;padding:.26em .62em;white-space:nowrap;text-align:center;justify-self:center}}
.logos{{display:flex;align-items:center;gap:{gap}}}
.bar img{{object-fit:contain;display:block}}
.l-molab{{height:{hm}}} .l-hrdk{{height:{hh}}} .l-goyang{{height:{hg}}} .l-kdp{{height:{hk}}}'''

def page(kind, theme):
    t = THEMES[theme]
    art = net(5000, 900, 7, t) if theme == 'A' else grid(5000, 900, t, .40)
    artx = net(600, 1800, 11, t) if theme == 'A' else grid(600, 1800, t, .60)
    frame = '' if theme == 'A' else '<div class="frame"></div>'
    scrim = '' if theme == 'A' else '<div class="scrim"></div>'
    if kind == 'h':
        return f'''<!doctype html><meta charset="utf-8"><style>{FONTCSS}
@page{{size:5000mm 900mm;margin:0}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:5000mm;height:900mm;font-family:'NS';overflow:hidden;background:{t['bg_h']}}}
.wrap{{position:relative;width:5000mm;height:900mm;display:flex;flex-direction:column;overflow:hidden}}
.bgart{{position:absolute;inset:0;width:100%;height:100%}}
.glow{{position:absolute;right:-6%;top:-40%;width:52%;height:180%;border-radius:50%;
 background:radial-gradient(circle,{'rgba(63,169,245,.38)' if theme=='A' else 'rgba(34,230,255,.30)'} 0%,rgba(0,0,0,0) 62%)}}
.frame{{position:absolute;inset:34mm;border:1.4mm solid {t['c1']};opacity:.30;border-radius:4mm}}
.main{{position:relative;z-index:2;flex:1;display:flex;align-items:center;padding:0 165mm}}
.left{{flex:1}}
.eyebrow{{font-size:52mm;color:{t['c2']};font-weight:700;margin-bottom:22mm}}
h1{{font-family:'NSR';font-size:152mm;line-height:1.02;color:#fff;letter-spacing:-.025em;
 text-shadow:{t['glowtxt']}}}
h1 .hl{{background:linear-gradient(90deg,{t['c1']},{t['c2']});-webkit-background-clip:text;
 -webkit-text-fill-color:transparent}}
.slogan{{margin-top:26mm;font-size:54mm;color:{t['body']}}}
.right{{flex:0 0 940mm;text-align:right}}
.dbox{{display:inline-block;border-left:8mm solid {t['c2']};padding:16mm 0 16mm 32mm;text-align:left}}
.dbox .d{{font-size:68mm;font-weight:700;color:#fff;line-height:1.25}}
.dbox .p{{font-size:46mm;color:{t['dim']};margin-top:8mm}}
.bar{{flex:0 0 160mm;width:5000mm;padding:0 120mm}}
{bar_css(True, '42mm', '48mm', '0', '80mm', '50mm', '82mm', '58mm')}
</style>
<div class="wrap">{art}<div class="glow"></div>{frame}
 <div class="main">
  <div class="left">
   <div class="eyebrow">{TITLE_SMALL}</div>
   <h1><span class="hl">{TITLE_1}</span> {TITLE_2}</h1>
   <div class="slogan">{SLOGAN}</div>
  </div>
  <div class="right"><div class="dbox">
   <div class="d">{LECTURE}</div><div class="p">{PLACE}</div></div></div>
 </div>
 <div class="bar">{BAR_ROWS}</div>
</div>'''

    steps = ''.join(
        f'<div class="st"><div class="no">{n}</div><div class="tx"><div class="nm">{ti}</div>'
        f'<div class="sub">{s}</div></div><div class="dt">{d}</div></div>' for n, ti, d, s in STEPS)
    return f'''<!doctype html><meta charset="utf-8"><style>{FONTCSS}
@page{{size:600mm 1800mm;margin:0}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:600mm;height:1800mm;font-family:'NS';overflow:hidden;background:{t['bg_x']}}}
.wrap{{position:relative;width:600mm;height:1800mm;display:flex;flex-direction:column;overflow:hidden}}
.bgart{{position:absolute;inset:0;width:100%;height:100%}}
.glow{{position:absolute;left:-30%;top:3%;width:160%;height:34%;border-radius:50%;
 background:radial-gradient(circle,{'rgba(63,169,245,.34)' if theme=='A' else 'rgba(155,124,255,.26)'} 0%,rgba(0,0,0,0) 62%)}}
.frame{{position:absolute;left:26mm;right:26mm;top:26mm;bottom:216mm;
 border:1.1mm solid {t['c1']};opacity:.28;border-radius:5mm}}
.scrim{{position:absolute;left:0;right:0;bottom:196mm;height:46%;z-index:1;
 background:linear-gradient(to bottom,rgba(1,3,10,0) 0%,rgba(1,3,10,.55) 48%,rgba(1,3,10,.78) 100%)}}
.body{{position:relative;z-index:2;flex:1;display:flex;flex-direction:column;
 justify-content:space-evenly;padding:74mm 0 44mm}}
.top{{padding:0 56mm}}
.eyebrow{{font-size:22mm;color:{t['c2']};font-weight:700;line-height:1.5;margin-bottom:16mm}}
h1{{font-family:'NSR';font-size:86mm;line-height:1.04;letter-spacing:-.03em;
 background:linear-gradient(90deg,{t['c1']},{t['c2']});-webkit-background-clip:text;
 -webkit-text-fill-color:transparent}}
h2{{font-family:'NSR';font-size:48mm;line-height:1.16;color:#fff;letter-spacing:-.02em;
 margin-top:10mm;text-shadow:{t['glowtxt']}}}
.slogan{{margin-top:24mm;font-size:26mm;color:{t['body']};line-height:1.45}}
.rule{{margin:0 56mm;height:1.2mm;background:linear-gradient(90deg,{t['c1']},rgba(0,0,0,0))}}
.steps{{padding:0 56mm;display:flex;flex-direction:column;gap:15mm}}
.st{{display:flex;align-items:center;gap:16mm;background:{t['card']};
 border:.8mm solid {t['cardline']};border-radius:9mm;padding:16mm 20mm}}
.no{{font-family:'NSR';font-size:26mm;color:{t['c1']};flex:0 0 auto;letter-spacing:.04em}}
.tx{{flex:1}}
.nm{{font-size:27mm;font-weight:700;color:#fff;line-height:1.2}}
.sub{{font-size:17mm;color:{t['dim']};margin-top:4mm}}
.dt{{font-size:23mm;font-weight:700;color:#fff;white-space:nowrap}}
.prize{{margin:0 56mm;border-radius:10mm;padding:26mm 20mm;text-align:center;
 background:linear-gradient(120deg,{t['card']},rgba(255,255,255,.03));
 border:1mm solid {t['cardline']}}}
.prize .k{{font-size:21mm;color:{t['c2']};font-weight:700}}
.prize .v{{font-family:'NSR';font-size:52mm;color:#fff;margin-top:8mm;text-shadow:{t['glowtxt']}}}
.prize .d{{font-size:17mm;color:{t['dim']};margin-top:9mm;line-height:1.5}}
.info{{margin:0 56mm;font-size:20mm;color:{t['body']};line-height:1.75}}
.info b{{color:#fff;font-weight:700}}
.bar{{flex:0 0 196mm;width:600mm}}
{bar_css(False, '16mm', '24mm', '18mm', '30mm', '19mm', '31mm', '22mm')}
</style>
<div class="wrap">{artx}<div class="glow"></div>{scrim}{frame}
 <div class="body">
  <div class="top">
   <div class="eyebrow">{TITLE_SMALL}</div>
   <h1>{TITLE_1}</h1><h2>{TITLE_2}</h2>
   <div class="slogan">{SLOGAN}</div>
  </div>
  <div class="rule"></div>
  <div class="steps">{steps}</div>
  <div class="prize"><div class="k">총 시상 규모</div><div class="v">2,500,000원</div>
   <div class="d">대상 100만 · 최우수 50만 · 우수 30만 · 장려 10만 × 7팀</div></div>
  <div class="info">
   <b>참가대상</b>  고양시·경기북부 거주 대학(원)생 <span style="white-space:nowrap">(개인 또는 1~4인 팀)</span><br>
   <b>장　　소</b>  한국항공대학교 대강당 · 스타트업 라운지<br>
   <b>참가문의</b>  (주)리본마켓 ces@rebornmarket.org</div>
 </div>
 <div class="bar">{BAR_ROWS}</div>
</div>'''

def main():
  for theme, label in (('A', '기본형'), ('B', '미래형')):
      for kind, stem in (('h', '현수막_5000x900'), ('x', 'X배너_600x1800')):
          name = f'{stem}_{theme}안_{label}'
          src = HERE / f'{name}.html'
          src.write_text(page(kind, theme), encoding='utf-8')
          subprocess.run([CHROME, '--headless', '--disable-gpu', '--no-sandbox',
                          '--allow-file-access-from-files', '--font-render-hinting=none',
                          f'--print-to-pdf={HERE / (name + ".pdf")}', '--no-pdf-header-footer',
                          f'file://{src}'], check=True, capture_output=True)
          print('  ', name + '.pdf')

if __name__ == '__main__':
    main()
