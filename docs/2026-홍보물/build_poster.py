# -*- coding: utf-8 -*-
"""2026 바이브 코딩 특강·창업 경진대회 포스터.

규격 : A2 420x594mm(교내 게시 표준) / A1 594x841mm
테마 : build.py의 A 기본형 / B 미래형을 그대로 공유한다.

치수는 전부 rem으로 쓰고 1rem = 페이지 폭의 1%로 잡는다. 그래야 A2와 A1을
같은 레이아웃 한 벌로 뽑을 수 있다. mm를 직접 박으면 규격마다 다시 짜야 한다.
"""
import pathlib, subprocess
from build import (THEMES, IMG, FONTCSS, net, grid, CHROME,
                   TITLE_SMALL, TITLE_1, TITLE_2, SLOGAN, LECTURE, PLACE, STEPS)

HERE = pathlib.Path(__file__).parent

def poster(theme, w, h):
    t = THEMES[theme]
    art = net(w, h, 23, t, .62) if theme == 'A' else grid(w, h, t, .58)
    extra = '<div class="scrim"></div>' + ('' if theme == 'A' else '<div class="frame"></div>')
    steps = ''.join(
        f'<div class="st"><span class="no">{n}</span>'
        f'<span class="nm">{ti}</span><span class="sub">{s}</span>'
        f'<span class="dt">{d}</span></div>' for n, ti, d, s in STEPS)
    return f'''<!doctype html><meta charset="utf-8"><style>{FONTCSS}
@page{{size:{w}mm {h}mm;margin:0}}
*{{margin:0;padding:0;box-sizing:border-box}}
html{{font-size:calc({w}mm / 100)}}          /* 1rem = 페이지 폭의 1% */
body{{width:{w}mm;height:{h}mm;font-family:'NS';overflow:hidden;background:{t['bg_x']}}}
.wrap{{position:relative;width:{w}mm;height:{h}mm;display:flex;flex-direction:column;overflow:hidden}}
.bgart{{position:absolute;inset:0;width:100%;height:100%}}
.glow{{position:absolute;left:-26%;top:-6%;width:152%;height:42%;border-radius:50%;
 background:radial-gradient(circle,{'rgba(63,169,245,.36)' if theme=='A' else 'rgba(155,124,255,.28)'} 0%,rgba(0,0,0,0) 62%)}}
.scrim{{position:absolute;left:0;right:0;bottom:11.5rem;height:48%;z-index:1;
 background:linear-gradient(to bottom,{'rgba(7,19,49,0) 0%,rgba(7,19,49,.42) 46%,rgba(8,21,47,.66)' if theme=='A' else 'rgba(1,3,10,0) 0%,rgba(1,3,10,.58) 46%,rgba(1,3,10,.80)'} 100%)}}
.frame{{position:absolute;left:2.6rem;right:2.6rem;top:2.6rem;bottom:13.6rem;
 border:.16rem solid {t['c1']};opacity:.28;border-radius:.7rem}}
.body{{position:relative;z-index:2;flex:1;display:flex;flex-direction:column;
 justify-content:space-between;padding:7.6rem 6.6rem 4.4rem}}

.eyebrow{{font-size:2.55rem;color:{t['c2']};font-weight:700;margin-bottom:1.9rem;letter-spacing:.01em}}
h1{{font-family:'NSR';font-size:11.4rem;line-height:1.0;letter-spacing:-.035em;
 background:linear-gradient(92deg,{t['c1']},{t['c2']});-webkit-background-clip:text;
 -webkit-text-fill-color:transparent}}
h2{{font-family:'NSR';font-size:6.15rem;line-height:1.14;color:#fff;letter-spacing:-.025em;
 margin-top:1.1rem;text-shadow:{t['glowtxt']}}}
.slogan{{margin-top:2.6rem;font-size:3.15rem;color:{t['body']};line-height:1.4}}
.when{{margin-top:3.1rem;display:inline-block;border-left:.5rem solid {t['c2']};padding:.9rem 0 .9rem 2.1rem}}
.when .d{{font-size:3.6rem;font-weight:700;color:#fff;line-height:1.24}}
.when .p{{font-size:2.5rem;color:{t['dim']};margin-top:.5rem}}

.steps{{display:flex;flex-direction:column;gap:1.35rem}}
.st{{display:flex;align-items:center;gap:1.9rem;background:{t['card']};
 border:.11rem solid {t['cardline']};border-radius:1.1rem;padding:1.85rem 2.3rem}}
.no{{font-family:'NSR';font-size:3.1rem;color:{t['c1']};letter-spacing:.04em;flex:0 0 auto}}
.nm{{font-size:3.15rem;font-weight:700;color:#fff;flex:0 0 auto}}
.sub{{font-size:2.05rem;color:{t['dim']};flex:1}}
.dt{{font-size:2.75rem;font-weight:700;color:#fff;white-space:nowrap}}

.foot{{display:flex;gap:2.4rem;align-items:stretch}}
.prize{{flex:1.05;border-radius:1.2rem;padding:2.7rem 1.6rem;text-align:center;
 background:linear-gradient(120deg,{t['card']},rgba(255,255,255,.03));
 border:.13rem solid {t['cardline']};display:flex;flex-direction:column;justify-content:center}}
.prize .k{{font-size:2.4rem;color:{t['c2']};font-weight:700}}
.prize .v{{font-family:'NSR';font-size:6.4rem;color:#fff;margin-top:.7rem;text-shadow:{t['glowtxt']}}}
.prize .d{{font-size:1.95rem;color:{t['dim']};margin-top:1rem;line-height:1.5}}
.info{{flex:1;display:flex;flex-direction:column;justify-content:center;gap:2.5rem;padding-left:.6rem}}
.info .k{{font-size:2.15rem;font-weight:700;color:{t['c2']};margin-bottom:.75rem;letter-spacing:.01em}}
.info .v{{font-size:2.45rem;color:{t['body']};line-height:1.42}}
.info .v small{{font-size:2.05rem;color:{t['dim']}}}

.bar{{position:relative;z-index:3;flex:0 0 11.5rem;width:{w}mm;background:#fff;
 display:grid;grid-template-columns:auto auto;align-items:center;align-content:center;
 justify-content:center;column-gap:2.7rem;row-gap:2.0rem}}
.lbl{{font-size:1.95rem;font-weight:700;color:#0E2A63;background:#EAF1FB;
 border-radius:.28em;padding:.26em .62em;white-space:nowrap;justify-self:center}}
.logos{{display:flex;align-items:center;gap:2.9rem}}
.bar img{{object-fit:contain;display:block}}
.l-molab{{height:3.5rem}} .l-hrdk{{height:2.2rem}}
.l-goyang{{height:3.6rem}} .l-kdp{{height:2.55rem}}
</style>
<div class="wrap">{art}<div class="glow"></div>{extra}
 <div class="body">
  <div class="hero">
   <div class="eyebrow">{TITLE_SMALL}</div>
   <h1>{TITLE_1}</h1><h2>{TITLE_2}</h2>
   <div class="slogan">{SLOGAN}</div>
   <div class="when"><div class="d">{LECTURE}</div><div class="p">{PLACE}</div></div>
  </div>
  <div class="steps">{steps}</div>
  <div class="foot">
   <div class="prize"><div class="k">총 시상 규모</div><div class="v">2,500,000원</div>
    <div class="d">대상 100만 · 최우수 50만<br>우수 30만 · 장려 10만 × 7팀</div></div>
   <div class="info">
    <div><div class="k">참가대상</div>
     <div class="v">고양시·경기북부 거주 대학(원)생<br><small>대학원 포함 · 개인 또는 1~4인 팀</small></div></div>
    <div><div class="k">장소</div>
     <div class="v">한국항공대학교<br><small>대강당 · 스타트업 라운지</small></div></div>
    <div><div class="k">참가문의</div>
     <div class="v">(주)리본마켓<br><small>010-5843-0627</small></div></div>
   </div>
  </div>
 </div>
 <div class="bar">
  <span class="lbl">주최</span>
  <span class="logos"><img class="l-molab" src="{IMG['molab']}"><img class="l-hrdk" src="{IMG['hrdk']}"></span>
  <span class="lbl">주관</span>
  <span class="logos"><img class="l-goyang" src="{IMG['goyang']}"><img class="l-kdp" src="{IMG['kdp']}"></span>
 </div>
</div>'''

SIZES = [('A2', 420, 594), ('A1', 594, 841)]
for theme, label in (('A', '기본형'), ('B', '미래형')):
    for tag, w, h in SIZES:
        name = f'포스터_{tag}_{w}x{h}_{theme}안_{label}'
        src = HERE / f'{name}.html'
        src.write_text(poster(theme, w, h), encoding='utf-8')
        subprocess.run([CHROME, '--headless', '--disable-gpu', '--no-sandbox',
                        '--allow-file-access-from-files', '--font-render-hinting=none',
                        f'--print-to-pdf={HERE / (name + ".pdf")}', '--no-pdf-header-footer',
                        f'file://{src}'], check=True, capture_output=True)
        print('  ', name + '.pdf')
