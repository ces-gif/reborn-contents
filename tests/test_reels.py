"""릴스 영상 생성 + 릴스 게시 (HTTP·ffmpeg 는 실제로 돌린다/갈아끼운다)."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from PIL import Image

from reborn import instagram, reels


def _cards(tmp_path: Path, n: int = 3) -> list[Path]:
    out = []
    for i in range(n):
        p = tmp_path / f"{i:02d}.png"
        Image.new("RGB", (1080, 1920), (30 + i * 40, 90, 160)).save(p)
        out.append(p)
    return out


def test_card_shows_for_the_time_we_asked():
    assert reels.plan_durations(10, seconds_per_card=0.8) == [0.8] * 10


def test_short_day_is_stretched_to_instagram_minimum():
    # 카드 2장이면 1.6초라 인스타 최소(3초)에 못 미친다 — 마지막 장을 늘려 채운다
    durations = reels.plan_durations(2, seconds_per_card=0.8)
    assert sum(durations) >= reels.MIN_DURATION
    assert durations[0] == 0.8 and durations[1] > 0.8


def test_no_cards_no_durations():
    assert reels.plan_durations(0) == []


def test_builds_a_vertical_mp4_with_audio(tmp_path):
    out = reels.build_slideshow(_cards(tmp_path, 4), tmp_path / "릴스.mp4", seconds_per_card=0.8)
    assert out.exists() and out.stat().st_size > 0

    probe = subprocess.run(
        [reels.ffmpeg_exe(), "-hide_banner", "-i", str(out)],
        capture_output=True,
        text=True,
    ).stderr
    # 인스타 릴스가 받는 형태여야 한다: 세로 9:16 H.264 + 오디오 트랙
    assert "1080x1920" in probe
    assert "h264" in probe
    assert "Audio: aac" in probe


def test_empty_card_list_is_refused(tmp_path):
    with pytest.raises(ValueError):
        reels.build_slideshow([], tmp_path / "x.mp4")


def test_path_with_quote_does_not_break_concat(tmp_path):
    # concat 목록은 작은따옴표로 감싸므로 경로에 따옴표가 있으면 깨질 수 있다
    odd = tmp_path / "reborn's cards"
    odd.mkdir()
    out = reels.build_slideshow(_cards(odd, 4), tmp_path / "q.mp4")
    assert out.exists()


# ---------------------------------------------------------------- 게시
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


def test_publish_reel_sends_reels_type_and_video_url(creds, monkeypatch):
    posts = []

    def fake_post(url, data=None, timeout=None):
        posts.append((url, data))
        return FakeResponse({"id": "c-1" if url.endswith("/media") else "m-9"})

    monkeypatch.setattr(instagram.requests, "post", fake_post)
    monkeypatch.setattr(
        instagram.requests, "get", lambda *a, **k: FakeResponse({"status_code": "FINISHED"})
    )

    assert instagram.publish_reel("https://cdn/x.mp4", "캡션", cover_url="https://cdn/c.png") == "m-9"

    fields = posts[0][1]
    assert fields["media_type"] == "REELS"
    assert fields["video_url"] == "https://cdn/x.mp4"
    assert fields["cover_url"] == "https://cdn/c.png"
    # 릴스 탭에만 남지 않고 프로필 피드에도 남아야 한다
    assert fields["share_to_feed"] == "true"
    assert posts[1][1]["creation_id"] == "c-1"


def test_reel_waits_for_video_encoding(creds, monkeypatch):
    seen = {"n": 0}

    def fake_get(url, params=None, timeout=None):
        seen["n"] += 1
        return FakeResponse({"status_code": "FINISHED" if seen["n"] > 2 else "IN_PROGRESS"})

    monkeypatch.setattr(instagram.requests, "post", lambda *a, **k: FakeResponse({"id": "x"}))
    monkeypatch.setattr(instagram.requests, "get", fake_get)
    monkeypatch.setattr(instagram.time, "sleep", lambda s: None)

    instagram.publish_reel("https://cdn/x.mp4", "캡션")
    assert seen["n"] == 3  # 끝날 때까지 기다렸다


def test_reel_gives_up_with_reason_when_encoding_errors(creds, monkeypatch):
    monkeypatch.setattr(instagram.requests, "post", lambda *a, **k: FakeResponse({"id": "x"}))
    monkeypatch.setattr(
        instagram.requests,
        "get",
        lambda *a, **k: FakeResponse({"status_code": "ERROR", "status": "형식 오류"}),
    )
    with pytest.raises(RuntimeError, match="형식 오류"):
        instagram.publish_reel("https://cdn/x.mp4", "캡션")


def test_skips_without_credentials(tmp_path, monkeypatch):
    monkeypatch.delenv("IG_USER_ID", raising=False)
    monkeypatch.delenv("IG_ACCESS_TOKEN", raising=False)
    video = reels.build_slideshow(_cards(tmp_path, 4), tmp_path / "r.mp4")
    report = instagram.publish_reel_video(video, caption="c", key_prefix="reels/x")
    assert not report.ok and "IG_USER_ID" in report.skipped_reason
    # 게시는 못 했어도 영상은 남아 있어야 한다 — 손으로 올릴 수 있게
    assert report.video and report.video.exists()


def test_missing_video_is_reported_not_crashed(tmp_path):
    report = instagram.publish_reel_video(
        tmp_path / "없는파일.mp4", caption="c", key_prefix="reels/x"
    )
    assert not report.ok and "영상이 없습니다" in report.skipped_reason


def test_caption_is_trimmed_to_instagram_limit():
    long = "\n".join(["가" * 100] * 40)  # 2200자 초과
    out = instagram.trim_caption(long)
    assert len(out) <= instagram.CAPTION_MAX
    assert out.endswith("…")


def test_short_caption_is_left_alone():
    assert instagram.trim_caption("짧은 캡션") == "짧은 캡션"
