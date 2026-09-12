import pytest

from cauterule.config import Config, LLMConfig
from cauterule.llm.factory import get_llm
from cauterule.llm.provider import (
    AnthropicProvider,
    LiteLLMProvider,
    OllamaProvider,
    OpenAIProvider,
)


def test_get_llm_openai() -> None:
    cfg = Config(
        llm=LLMConfig(
            provider="openai", model="gpt-4o", api_key="sk", base_url="https://api.openai.com"
        )
    )
    llm = get_llm(cfg)
    assert isinstance(llm, OpenAIProvider)
    assert llm.name == "openai"


def test_get_llm_anthropic() -> None:
    cfg = Config(llm=LLMConfig(provider="anthropic", model="claude-3"))
    llm = get_llm(cfg)
    assert isinstance(llm, AnthropicProvider)


def test_get_llm_ollama() -> None:
    cfg = Config(
        llm=LLMConfig(provider="ollama", model="llama3", base_url="http://localhost:11434")
    )
    llm = get_llm(cfg)
    assert isinstance(llm, OllamaProvider)


def test_get_llm_litellm() -> None:
    cfg = Config(llm=LLMConfig(provider="litellm", model="gpt-4o"))
    llm = get_llm(cfg)
    assert isinstance(llm, LiteLLMProvider)


def test_get_llm_case_insensitive() -> None:
    cfg = Config(llm=LLMConfig(provider="OpenAI", model="gpt-4o"))
    llm = get_llm(cfg)
    assert isinstance(llm, OpenAIProvider)


def test_get_llm_unknown() -> None:
    cfg = Config(llm=LLMConfig(provider="unknown", model="x"))
    with pytest.raises(ValueError, match="Unknown LLM provider"):
        get_llm(cfg)


def test_get_llm_whitespace() -> None:
    cfg = Config(llm=LLMConfig(provider="  openai  ", model="gpt-4o"))
    llm = get_llm(cfg)
    assert isinstance(llm, OpenAIProvider)
