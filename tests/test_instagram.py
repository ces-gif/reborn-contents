"""인스타그램 스토리 게시 (HTTP 는 가짜로 갈아끼운다)."""

from __future__ import annotations

from pathlib import Path

import pytest

from reborn import imagehost, instagram


class FakeResponse:
    def __init__(self, payload, status=200):
        self._payload = payload
        self.status_code = status
        self.content = b"x"
        self.text = str(payload)

    def json(self):
        return self._payload


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("IG_USER_ID", "1784")
    monkeypatch.setenv("IG_ACCESS_TOKEN", "tok")


def test_not_configured_without_credentials(monkeypatch):
    monkeypatch.delenv("IG_USER_ID", raising=False)
    monkeypatch.delenv("IG_ACCESS_TOKEN", raising=False)
    assert not instagram.is_configured()


def test_publish_story_follows_meta_three_step_flow(creds, monkeypatch):
    posts, gets = [], []

    def fake_post(url, data=None, timeout=None):
        posts.append((url, data))
        if url.endswith("/media"):
            return FakeResponse({"id": "container-1"})
        return FakeResponse({"id": "media-9"})

    def fake_get(url, params=None, timeout=None):
        gets.append(url)
        return FakeResponse({"status_code": "FINISHED"})

    monkeypatch.setattr(instagram.requests, "post", fake_post)
    monkeypatch.setattr(instagram.requests, "get", fake_get)

    assert instagram.publish_story("https://cdn.example/card.png") == "media-9"

    # 1) 컨테이너 생성 — 스토리 타입과 공개 URL
    assert posts[0][0].endswith("/1784/media")
    assert posts[0][1]["media_type"] == "STORIES"
    assert posts[0][1]["image_url"] == "https://cdn.example/card.png"
    # 2) 상태 확인  3) 게시
    assert gets and "container-1" in gets[0]
    assert posts[1][0].endswith("/1784/media_publish")
    assert posts[1][1]["creation_id"] == "container-1"


def test_api_error_is_raised_with_message(creds, monkeypatch):
    monkeypatch.setattr(
        instagram.requests,
        "post",
        lambda *a, **k: FakeResponse({"error": {"message": "권한 없음"}}, status=400),
    )
    with pytest.raises(RuntimeError, match="권한 없음"):
        instagram.publish_story("https://cdn.example/card.png")


def test_container_error_status_is_raised(creds, monkeypatch):
    monkeypatch.setattr(
        instagram.requests, "post", lambda *a, **k: FakeResponse({"id": "container-1"})
    )
    monkeypatch.setattr(
        instagram.requests,
        "get",
        lambda *a, **k: FakeResponse({"status_code": "ERROR", "status": "이미지 형식 오류"}),
    )
    with pytest.raises(RuntimeError, match="이미지 형식 오류"):
        instagram.publish_story("https://cdn.example/card.png")


def test_publish_cards_skips_without_image_host(creds, monkeypatch, tmp_path):
    monkeypatch.setattr(imagehost, "is_configured", lambda: False)
    report = instagram.publish_cards([tmp_path / "a.png"], key_prefix="k")
    assert report.results == [] and "R2" in report.skipped_reason


def test_one_failure_does_not_stop_the_rest(creds, monkeypatch, tmp_path):
    cards = [tmp_path / f"{i}.png" for i in range(3)]
    for c in cards:
        c.write_bytes(b"x")

    monkeypatch.setattr(imagehost, "is_configured", lambda: True)
    monkeypatch.setattr(imagehost, "upload_public", lambda p, key: f"https://cdn/{key}")

    calls = []

    def flaky(url):
        calls.append(url)
        if "1.png" in url:
            raise RuntimeError("일시 오류")
        return "media-x"

    monkeypatch.setattr(instagram, "publish_story", flaky)

    report = instagram.publish_cards(cards, key_prefix="k", delay_seconds=0)
    assert len(calls) == 3
    assert len(report.published) == 2
    assert len(report.failed) == 1
    assert report.failed[0].error == "일시 오류"


def test_daily_cap_limits_how_many_stories_go_up(creds, monkeypatch, tmp_path):
    cards = [tmp_path / f"{i}.png" for i in range(8)]
    for c in cards:
        c.write_bytes(b"x")
    monkeypatch.setattr(imagehost, "is_configured", lambda: True)
    monkeypatch.setattr(imagehost, "upload_public", lambda p, key: f"https://cdn/{key}")
    monkeypatch.setattr(instagram, "publish_story", lambda url: "media-x")

    report = instagram.publish_cards(cards, key_prefix="k", max_stories=3, delay_seconds=0)
    assert len(report.published) == 3


def test_imagehost_reports_not_configured(monkeypatch):
    for key in ("R2_ACCOUNT_ID", "R2_ENDPOINT", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY", "R2_BUCKET"):
        monkeypatch.delenv(key, raising=False)
    assert not imagehost.is_configured()
    with pytest.raises(imagehost.NotConfigured):
        imagehost.upload_public(Path("x.png"), "k")
