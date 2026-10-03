#!/usr/bin/env python3
"""학생 배포용 안내문 — 16:9 발표 슬라이드용과 A4 인쇄용 두 판형."""
import base64, io, subprocess
from pathlib import Path
import segno

HERE = Path(__file__).resolve().parent
LOGO = HERE.parent / '2026-홍보물' / 'logo'
FONT = '/usr/share/fonts/truetype/nanum'
CHROME = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'

FORM_URL = 'https://forms.gle/jhbnBwNXsBiTEatQ7'
MAIL = 'ces@rebornmarket.org'

def b64(data):
    return 'data:image/png;base64,' + base64.b64encode(data).decode()

IMG = {k: b64((LOGO / f'{k}.png').read_bytes()) for k in ('molab', 'hrdk', 'goyang', 'kdp')}

def make_qr():
    buf = io.BytesIO()
    segno.make(FORM_URL, error='h').save(buf, kind='png', scale=20, border=2,
                                         dark='#0B1F46', light='white')
    (HERE / 'qr_신청서.png').write_bytes(buf.getvalue())
    return b64(buf.getvalue())

STEPS = [
    ('01', '서류 접수',             '9. 28.(월) ~ 10. 9.(금) 18:00', '참가신청서 + 사업계획서 온라인 제출'),
    ('02', '서류 합격자 발표',       '10. 12.(월)',                    '신청서에 적어주신 이메일로 개별 통보'),
    ('03', '온라인 팀별 멘토링',     '10. 13.(화) ~ 10. 18.(일)',       '서류 합격 팀 대상 · 팀당 1회 · 온라인'),
    ('04', '최종 발표 평가 및 시상',  '10. 22.(목)',                    '발표 심사 및 라이브 데모'),
]
PRIZES = [('대상', '1팀', '100만원'), ('최우수상', '1팀', '50만원'),
          ('우수상', '1팀', '30만원'), ('장려상', '7팀', '각 10만원 상당')]

TARGET_1 = '고양시 및 경기북부에 거주하는<br>대학교(대학원 포함) 재학생'
TARGET_2 = '개인 또는 1~4인 팀<br>전공 무관 · 코딩 경험 없어도 됩니다'

DOCS = ('<li><b>참가신청서</b> — 온라인 폼 작성 (팀명 · 팀원 · 연락처 · 아이템 한 줄 소개)</li>'
        '<li><b>AI 창업 아이템 사업계획서</b> 1부 — PDF · 한글(HWP) · 워드(DOCX) 중 택1, '
        '20MB 이내, <b>양식 자유</b></li>')
DOCS_NOTE = ('서류 심사는 사업계획서만으로 진행합니다. 프로토타입은 최종 발표에서 시연합니다. '
             '마감 전까지는 다시 제출하실 수 있으며, 마지막 제출본으로 평가합니다.')

CRITERIA = [('문제 정의 능력', 10), ('AI를 통한 솔루션의 적합성', 20), ('시장 규모', 15),
            ('비즈니스 모델 타당성', 20), ('아이템 구현에 대한 계획', 20), ('사업 의지', 15)]
CRIT_ROWS = ''.join(f'<tr><td class="p">{k}</td><td class="m">{v}점</td></tr>'
                    for k, v in CRITERIA)

NOTE = (f'※ <b>위 일정은 운영 사정에 따라 변경될 수 있으며, 변경 시 신청서에 적어주신 이메일로 '
        f'개별 안내드립니다.</b><br>'
        f'※ 창업 특강은 9. 28.(월) 12:00 ~ 14:00 한국항공대학교 대강당에서 진행합니다. '
        f'특강 참석은 선택이며 참가 자격과 무관합니다.　｜　'
        f'<span style="white-space:nowrap">문의 : {MAIL}</span>')

BAR = (f'<span class="lbl">주최</span><span class="logos">'
       f'<img class="l-molab" src="{IMG["molab"]}"><img class="l-hrdk" src="{IMG["hrdk"]}"></span>'
       f'<span class="lbl">주관</span><span class="logos">'
       f'<img class="l-goyang" src="{IMG["goyang"]}"><img class="l-kdp" src="{IMG["kdp"]}"></span>')

FONTCSS = f'''
@font-face{{font-family:'NS';src:url('file://{FONT}/NanumBarunGothic.ttf');font-weight:400}}
@font-face{{font-family:'NS';src:url('file://{FONT}/NanumBarunGothicBold.ttf');font-weight:700}}
'''

BASE = '''
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'NS',sans-serif;color:#1A2332;
 -webkit-print-color-adjust:exact;print-color-adjust:exact}
.wrap>*{flex:0 0 auto}
h1 em{font-style:normal;color:#6FE0FF}
.head{background:linear-gradient(120deg,#0B1F46 0%,#16336B 55%,#1E4FA0 100%);
 color:#fff;position:relative;overflow:hidden}
.head::after{content:'';position:absolute;border-radius:50%;
 background:radial-gradient(circle,rgba(93,214,255,.34),transparent 68%)}
.eyebrow{color:#8FD4FF}
.slogan{color:#CFE2FF}
.deadline{display:inline-block;background:#fff;color:#0B1F46;font-weight:700}
.deadline b{color:#C4372F}
h2{color:#0B1F46;border-left-style:solid;border-left-color:#1E4FA0;line-height:1.1}
.sub{font-weight:400;color:#6B7684}
.box{border-style:solid;border-color:#D5DCE6}
.step{display:grid;align-items:center;border-style:solid;border-color:#D5DCE6}
.step .n{font-weight:700;color:#9AAFC9}
.step .t{font-weight:700}
.step .d{color:#6B7684}
.step .w{font-weight:700;color:#1E4FA0;text-align:right;white-space:nowrap}
.step.now{border-color:#1E4FA0;background:#F3F7FE}
ul{list-style:none}
li{position:relative}
li::before{content:'·';position:absolute;left:0;color:#1E4FA0;font-weight:700}
small{color:#6B7684}
table{width:100%;border-collapse:collapse}
td{border-bottom-style:solid;border-bottom-color:#E8EDF3}
tr:last-child td{border-bottom:0}
td.p{font-weight:700;color:#0B1F46}
td.t{color:#6B7684;text-align:center}
td.m{text-align:right;font-weight:700;color:#1E4FA0}
.qr{background:#F3F7FE;border-style:solid;border-color:#C9DAF3;text-align:center}
.qr img{display:block;margin:0 auto;background:#fff}
.qr .u{font-weight:700;color:#0B1F46;word-break:break-all}
.note b{color:#C4372F}
.bar{display:grid;grid-template-columns:auto auto auto auto;justify-content:center;
 align-items:center}
.lbl{font-weight:700;color:#4A5568;background:#EDF1F7;text-align:center}
.logos{display:flex;align-items:center}
.logos img{display:block}
'''

# ── 16:9 (PowerPoint 와이드스크린 33.867 × 19.05 cm) ────────────────────────
def slide(qr):
    steps = ''.join(f'''<div class="step{' now' if i==0 else ''}">
      <div class="n">{n}</div>
      <div><div class="t">{t}</div><div class="d">{d}</div></div>
      <div class="w">{w}</div></div>''' for i, (n, t, w, d) in enumerate(STEPS))
    prizes = ''.join(f'<tr><td class="p">{a}</td><td class="t">{b}</td><td class="m">{c}</td></tr>'
                     for a, b, c in PRIZES)
    return f'''<!doctype html><meta charset="utf-8"><style>{FONTCSS}
@page{{size:338.67mm 190.5mm;margin:0}}{BASE}
.wrap{{width:338.67mm;height:190.5mm;padding:7mm 13mm 0;display:flex;flex-direction:column}}
.head{{border-radius:2.6mm;padding:3.6mm 9mm;display:flex;align-items:center;
 justify-content:space-between;gap:10mm}}
.head::after{{right:-16mm;top:-20mm;width:70mm;height:70mm}}
.eyebrow{{font-size:3.2mm;letter-spacing:.7mm;margin-bottom:2mm}}
h1{{font-size:8.6mm;line-height:1.12;letter-spacing:-.3mm}}
.slogan{{margin-top:2mm;font-size:4mm}}
.deadline{{border-radius:1.6mm;padding:3mm 6mm;font-size:4.8mm;text-align:center;
 line-height:1.4;position:relative;z-index:1;white-space:nowrap}}
.deadline span{{display:block;font-size:3.3mm;color:#5A6B85;font-weight:400;margin-bottom:.6mm}}
.cols{{display:grid;grid-template-columns:1fr 86mm 78mm;gap:8mm;margin-top:3.6mm;
 align-items:start}}
h2{{font-size:4.4mm;margin:0 0 1.8mm;padding-left:2.6mm;border-left-width:1.3mm}}
h2.gap{{margin-top:3.2mm}}
.sub{{font-size:3.3mm;margin-left:1.6mm}}
.step{{grid-template-columns:8mm 1fr 47mm;gap:3mm;border-width:.28mm;border-radius:2mm;
 padding:1.8mm 4mm;margin-bottom:1mm}}
.step .n{{font-size:4.4mm}} .step .t{{font-size:4.2mm}}
.step .d{{font-size:3.2mm;margin-top:.6mm}} .step .w{{font-size:4mm}}
.box{{border-width:.28mm;border-radius:2mm;padding:2.6mm 4.5mm}}
p,li{{font-size:3.5mm;line-height:1.45}}
li{{padding-left:3.4mm;margin-bottom:.6mm}}
small{{font-size:3.2mm}}
td{{font-size:3.5mm;padding:.75mm 0;border-bottom-width:.2mm}}
.qr{{border-width:.28mm;border-radius:2.4mm;padding:3.2mm 4mm 3mm}}
.qr img{{width:31mm;height:31mm;padding:1.2mm;border-radius:1.4mm}}
.qr .k{{font-size:4mm;font-weight:700;color:#0B1F46;margin-bottom:2mm}}
.qr .u{{font-size:3.2mm;margin-top:2.4mm}}
.qr .x{{font-size:3mm;color:#6B7684;margin-top:1.6mm;line-height:1.4}}
.docs{{margin-top:2.6mm;display:grid;grid-template-columns:1fr 104mm;gap:8mm;align-items:start}}
.crit{{padding-top:1.4mm;padding-bottom:1.4mm}}
.crit table{{table-layout:fixed}}
.crit td{{padding:.9mm 0;font-size:3.4mm}}
.note{{margin-top:2.2mm;font-size:3.1mm;color:#6B7684;line-height:1.45}}
.bar{{margin-top:auto;border-top:.3mm solid #D5DCE6;padding:2.6mm 0 3mm;column-gap:6mm}}
.lbl{{font-size:3mm;border-radius:1mm;padding:1mm 2.6mm}}
.logos{{gap:6.5mm}}
.l-molab{{height:5.6mm}} .l-hrdk{{height:4.8mm}} .l-goyang{{height:6.4mm}} .l-kdp{{height:5.2mm}}
</style>
<div class="wrap">
 <div class="head">
  <div>
   <div class="eyebrow">고용노동부 · 한국산업인력공단 K-하이테크 플랫폼</div>
   <h1>2026년 고양시 <em>바이브 코딩</em> 창업경진대회</h1>
   <div class="slogan">코딩을 몰라도, AI에게 말로 시켜서 내 서비스를 만든다</div>
  </div>
  <div class="deadline"><span>서류 접수</span>9. 28.(월) ~ <b>10. 9.(금) 18:00</b></div>
 </div>

 <div class="cols">
  <div>
   <h2>추진 일정</h2>
   {steps}
  </div>
  <div>
   <h2>참가 대상</h2>
   <div class="box"><p><b>{TARGET_1}</b></p>
    <p style="margin-top:1.6mm"><small>{TARGET_2}</small></p></div>
   <h2 class="gap">시상 <span class="sub">총 250만원</span></h2>
   <div class="box" style="padding-top:2mm;padding-bottom:2mm"><table>{prizes}</table></div>
  </div>
  <div>
   <h2>신청하기</h2>
   <div class="qr">
    <div class="k">QR을 찍으면 바로 신청</div>
    <img src="{qr}">
    <div class="u">{FORM_URL}</div>
    <div class="x">신청서 작성과 사업계획서 첨부를<br>한 번에 하시면 접수 완료<br>
     Google 계정 로그인 필요</div>
   </div>
  </div>
 </div>

 <div class="docs">
  <div><h2>제출 서류</h2>
   <div class="box"><ul>{DOCS}</ul>
    <p style="margin-top:1.4mm"><small>{DOCS_NOTE}</small></p></div></div>
  <div><h2>서류 평가 <span class="sub">총 100점</span></h2>
   <div class="box crit"><table>{CRIT_ROWS}</table></div></div>
 </div>

 <div class="note">{NOTE}</div>
 <div class="bar">{BAR}</div>
</div>'''

# ── A4 세로 (인쇄·메일 첨부용) ──────────────────────────────────────────────
def a4(qr):
    steps = ''.join(f'''<div class="step{' now' if i==0 else ''}">
      <div class="n">{n}</div>
      <div><div class="t">{t}</div><div class="d">{d}</div></div>
      <div class="w">{w}</div></div>''' for i, (n, t, w, d) in enumerate(STEPS))
    prizes = ''.join(f'<tr><td class="p">{a}</td><td class="t">{b}</td><td class="m">{c}</td></tr>'
                     for a, b, c in PRIZES)
    return f'''<!doctype html><meta charset="utf-8"><style>{FONTCSS}
@page{{size:210mm 297mm;margin:0}}{BASE}
.wrap{{width:210mm;height:297mm;padding:10mm 15mm 0;display:flex;flex-direction:column}}
.head{{border-radius:3mm;padding:3.6mm 9mm}}
.head::after{{right:-14mm;top:-16mm;width:56mm;height:56mm}}
.eyebrow{{font-size:3.3mm;letter-spacing:.7mm;margin-bottom:2.6mm}}
h1{{font-size:7.4mm;line-height:1.14;letter-spacing:-.2mm}}
.slogan{{margin-top:2.4mm;font-size:4.1mm}}
.deadline{{margin-top:2.8mm;border-radius:1.6mm;padding:1.9mm 4.2mm;font-size:4mm}}
h2{{font-size:4.2mm;margin:2.1mm 0 1.3mm;padding-left:2.6mm;border-left-width:1.3mm}}
.sub{{font-size:3.4mm;margin-left:1.6mm}}
.step{{grid-template-columns:7mm 1fr 46mm;gap:3mm;border-width:.28mm;border-radius:2mm;
 padding:1.4mm 4mm;margin-bottom:.8mm}}
.step .n{{font-size:4.6mm}} .step .t{{font-size:4.1mm}}
.step .d{{font-size:3.1mm;margin-top:.6mm}} .step .w{{font-size:3.9mm}}
.cols{{display:grid;grid-template-columns:1fr 1fr;gap:6mm;align-items:stretch}}
.cols>div{{display:flex;flex-direction:column}}
.cols>div>.box{{flex:1}}
.box{{border-width:.28mm;border-radius:2mm;padding:2.1mm 4.5mm}}
p,li{{font-size:3.5mm;line-height:1.5}}
li{{padding-left:3.4mm}}
small{{font-size:3.15mm}}
td{{font-size:3.4mm;padding:.8mm 0;border-bottom-width:.2mm}}
.qr{{border-width:.28mm;border-radius:2mm;padding:2.8mm 5mm;display:grid;
 grid-template-columns:1fr 30mm;gap:5mm;align-items:center;text-align:left}}
.qr img{{width:30mm;height:30mm;padding:1.2mm;border-radius:1.2mm}}
.qr .k{{font-size:3.7mm;font-weight:700;color:#0B1F46;margin-bottom:1.4mm}}
.qr .u{{font-size:3.5mm;margin:1.4mm 0}}
.qr .x{{font-size:3.1mm;color:#6B7684;line-height:1.45}}
.note{{margin-top:2.4mm;font-size:3.05mm;color:#6B7684;line-height:1.5}}
.crit{{font-size:3.2mm;line-height:1.55;padding-top:1.5mm;padding-bottom:1.5mm}}
.crit b{{color:#1E4FA0}}
.bar{{margin-top:auto;border-top:.3mm solid #D5DCE6;padding:2.2mm 0 2.2mm;column-gap:5mm}}
.lbl{{font-size:2.9mm;border-radius:1mm;padding:1mm 2.4mm}}
.logos{{gap:6mm}}
.l-molab{{height:5.4mm}} .l-hrdk{{height:4.6mm}} .l-goyang{{height:6.2mm}} .l-kdp{{height:5mm}}
</style>
<div class="wrap">
 <div class="head">
  <div class="eyebrow">고용노동부 · 한국산업인력공단 K-하이테크 플랫폼</div>
  <h1>2026년 고양시<br><em>바이브 코딩</em> 창업경진대회</h1>
  <div class="slogan">코딩을 몰라도, AI에게 말로 시켜서 내 서비스를 만든다</div>
  <div class="deadline">서류 접수 &nbsp;9. 28.(월) ~ <b>10. 9.(금) 18:00</b></div>
 </div>
 <h2>추진 일정</h2>
 {steps}
 <div class="cols">
  <div><h2>참가 대상</h2>
   <div class="box"><p><b>{TARGET_1}</b></p>
    <p style="margin-top:1.6mm"><small>{TARGET_2}</small></p></div></div>
  <div><h2>시상 <span class="sub">총 250만원</span></h2>
   <div class="box"><table>{prizes}</table></div></div>
 </div>
 <h2>제출 서류</h2>
 <div class="box"><ul>{DOCS}</ul>
  <p style="margin-top:1.6mm"><small>{DOCS_NOTE}</small></p></div>
 <h2>서류 평가 <span class="sub">총 100점</span></h2>
 <div class="box crit">{' · '.join(f'<span style="white-space:nowrap">{k} <b>{v}</b></span>' for k, v in CRITERIA)}</div>
 <h2>신청 방법</h2>
 <div class="qr">
  <div><div class="k">QR을 찍으면 바로 신청서로 연결됩니다</div>
   <div class="u">{FORM_URL}</div>
   <div class="x">신청서 작성과 사업계획서 첨부를 한 번에 하시면 접수가 완료됩니다.
    파일 첨부를 위해 Google 계정 로그인이 필요합니다.
    업로드가 되지 않으면 <b>{MAIL}</b> 로 메일 제출하셔도 접수됩니다.</div></div>
  <img src="{qr}">
 </div>
 <div class="note">{NOTE}</div>
 <div class="bar">{BAR}</div>
</div>'''

def render(name, html):
    src = HERE / f'{name}.html'
    src.write_text(html, encoding='utf-8')
    out = HERE / f'{name}.pdf'
    subprocess.run([CHROME, '--headless', '--disable-gpu', '--no-sandbox',
                    '--allow-file-access-from-files', '--font-render-hinting=none',
                    f'--print-to-pdf={out}', '--no-pdf-header-footer',
                    f'file://{src}'], check=True, capture_output=True)
    print('  ', out.name)

def main():
    qr = make_qr()
    render('참가신청_안내문_16대9', slide(qr))
    render('참가신청_안내문_A4', a4(qr))

if __name__ == '__main__':
    main()
