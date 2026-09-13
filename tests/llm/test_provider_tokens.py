"""Token-usage capture for every LLM provider (#653/#486, #802 cost measurement)."""

from __future__ import annotations

import sys
import types
from typing import Any

from cauterule.llm.provider import (
    AnthropicProvider,
    LiteLLMProvider,
    OllamaProvider,
    OpenAIProvider,
)


def _fake_openai(usage: Any) -> types.SimpleNamespace:
    class _Msg:
        content = "hello"

    class _Choice:
        message = _Msg()

    class _Resp:
        choices = (_Choice(),)

        def __init__(self) -> None:
            if usage is not None:
                self.usage = usage

    class _Completions:
        def create(self, **_kwargs: object) -> _Resp:
            return _Resp()

    class _Chat:
        completions = _Completions()

    class _Client:
        def __init__(self, **_kwargs: object) -> None:
            self.chat = _Chat()

    return types.SimpleNamespace(OpenAI=_Client)


class _Usage:
    def __init__(self, prompt: int, completion: int) -> None:
        self.prompt_tokens = prompt
        self.completion_tokens = completion


def test_openai_provider_captures_token_usage(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setitem(sys.modules, "openai", _fake_openai(_Usage(11, 7)))
    provider = OpenAIProvider(model="m", api_key="k", base_url="http://x/v1")
    resp = provider.complete("prompt")
    assert resp.text == "hello"
    assert resp.prompt_tokens == 11
    assert resp.completion_tokens == 7


def test_openai_provider_usage_defaults_to_zero(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setitem(sys.modules, "openai", _fake_openai(None))
    provider = OpenAIProvider(model="m", api_key="k", base_url="http://x/v1")
    resp = provider.complete("prompt")
    assert resp.prompt_tokens == 0
    assert resp.completion_tokens == 0


# ── Anthropic (#802) ─────────────────────────────────────────────────


class _AnthropicUsage:
    def __init__(self, input_tokens: int, output_tokens: int) -> None:
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens


def _fake_anthropic(usage: Any) -> types.SimpleNamespace:
    class _Block:
        text = "hello"

    class _Resp:
        content = (_Block(),)

        def __init__(self) -> None:
            if usage is not None:
                self.usage = usage

    class _Messages:
        def create(self, **_kwargs: object) -> _Resp:
            return _Resp()

    class _Client:
        def __init__(self, **_kwargs: object) -> None:
            self.messages = _Messages()

    return types.SimpleNamespace(Anthropic=_Client)


def test_anthropic_provider_captures_token_usage(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setitem(sys.modules, "anthropic", _fake_anthropic(_AnthropicUsage(11, 7)))
    provider = AnthropicProvider(model="m", api_key="k")
    resp = provider.complete("prompt")
    assert resp.text == "hello"
    assert resp.prompt_tokens == 11
    assert resp.completion_tokens == 7


def test_anthropic_provider_usage_defaults_to_zero(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setitem(sys.modules, "anthropic", _fake_anthropic(None))
    provider = AnthropicProvider(model="m", api_key="k")
    resp = provider.complete("prompt")
    assert resp.prompt_tokens == 0
    assert resp.completion_tokens == 0


# ── Ollama (#802) ────────────────────────────────────────────────────


def _fake_requests(payload: dict[str, Any]) -> types.SimpleNamespace:
    class _Resp:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, Any]:
            return payload

    def _post(_url: str, **_kwargs: object) -> _Resp:
        return _Resp()

    return types.SimpleNamespace(post=_post)


def test_ollama_provider_captures_token_usage(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    fake = _fake_requests(
        {"response": "hello", "prompt_eval_count": 11, "eval_count": 7}
    )
    monkeypatch.setitem(sys.modules, "requests", fake)
    provider = OllamaProvider(model="m")
    resp = provider.complete("prompt")
    assert resp.text == "hello"
    assert resp.prompt_tokens == 11
    assert resp.completion_tokens == 7


def test_ollama_provider_usage_defaults_to_zero(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setitem(sys.modules, "requests", _fake_requests({"response": "hello"}))
    provider = OllamaProvider(model="m")
    resp = provider.complete("prompt")
    assert resp.prompt_tokens == 0
    assert resp.completion_tokens == 0


# ── LiteLLM (#802) ───────────────────────────────────────────────────


def _fake_litellm(usage: Any) -> types.SimpleNamespace:
    class _Msg:
        content = "hello"

    class _Choice:
        message = _Msg()

    class _Resp:
        choices = (_Choice(),)

        def __init__(self) -> None:
            if usage is not None:
                self.usage = usage

    def _completion(**_kwargs: object) -> _Resp:
        return _Resp()

    return types.SimpleNamespace(completion=_completion)


def test_litellm_provider_captures_token_usage(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setitem(sys.modules, "litellm", _fake_litellm(_Usage(11, 7)))
    provider = LiteLLMProvider(model="m")
    resp = provider.complete("prompt")
    assert resp.text == "hello"
    assert resp.prompt_tokens == 11
    assert resp.completion_tokens == 7


def test_litellm_provider_usage_defaults_to_zero(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setitem(sys.modules, "litellm", _fake_litellm(None))
    provider = LiteLLMProvider(model="m")
    resp = provider.complete("prompt")
    assert resp.prompt_tokens == 0
    assert resp.completion_tokens == 0
