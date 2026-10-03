#!/usr/bin/env python3
"""초기창업 시작하기 — 강의자료 30장 (16:9, 338.67 × 190.5mm)."""
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
FONT = '/usr/share/fonts/truetype/nanum'
CHROME = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'

TITLE = '초기창업 시작하기'
SUB = '사업자등록부터 정부지원사업 · 벤처투자까지'
ORG = '한국항공대학교 SW중심대학사업단 창업교육'
LECTURER = '(주)리본마켓'
MADE = '2025. 11. 30. 제작'

CSS = f'''
@font-face{{font-family:'NS';src:url('file://{FONT}/NanumBarunGothic.ttf');font-weight:400}}
@font-face{{font-family:'NS';src:url('file://{FONT}/NanumBarunGothicBold.ttf');font-weight:700}}
@font-face{{font-family:'SQ';src:url('file://{FONT}/NanumSquareB.ttf');font-weight:700}}
@page{{size:338.67mm 190.5mm;margin:0}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'NS',sans-serif;color:#1A2332;
 -webkit-print-color-adjust:exact;print-color-adjust:exact}}
.s{{width:338.67mm;height:190.5mm;padding:16mm 20mm 13mm;position:relative;
 display:flex;flex-direction:column;overflow:hidden;background:#fff}}
.s+.s{{page-break-before:always}}
.s>*{{flex:0 0 auto}}

.no{{position:absolute;right:14mm;bottom:7mm;font-size:3.4mm;color:#9AA5B4}}
.tag{{position:absolute;left:20mm;bottom:7mm;font-size:3.4mm;color:#9AA5B4}}

h2{{font-family:'SQ';font-size:9mm;color:#0B1F46;line-height:1.2;letter-spacing:-.3mm}}
.lead{{font-size:4.4mm;color:#5A6B85;margin-top:2.6mm}}
.rule{{height:1mm;width:26mm;background:#1E4FA0;margin:4.5mm 0 6mm}}
.body{{flex:1;min-height:0}}

/* 표지 */
.cover{{background:linear-gradient(125deg,#08152F 0%,#12305F 52%,#1E4FA0 100%);color:#fff;
 justify-content:center;padding:0 24mm}}
.cover::after{{content:'';position:absolute;right:-30mm;top:-40mm;width:150mm;height:150mm;
 border-radius:50%;background:radial-gradient(circle,rgba(93,214,255,.24),transparent 66%)}}
.cover .eyebrow{{font-size:4.6mm;color:#8FD4FF;letter-spacing:1.2mm;margin-bottom:6mm}}
.cover h1{{font-family:'SQ';font-size:20mm;line-height:1.12;letter-spacing:-.8mm;position:relative;z-index:1}}
.cover .sub{{font-size:6.4mm;color:#CFE2FF;margin-top:6mm}}
.cover .meta{{margin-top:16mm;font-size:4.4mm;color:#AFC8EA;line-height:1.9;
 border-top:.4mm solid rgba(255,255,255,.28);padding-top:6mm;position:relative;z-index:1}}
.cover .meta b{{color:#fff}}

/* 간지 */
.part{{background:#0B1F46;color:#fff;justify-content:center;padding:0 26mm}}
.part .pn{{font-family:'SQ';font-size:5mm;color:#6FE0FF;letter-spacing:2mm;margin-bottom:5mm}}
.part h2{{color:#fff;font-size:14mm}}
.part ul{{margin-top:11mm;list-style:none;display:grid;grid-template-columns:1fr 1fr 1fr;gap:7mm}}
.part li{{font-size:4.4mm;color:#CFE2FF;line-height:1.55;padding-top:4mm;
 border-top:.5mm solid rgba(255,255,255,.3)}}
.part li b{{display:block;font-size:5mm;color:#fff;margin-bottom:1.6mm}}

/* 공통 블록 */
.cols{{display:grid;gap:7mm}}
.body.cols{{height:100%}}
.c2{{grid-template-columns:1fr 1fr}} .c3{{grid-template-columns:1fr 1fr 1fr}}
.card{{border:.3mm solid #D5DCE6;border-radius:2.4mm;padding:6mm 6.5mm}}
.card.fill{{background:#F4F7FC;border-color:#C9DAF3}}
.card .k{{font-size:4.6mm;font-weight:700;color:#0B1F46;margin-bottom:3.4mm}}
.card .k em{{font-style:normal;color:#1E4FA0}}
p,li{{font-size:4.1mm;line-height:1.72}}
ul.dot{{list-style:none}}
ul.dot>li{{padding-left:4.6mm;position:relative;margin-bottom:2mm}}
ul.dot>li::before{{content:'';position:absolute;left:.6mm;top:2.4mm;width:1.6mm;height:1.6mm;
 border-radius:50%;background:#1E4FA0}}
.hl{{color:#C4372F;font-weight:700}}
.num{{color:#1E4FA0;font-weight:700}}
small{{font-size:3.5mm;color:#6B7684;line-height:1.6}}

table{{width:100%;border-collapse:collapse}}
th{{background:#0B1F46;color:#fff;font-size:3.9mm;padding:3.2mm 3mm;text-align:left;font-weight:700}}
td{{border-bottom:.25mm solid #E1E7EF;font-size:3.9mm;padding:3mm;vertical-align:top;line-height:1.5}}
tr:last-child td{{border-bottom:0}}
td.h{{font-weight:700;color:#0B1F46;background:#F4F7FC}}
td.c{{text-align:center}}
.z tr:nth-child(even) td{{background:#FAFBFD}}

.steps{{display:grid;grid-auto-flow:column;grid-auto-columns:1fr;gap:4mm}}
.step{{border:.3mm solid #D5DCE6;border-radius:2.4mm;padding:5mm 4.5mm;position:relative}}
.step .n{{font-family:'SQ';font-size:8mm;color:#C9DAF3;line-height:1}}
.step .t{{font-size:4.4mm;font-weight:700;margin:2.4mm 0 2mm;color:#0B1F46}}
.step .d{{font-size:3.5mm;color:#6B7684;line-height:1.55}}

.note{{margin-top:auto;background:#F4F7FC;border-left:1.4mm solid #1E4FA0;
 padding:4mm 5mm;font-size:3.7mm;color:#33445E;line-height:1.65}}
.note b{{color:#0B1F46}}
.warn{{background:#FDF4F3;border-left-color:#C4372F}}
.warn b{{color:#C4372F}}
'''


def slide(inner, n=None, cls='', tag=''):
    foot = f'<div class="no">{n}</div>' if n else ''
    foot += f'<div class="tag">{tag}</div>' if tag else ''
    return f'<div class="s {cls}">{inner}{foot}</div>'


def head(t, lead=''):
    return f'<h2>{t}</h2>' + (f'<div class="lead">{lead}</div>' if lead else '') + '<div class="rule"></div>'


def part(pn, t, items):
    li = ''.join(f'<li><b>{a}</b>{b}</li>' for a, b in items)
    return f'<div class="pn">PART {pn}</div><h2>{t}</h2><ul>{li}</ul>'


def card(k, body, fill=False):
    return f'<div class="card{" fill" if fill else ""}"><div class="k">{k}</div>{body}</div>'


def dots(*items):
    return '<ul class="dot">' + ''.join(f'<li>{i}</li>' for i in items) + '</ul>'


def table(headers, rows, z=True):
    th = ''.join(f'<th>{h}</th>' for h in headers)
    tr = ''
    for r in rows:
        tds = ''
        for i, c in enumerate(r):
            cls = ' class="h"' if i == 0 else ''
            tds += f'<td{cls}>{c}</td>'
        tr += f'<tr>{tds}</tr>'
    return f'<table class="{"z" if z else ""}"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>'


def steps(items):
    return '<div class="steps">' + ''.join(
        f'<div class="step"><div class="n">{n}</div><div class="t">{t}</div><div class="d">{d}</div></div>'
        for n, t, d in items) + '</div>'


# ══════════════════════════════════════════════════════ 슬라이드 본문
S = []

# 1 표지
S.append(slide(f'''
 <div class="eyebrow">{ORG}</div>
 <h1>{TITLE}</h1>
 <div class="sub">{SUB}</div>
 <div class="meta">
  대상 <b>창업에 관심 있는 재학생 · 예비창업자</b> &nbsp;｜&nbsp; 교육시간 <b>2시간</b><br>
  강의 <b>{LECTURER}</b> &nbsp;｜&nbsp; {MADE}
 </div>''', cls='cover'))

# 2 강의 개요
S.append(slide(head('이 강의가 답하는 질문',
  '창업을 "생각"에서 "실행"으로 옮길 때 실제로 부딪히는 순서대로 다룹니다.') + f'''
 <div class="body cols c2">
  {card('강의 목표', dots(
    '창업 첫 3개월에 <b>무엇을 어떤 순서로</b> 해야 하는지 안다',
    '개인사업자와 법인 중 <b>내 상황에 맞는 선택</b>을 판단할 수 있다',
    '정부지원사업을 <b>찾고 · 쓰고 · 정산</b>하는 흐름을 안다',
    '투자 유치가 <b>무엇을 주고 무엇을 받는 거래</b>인지 이해한다'), True)}
  {card('다루지 않는 것', dots(
    '개별 아이템에 대한 사업성 진단',
    '세무 · 법률 자문 (전문가 상담이 필요한 영역)',
    '특정 지원사업의 당해연도 공고 해석',
    '업종별 인허가 요건 (별도 확인 필요)')
    + '<div class="note" style="margin-top:5mm"><b>수치는 2025년 기준입니다.</b> '
      '세법 기준금액과 지원사업 규모는 매년 바뀌므로, 실제 신청 시점에 공고문을 다시 확인하세요.</div>')}
 </div>''', 2, tag=TITLE))

# 3 목차
S.append(slide(head('목차') + f'''
 <div class="body cols c3" style="align-content:start">
  {card('<em>PART 1</em> &nbsp;창업 준비', dots('창업 준비 5단계 로드맵', '시작 전 자가진단', '아이템 검증의 세 가지 질문'))}
  {card('<em>PART 2</em> &nbsp;사업자등록', dots('언제 · 어디서 · 무엇을', '업종과 과세유형 선택', '사업장 주소와 등록 직후 할 일'))}
  {card('<em>PART 3</em> &nbsp;개인 vs 법인', dots('항목별 비교', '세율과 자금 인출 구조', '전환 시점 판단'))}
  {card('<em>PART 4</em> &nbsp;정부지원사업', dots('지원사업 지도', '단계별 대표 사업', '사업계획서와 심사'))}
  {card('<em>PART 5</em> &nbsp;벤처투자 기초', dots('자금조달 사다리', '투자 단계와 투자자', '밸류에이션 · IR'))}
  {card('<em>마무리</em>', dots('오늘의 요약', '바로 쓰는 참고 사이트', 'Q &amp; A'))}
 </div>''', 3, tag=TITLE))

# 4 PART 1 간지
S.append(slide(part(1, '창업, 무엇부터 시작하나', [
  ('순서를 안다', '아이템 검증 → 사업자등록 → 자금 → 성장. 순서가 어긋나면 시간과 돈이 샌다'),
  ('나를 점검한다', '지금 시작해도 되는 상태인지 스스로 확인하는 여섯 가지'),
  ('아이템을 검증한다', '"좋은 아이디어"가 아니라 "팔리는 문제"인지 확인하는 방법'),
]), 4, cls='part'))

# 5 로드맵
S.append(slide(head('창업 준비 5단계 로드맵', '아래 순서를 건너뛰면 대부분 3번에서 막힙니다.') + f'''
 <div class="body">
  {steps([
    ('01', '아이템 검증', '고객 인터뷰 10명<br>문제가 진짜인지 확인'),
    ('02', '사업 모델 설계', '누가 · 왜 · 얼마를<br>지불하는지 정의'),
    ('03', '사업자등록', '개인/법인 결정<br>업종 · 과세유형 선택'),
    ('04', '자금 확보', '자기자본 → 정부지원<br>→ 융자 → 투자'),
    ('05', '성장과 검증', '매출 · 재구매 지표<br>다음 단계 자금 준비'),
  ])}
  <div class="note"><b>1~2단계에 충분히 시간을 쓰세요.</b> 사업자등록은 하루면 되지만,
  검증되지 않은 아이템으로 등록부터 하면 매달 나가는 고정비와 4대보험, 세무 신고 의무가 먼저 생깁니다.
  등록 시점은 <span class="hl">매출이 발생하기 직전</span>이 가장 좋습니다.</div>
 </div>''', 5, tag='PART 1  창업 준비'))

# 6 자가진단
S.append(slide(head('시작 전 자가진단', '여섯 항목 중 네 개 이상 "예"가 되기 전에는 등록을 미루세요.') + f'''
 <div class="body cols c2">
  {card('꼭 확인할 여섯 가지', table(['점검 항목', '확인'], [
    ['해결하려는 문제를 한 문장으로 말할 수 있다', '□'],
    ['그 문제를 겪는 사람을 10명 이상 직접 만났다', '□'],
    ['돈을 낼 사람과 쓸 사람이 같은지 구분했다', '□'],
    ['6개월 버틸 생활비가 확보되어 있다', '□'],
    ['혼자 못 하는 일을 누가 할지 정했다', '□'],
    ['해당 업종의 인허가 요건을 확인했다', '□'],
  ], z=False))}
  {card('자주 하는 착각', dots(
    '<b>"아이디어가 좋으면 된다"</b> → 실행과 검증이 9할입니다',
    '<b>"일단 등록하고 보자"</b> → 등록 순간부터 신고 의무가 생깁니다',
    '<b>"지원금 받아서 시작하자"</b> → 지원사업은 <span class="hl">이미 하는 일</span>을 가속하는 수단입니다',
    '<b>"투자부터 받자"</b> → 초기 투자 판단 기준은 대부분 팀과 실행 속도입니다')
    + '<div class="note warn"><b>가장 흔한 실패 순서</b><br>'
      '등록 → 사무실 계약 → 개발 6개월 → 첫 고객 만남 → 문제가 없었음을 발견</div>')}
 </div>''', 6, tag='PART 1  창업 준비'))

# 7 아이템 검증
S.append(slide(head('아이템 검증 — 세 가지 질문', '이 세 칸을 채우지 못하면 아직 사업이 아니라 아이디어입니다.') + f'''
 <div class="body cols c3">
  {card('1 &nbsp;문제', dots(
    '누가 겪는 문제인가 (대상을 좁게)',
    '얼마나 자주 겪는가',
    '지금은 어떻게 해결하고 있는가',
    '그 대안이 왜 불편한가')
    + '<div class="note"><b>확인 방법</b><br>고객 인터뷰. "이거 필요하세요?"가 아니라 '
      '<b>"최근에 그 일을 어떻게 하셨어요?"</b>라고 묻습니다.</div>', True)}
  {card('2 &nbsp;고객', dots(
    '첫 100명은 누구인가',
    '그들을 어디서 만날 수 있는가',
    '돈을 내는 사람과 쓰는 사람이 같은가',
    '시장 규모는 얼마나 되는가')
    + '<div class="note"><b>시장 규모 추정</b><br>'
      'TAM(전체) → SAM(유효) → SOM(초기 확보 가능). 근거 있는 숫자로 좁혀 갑니다.</div>')}
  {card('3 &nbsp;해결', dots(
    '기존 대안 대비 무엇이 나은가',
    '왜 지금인가 (시장 · 기술 변화)',
    '우리가 해야 하는 이유는 무엇인가',
    '최소 기능(MVP)은 무엇인가')
    + '<div class="note"><b>MVP의 기준</b><br>'
      '"만들 수 있는 최소"가 아니라 <b>"고객이 돈을 낼지 확인할 수 있는 최소"</b>입니다.</div>')}
 </div>''', 7, tag='PART 1  창업 준비'))

# 8 PART 2 간지
S.append(slide(part(2, '사업자등록 실무', [
  ('언제 해야 하나', '사업 개시일부터 20일 이내. 늦으면 가산세와 매입세액 불공제'),
  ('무엇을 정해야 하나', '업태 · 종목, 과세유형, 사업장 주소 — 나중에 바꾸기 번거로운 항목'),
  ('등록 후 무엇을 하나', '통장 · 카드 등록, 세무 일정 확인, 4대보험'),
]), 8, cls='part'))

# 9 사업자등록 개요
S.append(slide(head('사업자등록 — 언제 · 어디서 · 무엇을') + f'''
 <div class="body cols c3">
  {card('언제', dots(
    '사업 개시일부터 <span class="hl">20일 이내</span>',
    '개시 전에도 신청 가능 (사업 준비 단계)',
    '늦으면 <b>가산세</b>와 등록 전 <b>매입세액 불공제</b>')
    + '<div class="note"><b>실무 팁</b><br>인테리어비 · 장비 구입 등 초기 지출이 크다면, '
      '지출 전에 등록해야 매입세액 공제를 받습니다.</div>', True)}
  {card('어디서', dots(
    '<b>홈택스</b> 온라인 신청 (공동·금융인증서 필요)',
    '세무서 민원실 방문',
    '처리 기간 보통 <b>2~3일</b>, 즉시 발급되기도 함',
    '수수료 없음'))}
  {card('무엇을 (서류)', table(['구분', '서류'], [
    ['공통', '사업자등록 신청서'],
    ['임차', '임대차계약서 사본'],
    ['자택', '별도 서류 불필요 (업종 제한 확인)'],
    ['인허가업종', '인허가증 사본'],
    ['법인', '법인등기부등본 · 정관 · 주주명부'],
    ['공동', '동업계약서'],
  ], z=False))}
 </div>''', 9, tag='PART 2  사업자등록'))

# 10 업종
_upjong = ('<p><b>업태</b>는 사업의 형태, <b>종목</b>은 구체적인 취급 품목입니다.</p>'
           + table(['예시', '업태', '종목'], [
               ['앱 개발', '정보통신업', '소프트웨어 개발 및 공급업'],
               ['온라인 쇼핑몰', '도소매업', '전자상거래 소매업'],
               ['컨설팅', '서비스업', '경영컨설팅업'],
               ['카페', '음식점업', '커피 전문점'],
           ]))
S.append(slide(head('업종(업태 · 종목) 정하기', '한 번 정하면 세금·지원사업·인허가가 모두 여기에 묶입니다.') + f'''
 <div class="body cols c2">
  {card('업태와 종목', _upjong)}
  {card('정할 때 주의할 점', dots(
    '실제 하는 일과 <b>다르면 안 됩니다</b>. 지원사업 · 세액감면 심사에서 확인합니다',
    '주업종코드가 <b>단순경비율 · 세액감면</b> 적용 기준이 됩니다',
    '여러 개를 등록할 수 있고, 매출이 가장 큰 것이 <b>주업종</b>이 됩니다',
    '나중에 추가 · 변경 가능하지만 <b>정정 신고</b>가 필요합니다',
    '인허가 업종(식품 · 교육 · 의료 · 여행 등)은 <span class="hl">등록 전에</span> 인허가부터')
    + '<div class="note"><b>창업중소기업 세액감면</b>을 노린다면 업종이 결정적입니다. '
      '수도권 과밀억제권역 밖 창업, 청년 창업 등 조건에 따라 소득세·법인세를 '
      '<b>50~100%</b> 감면받을 수 있으나, 감면 대상 업종이 법에 열거되어 있습니다.</div>')}
 </div>''', 10, tag='PART 2  사업자등록'))

# 11 과세유형
S.append(slide(head('과세유형 — 일반과세자 vs 간이과세자', '2025년 기준. 기준금액은 매년 바뀔 수 있습니다.') + f'''
 <div class="body">
  {table(['구분', '일반과세자', '간이과세자'], [
    ['기준 (직전연도 공급대가)', '1억 400만원 이상', '<b>1억 400만원 미만</b>'],
    ['부가세율', '공급가액의 10%', '업종별 부가가치율 적용 (1.5~4%)'],
    ['매입세액 공제', '전액 공제', '매입액의 0.5% (제한적)'],
    ['세금계산서 발급', '가능', '연 매출 4,800만원 이상만 가능'],
    ['부가세 신고', '연 2회 (1월 · 7월)', '연 1회 (1월)'],
    ['납부 면제', '해당 없음', '연 매출 <span class="hl">4,800만원 미만이면 납부 면제</span>'],
  ])}
  <div class="note"><b>어느 쪽이 유리한가</b> — 매출 규모만 보고 정하지 마세요.
  초기 투자(장비 · 인테리어 · 개발 외주)가 커서 <b>매입세액이 많다면 일반과세자</b>가 유리합니다.
  간이과세자는 매입세액을 거의 돌려받지 못합니다. 또한 거래처가 사업자라면
  <b>세금계산서 발급</b>이 필요해 간이과세로는 거래 자체가 어려울 수 있습니다.
  <span class="hl">B2B 사업이라면 사실상 일반과세자를 선택하게 됩니다.</span></div>
 </div>''', 11, tag='PART 2  사업자등록'))

# 12 사업장 주소
S.append(slide(head('사업장 주소 정하기', '비용 · 지원사업 자격 · 세액감면이 모두 주소에 걸립니다.') + f'''
 <div class="body cols c2">
  {card('선택지 비교', table(['방식', '비용', '유의사항'], [
    ['자택', '없음', '업종 제한 · 주택 용도 확인 · 임대차 동의 필요'],
    ['공유오피스', '월 10~30만원', '비상주는 일부 업종 · 지원사업에서 불인정'],
    ['창업보육센터', '저렴 (입주 심사)', '대학 · 지자체 운영, 멘토링 연계'],
    ['일반 임차', '보증금 + 월세', '고정비 부담 큼, 초기에는 권하지 않음'],
  ], z=False))}
  {card('반드시 확인할 것', dots(
    '<b>지자체 지원사업</b>은 대부분 <span class="hl">관내 사업장</span>을 요건으로 합니다',
    '<b>창업중소기업 세액감면</b>은 수도권 과밀억제권역 여부에 따라 감면율이 갈립니다',
    '비상주 사무실은 <b>실제 사업장으로 인정받지 못하는 경우</b>가 있습니다',
    '주소 변경 시 <b>사업자등록 정정신고</b>가 필요합니다')
    + '<div class="note"><b>재학생이라면</b> 소속 대학의 창업보육센터 · 창업지원단을 먼저 확인하세요. '
      '주소 제공과 함께 시제품 제작 · 멘토링 · 교내 창업경진대회까지 연결되는 경우가 많습니다.</div>')}
 </div>''', 12, tag='PART 2  사업자등록'))

# 13 등록 직후
S.append(slide(head('등록 직후 해야 할 다섯 가지', '이 다섯 개를 놓치면 첫 신고 때 반드시 문제가 됩니다.') + f'''
 <div class="body">
  {steps([
    ('01', '사업용 계좌', '개인 돈과 분리.<br>국세청 신고 대상'),
    ('02', '사업용 신용카드', '홈택스 등록 시<br>매입세액 자동 집계'),
    ('03', '세금계산서 준비', '전자세금계산서용<br>사업자 인증서 발급'),
    ('04', '세무 일정 확인', '부가세 · 원천세<br>종합소득세/법인세'),
    ('05', '4대보험', '직원 채용 시<br>14일 이내 신고'),
  ])}
  <div class="note"><b>세무 일정 (개인 일반과세자 기준)</b><br>
  부가가치세 <b>1월 · 7월</b> (연 2회) &nbsp;｜&nbsp; 종합소득세 <b>5월</b> &nbsp;｜&nbsp;
  원천세 <b>매월 10일</b> (반기납 신청 시 연 2회) &nbsp;｜&nbsp; 법인은 부가세 연 4회 · 법인세는 사업연도 종료 후 3개월 이내<br>
  <span class="hl">매출이 없어도 신고 의무는 있습니다.</span> 무실적이면 무실적 신고를 해야 가산세가 붙지 않습니다.</div>
 </div>''', 13, tag='PART 2  사업자등록'))

# 14 PART 3 간지
S.append(slide(part(3, '개인사업자와 법인사업자', [
  ('무엇이 다른가', '설립 절차, 책임 범위, 세율, 돈을 꺼내는 방법이 전부 다르다'),
  ('무엇이 유리한가', '매출 규모와 투자 계획에 따라 답이 갈린다'),
  ('언제 바꾸나', '전환 시점을 판단하는 세 가지 신호'),
]), 14, cls='part'))

# 15 비교표
S.append(slide(head('한눈에 보는 비교') + f'''
 <div class="body">
  {table(['구분', '개인사업자', '법인사업자 (주식회사)'], [
    ['설립 절차', '사업자등록만 (1~3일)', '법인설립등기 후 사업자등록 (1~2주)'],
    ['설립 비용', '없음', '등록면허세 · 법무사 비용 등 30~60만원'],
    ['자본금', '제한 없음', '제한 없음 (실무상 100만원 이상 권장)'],
    ['책임 범위', '<span class="hl">무한책임</span> — 개인 재산까지', '유한책임 — 출자 범위 내 (대표 연대보증 시 예외)'],
    ['세율', '소득세 <b>6~45%</b> (8구간)', '법인세 <b>9~24%</b> (4구간)'],
    ['대표자 급여', '비용 처리 불가', '급여로 <b>비용 처리 가능</b>'],
    ['이익금 인출', '자유롭게 인출', '급여 · 배당 · 상여로만 (인출 시 과세)'],
    ['대외 신뢰도', '상대적으로 낮음', '높음 (관공서 · 대기업 거래에 유리)'],
    ['투자 유치', '<span class="hl">사실상 불가</span>', '가능 (지분 발행)'],
    ['폐업', '간단', '청산 절차 필요'],
  ])}
 </div>''', 15, tag='PART 3  개인 vs 법인'))

# 16 세율
S.append(slide(head('세금 차이 — 세율 구조', '단순히 "법인이 싸다"가 아닙니다. 꺼낼 때 한 번 더 냅니다.') + f'''
 <div class="body cols c2">
  {card('소득세 (개인) — 누진', table(['과세표준', '세율'], [
    ['1,400만원 이하', '6%'],
    ['1,400 ~ 5,000만원', '15%'],
    ['5,000 ~ 8,800만원', '24%'],
    ['8,800 ~ 1억 5천만원', '35%'],
    ['1억 5천 ~ 3억원', '38%'],
    ['3억 ~ 5억원', '40%'],
    ['5억 ~ 10억원', '42%'],
    ['10억원 초과', '45%'],
  ], z=False) + '<small>지방소득세 10% 별도</small>')}
  {card('법인세 — 4구간', table(['과세표준', '세율'], [
    ['2억원 이하', '9%'],
    ['2억 ~ 200억원', '19%'],
    ['200억 ~ 3,000억원', '21%'],
    ['3,000억원 초과', '24%'],
  ], z=False)
    + '<div class="note warn" style="margin-top:5mm"><b>법인세만 보면 안 됩니다.</b><br>'
      '법인의 이익은 <b>법인 돈</b>입니다. 대표가 쓰려면 급여(근로소득세) 또는 '
      '배당(배당소득세)으로 꺼내야 하고, 그때 <span class="hl">개인 소득세를 한 번 더</span> 냅니다. '
      '이를 <b>이중과세</b>라 합니다.</div>')}
 </div>''', 16, tag='PART 3  개인 vs 법인'))

# 17 전환 시점
S.append(slide(head('언제 법인으로 바꾸나', '아래 신호 중 하나라도 해당되면 전환을 검토할 시점입니다.') + f'''
 <div class="body cols c3">
  {card('신호 1 &nbsp;세금', dots(
    '과세표준이 <span class="hl">약 8,800만원</span>을 넘어 소득세율 35% 구간에 진입',
    '이익을 전부 인출하지 않고 <b>재투자</b>할 계획이 있다',
    '대표 급여를 비용으로 처리해 절세 여지가 있다')
    + '<div class="note"><b>기준선</b><br>단순 비교로는 과세표준 8,800만원 부근에서 법인이 유리해집니다. '
      '다만 인출 계획에 따라 달라지므로 세무사 상담을 권합니다.</div>', True)}
  {card('신호 2 &nbsp;투자', dots(
    '외부 <b>투자 유치</b>를 계획하고 있다',
    '공동창업자와 <b>지분</b>을 나눠야 한다',
    '스톡옵션으로 인재를 확보하려 한다',
    '<b>TIPS · 벤처기업 확인</b> 등을 준비한다')
    + '<div class="note warn"><b>투자를 받으려면 법인은 필수입니다.</b> '
      '개인사업자는 지분을 발행할 수 없어 투자 구조 자체가 성립하지 않습니다.</div>')}
  {card('신호 3 &nbsp;거래', dots(
    '대기업 · 공공기관과 거래하려 한다',
    '입찰 참여 자격에 법인이 요구된다',
    '매출 규모가 커져 신용도가 필요하다',
    '사업 리스크가 커져 <b>유한책임</b>이 필요하다')
    + '<div class="note"><b>전환 방법</b><br>① 개인 폐업 후 법인 신설 (간단, 일반적)<br>'
      '② 현물출자 · 사업양수도 (자산 이전, 절차 복잡)</div>')}
 </div>''', 17, tag='PART 3  개인 vs 법인'))

# 18 법인 설립 절차
S.append(slide(head('법인 설립 절차와 비용', '온라인(등기소 인터넷등기)으로 직접 하면 비용을 크게 줄일 수 있습니다.') + f'''
 <div class="body">
  {steps([
    ('01', '상호 · 목적 결정', '유사상호 확인<br>사업목적 문구 작성'),
    ('02', '정관 작성', '발기인 · 자본금<br>주식 수 · 액면가'),
    ('03', '자본금 납입', '발기인 계좌 입금<br>잔고증명서 발급'),
    ('04', '설립등기', '관할 등기소<br>또는 인터넷등기소'),
    ('05', '사업자등록', '등기부등본 첨부<br>세무서 · 홈택스'),
  ])}
  <div class="cols c2" style="margin-top:6mm">
   {card('비용 (자본금 1,000만원 기준 · 수도권)', table(['항목', '금액'], [
     ['등록면허세 · 지방교육세', '자본금의 0.48% (과밀억제권역 3배 중과)'],
     ['등기 수수료 · 인지대', '약 3~5만원'],
     ['법무사 대행 (선택)', '약 30~50만원'],
     ['법인인감 · 등기부등본', '약 3~5만원'],
   ], z=False))}
   {card('자주 놓치는 것', dots(
     '<b>사업목적</b>은 앞으로 할 일까지 넉넉히 넣으세요. 나중에 추가하려면 변경등기 비용이 듭니다',
     '<b>수도권 과밀억제권역</b>에 설립하면 등록면허세가 <span class="hl">3배 중과</span>됩니다',
     '<b>주주 구성</b>은 신중히. 초기 지분 분배는 되돌리기 어렵습니다',
     '설립 후 <b>주주명부 · 법인인감</b>을 반드시 보관하세요'))}
  </div>
 </div>''', 18, tag='PART 3  개인 vs 법인'))

# 19 PART 4 간지
S.append(slide(part(4, '정부지원사업 활용법', [
  ('어디에 무엇이 있나', '중앙부처 · 지자체 · 공공기관으로 나뉘는 지원사업 지도'),
  ('내 단계에 맞는 사업', '예비 → 초기(3년) → 도약(7년), 단계마다 문이 다르다'),
  ('어떻게 붙나', '사업계획서 PSST 구조와 심사에서 갈리는 지점'),
]), 19, cls='part'))

# 20 지원사업 지도
S.append(slide(head('지원사업 지도 — 누가 무엇을 주나') + f'''
 <div class="body cols c3">
  {card('중앙부처', dots(
    '<b>중소벤처기업부 / 창업진흥원</b><br>창업 사업화 지원의 중심',
    '<b>과학기술정보통신부</b><br>기술창업 · ICT 분야',
    '<b>고용노동부</b><br>고용 창출 · 인건비 연계',
    '<b>특허청</b><br>IP 나래 · 지식재산 지원')
    + '<div class="note"><b>창구</b><br>K-Startup (k-startup.go.kr)<br>기업마당 (bizinfo.go.kr)</div>', True)}
  {card('지자체', dots(
    '<b>시 · 도 창업지원센터</b>',
    '<b>테크노파크(TP)</b> — 지역 기술기업 지원',
    '<b>경제진흥원 · 산업진흥원</b><br>예) 고양산업진흥원',
    '<b>신용보증재단</b> — 지역 보증')
    + '<div class="note warn"><b>핵심</b><br>지자체 사업은 <span class="hl">관내 사업장</span>이 요건입니다. '
      '경쟁률이 중앙부처보다 낮은 경우가 많아 <b>가장 먼저 노려볼 만합니다.</b></div>')}
  {card('공공기관 · 대학', dots(
    '<b>기술보증기금 · 신용보증기금</b><br>보증서 기반 융자',
    '<b>중소벤처기업진흥공단</b><br>정책자금 융자',
    '<b>대학 창업지원단 · 창업보육센터</b>',
    '<b>SW중심대학사업단</b> 등 교내 프로그램')
    + '<div class="note"><b>재학생이라면</b><br>교내 프로그램이 경쟁 범위가 좁아 '
      '가장 현실적인 첫 단추입니다.</div>')}
 </div>''', 20, tag='PART 4  정부지원사업'))

# 21 단계별 대표 사업
S.append(slide(head('창업 단계별 대표 사업', '2025년 공고 기준. 금액과 요건은 매년 바뀌므로 신청 시점 공고문을 확인하세요.') + f'''
 <div class="body">
  {table(['사업명', '대상', '지원 규모', '주관'], [
    ['예비창업패키지', '사업자등록 전 예비창업자', '최대 <b>6,000만원</b><br><small>1차 2,000 + 평가 후 2차 4,000</small>', '중기부 · 창업진흥원'],
    ['초기창업패키지', '창업 <b>3년 이내</b> 기업', '평균 <b>7,000만원</b>', '중기부 · 창업진흥원'],
    ['창업도약패키지', '창업 <b>3~7년</b> 기업', '최대 3억원 수준', '중기부 · 창업진흥원'],
    ['청년창업사관학교', '만 39세 이하, 창업 3년 이내', '최대 1억원 + 입주공간', '중소벤처기업진흥공단'],
    ['TIPS', '민간 투자 선행 기술창업팀', 'R&D 최대 5억원 수준', '중기부 · TIPS 운영사'],
  ])}
  <div class="note"><b>공통 유의사항</b><br>
  ① <b>창업 7년 이내</b>가 대부분 사업의 기본 자격입니다 (중소기업창업 지원법 기준) &nbsp;
  ② 같은 해에 <b>중복 수혜가 제한</b>되는 조합이 있습니다 &nbsp;
  ③ 대부분 <b>자부담(현금 · 현물)</b>이 함께 요구됩니다 &nbsp;
  ④ 사업비는 <span class="hl">정해진 비목대로만</span> 집행하고 증빙해야 하며, 어기면 환수 대상입니다</div>
 </div>''', 21, tag='PART 4  정부지원사업'))

# 22 K-Startup 활용법
S.append(slide(head('K-Startup 활용법', '공고를 "찾는" 게 아니라 "기다리는" 구조로 만들어 두세요.') + f'''
 <div class="body cols c2">
  {card('연간 흐름 읽기', dots(
    '<b>1~3월</b> — 한 해 대부분의 사업이 공고됩니다. 가장 중요한 시기',
    '<b>4~6월</b> — 상반기 선정 · 협약 · 사업 개시',
    '<b>7~9월</b> — 일부 사업 2차 모집, 지자체 사업 집중',
    '<b>10~12월</b> — 정산 · 결과보고. 다음 해 계획 수립')
    + '<div class="note"><b>준비는 전년도 말부터</b><br>1월 공고를 보고 준비하면 늦습니다. '
      '전년도 공고문으로 미리 사업계획서 초안을 써 두면 '
      '<span class="hl">2주 안에 지원</span>할 수 있습니다.</div>', True)}
  {card('실무 요령', dots(
    'K-Startup에서 <b>관심공고 알림</b>을 설정합니다',
    '<b>기업마당(bizinfo.go.kr)</b>도 함께 봅니다 — 부처 · 지자체 사업이 모입니다',
    '지역 <b>창업지원센터 뉴스레터</b>를 구독합니다',
    '작년 <b>선정기업 명단</b>을 보면 어떤 팀이 붙는지 감이 옵니다',
    '<b>사업계획서 표준 양식</b>은 매년 거의 같습니다. 한 번 잘 써 두면 재사용됩니다')
    + '<div class="note warn"><b>대행업체 주의</b><br>"합격 보장" · "성공보수 30%" 같은 제안은 걸러내세요. '
      '사업계획서는 결국 <b>본인이 실행할 내용</b>이라 대필로는 대면평가에서 드러납니다.</div>')}
 </div>''', 22, tag='PART 4  정부지원사업'))

# 23 PSST
S.append(slide(head('사업계획서 — PSST 구조', '정부지원사업 표준 양식은 대부분 이 네 덩어리입니다.') + f'''
 <div class="body">
  {steps([
    ('P', 'Problem<br>문제 인식', '왜 이 사업을 하는가<br>시장의 문제와 기회<br><b>객관적 근거 · 통계</b>'),
    ('S', 'Solution<br>실현 가능성', '어떻게 해결하는가<br>기술 · 제품 · 차별성<br><b>현재 개발 단계</b>'),
    ('S', 'Scale-up<br>성장 전략', '어떻게 팔고 키우는가<br>목표시장 · 매출계획<br><b>자금 집행 계획</b>'),
    ('T', 'Team<br>팀 구성', '왜 우리가 하는가<br>대표 · 팀원 역량<br><b>외부 협력 체계</b>'),
  ])}
  <div class="cols c2" style="margin-top:6mm">
   {card('잘 쓴 사업계획서의 공통점', dots(
     '<b>숫자에 근거가 있다</b> — "시장이 크다"가 아니라 출처 있는 규모 추정',
     '<b>이미 한 일이 있다</b> — 고객 인터뷰, 시제품, 테스트 매출, LOI',
     '<b>자금 사용처가 구체적이다</b> — 비목별로 왜 그 금액인지 설명된다',
     '<b>팀이 이 일을 할 이유가 보인다</b> — 경력과 아이템이 연결된다'))}
   {card('탈락하는 사업계획서', dots(
     '기술 설명만 길고 <b>누가 왜 사는지</b>가 없다',
     '시장 규모가 <b>전 세계 시장 전체</b>로 잡혀 있다',
     '경쟁사가 <b>"없다"</b>고 쓰여 있다 (대안은 항상 존재합니다)',
     '자금 계획이 <b>인건비와 마케팅비 뭉텅이</b>로만 되어 있다',
     '양식의 <b>분량 · 서식 요건</b>을 지키지 않았다 (형식 요건 미달은 즉시 탈락)'))}
  </div>
 </div>''', 23, tag='PART 4  정부지원사업'))

# 24 PART 5 간지
S.append(slide(part(5, '벤처투자 기초', [
  ('자금의 순서', '자기자본 → 정부지원 → 융자 → 투자. 각각 성격과 대가가 다르다'),
  ('투자란 무엇인가', '지분을 팔아 현금을 받는 거래. 돌려받지 않는 대신 회사의 일부를 넘긴다'),
  ('무엇을 준비하나', '밸류에이션 · 지분 희석 · IR 자료 · 텀시트의 기본'),
]), 24, cls='part'))

# 25 자금조달 사다리
S.append(slide(head('자금조달 사다리', '아래에서 위로 올라갑니다. 건너뛰면 조건이 나빠집니다.') + f'''
 <div class="body">
  {table(['단계', '수단', '성격', '대가'], [
    ['1', '자기자본 · 지인', '가장 빠름, 금액 한계', '없음 (관계 리스크)'],
    ['2', '정부지원금', '<b>갚지 않음</b>, 지분 희석 없음', '사업비 집행 · 정산 의무'],
    ['3', '융자 (보증서 기반)', '기술보증기금 · 신용보증기금 · 중진공', '<b>원리금 상환</b>, 대표 연대보증 가능성'],
    ['4', '투자 (지분)', '엔젤 · 액셀러레이터 · VC', '<b>지분 희석</b>, 경영 관여, Exit 압박'],
  ])}
  <div class="note"><b>순서가 중요한 이유</b><br>
  정부지원금은 <span class="hl">지분을 요구하지 않는 유일한 자금</span>입니다.
  받을 수 있는데 건너뛰고 투자부터 받으면, 같은 금액을 위해 회사 지분을 내주게 됩니다.
  반대로 매출도 검증도 없는 상태에서 투자 유치에만 매달리면 시간만 소모합니다.
  <b>정부지원금으로 검증하고, 검증된 지표로 투자를 받는</b> 순서가 일반적입니다.</div>
 </div>''', 25, tag='PART 5  벤처투자'))

# 26 투자 단계와 투자자
S.append(slide(head('투자 단계와 투자자 유형') + f'''
 <div class="body cols c2">
  {card('투자 단계', table(['단계', '시기', '규모 (통상)'], [
    ['Seed', '아이디어 ~ 초기 제품', '수천만 ~ 3억원'],
    ['Pre-A', '초기 매출 · 지표 확인', '3억 ~ 10억원'],
    ['Series A', '사업 모델 검증 완료', '10억 ~ 50억원'],
    ['Series B 이상', '스케일업 · 시장 확대', '50억원 이상'],
  ], z=False))}
  {card('투자자 유형', table(['유형', '특징'], [
    ['<b>엔젤투자자</b>', '개인. 초기 소액. 의사결정 빠름'],
    ['<b>액셀러레이터(AC)</b>', '보육 + 소액투자. TIPS 운영사인 경우 많음'],
    ['<b>벤처캐피탈(VC)</b>', '펀드 운용. Series A 이후 중심'],
    ['<b>CVC</b>', '대기업 산하. 사업 시너지 중시'],
  ], z=False)
    + '<div class="note"><b>초기 창업팀의 현실적인 경로</b><br>'
      '정부지원사업 → 액셀러레이터 투자 유치 → <b>TIPS 선정</b> → Series A<br>'
      'TIPS는 민간 투자(통상 1억원 이상)가 선행되어야 신청할 수 있습니다.</div>')}
 </div>''', 26, tag='PART 5  벤처투자'))

# 27 밸류에이션 · 지분
_val = ('<p><b>Pre-money</b> 투자 전 기업가치 &nbsp;·&nbsp; <b>Post-money</b> = Pre-money + 투자금</p>'
        '<p style="margin-top:2.6mm"><b>투자자 지분율 = 투자금 ÷ Post-money</b></p>'
        + table(['예시', '값'], [
            ['Pre-money 기업가치', '20억원'],
            ['투자금', '5억원'],
            ['Post-money', '25억원'],
            ['투자자 지분', '<b>5 ÷ 25 = 20%</b>'],
            ['창업팀 지분', '100% → <span class="hl">80%</span>'],
        ], z=False))
S.append(slide(head('밸류에이션과 지분 희석', '투자 유치는 "얼마를 받느냐"보다 "얼마를 내주느냐"가 중요합니다.') + f'''
 <div class="body cols c2">
  {card('계산의 기본', _val, True)}
  {card('반드시 기억할 것', dots(
    '<b>지분은 줄어들기만 합니다.</b> 라운드를 거듭할수록 창업팀 지분은 계속 희석됩니다',
    '초기에 <b>기업가치를 너무 높게</b> 잡으면 다음 라운드에서 하향(다운라운드) 부담이 생깁니다',
    '<b>공동창업자 지분</b>은 처음에 신중히. 나중에 되돌리기 어렵습니다',
    '<b>베스팅(vesting)</b> 조항으로 중도 이탈 시 지분 회수 장치를 두는 것이 일반적입니다',
    'Series A 이후에도 <b>대표가 최대주주</b>를 유지하는 것이 통상적인 목표입니다')
    + '<div class="note warn"><b>초기 투자에서 가장 흔한 실수</b><br>'
      '급한 자금 때문에 시드 단계에서 <span class="hl">30~40% 지분</span>을 내주는 것. '
      '이후 라운드에서 창업팀 지분이 지나치게 낮아져 <b>후속 투자 자체가 어려워집니다.</b></div>')}
 </div>''', 27, tag='PART 5  벤처투자'))

# 28 IR과 텀시트
S.append(slide(head('IR 자료와 텀시트 기초') + f'''
 <div class="body cols c2">
  {card('IR 덱 기본 구성 (10~15장)', table(['순서', '내용'], [
    ['1', '한 줄 소개 — 무엇을 하는 회사인가'],
    ['2~3', '문제 — 누가, 얼마나 불편한가'],
    ['4~5', '솔루션 — 제품 · 데모'],
    ['6', '시장 규모 — TAM / SAM / SOM'],
    ['7', '비즈니스 모델 — 수익 구조'],
    ['8', '경쟁 · 차별성'],
    ['9', '트랙션 — <b>지금까지의 성과 지표</b>'],
    ['10', '팀'],
    ['11~12', '재무 계획 · 투자 요청 금액과 사용처'],
  ], z=False))}
  {card('텀시트에서 자주 보는 조항', table(['조항', '뜻'], [
    ['<b>상환전환우선주<br>(RCPS)</b>', '국내 벤처투자의 일반적 형태. 상환권 + 전환권 + 우선권'],
    ['<b>우선청구권</b>', '청산 · 매각 시 투자자가 먼저 회수'],
    ['<b>희석방지</b>', '후속 라운드가 낮은 가치일 때 투자자 지분 보정'],
    ['<b>동반매도권</b>', '투자자 매각 시 창업자 지분도 함께 매각 요구'],
    ['<b>이사 지명권</b>', '투자자가 이사회에 인원을 지명'],
  ], z=False)
    + '<div class="note warn"><b>텀시트는 반드시 전문가 검토를 받으세요.</b> '
      '금액보다 조항이 회사의 미래를 더 크게 좌우합니다.</div>')}
 </div>''', 28, tag='PART 5  벤처투자'))

# 29 요약
_sum1 = ('<p>검증 → 등록 → 자금 → 성장.<br>사업자등록은 <b>매출 직전</b>에.</p>'
         '<p style="margin-top:3.4mm"><small>등록하는 순간부터 신고 의무와 고정비가 생깁니다. '
         '아이템 검증에 쓸 시간을 등록 절차에 쓰지 마세요.</small></p>')
_sum2 = ('<p>투자 계획이 있으면 <b>법인</b>,<br>아니면 <b>개인</b>으로 시작해도 됩니다.</p>'
         '<p style="margin-top:3.4mm"><small>과세표준 8,800만원 부근, 또는 투자 유치 · 지분 분배가 '
         '필요해지는 시점이 전환 신호입니다.</small></p>')
_sum3 = ('<p>정부지원금 → 융자 → 투자.<br><b>지분은 가장 비싼 자금</b>입니다.</p>'
         '<p style="margin-top:3.4mm"><small>지원금으로 검증하고, 검증된 지표로 투자를 받습니다. '
         '순서를 건너뛰면 같은 돈에 더 많은 지분을 냅니다.</small></p>')
S.append(slide(head('오늘의 요약', '기억해야 할 것은 세 가지입니다.') + f'''
 <div class="body cols c3">
  {card('<em>01</em> &nbsp;순서를 지킨다', _sum1, True)}
  {card('<em>02</em> &nbsp;형태는 계획을 따른다', _sum2)}
  {card('<em>03</em> &nbsp;싼 돈부터 쓴다', _sum3)}
 </div>
 <div class="note" style="margin-top:6mm"><b>다음 한 주 안에 해볼 것</b> &nbsp;
 ① 고객이 될 사람 3명과 대화하기 &nbsp; ② K-Startup 알림 설정하기 &nbsp;
 ③ 학교 창업지원단 프로그램 확인하기</div>''', 29, tag='마무리'))

# 30 참고 자료
S.append(slide(head('바로 쓰는 참고 사이트', '북마크해 두면 창업 첫해 내내 씁니다.') + f'''
 <div class="body cols c2">
  {card('공고 · 지원사업', table(['구분', '사이트'], [
    ['창업지원 통합', 'K-Startup &nbsp; www.k-startup.go.kr'],
    ['정부지원 통합', '기업마당 &nbsp; www.bizinfo.go.kr'],
    ['중기부', 'www.mss.go.kr'],
    ['창업진흥원', 'www.kised.or.kr'],
    ['벤처확인 · 투자', '중소벤처24 &nbsp; www.smes.go.kr'],
  ], z=False))}
  {card('세무 · 등기 · 보증', table(['구분', '사이트'], [
    ['사업자등록 · 세금', '홈택스 &nbsp; www.hometax.go.kr'],
    ['법인 설립등기', '인터넷등기소 &nbsp; www.iros.go.kr'],
    ['4대보험', '4대사회보험 정보연계센터 &nbsp; www.4insure.or.kr'],
    ['기술보증', '기술보증기금 &nbsp; www.kibo.or.kr'],
    ['정책자금 융자', '중소벤처기업진흥공단 &nbsp; www.kosmes.or.kr'],
  ], z=False))}
 </div>
 <div class="note" style="margin-top:6mm">
 <b>본 자료는 2025년 11월 기준으로 작성되었습니다.</b>
 세법상 기준금액, 지원사업의 지원 규모와 자격 요건은 매년 변경되므로,
 실제 신청 · 신고 시점에는 반드시 해당 기관의 최신 공고문과 법령을 확인하시기 바랍니다.
 개별 사안에 대한 판단은 세무사 · 변호사 등 전문가 상담을 권합니다.</div>''', 30, tag='마무리'))


HTML = f'<!doctype html><meta charset="utf-8"><title>{TITLE}</title><style>{CSS}</style>' + ''.join(S)


def main():
    src = HERE / '초기창업_시작하기_강의자료.html'
    src.write_text(HTML, encoding='utf-8')
    out = HERE / '초기창업_시작하기_강의자료.pdf'
    subprocess.run([CHROME, '--headless', '--disable-gpu', '--no-sandbox',
                    '--allow-file-access-from-files', '--font-render-hinting=none',
                    f'--print-to-pdf={out}', '--no-pdf-header-footer',
                    f'file://{src}'], check=True, capture_output=True)
    print('  ', out.name, f'({len(S)}장)')


if __name__ == '__main__':
    main()
