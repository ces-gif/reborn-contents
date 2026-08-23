"""드라이브와 모델을 가짜로 갈아끼우고 파이프라인 전체를 한 번 돌려본다."""

from __future__ import annotations

import json
from datetime import date, datetime, timezone
from pathlib import Path

import pytest
from PIL import Image

from reborn import blog, branding, pipeline, ranking, research, vision
from reborn.config import load_settings
from reborn.drive import DriveFile


class FakeDrive:
    def __init__(self, files_by_folder, photo_bytes, logo_bytes):
        self.files_by_folder = files_by_folder
        self.photo_bytes = photo_bytes
        self.logo_bytes = logo_bytes
        self.folders: dict[tuple[str | None, str], str] = {}
        self.uploaded: dict[str, bytes] = {}

    def list_children(self, folder_id, only_images=False, page_size=200):
        return list(self.files_by_folder.get(folder_id, []))

    def get_parent(self, file_id):
        return "PARENT"

    def ensure_folder(self, name, parent_id=None):
        key = (parent_id, name)
        return self.folders.setdefault(key, f"folder-{len(self.folders)}-{name}")

    def find_child(self, parent_id, name, mime_type=None):
        return None

    def download(self, file_id, dest: Path):
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(self.logo_bytes if file_id == "LOGO" else self.photo_bytes)
        return dest

    def upload(self, path: Path, parent_id, mime_type=None, name=None):
        self.uploaded[name or path.name] = path.read_bytes()
        return f"file-{name or path.name}"


class FakeLLM:
    """LLMClient 흉내. schema 클래스 이름으로 응답을 고른다."""

    def __init__(self, kinds_per_group=None, classify_kinds=None):
        self.calls: list[str] = []
        self.kinds_per_group = kinds_per_group  # [["price_tag"], ["price_tag","product"], ...]
        # 1차 판독(사진 한 장씩 가격표/상품 구분)이 돌려줄 답을 준 순서대로 꺼내 쓴다
        self.classify_kinds = list(classify_kinds or [])
        self.assigned: list[str] = []  # 1차 판독에서 실제로 내준 답 (2차 판독도 같은 답을 낸다)
        self.searched: list[str] = []
        self.name = "fake"

    def structured(self, *, system, parts, schema, max_tokens=8000, search=False, model=None):
        name = schema.__name__
        self.calls.append(name)
        if search:
            self.searched.append(name)

        if name == "PhotoBatch":
            images = [p for p in parts if p["type"] == "image"]
            kinds = [
                self.classify_kinds.pop(0) if self.classify_kinds else "product"
                for _ in images
            ]
            self.assigned.extend(kinds)
            return vision.PhotoBatch(
                photos=[
                    vision.PhotoClass(index=i + 1, kind=k, item="") for i, k in enumerate(kinds)
                ]
            )

        if name == "ProductRead":
            images = [p for p in parts if p["type"] == "image"]
            idx = sum(1 for c in self.calls if c == "ProductRead")
            if self.kinds_per_group:
                kinds = self.kinds_per_group[idx - 1]
            elif self.assigned:
                kinds = [self.assigned.pop(0) for _ in images]
            else:
                kinds = ["both"] if len(images) == 1 else ["price_tag", "product"]
            return vision.ProductRead(
                photos=[vision.PhotoRead(index=i + 1, kind=k) for i, k in enumerate(kinds)],
                product_name=f"쿠쿠 {idx}호 밥솥",
                tag_text="온라인가 200,000 / 리본가 100,000",
                condition_note="",
                category="가전",
                original_price=200000,
                sale_price=100000,
                discount_pct=None,
                price_source="가격표",
                best_photo_index=next(
                    (i for i, k in enumerate(kinds, start=1) if k in ("product", "both")), 0
                ),
                review_reason="",
            )

        if name == "Research":
            assert search, "웹 검색을 켜지 않았습니다"
            return research.Research(
                matched=True,
                official_name="쿠쿠 6인용 IH 압력밥솥",
                spec_line="6인용 IH 압력밥솥, 3중 코팅 내솥",
                description="6인 가구용 IH 압력밥솥입니다. 밥맛 코스가 여러 가지 들어 있습니다.",
                key_points=["IH 가열", "6인용"],
                sources=["https://example.com/a"],
            )

        if name == "Ranking":
            return ranking.Ranking(ranking=[ranking.RankedItem(id=0, why="할인 폭이 큽니다")])

        if name == "PostDraft":
            n = sum(1 for c in self.calls if c == "ProductRead")
            return blog.PostDraft(
                category_tag="오늘의 리본 특가",
                title="평택 리퍼브 가전 BEST",
                intro=[["안녕하세요.", "리본마켓 평택점입니다."]],
                transition=["그래서 오늘은 준비했어요."],
                items=[
                    blog.PostItem(
                        heading=f"{i}번째 상품",
                        body=[["본문", "두 줄"]],
                        personal_note="저는 이렇게 쓰곤 해요.",
                    )
                    for i in range(1, n + 1)
                ],
                table_intro="한눈에 보시라고 정리했어요.",
                table_wrapup=["표에서 보시다시피 반값입니다."],
                closing=[["오늘도 좋은 하루 되세요."]],
                tags=["리본마켓", "평택리퍼브"],
            )

        raise AssertionError(f"예상 못 한 schema: {name}")


@pytest.fixture
def wired(tmp_path, monkeypatch):
    photo = tmp_path / "p.jpg"
    Image.new("RGB", (1600, 1200), (230, 232, 238)).save(photo)
    logo = tmp_path / "logo.png"
    Image.new("RGBA", (600, 160), (253, 111, 35, 255)).save(logo)

    def f(name, iso):
        dt = datetime.fromisoformat(iso).astimezone(timezone.utc)
        return DriveFile(id=name, name=name, mime_type="image/jpeg",
                         created_time=dt, modified_time=dt, size=100)

    settings = load_settings()
    refurb_id = settings.sources[0].folder_id
    new_id = settings.sources[1].folder_id
    files_by_folder = {
        refurb_id: [
            f("20260823_104712.jpg", "2026-08-23T10:47:12+09:00"),
            f("20260823_104733.jpg", "2026-08-23T10:47:33+09:00"),  # 같은 상품
            f("20260823_105300.jpg", "2026-08-23T10:53:00+09:00"),  # 다른 상품
            f("20260822_180000.jpg", "2026-08-22T18:00:00+09:00"),  # 어제분 → 제외
        ],
        new_id: [
            f("20260823_111000.jpg", "2026-08-23T11:10:00+09:00"),  # 새상품 1개
        ],
    }
    drive = FakeDrive(files_by_folder, photo.read_bytes(), logo.read_bytes())
    # 리퍼 3장 = (상품+가격표) 1개 + (상품·가격표 한 장) 1개, 새상품 1장 = 1개
    client = FakeLLM(classify_kinds=["product", "price_tag", "both", "both"])

    monkeypatch.setattr(pipeline, "Drive", lambda *a, **k: drive)
    monkeypatch.setattr(pipeline, "make_llm", lambda s: client)
    monkeypatch.setattr(branding, "LOGO_CACHE", tmp_path / "cache-logo.png")
    monkeypatch.setenv(branding.LOGO_ENV_PATH, str(logo))
    return drive, client, tmp_path


def test_full_run_produces_cards_blog_social_and_uploads(wired):
    drive, client, tmp_path = wired
    settings = load_settings()
    settings.logo_file_id = "LOGO"

    result = pipeline.run(
        settings,
        day=date(2026, 8, 23),
        out_root=tmp_path / "out",
        work_root=tmp_path / "work",
    )

    # 어제 사진은 빠지고, 리퍼 3장(상품 2개) + 새상품 1장(상품 1개)
    assert result.photos_seen == 4
    assert result.per_source == {"리퍼": 3, "새상품": 1}
    assert result.groups == 3
    assert len(result.cards) == 3

    for card in result.cards:
        with Image.open(card) as img:
            assert img.size == (1080, 1920)

    day_dir = tmp_path / "out" / "2026-08-23"
    assert list((day_dir / "블로그").glob("2026-08-23-best*-blog.html"))
    assert list((day_dir / "블로그").glob("2026-08-23-best*-blog.md"))
    assert (day_dir / "소셜" / "2026-08-23-카톡공지.txt").exists()
    assert (day_dir / "소셜" / "2026-08-23-인스타캡션.txt").exists()

    products = json.loads((day_dir / "_data" / "products.json").read_text(encoding="utf-8"))
    assert len(products) == 3 and products[0]["publishable"]

    # 드라이브에 카드/블로그/공지가 다 올라갔고 원장도 갱신됐다
    assert any(n.endswith(".png") for n in result.uploaded)
    assert "_ledger.json" in drive.uploaded
    ledger = json.loads(drive.uploaded["_ledger.json"].decode("utf-8"))
    assert len(ledger["processed_file_ids"]) == 4


def test_second_run_skips_already_processed_photos(wired):
    drive, client, tmp_path = wired
    settings = load_settings()
    settings.logo_file_id = "LOGO"
    kwargs = dict(day=date(2026, 8, 23), out_root=tmp_path / "out", work_root=tmp_path / "work")

    pipeline.run(settings, **kwargs)
    # 원장이 드라이브에 올라갔으니 다음 실행에서 그대로 읽힌다
    drive.find_child = lambda parent, name, mime_type=None: (
        "LEDGER" if name == "_ledger.json" else None
    )
    original_download = drive.download

    def download(file_id, dest):
        if file_id == "LEDGER":
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(drive.uploaded["_ledger.json"])
            return dest
        return original_download(file_id, dest)

    drive.download = download

    again = pipeline.run(settings, **kwargs)
    assert again.photos_seen == 0
    assert again.skipped_reason


def test_slugify_keeps_korean_and_strips_symbols():
    assert pipeline.slugify("삼성 비스포크 큐브 에어 (전시품)") == "삼성-비스포크-큐브-에어-전시품"
    assert pipeline.slugify("") == "상품"


def test_price_tag_only_group_makes_no_card_but_is_reported(wired, monkeypatch):
    """은성님 지시: 가격표만 찍힌 건 정보 전달용이라 카드뉴스를 만들지 않는다."""
    drive, client, tmp_path = wired
    # 1번 묶음은 가격표만, 2번 묶음은 가격표 + 상품
    client.kinds_per_group = [["price_tag", "price_tag"], ["price_tag"], ["price_tag"]]

    settings = load_settings()
    settings.logo_file_id = "LOGO"
    result = pipeline.run(
        settings, day=date(2026, 8, 23),
        out_root=tmp_path / "out", work_root=tmp_path / "work",
    )

    assert result.groups == 3
    assert result.cards == []
    assert len(result.needs_review) == 3
    assert all("가격표만" in p.review_reason for p in result.needs_review)

    report = (tmp_path / "out" / "2026-08-23" / "_data" / "리포트.md").read_text(encoding="utf-8")
    assert "사람이 확인해야 하는 건" in report and "가격표만" in report


def test_web_research_line_is_used_on_the_card(wired):
    """인터넷에서 확인된 제품 설명이 카드뉴스 한 줄로 들어간다."""
    drive, client, tmp_path = wired
    settings = load_settings()
    settings.logo_file_id = "LOGO"

    result = pipeline.run(
        settings, day=date(2026, 8, 23),
        out_root=tmp_path / "out", work_root=tmp_path / "work",
    )

    assert "Research" in client.searched, "웹 검색 단계가 돌지 않았습니다"
    for product in result.published:
        assert product.research_matched
        assert product.card_line == "6인용 IH 압력밥솥, 3중 코팅 내솥"


def test_research_failure_does_not_stop_publishing(wired, monkeypatch):
    """검색이 실패해도 카드뉴스는 그대로 나온다 (설명만 비워진다)."""
    drive, client, tmp_path = wired

    original = client.structured

    def flaky(*, schema, **kwargs):
        if schema.__name__ == "Research":
            raise RuntimeError("검색 서버 오류")
        return original(schema=schema, **kwargs)

    monkeypatch.setattr(client, "structured", flaky)

    settings = load_settings()
    settings.logo_file_id = "LOGO"
    result = pipeline.run(
        settings, day=date(2026, 8, 23),
        out_root=tmp_path / "out", work_root=tmp_path / "work",
    )

    assert len(result.cards) == 3
    assert all(not p.research_matched and p.card_line == "" for p in result.published)


def test_new_goods_folder_gets_its_own_wording_and_folder(wired):
    """새상품 폴더는 제조사 직거래 미개봉 새상품이라 눈썹 문구가 다르다."""
    drive, client, tmp_path = wired
    settings = load_settings()
    settings.logo_file_id = "LOGO"

    result = pipeline.run(
        settings, day=date(2026, 8, 23),
        out_root=tmp_path / "out", work_root=tmp_path / "work",
    )

    by_source = {p.source_name: p for p in result.published}
    assert by_source["리퍼"].eyebrow == "오늘의 리본 특가"
    assert by_source["새상품"].eyebrow == "제조사 직거래 새상품"
    assert by_source["새상품"].is_new_goods

    cards = tmp_path / "out" / "2026-08-23" / "카드뉴스"
    assert list((cards / "리퍼").glob("*.png"))
    assert list((cards / "새상품").glob("*.png"))


def test_new_goods_may_say_it_is_new_but_refurb_may_not(wired):
    """새상품은 폴더 자체가 근거라 '미개봉 새상품'을 쓸 수 있고, 리퍼는 가격표 근거가 필요하다."""
    from reborn.vision import Product, sanity_check

    def make(kind):
        return sanity_check(Product(
            product_name="테스트", category="가전", tag_text="정가 100,000",
            condition_note="미개봉 새상품입니다", original_price=100000, sale_price=50000,
            photo_kinds=["both"], photo_paths=["a.jpg"], best_photo_index=1, source_kind=kind,
        ))

    assert make("new").condition_note == "미개봉 새상품입니다"
    assert make("refurb").condition_note == ""


def test_instagram_is_skipped_cleanly_without_credentials(wired):
    drive, client, tmp_path = wired
    settings = load_settings()
    settings.logo_file_id = "LOGO"

    result = pipeline.run(
        settings, day=date(2026, 8, 23),
        out_root=tmp_path / "out", work_root=tmp_path / "work",
    )

    assert result.stories is not None
    assert result.stories.skipped_reason
    assert result.stories.results == []
    # 인스타가 안 되더라도 나머지 발행은 다 끝나 있어야 한다
    assert result.cards and result.drive_folder_url
