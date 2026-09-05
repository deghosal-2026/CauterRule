# mypy: ignore-errors
import pytest

from cauterule.llm.provider import (
    AnthropicProvider,
    LiteLLMProvider,
    OllamaProvider,
    OpenAIProvider,
)


def test_openai_provider() -> None:
    p = OpenAIProvider(model="gpt-4o", api_key="sk", base_url="https://api.openai.com")
    assert p.name == "openai"
    assert "openai" in repr(p)
    resp = p.complete("hello")
    assert resp.provider == "openai"
    assert "gpt-4o" in resp.text
    assert "hello" in resp.text


def test_anthropic_provider() -> None:
    p = AnthropicProvider(model="claude-3", api_key="sk")
    assert p.name == "anthropic"
    resp = p.complete("hello")
    assert resp.provider == "anthropic"
    assert "claude-3" in resp.text


def test_ollama_provider() -> None:
    p = OllamaProvider(model="llama3", base_url="http://localhost:11434")
    assert p.name == "ollama"
    resp = p.complete("hello")
    assert resp.provider == "ollama"
    assert "llama3" in resp.text


def test_litellm_provider() -> None:
    p = LiteLLMProvider(model="gpt-4o")
    assert p.name == "litellm"
    resp = p.complete("hello")
    assert resp.provider == "litellm"


def test_provider_import_errors(monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    import builtins

    orig_import = builtins.__import__  # type: ignore[attr-defined]

    def fake_import(name: str, *args: object, **kwargs: object) -> object:  # type: ignore[no-untyped-def]
        if name == "openai":
            raise ImportError("No module named 'openai'")
        if name == "anthropic":
            raise ImportError("No module named 'anthropic'")
        if name == "litellm":
            raise ImportError("No module named 'litellm'")
        return orig_import(name, *args, **kwargs)  # type: ignore[call-arg,arg-type]

    monkeypatch.setattr(builtins, "__import__", fake_import)  # type: ignore[arg-type]

    with pytest.raises(ImportError, match="openai"):
        OpenAIProvider().complete("hi")
    with pytest.raises(ImportError, match="anthropic"):
        AnthropicProvider().complete("hi")
    with pytest.raises(ImportError, match="litellm"):
        LiteLLMProvider().complete("hi")
