"""모델 공급자 추상화 — 구독(claude CLI) / Gemini / Anthropic 중에 골라 쓴다.

파이프라인 나머지 코드는 이 파일의 `LLMClient.structured()` 하나만 안다.
어느 회사 모델을 쓰는지는 설정(model.provider)에서 정한다.

- claude-cli : 설치된 `claude` 명령을 부른다. **은성님 클로드 구독**으로 돌아서
               API 키도 종량 결제도 필요 없다. 코워크에서 쓰시던 것과 같은 방식.
- gemini     : 구글 AI 스튜디오. 무료 등급은 모델당 하루 20회라 상품 10개쯤에서 막힌다.
               한도를 풀려면 API 키가 붙은 프로젝트에 결제를 켜야 한다.
- anthropic  : Claude API. 별도 선불 크레딧이 필요하다(구독과 별개).

둘 다 "스키마를 주면 그 모양의 객체를 돌려준다"는 같은 약속을 지킨다.
"""

from __future__ import annotations

import base64
import io
import json
import logging
import os
import re
import shutil
import subprocess
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
    # 어느 모델을 쓸지는 공급자가 안다. 파이프라인은 여기에 물어본다 —
    # 구독으로 돌 때와 API 로 돌 때 모델 이름이 서로 다르기 때문이다.
    vision_model: str = ""
    writing_model: str = ""

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



# ------------------------------------------------- Claude Code CLI (구독으로)

CLI_TIMEOUT = 300
CLI_HELP = (
    "클로드 코드 CLI 로 로그인이 안 되어 있습니다. 깃허브 액션에서 쓰시려면 "
    "CLAUDE_CODE_OAUTH_TOKEN 시크릿이 필요합니다 (내 컴퓨터에서 `claude setup-token` 으로 발급). "
    "docs/SETUP.md 의 '클로드 구독으로 돌리기' 참고."
)


class ClaudeCliClient(LLMClient):
    """설치된 `claude` 명령을 불러서 쓴다 — 구독으로 도는 길.

    별도 API 키도, 종량 결제도 필요 없다. 은성님이 코워크에서 쓰시던 것과 같은
    구독을 그대로 쓴다. 사진은 파일 경로로 넘기고 CLI 안의 Read 도구가 읽는다.
    """

    name = "claude-cli"

    def __init__(self, *, vision_model: str, writing_model: str, binary: str = "claude"):
        self.vision_model = vision_model
        self.writing_model = writing_model
        self.binary = binary
        if shutil.which(binary) is None:
            raise LLMError(f"`{binary}` 명령을 찾을 수 없습니다. {CLI_HELP}")

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
        prompt = _cli_prompt(system, parts, schema, search=search)
        tools = ["Read", "WebSearch"] if search else ["Read"]
        raw = self._run(prompt, model=model or self.writing_model, tools=tools)
        return _parse_json_into(schema, raw)

    def _child_env(self) -> dict[str, str]:
        """구독 토큰이 API 키에 밀리지 않게 환경을 정리한다.

        ANTHROPIC_API_KEY 가 환경에 있으면 claude CLI 는 그걸 먼저 쓴다.
        그 키에 크레딧이 없으면 구독 토큰이 멀쩡해도 전부
        "Credit balance is too low" 로 실패한다 (실제로 그렇게 됐다).
        구독으로 돌기로 한 이상 API 키 쪽 설정은 자식 프로세스에서 걷어낸다.
        """
        env = dict(os.environ)
        for name in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL"):
            env.pop(name, None)
        return env

    def _run(self, prompt: str, *, model: str, tools: list[str]) -> str:
        command = [
            self.binary,
            "-p",
            prompt,
            "--output-format",
            "json",
            "--allowedTools",
            *tools,
        ]
        if model:
            command += ["--model", model]
        try:
            done = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=CLI_TIMEOUT,
                stdin=subprocess.DEVNULL,
                env=self._child_env(),
            )
        except subprocess.TimeoutExpired as exc:
            raise LLMError(f"claude CLI 가 {CLI_TIMEOUT}초 안에 답하지 않았습니다") from exc

        if done.returncode != 0:
            tail = (done.stderr or done.stdout or "").strip()[-400:]
            raise LLMError(f"claude CLI 실패(코드 {done.returncode}): {tail}\n{CLI_HELP}")

        try:
            payload = json.loads(done.stdout)
        except json.JSONDecodeError as exc:
            raise LLMError(f"claude CLI 응답을 읽지 못했습니다: {done.stdout[:300]}") from exc

        message = str(payload.get("result") or "")
        if payload.get("is_error") or payload.get("api_error_status"):
            if "redit balance" in message:
                raise LLMError(
                    "클로드 API 키(선불 크레딧)로 붙어서 실패했습니다. 구독으로 돌리려면 "
                    "ANTHROPIC_API_KEY 없이 CLAUDE_CODE_OAUTH_TOKEN 만 있어야 합니다. "
                    f"(원문: {message})"
                )
            raise LLMError(f"claude CLI 오류: {message or payload.get('subtype')}")
        result = payload.get("result")
        if not result:
            raise LLMError("claude CLI 가 빈 답을 돌려줬습니다")
        return result


def _cli_prompt(
    system: str, parts: Sequence[dict], schema: type[BaseModel], *, search: bool
) -> str:
    """CLI 는 시스템 프롬프트·이미지 첨부가 따로 없으니 하나의 글로 합친다.

    사진은 바이트 대신 **경로**로 넘긴다. CLI 안의 Read 도구가 직접 열어 본다 —
    그래서 사진을 다시 인코딩할 필요가 없다.
    """
    lines = [system, "", "---", ""]
    for part in parts:
        if part["type"] == "text":
            lines.append(part["text"])
        else:
            lines.append(f"(사진 파일: {Path(part['path']).resolve()} — Read 도구로 열어서 보세요)")
    if search:
        lines += ["", "WebSearch 도구로 인터넷을 찾아보고 답하세요."]
    lines += [
        "",
        "---",
        "",
        "아래 JSON 스키마에 **정확히** 맞는 JSON 하나만 출력하세요.",
        "설명, 인사말, 코드펜스 없이 JSON 본문만 출력합니다.",
        "",
        json.dumps(schema.model_json_schema(), ensure_ascii=False),
    ]
    return "\n".join(lines)

def make_client(settings) -> LLMClient:
    """설정과 환경변수를 보고 쓸 수 있는 공급자를 고른다."""
    provider = (settings.provider or "").lower()

    gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    cli_token = os.environ.get("CLAUDE_CODE_OAUTH_TOKEN")

    if provider == "auto":
        # 구독으로 도는 길이 있으면 그게 제일 낫다 — 한도도 결제도 없다.
        if cli_token or shutil.which("claude"):
            provider = "claude-cli"
        else:
            provider = "gemini" if gemini_key else "anthropic"

    if provider in ("claude-cli", "subscription"):
        log.info(
            "모델 공급자: 클로드 구독(claude CLI) — %s / %s",
            getattr(settings, "cli_vision_model", "") or settings.vision_model,
            getattr(settings, "cli_writing_model", "") or settings.writing_model,
        )
        return ClaudeCliClient(
            vision_model=getattr(settings, "cli_vision_model", "") or settings.vision_model,
            writing_model=getattr(settings, "cli_writing_model", "") or settings.writing_model,
        )

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

    raise LLMError(
        f"모르는 모델 공급자입니다: {provider!r} (claude-cli / gemini / anthropic)"
    )
