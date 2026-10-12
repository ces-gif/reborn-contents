# -*- coding: utf-8 -*-
"""창업경진대회 인스타그램 소재 — 스토리(1080x1920) / 피드(1080x1350).

build.py 의 테마·배경·로고를 그대로 쓴다. 일정은 확정본 기준.
MODE = '본선'  : 서류 합격 발표 이후 ~ 최종발표 예고 (10.12 이후)
MODE = '모집'  : 서류 접수 중 (9.28 ~ 10.9) · QR 노출
"""
import pathlib, subprocess, base64, io
import segno
from PIL import Image
from build import THEMES, FONTCSS, IMG, net, grid

HERE = pathlib.Path(__file__).parent
CHROME = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
FORM_URL = 'https://forms.gle/jhbnBwNXsBiTEatQ7'

MODE = '본선'
THEME = 'B'

TITLE_SMALL = '고용노동부 · 한국산업인력공단 K-하이테크 플랫폼'
T1, T2 = '바이브 코딩', '창업경진대회'
YEAR = '2026 고양시'
SLOGAN = '코딩을 몰라도, AI에게 말로 시켜서 내 서비스를 만든다'

# (번호, 제목, 날짜, 상태)  상태 done/now/next
STEPS = [
    ('01', '서류 접수',            '9. 28. ~ 10. 9.',  'done'),
    ('02', '서류 합격자 발표',      '10. 12.(월)',       'done'),
    ('03', '온라인 팀별 멘토링',    '10. 13. ~ 10. 18.', 'now'),
    ('04', '최종 발표 평가 · 시상',  '10. 22.(목)',       'next'),
]
PRIZE = [('대상', '100만원'), ('최우수상', '50만원'), ('우수상', '30만원'), ('장려상', '각 10만원')]


def qr_b64():
    buf = io.BytesIO()
    segno.make(FORM_URL, error='h').save(buf, kind='png', scale=16, border=2,
                                         dark='#06122E', light='white')
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()


def common_css(w, h, t):
    return f'''{FONTCSS}
@page{{size:{w}px {h}px;margin:0}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{w}px;height:{h}px}}
body{{font-family:'NS',sans-serif;color:#fff;overflow:hidden;
 -webkit-print-color-adjust:exact;print-color-adjust:exact}}
.wrap{{width:{w}px;height:{h}px;position:relative;overflow:hidden;
 background:{t['bg_x']};display:flex;flex-direction:column}}
.bgart{{position:absolute;inset:0;width:100%;height:100%}}
.scrim{{position:absolute;inset:0;background:
 linear-gradient(180deg,rgba(2,5,14,.55) 0%,rgba(2,5,14,.12) 32%,
 rgba(2,5,14,.42) 68%,rgba(2,5,14,.86) 100%)}}
.glow{{position:absolute;left:50%;top:-14%;width:120%;height:60%;transform:translateX(-50%);
 background:radial-gradient(ellipse at 50% 50%,rgba(34,230,255,.20),transparent 62%)}}
.in{{position:relative;z-index:2;display:flex;flex-direction:column;height:100%}}
.eyebrow{{color:{t['dim']};letter-spacing:.06em}}
h1 em{{font-style:normal;color:{t['c1']};text-shadow:{t['glowtxt']}}}
.slogan{{color:{t['body']}}}
.step{{display:grid;align-items:center;border-radius:14px;
 border:1px solid rgba(255,255,255,.10);background:rgba(255,255,255,.04)}}
.step.now{{border-color:{t['c2']};background:rgba(155,124,255,.16)}}
.step.done{{opacity:.42}}
.step .n{{font-weight:700;color:{t['dim']}}}
.step .t{{font-weight:700}}
.step .d{{color:{t['body']}}}
.step.now .d{{color:{t['c1']}}}
.badge{{display:inline-block;border-radius:999px;background:{t['c2']};color:#07102A;
 font-weight:700;letter-spacing:.02em}}
.bar{{display:grid;grid-template-columns:auto auto auto auto;justify-content:center;
 align-items:center;background:#fff;border-radius:16px}}
.lbl{{font-weight:700;color:#4A5568;background:#EDF1F7;border-radius:6px;text-align:center}}
.logos{{display:flex;align-items:center}}
.logos img{{display:block}}
'''


BAR = (f'<span class="lbl">주최</span><span class="logos">'
       f'<img class="l-molab" src="{IMG["molab"]}"><img class="l-hrdk" src="{IMG["hrdk"]}"></span>'
       f'<span class="lbl">주관</span><span class="logos">'
       f'<img class="l-goyang" src="{IMG["goyang"]}"><img class="l-kdp" src="{IMG["kdp"]}"></span>')


def steps_html(show_state=True):
    out = ''
    for n, title, date, st in STEPS:
        cls = f'step {st}' if show_state else 'step'
        tick = '✓ ' if st == 'done' else ''
        out += (f'<div class="{cls}"><div class="n">{n}</div>'
                f'<div class="t">{tick}{title}</div><div class="d">{date}</div></div>')
    return out


# ══════════════════════════════════════════ 스토리 1080 × 1920
def story():
    t = THEMES[THEME]
    W, H = 1080, 1920
    art = grid(W, H, t, horizon=.42) if THEME == 'B' else net(W, H, 7, t, .9)
    cta = ('<div class="qr"><img src="' + qr_b64() + '">'
           '<div class="qt">QR을 찍으면<br>바로 신청</div></div>') if MODE == '모집' else \
          '<div class="final"><div class="fk">FINAL</div>'\
          '<div class="fd">10. 22.<span>(목)</span></div>'\
          '<div class="fs">최종 발표 평가 및 시상</div></div>'
    return f'''<!doctype html><meta charset="utf-8"><style>{common_css(W,H,t)}
.in{{padding:210px 84px 300px}}
.eyebrow{{font-size:25px;margin-bottom:34px}}
.year{{font-size:40px;color:{t['body']};font-weight:700;margin-bottom:10px}}
h1{{font-size:104px;line-height:1.1;letter-spacing:-.02em;font-weight:700}}
.slogan{{font-size:30px;line-height:1.5;margin-top:34px}}
.final{{margin-top:62px;border:2px solid {t['c1']};border-radius:28px;
 padding:42px 44px;background:rgba(34,230,255,.08);text-align:center}}
.fk{{font-size:26px;letter-spacing:.34em;color:{t['c1']};font-weight:700}}
.fd{{font-size:118px;font-weight:700;line-height:1.08;margin:8px 0 4px;
 text-shadow:{t['glowtxt']}}}
.fd span{{font-size:52px}}
.fs{{font-size:31px;color:{t['body']}}}
.qr{{margin-top:62px;background:#fff;border-radius:28px;padding:40px;display:flex;
 align-items:center;gap:36px}}
.qr img{{width:260px;height:260px;display:block}}
.qt{{font-size:40px;font-weight:700;color:#06122E;line-height:1.35}}
.steps{{margin-top:auto;display:grid;gap:14px}}
.step{{grid-template-columns:62px 1fr auto;gap:22px;padding:22px 30px}}
.step .n{{font-size:30px}} .step .t{{font-size:33px}} .step .d{{font-size:28px}}
.bar{{margin-top:34px;padding:26px 30px;column-gap:28px;row-gap:18px;
 grid-template-columns:auto auto}}
.lbl{{font-size:22px;padding:7px 16px}}
.logos{{gap:34px}}
.l-molab{{height:40px}} .l-hrdk{{height:34px}} .l-goyang{{height:46px}} .l-kdp{{height:37px}}
</style>
<div class="wrap">{art}<div class="scrim"></div><div class="glow"></div>
 <div class="in">
  <div class="eyebrow">{TITLE_SMALL}</div>
  <div class="year">{YEAR}</div>
  <h1><em>{T1}</em><br>{T2}</h1>
  <div class="slogan">{SLOGAN}</div>
  {cta}
  <div class="steps">{steps_html()}</div>
  <div class="bar">{BAR}</div>
 </div>
</div>'''


# ══════════════════════════════════════════ 피드 1080 × 1350 (4:5)
def feed():
    t = THEMES[THEME]
    W, H = 1080, 1350
    art = grid(W, H, t, horizon=.40) if THEME == 'B' else net(W, H, 11, t, .9)
    prize = ''.join(f'<div class="p"><span>{k}</span><b>{v}</b></div>' for k, v in PRIZE)
    tail = ('<div class="qr"><img src="' + qr_b64() + '">'
            '<div><div class="qt">신청 바로가기</div>'
            '<div class="qs">프로필 링크 · QR 스캔</div></div></div>') if MODE == '모집' else \
           f'<div class="prize"><div class="pk">총 시상 규모 <b>250만원</b></div>'\
           f'<div class="plist">{prize}</div></div>'\
           f'<div class="final"><div class="fk">FINAL</div>'\
           f'<div class="fd">10. 22.<span>(목)</span></div>'\
           f'<div class="fs">최종 발표 평가 및 시상 · 한국항공대학교</div></div>'
    return f'''<!doctype html><meta charset="utf-8"><style>{common_css(W,H,t)}
.in{{padding:78px 72px 64px}}
.eyebrow{{font-size:23px;margin-bottom:26px}}
.year{{font-size:34px;color:{t['body']};font-weight:700;margin-bottom:8px}}
h1{{font-size:82px;line-height:1.1;letter-spacing:-.02em;font-weight:700}}
.slogan{{font-size:26px;line-height:1.5;margin-top:26px}}
.steps{{margin-top:44px;display:grid;gap:12px}}
.step{{grid-template-columns:54px 1fr auto;gap:18px;padding:18px 26px}}
.step .n{{font-size:26px}} .step .t{{font-size:29px}} .step .d{{font-size:25px}}
.prize{{margin-top:30px;border:1px solid {t['cardline']};border-radius:18px;
 padding:26px 30px;background:{t['card']}}}
.pk{{font-size:26px;color:{t['body']};margin-bottom:16px}}
.pk b{{color:{t['c1']};font-size:32px}}
.plist{{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:14px;text-align:center}}
.p span{{display:block;font-size:22px;color:{t['dim']};margin-bottom:6px}}
.p b{{font-size:28px;color:#fff}}
.final{{margin-top:26px;border:2px solid {t['c1']};border-radius:20px;
 padding:26px 30px;background:rgba(34,230,255,.08);text-align:center}}
.fk{{font-size:21px;letter-spacing:.34em;color:{t['c1']};font-weight:700}}
.fd{{font-size:76px;font-weight:700;line-height:1.1;margin:4px 0 2px;
 text-shadow:{t['glowtxt']}}}
.fd span{{font-size:34px}}
.fs{{font-size:24px;color:{t['body']}}}
.qr{{margin-top:30px;background:#fff;border-radius:22px;padding:28px;display:flex;
 align-items:center;gap:28px}}
.qr img{{width:170px;height:170px;display:block}}
.qt{{font-size:36px;font-weight:700;color:#06122E}}
.qs{{font-size:24px;color:#54607A;margin-top:8px}}
.bar{{margin-top:auto;padding:20px 22px;column-gap:20px;grid-template-columns:auto auto auto auto}}
.lbl{{font-size:18px;padding:5px 12px}}
.logos{{gap:22px}}
.l-molab{{height:30px}} .l-hrdk{{height:26px}} .l-goyang{{height:35px}} .l-kdp{{height:28px}}
</style>
<div class="wrap">{art}<div class="scrim"></div><div class="glow"></div>
 <div class="in">
  <div class="eyebrow">{TITLE_SMALL}</div>
  <div class="year">{YEAR}</div>
  <h1><em>{T1}</em> {T2}</h1>
  <div class="slogan">{SLOGAN}</div>
  <div class="steps">{steps_html()}</div>
  {tail}
  <div class="bar">{BAR}</div>
 </div>
</div>'''


def shoot(name, html, w, h):
    src = HERE / f'{name}.html'
    src.write_text(html, encoding='utf-8')
    raw = HERE / f'_{name}_raw.png'
    subprocess.run([CHROME, '--headless', '--disable-gpu', '--no-sandbox',
                    '--hide-scrollbars', '--allow-file-access-from-files',
                    '--font-render-hinting=none', '--force-device-scale-factor=2',
                    f'--window-size={w},{h}', f'--screenshot={raw}',
                    f'file://{src}'], check=True, capture_output=True)
    im = Image.open(raw).convert('RGB').resize((w, h), Image.LANCZOS)
    out = HERE / f'{name}.png'
    im.save(out, quality=95)
    raw.unlink()
    print(f'   {out.name}  {w}×{h}')


def main():
    shoot(f'인스타_스토리_{MODE}_1080x1920', story(), 1080, 1920)
    shoot(f'인스타_게시물_{MODE}_1080x1350', feed(), 1080, 1350)


if __name__ == '__main__':
    main()
