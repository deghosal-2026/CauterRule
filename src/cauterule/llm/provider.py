"""LLM provider abstraction.

Unified interface for OpenAI, Anthropic, Ollama, and LiteLLM.
Each provider lazily imports its SDK so the package remains installable
without optional LLM dependencies.
"""

from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class LLMResponse:
    """Response from an LLM provider."""

    text: str
    model: str
    provider: str


class LLMProvider(abc.ABC):
    """Abstract LLM provider."""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Provider name."""

    @abc.abstractmethod
    def complete(self, prompt: str, **kwargs: Any) -> LLMResponse:
        """Generate a completion for *prompt*."""

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r})"


class OpenAIProvider(LLMProvider):
    """OpenAI provider (requires ``openai``)."""

    def __init__(self, model: str = "gpt-4o", api_key: str = "", base_url: str = "") -> None:
        self._model = model
        self._api_key = api_key
        self._base_url = base_url

    @property
    def name(self) -> str:
        return "openai"

    def complete(self, prompt: str, **kwargs: Any) -> LLMResponse:
        import openai

        client_kwargs: dict[str, Any] = {}
        if self._api_key:
            client_kwargs["api_key"] = self._api_key
        if self._base_url:
            client_kwargs["base_url"] = self._base_url
        temperature = kwargs.get("temperature", 0.5)
        client = openai.OpenAI(**client_kwargs)
        resp = client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )
        text = resp.choices[0].message.content or ""
        return LLMResponse(text=text, model=self._model, provider=self.name)


class AnthropicProvider(LLMProvider):
    """Anthropic provider (requires ``anthropic``)."""

    def __init__(self, model: str = "claude-3-5-sonnet-20241022", api_key: str = "", base_url: str = "") -> None:
        self._model = model
        self._api_key = api_key
        self._base_url = base_url

    @property
    def name(self) -> str:
        return "anthropic"

    def complete(self, prompt: str, **kwargs: Any) -> LLMResponse:
        import anthropic

        client_kwargs: dict[str, Any] = {}
        if self._api_key:
            client_kwargs["api_key"] = self._api_key
        if self._base_url:
            client_kwargs["base_url"] = self._base_url
        temperature = kwargs.get("temperature", 0.5)
        client = anthropic.Anthropic(**client_kwargs)
        resp = client.messages.create(
            model=self._model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )
        text = "".join(block.text if hasattr(block, "text") else str(block) for block in resp.content)
        return LLMResponse(text=text, model=self._model, provider=self.name)


class OllamaProvider(LLMProvider):
    """Ollama provider (local, requires ``ollama`` server)."""

    def __init__(self, model: str = "llama3", base_url: str = "http://localhost:11434") -> None:
        self._model = model
        self._base_url = base_url

    @property
    def name(self) -> str:
        return "ollama"

    def complete(self, prompt: str, **kwargs: Any) -> LLMResponse:
        import requests

        temperature = kwargs.get("temperature", 0.5)
        resp = requests.post(
            f"{self._base_url}/api/generate",
            json={"model": self._model, "prompt": prompt, "temperature": temperature, "stream": False},
            timeout=120,
        )
        resp.raise_for_status()
        text = resp.json().get("response", "")
        return LLMResponse(text=text, model=self._model, provider=self.name)


class LiteLLMProvider(LLMProvider):
    """LiteLLM provider (supports any LiteLLM-compatible model)."""

    def __init__(self, model: str = "gpt-4o", api_key: str = "", base_url: str = "") -> None:
        self._model = model
        self._api_key = api_key
        self._base_url = base_url

    @property
    def name(self) -> str:
        return "litellm"

    def complete(self, prompt: str, **kwargs: Any) -> LLMResponse:
        import litellm

        temperature = kwargs.get("temperature", 0.5)
        completion_kwargs: dict[str, Any] = {"model": self._model, "messages": [{"role": "user", "content": prompt}], "temperature": temperature}
        if self._api_key:
            completion_kwargs["api_key"] = self._api_key
        if self._base_url:
            completion_kwargs["api_base"] = self._base_url
        resp = litellm.completion(**completion_kwargs)
        text = resp.choices[0].message.content or ""
        return LLMResponse(text=text, model=self._model, provider=self.name)
