#!/usr/bin/env python3
"""2026년 고양시 바이브 코딩 창업경진대회 — 학생 배포용 A4 안내문 1쪽."""
import base64, subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOGO = HERE.parent / '2026-홍보물' / 'logo'
FONT = '/usr/share/fonts/truetype/nanum'
CHROME = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'

def b64(p):
    return 'data:image/png;base64,' + base64.b64encode(Path(p).read_bytes()).decode()

IMG = {k: b64(LOGO / f'{k}.png') for k in ('molab', 'hrdk', 'goyang', 'kdp')}

FORM_URL = '여기에 구글폼 주소를 넣어주세요'     # 폼 생성 후 교체
MAIL = 'ces@rebornmarket.org'

STEPS = [
    ('01', '서류 접수',            '9. 28.(월) ~ 10. 9.(금) 18:00', '참가신청서 + 사업계획서 온라인 제출'),
    ('02', '서류 합격자 발표',      '10. 12.(월)',                   '신청서에 적어주신 이메일로 개별 통보'),
    ('03', '온라인 팀별 멘토링',    '10. 13.(화) ~ 10. 18.(일)',      '서류 합격 팀 대상 · 팀당 1회 · 온라인'),
    ('04', '최종 발표 평가 및 시상', '10. 22.(목)',                   '발표 심사 및 라이브 데모'),
]

PRIZES = [('대상', '1팀', '100만원'), ('최우수상', '1팀', '50만원'),
          ('우수상', '1팀', '30만원'), ('장려상', '7팀', '각 10만원 상당')]

HTML = f'''<!doctype html><meta charset="utf-8">
<style>
@font-face{{font-family:'NS';src:url('file://{FONT}/NanumBarunGothic.ttf');font-weight:400}}
@font-face{{font-family:'NS';src:url('file://{FONT}/NanumBarunGothicBold.ttf');font-weight:700}}
@page{{size:210mm 297mm;margin:0}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'NS',sans-serif;color:#1A2332;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
.wrap{{width:210mm;height:297mm;padding:12mm 15mm 0;display:flex;flex-direction:column}}
.wrap>*{{flex:0 0 auto}}

.head{{background:linear-gradient(120deg,#0B1F46 0%,#16336B 55%,#1E4FA0 100%);
 color:#fff;border-radius:3mm;padding:4.5mm 9mm 4.5mm;position:relative;overflow:hidden}}
.head::after{{content:'';position:absolute;right:-14mm;top:-16mm;width:56mm;height:56mm;
 border-radius:50%;background:radial-gradient(circle,rgba(93,214,255,.34),transparent 68%)}}
.eyebrow{{font-size:3.3mm;letter-spacing:.7mm;color:#8FD4FF;margin-bottom:2.6mm}}
h1{{font-size:8mm;line-height:1.14;letter-spacing:-.2mm}}
h1 em{{font-style:normal;color:#6FE0FF}}
.slogan{{margin-top:2.4mm;font-size:4.1mm;color:#CFE2FF}}
.deadline{{margin-top:3.6mm;display:inline-block;background:#fff;color:#0B1F46;
 border-radius:1.6mm;padding:2.2mm 4.2mm;font-size:4.1mm;font-weight:700}}
.deadline b{{color:#C4372F}}

h2{{font-size:4.4mm;color:#0B1F46;margin:3.2mm 0 1.8mm;padding-left:2.6mm;
 border-left:1.3mm solid #1E4FA0;line-height:1.1}}
.sub{{font-weight:400;font-size:3.4mm;color:#6B7684;margin-left:1.6mm}}

.step{{display:grid;grid-template-columns:7mm 1fr 46mm;align-items:center;gap:3mm;
 border:.28mm solid #D5DCE6;border-radius:2mm;padding:2mm 4mm;margin-bottom:1.1mm}}
.step .n{{font-size:4.6mm;font-weight:700;color:#9AAFC9}}
.step .t{{font-size:4.1mm;font-weight:700}}
.step .d{{font-size:3.1mm;color:#6B7684;margin-top:.6mm}}
.step .w{{font-size:3.9mm;font-weight:700;color:#1E4FA0;text-align:right;white-space:nowrap}}
.step.now{{border-color:#1E4FA0;border-width:.6mm;background:#F3F7FE}}

.cols{{display:grid;grid-template-columns:1fr 1fr;gap:6mm;align-items:stretch}}
.cols>div{{display:flex;flex-direction:column}}
.cols>div>.box{{flex:1}}
.box{{border:.28mm solid #D5DCE6;border-radius:2mm;padding:2.8mm 4.5mm}}
.box .k{{font-size:3.5mm;font-weight:700;color:#1E4FA0;margin-bottom:2mm}}
p,li{{font-size:3.5mm;line-height:1.5}}
ul{{list-style:none}}
li{{padding-left:3.4mm;position:relative}}
li::before{{content:'·';position:absolute;left:.9mm;color:#1E4FA0;font-weight:700}}
small{{font-size:3.15mm;color:#6B7684}}

table{{width:100%;border-collapse:collapse}}
td{{font-size:3.5mm;padding:1.15mm 0;border-bottom:.2mm solid #E8EDF3}}
tr:last-child td{{border-bottom:0}}
td.p{{font-weight:700;color:#0B1F46}}
td.t{{color:#6B7684;text-align:center}}
td.m{{text-align:right;font-weight:700;color:#1E4FA0}}

.how{{background:#F3F7FE;border:.28mm solid #C9DAF3;border-radius:2mm;padding:3mm 5mm}}
.how .u{{font-size:3.7mm;font-weight:700;color:#0B1F46;word-break:break-all;margin:1.3mm 0 1.5mm}}

.note{{margin-top:2.4mm;font-size:3.05mm;color:#6B7684;line-height:1.5}}
.note b{{color:#C4372F}}

.bar{{margin-top:auto;border-top:.3mm solid #D5DCE6;padding:2.6mm 0 2.5mm;
 display:grid;grid-template-columns:auto auto;justify-content:center;
 align-items:center;column-gap:5mm;row-gap:2.6mm}}
.lbl{{font-size:2.9mm;font-weight:700;color:#4A5568;background:#EDF1F7;
 border-radius:1mm;padding:1mm 2.4mm;text-align:center}}
.logos{{display:flex;align-items:center;gap:6mm}}
.logos img{{display:block}}
.l-molab{{height:5.4mm}} .l-hrdk{{height:4.6mm}}
.l-goyang{{height:6.2mm}} .l-kdp{{height:5mm}}
</style>
<div class="wrap">

 <div class="head">
  <div class="eyebrow">고용노동부 · 한국산업인력공단 K-하이테크 플랫폼</div>
  <h1>2026년 고양시<br><em>바이브 코딩</em> 창업경진대회</h1>
  <div class="slogan">코딩을 몰라도, AI에게 말로 시켜서 내 서비스를 만든다</div>
  <div class="deadline">서류 접수 &nbsp;9. 28.(월) ~ <b>10. 9.(금) 18:00</b></div>
 </div>

 <h2>추진 일정</h2>
 {''.join(f"""<div class="step{' now' if i==0 else ''}">
   <div class="n">{n}</div>
   <div><div class="t">{t}</div><div class="d">{d}</div></div>
   <div class="w">{w}</div></div>""" for i,(n,t,w,d) in enumerate(STEPS))}

 <div class="cols">
  <div>
   <h2>참가 대상</h2>
   <div class="box">
    <p><b>고양시 및 경기북부에 거주하는<br>대학교(대학원 포함) 재학생</b></p>
    <p style="margin-top:1.6mm"><small>개인 또는 1~4인 팀<br>
     전공 무관 · 코딩 경험 없어도 됩니다</small></p>
   </div>
  </div>
  <div>
   <h2>시상 <span class="sub">총 250만원</span></h2>
   <div class="box">
    <table>{''.join(f'<tr><td class="p">{a}</td><td class="t">{b}</td><td class="m">{c}</td></tr>' for a,b,c in PRIZES)}</table>
   </div>
  </div>
 </div>

 <h2>제출 서류</h2>
 <div class="box">
  <ul>
   <li><b>참가신청서</b> — 온라인 폼 작성 (팀명 · 팀원 · 연락처 · 아이템 한 줄 소개)</li>
   <li><b>AI 창업 아이템 사업계획서</b> 1부 — PDF · 한글(HWP) · 워드(DOCX) 중 택1, 20MB 이내, <b>양식 자유</b></li>
  </ul>
  <p style="margin-top:1.6mm"><small>서류 심사는 사업계획서만으로 진행합니다. 프로토타입은 최종 발표에서 시연합니다.
  마감 전까지는 다시 제출하실 수 있으며, 마지막 제출본으로 평가합니다.</small></p>
 </div>

 <h2>신청 방법</h2>
 <div class="how">
  <p>아래 주소에서 <b>참가신청서 작성과 사업계획서 첨부를 한 번에</b> 하시면 접수가 완료됩니다.</p>
  <div class="u">{FORM_URL}</div>
  <p><small>파일 첨부를 위해 Google 계정 로그인이 필요합니다.
   업로드가 되지 않으면 <b>{MAIL}</b> 로 메일 제출하셔도 접수됩니다.</small></p>
 </div>

 <div class="note">
  ※ <b>위 일정은 운영 사정에 따라 변경될 수 있으며, 변경 시 신청서에 적어주신 이메일로 개별 안내드립니다.</b><br>
  ※ 창업 특강(바이브 코딩 실습 2시간)은 9. 28.(월) 13:00 한국항공대학교 대강당에서 진행합니다.
     특강 참석은 선택이며 참가 자격과 무관합니다.<br>
  ※ 문의 : (주)리본마켓 {MAIL}
 </div>

 <div class="bar">
  <span class="lbl">주최</span>
  <span class="logos"><img class="l-molab" src="{IMG['molab']}"><img class="l-hrdk" src="{IMG['hrdk']}"></span>
  <span class="lbl">주관</span>
  <span class="logos"><img class="l-goyang" src="{IMG['goyang']}"><img class="l-kdp" src="{IMG['kdp']}"></span>
 </div>

</div>'''

def main():
    src = HERE / '참가신청_안내문.html'
    src.write_text(HTML, encoding='utf-8')
    out = HERE / '참가신청_안내문.pdf'
    subprocess.run([CHROME, '--headless', '--disable-gpu', '--no-sandbox',
                    '--allow-file-access-from-files', '--font-render-hinting=none',
                    f'--print-to-pdf={out}', '--no-pdf-header-footer',
                    f'file://{src}'], check=True, capture_output=True)
    print('  ', out.name)

if __name__ == '__main__':
    main()
