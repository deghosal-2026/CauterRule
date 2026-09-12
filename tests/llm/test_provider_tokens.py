"""Token-usage capture for the OpenAI provider (#653/#486 cost measurement)."""

from __future__ import annotations

import sys
import types
from typing import Any

from cauterule.llm.provider import OpenAIProvider


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
