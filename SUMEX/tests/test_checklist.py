"""체크리스트 — 현장에서 틀리면 안 되는 항목이 실제로 나오는지."""
from sumex import checklist, registry


def _text(name):
    return checklist.render_text(checklist.build(registry.find(name)))


def test_sejong_stamp_warning():
    text = _text("세종스포츠")
    assert "도장 3종" in text
    assert "수술실" in text and "재무팀" in text and "심사팀" in text
    assert "버거킹" in text                       # 총무·심사팀 위치


def test_seoul_spine_is_three_copies():
    text = _text("서울척")
    assert "거래명세서 3장" in text
    assert "14층" in text and "지하 2층" in text


def test_redcross_five_copies():
    text = _text("적십자")
    assert "거래명세서 5장" in text
    assert "보험심사팀" in text


def test_snubh_time_windows_are_starred():
    text = _text("분당서울대")
    assert "09:00-11:00" in text
    assert "14:00 이전" in text
    assert "★" in text


def test_unconfirmed_copies_flagged():
    data = checklist.build(registry.find("서울대"))
    assert data["copies_unconfirmed"]
    assert "현장에서 확정" in checklist.render_text(data)


def test_conflicts_surface():
    text = _text("무척나은")
    assert "출처 불일치" in text
    assert "인수인계서" in text and "현장확인" in text


def test_korea_univ_closing_hard_rule():
    """거래명세서 수량 총합 == 선납서 수량 총합. 안 맞으면 마감이 통과되지 않는다."""
    text = _text("고대")
    assert "선납서" in text
    assert "두 값이 같아야" in text
    assert "오후 4시 이전" in text
    assert "마감 순서: 수술방 → 스마트엠" in text


def test_no_stamp_hospital_says_so():
    assert "도장 불필요" in _text("서울점프")


def test_markdown_render():
    md = checklist.render_md(checklist.build(registry.find("세종스포츠")))
    assert md.startswith("# 세종스포츠정형외과")
    assert "## 서류 준비·배부" in md


def test_audit_finds_gaps():
    findings = checklist.audit()
    kinds = {f["kind"] for f in findings}
    assert "매수 미확인" in kinds
    assert "출처 불일치" in kinds
    assert all(f["hospital"] and f["detail"] for f in findings)
