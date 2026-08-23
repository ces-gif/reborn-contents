"""모델 공급자 고르기 / 응답 파싱."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from PIL import Image
from pydantic import BaseModel

from reborn import llm
from reborn.config import load_settings


class Sample(BaseModel):
    name: str
    count: int


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for key in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "ANTHROPIC_API_KEY"):
        monkeypatch.delenv(key, raising=False)


def settings(provider):
    s = load_settings()
    s.provider = provider
    return s


# ------------------------------------------------------------ 공급자 선택

def _no_cli(monkeypatch):
    """claude 명령이 없는 환경인 척한다."""
    monkeypatch.delenv("CLAUDE_CODE_OAUTH_TOKEN", raising=False)
    monkeypatch.setattr(llm.shutil, "which", lambda name: None)


def test_auto_prefers_the_subscription_when_claude_is_available(monkeypatch):
    """구독으로 돌 수 있으면 그게 1순위다 — 하루 한도도 결제도 없다."""
    monkeypatch.setenv("GEMINI_API_KEY", "x")
    monkeypatch.setattr(llm.shutil, "which", lambda name: "/usr/bin/claude")
    monkeypatch.setattr(llm, "ClaudeCliClient", lambda *a, **k: "cli-client")
    assert llm.make_client(settings("auto")) == "cli-client"


def test_auto_prefers_free_gemini_when_its_key_is_present(monkeypatch):
    _no_cli(monkeypatch)
    monkeypatch.setenv("GEMINI_API_KEY", "x")
    monkeypatch.setattr(llm, "GeminiClient", lambda *a, **k: "gemini-client")
    assert llm.make_client(settings("auto")) == "gemini-client"


def test_auto_falls_back_to_anthropic_when_only_that_key_is_present(monkeypatch):
    _no_cli(monkeypatch)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "x")
    monkeypatch.setattr(llm, "AnthropicClient", lambda *a, **k: "claude-client")
    assert llm.make_client(settings("auto")) == "claude-client"


def test_google_api_key_also_works_for_gemini(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "x")
    monkeypatch.setattr(llm, "GeminiClient", lambda *a, **k: "gemini-client")
    assert llm.make_client(settings("gemini")) == "gemini-client"


def test_missing_gemini_key_points_at_the_free_signup_page():
    with pytest.raises(llm.LLMError, match="aistudio.google.com"):
        llm.make_client(settings("gemini"))


def test_missing_anthropic_key_suggests_the_free_option():
    with pytest.raises(llm.LLMError, match="gemini"):
        llm.make_client(settings("anthropic"))


def test_unknown_provider_is_rejected():
    with pytest.raises(llm.LLMError, match="모르는 모델 공급자"):
        llm.make_client(settings("openai"))


# --------------------------------------------------------------- 응답 파싱

def test_plain_json_is_parsed():
    got = llm._parse_json_into(Sample, '{"name": "밥솥", "count": 2}')
    assert got.name == "밥솥" and got.count == 2


def test_json_wrapped_in_markdown_fence_is_recovered():
    raw = '설명입니다.\n```json\n{"name": "밥솥", "count": 2}\n```\n끝.'
    assert llm._parse_json_into(Sample, raw).count == 2


def test_unparseable_response_raises_a_clear_error():
    with pytest.raises(llm.LLMError, match="JSON"):
        llm._parse_json_into(Sample, "죄송합니다, 답변할 수 없습니다.")


# ----------------------------------------------------------------- 이미지

def test_large_photo_is_shrunk_before_sending(tmp_path):
    path = tmp_path / "big.jpg"
    Image.new("RGB", (4000, 3000), (200, 200, 200)).save(path)
    data = llm._encode_jpeg(str(path))
    with Image.open(__import__("io").BytesIO(data)) as img:
        assert max(img.size) <= llm.MAX_EDGE
    assert data[:2] == b"\xff\xd8"  # JPEG


def test_parts_helpers_build_the_expected_shape(tmp_path):
    assert llm.text_part("안녕") == {"type": "text", "text": "안녕"}
    assert llm.image_part(Path("a.jpg")) == {"type": "image", "path": "a.jpg"}


# -------------------------------------------- 모델 종료 시 자동 전환

def test_successor_model_is_picked_up_from_google_error():
    """구글이 모델을 종료하면 404 메시지에 후속 모델 이름을 알려준다."""
    exc = Exception(
        "404 NOT_FOUND. {'error': {'code': 404, 'message': 'This model "
        "models/gemini-2.5-flash is no longer available to new users. Please update "
        "your code to use models/gemini-3.6-flash for the latest features.'}}"
    )
    assert llm._successor_model(exc) == "gemini-3.6-flash"


def test_ordinary_errors_do_not_trigger_a_model_swap():
    assert llm._successor_model(Exception("429 rate limit exceeded")) is None
    assert llm._successor_model(Exception("permission denied")) is None


def test_retired_model_is_retried_once_with_the_successor(monkeypatch):
    """종료된 모델로 부르면 후속 모델로 한 번 다시 시도하고, 다음부터는 그걸 쓴다."""
    monkeypatch.setenv("GEMINI_API_KEY", "x")

    calls: list[str] = []

    class FakeGemini(llm.GeminiClient):
        def __init__(self):  # 실제 SDK 를 부르지 않는다
            self.vision_model = "gemini-2.5-flash"
            self.writing_model = "gemini-2.5-flash"

        def _generate(self, model, contents, config):
            calls.append(model)
            if model == "gemini-2.5-flash":
                raise Exception(
                    "404 This model models/gemini-2.5-flash is no longer available to "
                    "new users. Please update your code to use models/gemini-3.6-flash"
                )

            class R:
                text = '{"name": "밥솥", "count": 1}'

            return R()

    client = FakeGemini()
    got = client._call(
        model="gemini-2.5-flash", system="s", contents=[], max_tokens=100, schema=Sample
    )
    assert calls == ["gemini-2.5-flash", "gemini-3.6-flash"]
    assert '"밥솥"' in got
    # 다음 호출부터는 새 모델을 기본으로 쓴다
    assert client.vision_model == "gemini-3.6-flash"
    assert client.writing_model == "gemini-3.6-flash"


def test_a_genuinely_broken_model_name_still_raises(monkeypatch):
    class FakeGemini(llm.GeminiClient):
        def __init__(self):
            self.vision_model = self.writing_model = "nope"

        def _generate(self, model, contents, config):
            raise Exception("400 invalid argument")

    with pytest.raises(llm.LLMError, match="제미나이 호출 실패"):
        FakeGemini()._call(model="nope", system="s", contents=[], max_tokens=100, schema=Sample)


# ------------------------------------------------------- 요청 한도(429) 다루기

_PER_DAY = (
    "429 RESOURCE_EXHAUSTED. Quota exceeded for metric: generate_content_free_tier_requests, "
    "quotaId: 'GenerateRequestsPerDayPerProjectPerModel-FreeTier'. Please retry in 37.5s."
)
_PER_MINUTE = (
    "429 RESOURCE_EXHAUSTED. quotaId: 'GenerateRequestsPerMinutePerProjectPerModel-FreeTier'. "
    "Please retry in 12.0s."
)


def test_per_minute_limit_says_how_long_to_wait():
    assert llm._quota_wait(RuntimeError(_PER_MINUTE)) == pytest.approx(13.0)


def test_per_day_limit_does_not_wait():
    """하루 한도는 기다려도 안 풀린다. 37초씩 헛기다리면 실행 시간만 날린다."""
    assert llm._quota_wait(RuntimeError(_PER_DAY)) is None


def test_other_errors_are_not_quota_errors():
    assert llm._quota_wait(RuntimeError("500 internal")) is None
    assert not llm._is_quota_error(RuntimeError("500 internal"))
    assert llm._is_quota_error(RuntimeError(_PER_DAY))


def test_daily_quota_raises_a_quota_error_that_tells_the_user_what_to_do(monkeypatch):
    client = llm.GeminiClient.__new__(llm.GeminiClient)
    client.vision_model = client.writing_model = "gemini-3.6-flash"

    def boom(model, contents, config):
        raise RuntimeError(_PER_DAY)

    monkeypatch.setattr(client, "_generate", boom)
    monkeypatch.setattr(llm, "_swap", lambda c, o, n: c)
    with pytest.raises(llm.LLMQuotaError) as caught:
        client._call(model="gemini-3.6-flash", system="s", contents=[], max_tokens=10)
    assert "결제를 켜면" in str(caught.value)


# ------------------------------------------ 구독으로 도는 길 (claude CLI)


class FakeRun:
    """subprocess.run 흉내."""

    def __init__(self, stdout="", returncode=0, stderr=""):
        self.stdout, self.returncode, self.stderr = stdout, returncode, stderr


class Tiny(BaseModel):
    name: str
    price: int


def _cli(monkeypatch, **run):
    monkeypatch.setattr(llm.shutil, "which", lambda n: "/usr/bin/claude")
    client = llm.ClaudeCliClient(vision_model="claude-sonnet-5", writing_model="claude-sonnet-5")
    seen = {}

    def fake_run(cmd, **kwargs):
        seen["cmd"] = cmd
        return FakeRun(**run)

    monkeypatch.setattr(llm.subprocess, "run", fake_run)
    return client, seen


def test_cli_returns_the_parsed_object(monkeypatch):
    client, _ = _cli(
        monkeypatch,
        stdout=json.dumps({"result": '{"name": "게이밍 의자", "price": 43500}'}),
    )
    got = client.structured(system="s", parts=[llm.text_part("hi")], schema=Tiny)
    assert (got.name, got.price) == ("게이밍 의자", 43500)


def test_cli_passes_photos_as_paths_not_bytes(tmp_path, monkeypatch):
    """사진은 바이트가 아니라 경로로 넘긴다 — CLI 안의 Read 도구가 파일을 직접 연다."""
    photo = tmp_path / "a.jpg"
    Image.new("RGB", (40, 30), (200, 200, 200)).save(photo)
    client, seen = _cli(monkeypatch, stdout=json.dumps({"result": '{"name":"x","price":1}'}))
    client.structured(system="s", parts=[llm.image_part(photo)], schema=Tiny)
    prompt = seen["cmd"][2]
    assert ".jpg" in prompt and "Read" in seen["cmd"]


def test_cli_straightens_rotated_photos_before_sending(tmp_path, monkeypatch):
    """휴대폰 사진은 EXIF 로만 회전돼 있다. 누운 가격표를 넘기면 모델이 못 읽는다."""
    photo = tmp_path / "rot.jpg"
    # EXIF orientation 6 = 90도 돌려서 봐야 하는 사진. 픽셀은 가로(60x20)로 누워 있다.
    img = Image.new("RGB", (60, 20), (10, 10, 10))
    exif = img.getexif()
    exif[274] = 6
    img.save(photo, exif=exif)

    monkeypatch.setattr(llm.shutil, "which", lambda n: "/usr/bin/claude")
    client = llm.ClaudeCliClient(vision_model="m", writing_model="m")
    seen: dict = {}

    def peek(cmd, **kwargs):
        # 임시 파일은 호출이 끝나면 지워지므로, 살아 있는 이 순간에 열어본다.
        path = re.search(r"사진 파일: (\S+)", cmd[2]).group(1)
        with Image.open(path) as opened:
            seen["size"] = opened.size
        return FakeRun(stdout=json.dumps({"result": '{"name":"x","price":1}'}))

    monkeypatch.setattr(llm.subprocess, "run", peek)
    client.structured(system="s", parts=[llm.image_part(photo)], schema=Tiny)
    assert seen["size"] == (20, 60), "사진이 똑바로 세워지지 않았습니다"


def test_cli_cleans_up_its_temp_photos(tmp_path, monkeypatch):
    photo = tmp_path / "a.jpg"
    Image.new("RGB", (40, 30), (200, 200, 200)).save(photo)
    monkeypatch.setattr(llm.shutil, "which", lambda n: "/usr/bin/claude")
    client = llm.ClaudeCliClient(vision_model="m", writing_model="m")
    seen: dict = {}

    def peek(cmd, **kwargs):
        seen["path"] = re.search(r"사진 파일: (\S+)", cmd[2]).group(1)
        return FakeRun(stdout=json.dumps({"result": '{"name":"x","price":1}'}))

    monkeypatch.setattr(llm.subprocess, "run", peek)
    client.structured(system="s", parts=[llm.image_part(photo)], schema=Tiny)
    assert not Path(seen["path"]).exists()


def test_cli_asks_for_web_search_only_when_wanted(monkeypatch):
    client, seen = _cli(monkeypatch, stdout=json.dumps({"result": '{"name":"x","price":1}'}))
    client.structured(system="s", parts=[llm.text_part("q")], schema=Tiny, search=True)
    assert "WebSearch" in seen["cmd"]

    client, seen = _cli(monkeypatch, stdout=json.dumps({"result": '{"name":"x","price":1}'}))
    client.structured(system="s", parts=[llm.text_part("q")], schema=Tiny)
    assert "WebSearch" not in seen["cmd"]


def test_cli_failure_says_how_to_log_in(monkeypatch):
    client, _ = _cli(monkeypatch, returncode=1, stderr="Invalid API key")
    with pytest.raises(llm.LLMError) as caught:
        client.structured(system="s", parts=[llm.text_part("q")], schema=Tiny)
    assert "CLAUDE_CODE_OAUTH_TOKEN" in str(caught.value)


def test_cli_reports_an_error_result(monkeypatch):
    client, _ = _cli(
        monkeypatch, stdout=json.dumps({"is_error": True, "result": "usage limit reached"})
    )
    with pytest.raises(llm.LLMError, match="usage limit"):
        client.structured(system="s", parts=[llm.text_part("q")], schema=Tiny)


def test_missing_claude_binary_is_explained(monkeypatch):
    monkeypatch.setattr(llm.shutil, "which", lambda n: None)
    with pytest.raises(llm.LLMError, match="찾을 수 없습니다"):
        llm.ClaudeCliClient(vision_model="m", writing_model="m")


def test_cli_hides_the_api_key_from_the_child_process(monkeypatch):
    """구독으로 돌기로 했으면 API 키가 끼어들면 안 된다.

    claude CLI 는 ANTHROPIC_API_KEY 를 먼저 쓴다. 그 키에 크레딧이 없으면
    구독 토큰이 멀쩡해도 전부 "Credit balance is too low" 로 실패한다.
    """
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-dead")
    monkeypatch.setenv("CLAUDE_CODE_OAUTH_TOKEN", "sk-ant-oat-alive")
    monkeypatch.setattr(llm.shutil, "which", lambda n: "/usr/bin/claude")
    client = llm.ClaudeCliClient(vision_model="m", writing_model="m")
    seen = {}

    def fake_run(cmd, **kwargs):
        seen["env"] = kwargs["env"]
        return FakeRun(stdout=json.dumps({"result": '{"name":"x","price":1}'}))

    monkeypatch.setattr(llm.subprocess, "run", fake_run)
    client.structured(system="s", parts=[llm.text_part("q")], schema=Tiny)

    assert "ANTHROPIC_API_KEY" not in seen["env"]
    assert seen["env"]["CLAUDE_CODE_OAUTH_TOKEN"] == "sk-ant-oat-alive"


def test_credit_error_explains_the_api_key_clash(monkeypatch):
    client, _ = _cli(
        monkeypatch,
        stdout=json.dumps({"api_error_status": 400, "result": "Credit balance is too low"}),
    )
    with pytest.raises(llm.LLMError) as caught:
        client.structured(system="s", parts=[llm.text_part("q")], schema=Tiny)
    assert "ANTHROPIC_API_KEY" in str(caught.value)
