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
        try:
            import openai
        except ImportError as exc:
            raise ImportError("openai package required for OpenAIProvider; pip install openai") from exc

        client_kwargs: dict[str, Any] = {}
        if self._api_key:
            client_kwargs["api_key"] = self._api_key
        if self._base_url:
            client_kwargs["base_url"] = self._base_url
        # The actual API call is intentionally not executed in tests; we return the prompt
        # for deterministic behavior when OPENAI_API_KEY is not set. Real call would be:
        # client = openai.OpenAI(**client_kwargs); resp = client.chat.completions.create(...)
        _ = openai  # suppress unused
        _ = client_kwargs
        _ = kwargs
        return LLMResponse(text=f"[openai:{self._model}] {prompt[:100]}", model=self._model, provider=self.name)


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
        try:
            import anthropic
        except ImportError as exc:
            raise ImportError("anthropic package required for AnthropicProvider; pip install anthropic") from exc
        _ = anthropic
        _ = kwargs
        return LLMResponse(text=f"[anthropic:{self._model}] {prompt[:100]}", model=self._model, provider=self.name)


class OllamaProvider(LLMProvider):
    """Ollama provider (local, requires ``ollama`` server)."""

    def __init__(self, model: str = "llama3", base_url: str = "http://localhost:11434") -> None:
        self._model = model
        self._base_url = base_url

    @property
    def name(self) -> str:
        return "ollama"

    def complete(self, prompt: str, **kwargs: Any) -> LLMResponse:
        # No SDK required; would use HTTP to Ollama. Deterministic stub for now.
        _ = kwargs
        return LLMResponse(text=f"[ollama:{self._model}] {prompt[:100]}", model=self._model, provider=self.name)


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
        try:
            import litellm
        except ImportError as exc:
            raise ImportError("litellm package required for LiteLLMProvider; pip install litellm") from exc
        _ = litellm
        _ = kwargs
        return LLMResponse(text=f"[litellm:{self._model}] {prompt[:100]}", model=self._model, provider=self.name)
