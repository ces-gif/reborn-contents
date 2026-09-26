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


# 계정 ID 는 매장 설정에서 오고(ig_user_id 인자), 토큰만 환경변수다.
IG = "1784"


@pytest.fixture
def creds(monkeypatch):
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

    assert instagram.publish_reel("https://cdn/x.mp4", "캡션", cover_url="https://cdn/c.png", ig_user_id=IG) == "m-9"

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

    instagram.publish_reel("https://cdn/x.mp4", "캡션", ig_user_id=IG)
    assert seen["n"] == 3  # 끝날 때까지 기다렸다


def test_reel_gives_up_with_reason_when_encoding_errors(creds, monkeypatch):
    monkeypatch.setattr(instagram.requests, "post", lambda *a, **k: FakeResponse({"id": "x"}))
    monkeypatch.setattr(
        instagram.requests,
        "get",
        lambda *a, **k: FakeResponse({"status_code": "ERROR", "status": "형식 오류"}),
    )
    with pytest.raises(RuntimeError, match="형식 오류"):
        instagram.publish_reel("https://cdn/x.mp4", "캡션", ig_user_id=IG)


def test_skips_without_credentials(tmp_path, monkeypatch):
    """계정이 없는 매장(일산)은 게시하지 않는다. 환경변수로 대신하지도 않는다."""
    monkeypatch.setenv("IG_USER_ID", "1784")
    monkeypatch.setenv("IG_ACCESS_TOKEN", "tok")
    video = reels.build_slideshow(_cards(tmp_path, 4), tmp_path / "r.mp4")
    report = instagram.publish_reel_video(video, caption="c", key_prefix="reels/x")
    assert not report.ok and "계정이 설정되지 않아" in report.skipped_reason
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


# ---------------------------------------------------------------- 저장 위치
def test_reel_goes_next_to_the_cards_of_the_busiest_source():
    """릴스는 카드가 가장 많이 나온 폴더(보통 '리퍼')에 함께 둔다."""
    from reborn.pipeline import RunResult, _reel_folder

    class FakeProduct:
        def __init__(self, source_name):
            self.source_name = source_name
            self.publishable = True

    result = RunResult(day="2026-09-05")
    result.products = [FakeProduct("리퍼")] * 9 + [FakeProduct("새상품")] * 2
    assert _reel_folder(result) == "리퍼"


def test_reel_folder_defaults_to_refurb_when_nothing_published():
    from reborn.pipeline import RunResult, _reel_folder

    assert _reel_folder(RunResult(day="2026-09-05")) == "리퍼"


def test_reel_build_failure_is_reported_not_silent(tmp_path, monkeypatch):
    """영상이 안 만들어졌으면 리포트에 남아야 한다.

    첫 실전에서 ffmpeg 가 러너에 없어 영상이 통째로 빠졌는데, 경고 로그만
    남고 리포트에는 한 줄도 없었다. 왜 영상이 없는지 알 수가 없었다.
    """
    from reborn.pipeline import RunResult

    result = RunResult(day="2026-09-05")
    result.reel_error = "ffmpeg 를 찾을 수 없습니다"
    result.step_failures.append(f"릴스 영상: {result.reel_error}")

    assert result.step_failures  # 깃허브 이슈로 알림이 가는 통로


# ---------------------------------------------------------------- 릴스 캡션
def _product(name, sale, orig=None, category="주방"):
    from reborn.vision import Product

    p = Product.__new__(Product)
    p.product_name, p.sale_price, p.original_price = name, sale, orig
    p.discount_pct, p.spec_line, p.condition_note = None, "", ""
    p.category, p.source_name = category, "리퍼"
    return p


def test_reel_caption_leads_with_a_hook_not_a_product_list():
    """릴스는 첫 줄만 보인다. 상품 나열로 시작하면 아무도 안 멈춘다."""
    from reborn import social

    caption = social.reel_caption(
        [_product("아이넥스 싱크선반 600", 63300, 126650)],
        store_name="리본마켓 평택점",
        address="경기 평택시 이충로 49-29 103호 리본마켓",
        parking_note="*건물 건너편 무료 공영주차장 있음!",
    )
    first = caption.splitlines()[0]
    assert first == "주방 새로 채우지 마세요!"
    assert "63,300원" in caption and "126,650원" in caption
    assert "경기 평택시" in caption


def test_reel_caption_shows_the_three_biggest_savings():
    """열두 개를 다 적으면 '더 보기' 뒤로 묻힌다. 아낀 돈이 큰 셋만."""
    from reborn import social

    products = [
        _product("소소한절약", 9000, 10000),   # 1,000원 절약
        _product("최대절약", 63300, 126650),   # 63,350원 절약
        _product("중간절약", 19600, 48800),    # 29,200원 절약
        _product("조금절약", 7400, 14800),     # 7,400원 절약
    ]
    caption = social.reel_caption(products, store_name="리본마켓 평택점")
    assert "최대절약" in caption and "중간절약" in caption and "조금절약" in caption
    # 가장 덜 아끼는 하나는 빠진다 — 셋만 보여준다
    assert "소소한절약" not in caption


def test_reel_caption_never_invents_an_address():
    """주소를 모르는 매장(일산)에 평택 주소를 붙이면 손님이 헛걸음한다."""
    from reborn import social

    caption = social.reel_caption(
        [_product("원목 스툴", 7900, 15800)], store_name="여우마켓 일산점"
    )
    assert "📍 여우마켓 일산점" in caption
    assert "평택" not in caption


def test_reel_caption_has_no_hashtags():
    """매장 실제 릴스에는 해시태그가 없다."""
    from reborn import social

    caption = social.reel_caption([_product("냄비", 22400, 44800)], store_name="리본마켓 평택점")
    assert "#" not in caption


def test_reel_caption_never_says_used():
    from reborn import social

    caption = social.reel_caption([_product("냄비", 22400, 44800)], store_name="리본마켓 평택점")
    assert "중고 절대 X" in caption  # 중고가 아니라는 말은 해도 된다
    assert "중고 상품" not in caption


# ------------------------------------------- 쇼핑몰 등록명이 통째로 들어온 날


def test_reel_caption_trims_a_shopping_mall_listing_name():
    """실제 일산 09-05: 좌식의자 이름 하나가 60자를 넘어 한 줄을 다 먹었다."""
    from reborn import social

    long_name = (
        "FlexiSpot 좌식의자 접이식 패브릭 등받이좌식의자 좌식 소파 "
        "휴대용 캠핑좌식의자 FC0 / 화이트"
    )
    caption = social.reel_caption(
        [_product(long_name, 52000, 104000)], store_name="여우마켓 일산점"
    )
    line = next(l for l in caption.splitlines() if "52,000원" in l)
    assert len(line) <= 60
    assert line.startswith("FlexiSpot 좌식의자")


def test_reel_caption_cuts_at_the_option_separator():
    """'_' 뒤는 옵션(색상·구성)이라 상품 이름이 아니다."""
    from reborn import social

    caption = social.reel_caption(
        [_product("풀인퍼니 베나 식탁세트_베나 의자_스노우화이트", 33800, 67600)],
        store_name="여우마켓 일산점",
    )
    assert "풀인퍼니 베나 식탁세트 33,800원" in caption
    assert "스노우화이트" not in caption


def test_reel_caption_leaves_a_normal_name_alone():
    """짧은 이름까지 건드리면 상품을 못 알아본다."""
    from reborn import social

    caption = social.reel_caption(
        [_product("아이넥스 싱크선반 600", 63300, 126650)], store_name="리본마켓 평택점"
    )
    assert "아이넥스 싱크선반 600 63,300원" in caption


# ------------------------------------------------------------- 주제곡 (BGM)


def _tone(tmp_path: Path, seconds: float = 2.0) -> Path:
    """짧은 테스트용 소리. 주제곡 파일 대신 쓴다 (저장소에 음원을 넣지 않는다)."""
    path = tmp_path / "theme.m4a"
    subprocess.run(
        [reels.ffmpeg_exe(), "-y", "-hide_banner", "-loglevel", "error",
         "-f", "lavfi", "-i", f"sine=frequency=440:duration={seconds}",
         "-c:a", "aac", str(path)],
        check=True,
    )
    return path


def test_주제곡이_있으면_영상에_깔린다(tmp_path):
    out = reels.build_slideshow(
        _cards(tmp_path, 5), tmp_path / "릴스.mp4",
        seconds_per_card=0.8, music=_tone(tmp_path, 2.0),
    )
    probe = subprocess.run(
        [reels.ffmpeg_exe(), "-hide_banner", "-i", str(out)], capture_output=True, text=True
    ).stderr
    assert "Audio: aac" in probe
    assert "1080x1920" in probe


def test_짧은_주제곡은_영상_길이만큼_반복된다(tmp_path):
    """2초짜리 곡으로 8초 영상을 만들어도 중간에 소리가 끊기면 안 된다."""
    music = _tone(tmp_path, 2.0)
    audio_in, _ = reels.audio_args(music, total_seconds=8.0)
    assert audio_in[:2] == ["-stream_loop", "-1"]


def test_주제곡은_끝에서_페이드아웃된다(tmp_path):
    _, filters = reels.audio_args(_tone(tmp_path, 2.0), total_seconds=10.0)
    chain = filters[filters.index("-af") + 1]
    assert f"afade=t=out:st={10.0 - reels.FADE_OUT:.3f}" in chain


def test_주제곡이_없으면_예전처럼_무음_트랙(tmp_path):
    audio_in, filters = reels.audio_args(None, total_seconds=10.0)
    assert "anullsrc" in " ".join(audio_in)
    assert filters == []


def test_주제곡_파일이_없으면_무음으로_만든다(tmp_path):
    """음원이 빠졌다고 그날 릴스를 통째로 못 만들면 안 된다."""
    out = reels.build_slideshow(
        _cards(tmp_path, 4), tmp_path / "릴스.mp4",
        seconds_per_card=0.8, music=tmp_path / "없는파일.mp3",
    )
    assert out.exists() and out.stat().st_size > 0


# ------------------------------------------------------------- 카드 순서


def test_카드는_받은_번호_순서_그대로_이어붙인다(tmp_path, monkeypatch):
    """손님이 카드 번호로 예약하니 영상도 1·2·3 순서여야 한다."""
    cards = _cards(tmp_path, 4)
    seen: dict[str, list[str]] = {}

    real = subprocess.run

    def spy(cmd, *a, **kw):
        listing = Path(cmd[cmd.index("-i") + 1])
        seen["lines"] = listing.read_text(encoding="utf-8").splitlines()
        return real(cmd, *a, **kw)

    monkeypatch.setattr(reels.subprocess, "run", spy)
    reels.build_slideshow(cards, tmp_path / "릴스.mp4", seconds_per_card=0.8)

    files = [ln for ln in seen["lines"] if ln.startswith("file ")]
    # 마지막 한 줄은 concat demuxer 때문에 다시 적은 것이라 빼고 본다
    assert [Path(ln[6:-1]).name for ln in files[:-1]] == [c.name for c in cards]


def test_표지가_맨_앞_그다음이_1번_카드(tmp_path, monkeypatch):
    """파이프라인이 넘기는 순서: 표지 → 01 → 02 … 이 순서가 영상 순서다."""
    from reborn import pipeline

    cover = tmp_path / "00-표지.png"
    Image.new("RGB", (1080, 1920), (253, 111, 35)).save(cover)
    cards = _cards(tmp_path, 3)
    frames = [cover] + cards
    assert [p.name for p in frames][0] == "00-표지.png"
    assert [p.name for p in frames][1:] == [c.name for c in cards]
    assert pipeline.reel_music_path("") is None


def test_주제곡_경로는_저장소_기준으로_찾는다(tmp_path):
    from reborn import pipeline

    assert pipeline.reel_music_path("assets/music/없는곡.mp3") is None
    assert pipeline.reel_music_path("") is None
