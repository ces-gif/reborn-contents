"""모델 공급자 추상화 — Gemini(무료) / Anthropic(유료) 중에 골라 쓴다.

파이프라인 나머지 코드는 이 파일의 `LLMClient.structured()` 하나만 안다.
어느 회사 모델을 쓰는지는 설정(model.provider)에서 정한다.

- gemini    : 구글 AI 스튜디오 무료 등급. 카드 등록 없이 하루 수백 건.
              사진 판독·글쓰기·구글 검색까지 다 된다. 기본값.
- anthropic : Claude. 유료(선불 크레딧)지만 판독 정확도가 조금 더 좋다.

둘 다 "스키마를 주면 그 모양의 객체를 돌려준다"는 같은 약속을 지킨다.
"""

from __future__ import annotations

import base64
import io
import json
import logging
import os
import re
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Sequence

from PIL import Image, ImageOps
from pydantic import BaseModel

log = logging.getLogger(__name__)

MAX_EDGE = 1568
JPEG_QUALITY = 82

# 구글이 모델을 종료하면 404 응답에 후속 모델 이름을 알려준다.
#   "This model models/gemini-2.5-flash is no longer available to new users.
#    Please update your code to use models/gemini-3.6-flash ..."
# 이 이름을 뽑아 한 번 자동으로 다시 시도한다. 안 그러면 어느 날 갑자기
# 카드뉴스가 0장이 되는데 원인을 찾기 어렵다.
_SUCCESSOR = re.compile(r"use\s+models/([A-Za-z0-9._-]+)")


class LLMError(RuntimeError):
    pass


class LLMQuotaError(LLMError):
    """하루 요청 한도를 다 썼다. 더 불러봐야 전부 같은 오류라 여기서 멈춘다."""


# --------------------------------------------------------------------- 입력


def text_part(text: str) -> dict:
    return {"type": "text", "text": text}


def image_part(path: Path | str) -> dict:
    return {"type": "image", "path": str(path)}


def _encode_jpeg(path: str) -> bytes:
    """사진을 모델에 넣기 좋은 크기로 줄여 JPEG 바이트로 만든다."""
    img = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    img.thumbnail((MAX_EDGE, MAX_EDGE), Image.LANCZOS)
    buffer = io.BytesIO()
    img.save(buffer, "JPEG", quality=JPEG_QUALITY)
    return buffer.getvalue()


# ------------------------------------------------------------------ 공통 틀


class LLMClient(ABC):
    name: str = "?"

    @abstractmethod
    def structured(
        self,
        *,
        system: str,
        parts: Sequence[dict],
        schema: type[BaseModel],
        max_tokens: int = 8000,
        search: bool = False,
        model: str | None = None,
    ) -> BaseModel:
        """스키마 모양으로 검증된 결과를 돌려준다. search=True 면 웹 검색을 붙인다."""


# ------------------------------------------------------------------- Gemini


class GeminiClient(LLMClient):
    name = "gemini"

    def __init__(self, api_key: str, *, vision_model: str, writing_model: str):
        try:
            from google import genai
        except ImportError as exc:  # pragma: no cover
            raise LLMError("google-genai 가 설치되어 있지 않습니다 (requirements.txt 확인)") from exc
        self._genai = genai
        self._client = genai.Client(api_key=api_key)
        self.vision_model = vision_model
        self.writing_model = writing_model

    def _contents(self, parts: Sequence[dict]) -> list:
        from google.genai import types

        out = []
        for part in parts:
            if part["type"] == "text":
                out.append(types.Part.from_text(text=part["text"]))
            else:
                out.append(
                    types.Part.from_bytes(
                        data=_encode_jpeg(part["path"]), mime_type="image/jpeg"
                    )
                )
        return out

    def structured(
        self,
        *,
        system: str,
        parts: Sequence[dict],
        schema: type[BaseModel],
        max_tokens: int = 8000,
        search: bool = False,
        model: str | None = None,
    ) -> BaseModel:
        from google.genai import types

        model = model or self.writing_model
        contents = self._contents(parts)

        # 제미나이는 '구글 검색'과 'JSON 스키마'를 한 번에 못 쓴다.
        # 그래서 검색이 필요하면 먼저 검색해서 글로 받고, 그 글을 다시 JSON 으로 정리한다.
        if search:
            found = self._call(
                model=model,
                system=system,
                contents=contents,
                max_tokens=max_tokens,
                tools=[types.Tool(google_search=types.GoogleSearch())],
            )
            contents = self._contents(
                [
                    text_part("아래는 웹에서 찾은 내용입니다. 이걸 근거로 정리해 주세요.\n\n" + found),
                ]
            )

        raw = self._call(
            model=model,
            system=system,
            contents=contents,
            max_tokens=max_tokens,
            schema=schema,
        )
        return _parse_json_into(schema, raw)

    def _generate(self, model: str, contents: list, config: dict):
        from google.genai import types

        return self._client.models.generate_content(
            model=model,
            contents=contents,
            config=types.GenerateContentConfig(**config),
        )

    def _call(
        self, *, model: str, system: str, contents: list, max_tokens: int, schema=None, tools=None
    ) -> str:
        from google.genai import types

        config: dict[str, Any] = {
            "system_instruction": system,
            "max_output_tokens": max_tokens,
        }
        if schema is not None:
            config["response_mime_type"] = "application/json"
            config["response_schema"] = schema
        if tools:
            config["tools"] = tools
            # google_search 는 서버가 알아서 도는 도구라 클라이언트 쪽 자동 함수호출이 필요 없다
            config["automatic_function_calling"] = types.AutomaticFunctionCallingConfig(
                disable=True
            )

        try:
            response = self._generate(model, contents, config)
        except Exception as exc:
            wait = _quota_wait(exc)
            if wait is not None:
                log.warning("제미나이 분당 한도에 걸려 %.0f초 쉬었다가 다시 시도합니다", wait)
                time.sleep(wait)
                try:
                    response = self._generate(model, contents, config)
                    text = getattr(response, "text", None)
                    if not text:
                        raise LLMError(f"제미나이가 빈 응답을 돌려줬습니다({model}).")
                    return text
                except LLMError:
                    raise
                except Exception as retry_exc:
                    exc = retry_exc
            if _is_quota_error(exc):
                raise LLMQuotaError(f"{QUOTA_HELP}\n(원문: {exc})") from exc
            successor = _successor_model(exc)
            if not successor:
                raise LLMError(f"제미나이 호출 실패({model}): {exc}") from exc
            log.warning("%s 모델이 종료되어 %s 로 자동 전환합니다", model, successor)
            self.vision_model = _swap(self.vision_model, model, successor)
            self.writing_model = _swap(self.writing_model, model, successor)
            try:
                response = self._generate(successor, contents, config)
            except Exception as retry_exc:
                raise LLMError(f"제미나이 호출 실패({successor}): {retry_exc}") from retry_exc

        text = getattr(response, "text", None)
        if not text:
            raise LLMError(f"제미나이가 빈 응답을 돌려줬습니다({model}). 안전 필터에 걸렸을 수 있습니다.")
        return text


# ---------------------------------------------------------------- Anthropic

ANTHROPIC_WEB_SEARCH = {
    "type": "web_search_20260209",
    "name": "web_search",
    "max_uses": 3,
    "user_location": {"type": "approximate", "country": "KR", "timezone": "Asia/Seoul"},
}
MAX_PAUSE_TURNS = 4


class AnthropicClient(LLMClient):
    name = "anthropic"

    def __init__(self, api_key: str, *, vision_model: str, writing_model: str):
        try:
            from anthropic import Anthropic
        except ImportError as exc:  # pragma: no cover
            raise LLMError("anthropic 이 설치되어 있지 않습니다 (requirements.txt 확인)") from exc
        self._client = Anthropic(api_key=api_key)
        self.vision_model = vision_model
        self.writing_model = writing_model

    def _content(self, parts: Sequence[dict]) -> list[dict]:
        out: list[dict] = []
        for part in parts:
            if part["type"] == "text":
                out.append({"type": "text", "text": part["text"]})
            else:
                out.append(
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": base64.standard_b64encode(
                                _encode_jpeg(part["path"])
                            ).decode("ascii"),
                        },
                    }
                )
        return out

    def structured(
        self,
        *,
        system: str,
        parts: Sequence[dict],
        schema: type[BaseModel],
        max_tokens: int = 8000,
        search: bool = False,
        model: str | None = None,
    ) -> BaseModel:
        model = model or self.writing_model
        messages = [{"role": "user", "content": self._content(parts)}]
        kwargs: dict[str, Any] = {}
        if search:
            kwargs["tools"] = [ANTHROPIC_WEB_SEARCH]

        try:
            for _ in range(MAX_PAUSE_TURNS):
                response = self._client.messages.parse(
                    model=model,
                    max_tokens=max_tokens,
                    system=system,
                    output_format=schema,
                    messages=messages,
                    **kwargs,
                )
                if response.stop_reason != "pause_turn":
                    return response.parsed_output
                messages = messages + [{"role": "assistant", "content": response.content}]
        except Exception as exc:
            raise LLMError(f"Claude 호출 실패({model}): {exc}") from exc
        raise LLMError("Claude 웹 검색이 끝나지 않았습니다")


# ------------------------------------------------------------------- 공통


_JSON_BLOCK = re.compile(r"\{.*\}", re.S)


_RETRY_DELAY = re.compile(r"[Rr]etry in ([0-9.]+)s")
QUOTA_HELP = (
    "제미나이 무료 등급의 하루 요청 수를 다 썼습니다. "
    "https://aistudio.google.com/apikey 에서 API 키가 붙어 있는 프로젝트에 결제를 켜면 "
    "한도가 풀립니다 (사진 판독은 하루 몇십 원 수준입니다). "
    "제미나이 앱 구독(Google One AI)은 API 한도와 별개라 도움이 되지 않습니다."
)


def _quota_wait(exc: Exception) -> float | None:
    """분당 한도라 잠깐 기다리면 되는 오류면 기다릴 초를 돌려준다.

    하루 한도(PerDay)는 기다려도 안 풀리니 None 을 돌려 바로 포기한다 —
    37초씩 헛기다리다 실행 시간만 날리는 게 제일 나쁘다.
    """
    message = str(exc)
    if "RESOURCE_EXHAUSTED" not in message and "429" not in message:
        return None
    if "PerDay" in message:
        return None
    match = _RETRY_DELAY.search(message)
    if not match:
        return None
    return min(float(match.group(1)) + 1, 65)


def _is_quota_error(exc: Exception) -> bool:
    message = str(exc)
    return "RESOURCE_EXHAUSTED" in message or "429" in message


def _successor_model(exc: Exception) -> str | None:
    """모델 종료 오류라면 구글이 알려준 후속 모델 이름을 돌려준다."""
    message = str(exc)
    if "no longer available" not in message and "not found" not in message.lower():
        return None
    match = _SUCCESSOR.search(message)
    return match.group(1) if match else None


def _swap(current: str, old: str, new: str) -> str:
    return new if current == old else current


def _parse_json_into(schema: type[BaseModel], raw: str) -> BaseModel:
    """모델이 JSON 앞뒤에 설명을 붙여도 건져낸다."""
    try:
        return schema.model_validate_json(raw)
    except Exception:
        pass
    match = _JSON_BLOCK.search(raw)
    if not match:
        raise LLMError(f"모델 응답에서 JSON 을 찾지 못했습니다: {raw[:200]}")
    try:
        return schema.model_validate(json.loads(match.group(0)))
    except Exception as exc:
        raise LLMError(f"모델 응답이 예상한 형식이 아닙니다: {exc}") from exc


def make_client(settings) -> LLMClient:
    """설정과 환경변수를 보고 쓸 수 있는 공급자를 고른다."""
    provider = (settings.provider or "").lower()

    gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")

    if provider == "auto":
        provider = "gemini" if gemini_key else "anthropic"

    if provider == "gemini":
        if not gemini_key:
            raise LLMError(
                "GEMINI_API_KEY 가 없습니다. https://aistudio.google.com/apikey 에서 "
                "무료로 발급받아 깃허브 시크릿에 넣어주세요. (docs/SETUP.md 참고)"
            )
        log.info("모델 공급자: 제미나이(무료) — %s / %s", settings.vision_model, settings.writing_model)
        return GeminiClient(
            gemini_key,
            vision_model=settings.vision_model,
            writing_model=settings.writing_model,
        )

    if provider == "anthropic":
        if not anthropic_key:
            raise LLMError(
                "ANTHROPIC_API_KEY 가 없습니다. 무료로 쓰시려면 설정의 model.provider 를 "
                "'gemini' 로 두고 GEMINI_API_KEY 를 넣어주세요. (docs/SETUP.md 참고)"
            )
        log.info("모델 공급자: Claude(유료) — %s / %s", settings.vision_model, settings.writing_model)
        return AnthropicClient(
            anthropic_key,
            vision_model=settings.vision_model,
            writing_model=settings.writing_model,
        )

    raise LLMError(f"모르는 모델 공급자입니다: {provider!r} (gemini 또는 anthropic)")
