"""거래처·품목 레지스트리 — 데이터가 코드가 기대하는 모양인지 검증한다."""
import pytest

from sumex import registry


def test_hospitals_load():
    rows = registry.hospitals()
    assert len(rows) >= 20
    assert all(h.id and h.name for h in rows)


def test_ids_are_unique():
    ids = [h.id for h in registry.hospitals()]
    assert len(ids) == len(set(ids)), f"중복 id: {[i for i in ids if ids.count(i) > 1]}"


@pytest.mark.parametrize("query,expected", [
    ("sejong-sports", "sejong-sports"),
    ("세종스포츠", "sejong-sports"),
    ("세종스포츠정형외과", "sejong-sports"),
    ("서울척", "seoul-spine"),
    ("적십자", "seoul-redcross"),
])
def test_find_by_alias(query, expected):
    assert registry.find(query).id == expected


def test_find_reports_candidates():
    with pytest.raises(registry.NotFound) as exc:
        registry.find("존재하지않는병원")
    assert exc.value.candidates


def test_ambiguous_query_lists_candidates():
    with pytest.raises(registry.NotFound) as exc:
        registry.find("병원")           # 여러 곳에 걸린다
    assert len(exc.value.candidates) > 1


def test_distribution_matches_copies():
    """배부처 합계가 총 매수와 맞아야 한다. 안 맞으면 현장에서 서류가 뜬다."""
    bad = []
    for h in registry.hospitals():
        if h.copies is None or not h.distribution:
            continue
        total = sum(d.get("copies", 0) for d in h.distribution)
        if total != h.copies:
            bad.append(f"{h.name}: 총 {h.copies}장 vs 배부 {total}장")
    assert not bad, "\n".join(bad)


def test_known_copy_rules():
    """인수인계 자료에서 확인된 값. 바뀌면 근거를 남기고 이 테스트를 고친다."""
    assert registry.find("서울척").copies == 3          # 여기만 3장
    assert registry.find("적십자").copies == 5          # 가장 많음
    assert registry.find("세종스포츠").copies == 4
    assert registry.find("세브란스").copies == 1
    assert registry.find("서울의료원").doc_type == "선납서"
    assert registry.find("고대").doc_type == "선납서"


def test_stamp_rules():
    assert registry.find("세종스포츠").stamp is True
    assert registry.find("서울점프").stamp is False
    assert len(registry.find("세종스포츠").doc.get("stamp_kinds")) == 3


def test_consignment_normalizes_absent():
    assert registry.find("서울점프").consignment is None
    assert registry.find("세종스포츠").consignment == "스타메디홀딩스"


def test_products_and_lookup():
    assert len(registry.products()) >= 15
    iconix = registry.find_product("아이코닉스")
    assert iconix and iconix["id"] == "iconix"
    assert registry.find_product("ICONIX")["id"] == "iconix"
    assert registry.find_product("없는품목") is None


def test_products_reference_real_hospitals():
    ids = {h.id for h in registry.hospitals()}
    for p in registry.products():
        for account in p.get("accounts") or []:
            assert account in ids, f"{p['name']} 이 없는 거래처 '{account}' 를 가리킨다"


def test_case_cover_has_seven_axes():
    assert len(registry.case_cover_axes()) == 7


def test_doc_types():
    assert registry.doc_type("거래명세서")
    assert registry.doc_type("demo_receipt")["form_no"] == "KQF-OPC-009-F"


def test_backlog_tasks_reference_real_hospitals():
    ids = {h.id for h in registry.hospitals()}
    for task in registry.backlog():
        hid = task.get("hospital")
        if hid:
            assert hid in ids, f"{task['id']} 이 없는 거래처 '{hid}' 를 가리킨다"


def test_task_ids_present():
    for task in registry.backlog():
        assert task.get("id"), f"id 없는 할 일: {task}"
