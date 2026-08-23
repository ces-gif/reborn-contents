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
