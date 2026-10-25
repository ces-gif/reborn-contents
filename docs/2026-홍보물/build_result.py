# -*- coding: utf-8 -*-
"""2026 바이브 코딩 창업경진대회 — 최종 결과 공지 이미지.

규격 : 공지용 1080x1350(4:5) / 스토리 1080x1920(9:16)
수상자는 상장과 동일하게 이름만 표기한다 (팀명 미표기).
"""
import pathlib, subprocess
from PIL import Image
from build import THEMES, FONTCSS, IMG, grid

HERE = pathlib.Path(__file__).parent
CHROME = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
THEME = 'B'

YEAR = '2026 고양시'
T1, T2 = '바이브 코딩', '창업경진대회'
HEAD = '최종 결과 발표'
DATE = '2026. 10. 22.(목) 최종 발표 평가 및 시상'

TOP = [
    ('대상',     ['유진수', '박준호'], '1,000,000원'),
    ('최우수상', ['김현수'],           '500,000원'),
    ('우수상',   ['하정묵'],           '300,000원'),
]
ENCOURAGE = [
    ['권오규', '장보성'],
    ['김승준'],
    ['김효나', '주소민'],
    ['곽세인', '강미주'],
    ['김성훈', '김채원', '신재훈', '김수빈'],
    ['윤지성'],
]
ENC_PRIZE = '각 100,000원 상당'
CLOSING = '끝까지 함께해 주신 모든 참가자 여러분께 감사드립니다.'

BAR = (f'<span class="lbl">주최</span><span class="logos">'
       f'<img class="l-molab" src="{IMG["molab"]}"><img class="l-hrdk" src="{IMG["hrdk"]}"></span>'
       f'<span class="lbl">주관</span><span class="logos">'
       f'<img class="l-goyang" src="{IMG["goyang"]}"><img class="l-kdp" src="{IMG["kdp"]}"></span>')


def base_css(w, h, t):
    return f'''{FONTCSS}
@page{{size:{w}px {h}px;margin:0}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{w}px;height:{h}px}}
body{{font-family:'NS',sans-serif;color:#fff;overflow:hidden;
 -webkit-print-color-adjust:exact;print-color-adjust:exact}}
.wrap{{width:{w}px;height:{h}px;position:relative;overflow:hidden;background:{t['bg_x']}}}
.bgart{{position:absolute;inset:0;width:100%;height:100%}}
.scrim{{position:absolute;inset:0;background:linear-gradient(180deg,
 rgba(2,5,14,.62) 0%,rgba(2,5,14,.15) 30%,rgba(2,5,14,.45) 66%,rgba(2,5,14,.88) 100%)}}
.glow{{position:absolute;left:50%;top:-12%;width:120%;height:56%;transform:translateX(-50%);
 background:radial-gradient(ellipse at 50% 50%,rgba(34,230,255,.20),transparent 62%)}}
.in{{position:relative;z-index:2;display:flex;flex-direction:column;height:100%}}
.in>*{{flex:0 0 auto}}
.year{{color:{t['body']};font-weight:700}}
h1 em{{font-style:normal;color:{t['c1']};text-shadow:{t['glowtxt']}}}
.head{{font-weight:700;color:#fff;letter-spacing:.02em}}
.date{{color:{t['dim']}}}
.row{{display:grid;align-items:center;border-radius:16px;
 border:1px solid rgba(255,255,255,.12);background:rgba(255,255,255,.05)}}
.row.gold{{border-color:#E8C77A;background:rgba(232,199,122,.14)}}
.row .rk{{font-weight:700;color:{t['c1']}}}
.row.gold .rk{{color:#F0D79B}}
.row .nm{{font-weight:700;color:#fff;white-space:nowrap}}
.row .pz{{color:{t['dim']};text-align:right;white-space:nowrap}}
.encbox{{border-radius:16px;border:1px solid rgba(255,255,255,.12);
 background:rgba(255,255,255,.05)}}
.enchd{{display:flex;justify-content:space-between;align-items:baseline;
 color:{t['c1']};font-weight:700}}
.enchd span{{color:{t['dim']};font-weight:400}}
.enclist{{display:grid;grid-template-columns:1fr;color:#fff}}
.enclist div{{position:relative;padding-left:1em;white-space:nowrap}}
.enclist div::before{{content:'·';position:absolute;left:.1em;color:{t['c2']}}}
.close{{color:{t['body']};text-align:center}}
.bar{{display:grid;grid-template-columns:auto auto auto auto;justify-content:center;
 align-items:center;background:#fff;border-radius:16px}}
.lbl{{font-weight:700;color:#4A5568;background:#EDF1F7;border-radius:6px;text-align:center}}
.logos{{display:flex;align-items:center}}
.logos img{{display:block}}
'''


def rows_html(nm_sep='，　'):
    out = ''
    for i, (rank, names, prize) in enumerate(TOP):
        out += (f'<div class="row{" gold" if i == 0 else ""}">'
                f'<div class="rk">{rank}</div>'
                f'<div class="nm">{nm_sep.join(names)}</div>'
                f'<div class="pz">{prize}</div></div>')
    return out


def enc_html():
    return ''.join(f'<div>{"，　".join(t)}</div>' for t in ENCOURAGE)


# ══════════════════════════════════════════ 공지용 1080 × 1350
def notice():
    t = THEMES[THEME]
    W, H = 1080, 1350
    art = grid(W, H, t, horizon=.36)
    return f'''<!doctype html><meta charset="utf-8"><style>{base_css(W,H,t)}
.in{{padding:54px 60px 46px}}
.year{{font-size:30px;margin-bottom:6px}}
h1{{font-size:62px;line-height:1.12;letter-spacing:-.02em;font-weight:700}}
.head{{font-size:46px;margin-top:22px;letter-spacing:.14em}}
.date{{font-size:23px;margin-top:11px}}
.rows{{margin-top:34px;display:grid;gap:17px}}
.row{{grid-template-columns:160px 1fr auto;gap:18px;padding:27px 28px}}
.row .rk{{font-size:33px}} .row .nm{{font-size:38px}} .row .pz{{font-size:25px}}
.encbox{{margin-top:17px;padding:28px}}
.enchd{{font-size:31px;margin-bottom:18px}}
.enchd span{{font-size:23px}}
.enclist{{gap:15px;font-size:28px;line-height:1.3}}
.close{{margin-top:auto;padding-top:24px;font-size:26px;line-height:1.55}}
.bar{{margin-top:18px;padding:17px 20px;column-gap:18px}}
.lbl{{font-size:18px;padding:5px 12px}}
.logos{{gap:22px}}
.l-molab{{height:30px}} .l-hrdk{{height:26px}} .l-goyang{{height:35px}} .l-kdp{{height:28px}}
</style>
<div class="wrap">{art}<div class="scrim"></div><div class="glow"></div>
 <div class="in">
  <div class="year">{YEAR}</div>
  <h1><em>{T1}</em> {T2}</h1>
  <div class="head">{HEAD}</div>
  <div class="date">{DATE}</div>
  <div class="rows">{rows_html()}</div>
  <div class="encbox">
   <div class="enchd">장려상 <span>{ENC_PRIZE}</span></div>
   <div class="enclist">{enc_html()}</div>
  </div>
  <div class="close">{CLOSING}</div>
  <div class="bar">{BAR}</div>
 </div>
</div>'''


# ══════════════════════════════════════════ 스토리 1080 × 1920
def story():
    t = THEMES[THEME]
    W, H = 1080, 1920
    art = grid(W, H, t, horizon=.32)
    return f'''<!doctype html><meta charset="utf-8"><style>{base_css(W,H,t)}
.in{{padding:190px 70px 250px}}
.year{{font-size:34px;margin-bottom:8px}}
h1{{font-size:74px;line-height:1.12;letter-spacing:-.02em;font-weight:700}}
.head{{font-size:55px;margin-top:28px;letter-spacing:.14em}}
.date{{font-size:25px;margin-top:13px}}
.rows{{margin-top:36px;display:grid;gap:13px}}
.row{{grid-template-columns:162px 1fr;gap:20px;padding:20px 28px}}
.row .rk{{font-size:34px}} .row .nm{{font-size:37px}}
.row .pz{{display:none}}
.encbox{{margin-top:15px;padding:22px 28px}}
.enchd{{font-size:30px;margin-bottom:14px}}
.enchd span{{font-size:25px}}
.enclist{{gap:11px;font-size:27px;line-height:1.3}}
.close{{margin-top:auto;padding-top:22px;font-size:25px;line-height:1.55}}
.bar{{margin-top:20px;padding:18px 22px;column-gap:20px;row-gap:14px;
 grid-template-columns:auto auto}}
.lbl{{font-size:21px;padding:6px 14px}}
.logos{{gap:30px}}
.l-molab{{height:36px}} .l-hrdk{{height:31px}} .l-goyang{{height:42px}} .l-kdp{{height:34px}}
</style>
<div class="wrap">{art}<div class="scrim"></div><div class="glow"></div>
 <div class="in">
  <div class="year">{YEAR}</div>
  <h1><em>{T1}</em><br>{T2}</h1>
  <div class="head">{HEAD}</div>
  <div class="date">{DATE}</div>
  <div class="rows">{rows_html()}</div>
  <div class="encbox">
   <div class="enchd">장려상 <span>{ENC_PRIZE}</span></div>
   <div class="enclist">{enc_html()}</div>
  </div>
  <div class="close">{CLOSING}</div>
  <div class="bar">{BAR}</div>
 </div>
</div>'''


def shoot(name, html, w, h):
    """크롬 --screenshot 은 뷰포트가 창보다 작아 하단이 잘린다.
    @page 로 PDF 를 뽑은 뒤 정확한 해상도로 래스터화한다."""
    src = HERE / f'{name}.html'
    src.write_text(html, encoding='utf-8')
    pdf = HERE / f'_{name}.pdf'
    subprocess.run([CHROME, '--headless', '--disable-gpu', '--no-sandbox',
                    '--allow-file-access-from-files', '--font-render-hinting=none',
                    f'--print-to-pdf={pdf}', '--no-pdf-header-footer',
                    f'file://{src}'], check=True, capture_output=True)
    # CSS px = 1/96in 이므로 192dpi 로 2배 래스터화 후 축소
    stem = HERE / f'_{name}_r'
    subprocess.run(['pdftoppm', '-png', '-r', '192', '-singlefile',
                    str(pdf), str(stem)], check=True, capture_output=True)
    raw = stem.with_suffix('.png')
    im = Image.open(raw).convert('RGB')
    # @page 크기가 pt 로 반올림되며 1px 가량 흰 테두리가 남는다. 비율대로 잘라낸다.
    im = im.crop((0, 0, im.width, round(im.width * h / w)))
    im.resize((w, h), Image.LANCZOS).save(HERE / f'{name}.png', quality=95)
    pdf.unlink(); raw.unlink()
    print(f'   {name}.png  {w}×{h}')


def main():
    shoot('결과발표_공지_1080x1350', notice(), 1080, 1350)
    shoot('결과발표_스토리_1080x1920', story(), 1080, 1920)
    n = sum(len(x[1]) for x in TOP) + sum(len(t) for t in ENCOURAGE)
    print(f'   수상 {len(TOP) + len(ENCOURAGE)}팀 · {n}명')


if __name__ == '__main__':
    main()
