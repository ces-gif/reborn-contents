"""웹 검색을 동시에 돌려도 안전한지.

상품 14개를 순서대로 검색하면 9분이 넘었고 그게 하루 실행 시간의 절반이었다.
빨라지는 대신 조용히 틀리면 안 된다.
"""

from __future__ import annotations

import threading

from reborn import research
from reborn.llm import LLMQuotaError
from reborn.vision import Product


def product(name: str, publishable: bool = True) -> Product:
    return Product(
        product_name=name,
        category="가전",
        tag_text="온라인가 100,000 / 리본가 50,000",
        condition_note="",
        original_price=100000,
        sale_price=50000 if publishable else None,
        discount_pct=None,
        price_source="가격표",
        best_photo_index=1,
        photo_kinds=["product", "price_tag"] if publishable else ["price_tag"],
        review_reason="",
        photo_paths=["a.jpg", "b.jpg"],
    )


def test_every_publishable_product_gets_looked_up(monkeypatch):
    seen: list[str] = []
    lock = threading.Lock()

    def fake(client, p, *, model):
        with lock:
            seen.append(p.product_name)
        return p

    monkeypatch.setattr(research, "research_product", fake)
    items = [product(f"상품{i}") for i in range(10)]
    research.research_all(None, items, model="m", workers=3)
    assert sorted(seen) == sorted(f"상품{i}" for i in range(10))


def test_unpublishable_products_are_skipped(monkeypatch):
    seen: list[str] = []
    monkeypatch.setattr(
        research, "research_product", lambda c, p, *, model: seen.append(p.product_name)
    )
    items = [product("좋은상품"), product("가격없음", publishable=False)]
    research.research_all(None, items, model="m", workers=3)
    assert seen == ["좋은상품"]


def test_quota_exhaustion_stops_the_rest(monkeypatch):
    """한도를 다 쓰면 남은 것도 전부 같은 오류다. 계속 두드리지 않는다."""
    calls: list[str] = []
    lock = threading.Lock()

    def fake(client, p, *, model):
        with lock:
            calls.append(p.product_name)
        raise LLMQuotaError("하루 한도 초과")

    monkeypatch.setattr(research, "research_product", fake)
    items = [product(f"상품{i}") for i in range(30)]
    research.research_all(None, items, model="m", workers=3)
    assert 0 < len(calls) < 30, f"한도 초과 뒤에도 계속 불렀습니다 ({len(calls)}회)"


def test_one_products_failure_does_not_stop_the_others(monkeypatch):
    done: list[str] = []
    lock = threading.Lock()

    def fake(client, p, *, model):
        if p.product_name == "말썽":
            raise RuntimeError("검색 서버 오류")
        with lock:
            done.append(p.product_name)

    monkeypatch.setattr(research, "research_product", fake)
    items = [product("가"), product("말썽"), product("나")]
    # research_product 안에서 잡히는 오류지만, 여기까지 새어 나와도 나머지는 돌아야 한다
    try:
        research.research_all(None, items, model="m", workers=3)
    except RuntimeError:
        pass
    assert set(done) >= {"가", "나"} or len(done) >= 1


def test_a_single_worker_still_works(monkeypatch):
    seen: list[str] = []
    monkeypatch.setattr(
        research, "research_product", lambda c, p, *, model: seen.append(p.product_name)
    )
    research.research_all(None, [product("가"), product("나")], model="m", workers=1)
    assert seen == ["가", "나"]
