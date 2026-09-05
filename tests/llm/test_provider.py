# mypy: ignore-errors
from __future__ import annotations

import sys
from types import ModuleType
from unittest.mock import MagicMock, patch

import pytest

from cauterule.llm.provider import (
    AnthropicProvider,
    LiteLLMProvider,
    OllamaProvider,
    OpenAIProvider,
)


@pytest.fixture(autouse=True)
def _fake_modules() -> None:
    for modname in ("openai", "anthropic", "requests", "litellm"):
        if modname not in sys.modules:
            sys.modules[modname] = ModuleType(modname)


def test_openai_provider(_fake_modules: None) -> None:
    mock_create = MagicMock()
    mock_create.return_value.choices = [MagicMock(message=MagicMock(content="response text"))]
    p = OpenAIProvider(model="gpt-4o", api_key="sk-test", base_url="https://api.openai.com")
    with patch("openai.OpenAI", create=True) as mock_client:
        mock_client.return_value.chat.completions.create = mock_create
        resp = p.complete("hello", temperature=0.7)

    assert resp.provider == "openai"
    assert resp.model == "gpt-4o"
    assert resp.text == "response text"
    mock_create.assert_called_once_with(
        model="gpt-4o",
        messages=[{"role": "user", "content": "hello"}],
        temperature=0.7,
    )


def test_anthropic_provider(_fake_modules: None) -> None:
    mock_create = MagicMock()
    text_block = MagicMock()
    text_block.text = "response text"
    mock_create.return_value.content = [text_block]
    p = AnthropicProvider(model="claude-3", api_key="sk-test")
    with patch("anthropic.Anthropic", create=True) as mock_client:
        mock_client.return_value.messages.create = mock_create
        resp = p.complete("hello", temperature=0.3)

    assert resp.provider == "anthropic"
    assert resp.model == "claude-3"
    assert resp.text == "response text"
    mock_create.assert_called_once_with(
        model="claude-3",
        max_tokens=4096,
        messages=[{"role": "user", "content": "hello"}],
        temperature=0.3,
    )


def test_ollama_provider(_fake_modules: None) -> None:
    mock_response = MagicMock()
    mock_response.json.return_value = {"response": "ollama says hi"}
    p = OllamaProvider(model="llama3", base_url="http://localhost:11434")
    with patch("requests.post", create=True) as mock_post:
        mock_post.return_value = mock_response
        resp = p.complete("hello", temperature=0.5)

    assert resp.provider == "ollama"
    assert resp.model == "llama3"
    assert resp.text == "ollama says hi"
    mock_post.assert_called_once_with(
        "http://localhost:11434/api/generate",
        json={"model": "llama3", "prompt": "hello", "temperature": 0.5, "stream": False},
        timeout=120,
    )


def test_litellm_provider(_fake_modules: None) -> None:
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock(message=MagicMock(content="litellm response"))]
    p = LiteLLMProvider(model="gpt-4o")
    with patch("litellm.completion", create=True) as mock_litellm:
        mock_litellm.return_value = mock_completion
        resp = p.complete("hello", temperature=0.9)

    assert resp.provider == "litellm"
    assert resp.model == "gpt-4o"
    assert resp.text == "litellm response"