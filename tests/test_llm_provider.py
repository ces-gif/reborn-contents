"""모델 공급자 고르기 / 응답 파싱."""

from __future__ import annotations

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

def test_auto_prefers_free_gemini_when_its_key_is_present(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "x")
    monkeypatch.setattr(llm, "GeminiClient", lambda *a, **k: "gemini-client")
    assert llm.make_client(settings("auto")) == "gemini-client"


def test_auto_falls_back_to_anthropic_when_only_that_key_is_present(monkeypatch):
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
