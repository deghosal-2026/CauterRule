import os
from pathlib import Path

import pytest

from cauterule.config import Config, config_to_dict, load_config


def test_defaults_no_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    # ensure no cauterule.toml
    for key in list(os.environ.keys()):
        if key.startswith("CAUTERULE_"):
            monkeypatch.delenv(key, raising=False)
    cfg = load_config()
    assert cfg.llm.provider == "openai"
    assert cfg.llm.model == "gpt-4o"
    assert cfg.paths.rules == "rules"
    assert cfg.promotion.mode == "hybrid"
    assert cfg.extraction.passes == 3


def test_toml_parsing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    toml = """
[llm]
provider = "anthropic"
model = "claude-3"
api_key = "sk-123"
base_url = "https://api.anthropic.com"
temperature = 0.7
max_tokens = 2048

[paths]
rules = "my_rules"
trajectories = "my_trajs"

[thresholds]
precision = 0.9
recall = 0.6

[promotion]
mode = "hybrid"

[redaction]
patterns = ["secret.*"]

[extraction]
passes = 5
temperatures = [0.0, 0.5]
confidence_threshold = 0.8
"""
    p = tmp_path / "cauterule.toml"
    p.write_text(toml)
    monkeypatch.chdir(tmp_path)
    for key in list(os.environ.keys()):
        if key.startswith("CAUTERULE_"):
            monkeypatch.delenv(key, raising=False)
    cfg = load_config()
    assert cfg.llm.provider == "anthropic"
    assert cfg.llm.model == "claude-3"
    assert cfg.llm.api_key == "sk-123"
    assert cfg.llm.temperature == 0.7
    assert cfg.llm.max_tokens == 2048
    assert cfg.paths.rules == "my_rules"
    assert cfg.thresholds.precision == 0.9
    assert cfg.promotion.mode == "hybrid"
    assert cfg.redaction.patterns == ("secret.*",)
    assert cfg.extraction.passes == 5
    assert cfg.extraction.temperatures == (0.0, 0.5)
    assert cfg.extraction.confidence_threshold == 0.8


def test_explicit_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    p = tmp_path / "custom.toml"
    p.write_text('[llm]\nprovider="ollama"\n')
    for key in list(os.environ.keys()):
        if key.startswith("CAUTERULE_"):
            monkeypatch.delenv(key, raising=False)
    cfg = load_config(path=p)
    assert cfg.llm.provider == "ollama"


def test_invalid_promotion_mode(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    p = tmp_path / "cauterule.toml"
    p.write_text('[promotion]\nmode="invalid"\n')
    monkeypatch.chdir(tmp_path)
    for key in list(os.environ.keys()):
        if key.startswith("CAUTERULE_"):
            monkeypatch.delenv(key, raising=False)
    with pytest.raises(ValueError, match="promotion.mode"):
        load_config()


def test_invalid_redaction_patterns(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    p = tmp_path / "cauterule.toml"
    p.write_text('[redaction]\npatterns="not a list"\n')
    monkeypatch.chdir(tmp_path)
    for key in list(os.environ.keys()):
        if key.startswith("CAUTERULE_"):
            monkeypatch.delenv(key, raising=False)
    with pytest.raises(ValueError, match="patterns must be a list"):
        load_config()


def test_invalid_extraction_passes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    p = tmp_path / "cauterule.toml"
    p.write_text("[extraction]\npasses=0\n")
    monkeypatch.chdir(tmp_path)
    for key in list(os.environ.keys()):
        if key.startswith("CAUTERULE_"):
            monkeypatch.delenv(key, raising=False)
    with pytest.raises(ValueError, match="passes must be"):
        load_config()


def test_invalid_extraction_temperatures(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    p = tmp_path / "cauterule.toml"
    p.write_text('[extraction]\ntemperatures="bad"\n')
    monkeypatch.chdir(tmp_path)
    for key in list(os.environ.keys()):
        if key.startswith("CAUTERULE_"):
            monkeypatch.delenv(key, raising=False)
    with pytest.raises(ValueError, match="temperatures must be a list"):
        load_config()


def test_env_overrides(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    # create empty toml
    (tmp_path / "cauterule.toml").write_text("")
    monkeypatch.setenv("CAUTERULE_LLM_PROVIDER", "ollama")
    monkeypatch.setenv("CAUTERULE_MODEL", "llama3")
    monkeypatch.setenv("CAUTERULE_PROMOTION_MODE", "human-review")
    monkeypatch.setenv("CAUTERULE_RULES_PATH", "custom_rules")
    monkeypatch.setenv("CAUTERULE_TRAJECTORIES_PATH", "custom_trajs")
    cfg = load_config()
    assert cfg.llm.provider == "ollama"
    assert cfg.llm.model == "llama3"
    assert cfg.promotion.mode == "human-review"
    assert cfg.paths.rules == "custom_rules"
    assert cfg.paths.trajectories == "custom_trajs"


def test_env_overrides_llm_fallback(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "cauterule.toml").write_text("")
    monkeypatch.setenv("CAUTERULE_LLM_MODEL", "gpt-4o-mini")
    monkeypatch.delenv("CAUTERULE_MODEL", raising=False)
    for key in [
        "CAUTERULE_LLM_PROVIDER",
        "CAUTERULE_LLM_API_KEY",
        "CAUTERULE_LLM_BASE_URL",
        "CAUTERULE_PROMOTION_MODE",
        "CAUTERULE_MODE",
    ]:
        monkeypatch.delenv(key, raising=False)
    cfg = load_config()
    assert cfg.llm.model == "gpt-4o-mini"


def test_env_invalid_promotion_mode(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "cauterule.toml").write_text("")
    monkeypatch.setenv("CAUTERULE_PROMOTION_MODE", "bad")
    with pytest.raises(ValueError, match="CAUTERULE_PROMOTION_MODE"):
        load_config()


def test_config_to_dict_roundtrip() -> None:
    cfg = Config()
    d = config_to_dict(cfg)
    assert d["llm"]["provider"] == "openai"
    assert d["paths"]["rules"] == "rules"
    # ensure load from dict via file works
    import tempfile

    # write dict to toml via manual string
    toml_str = '[llm]\nprovider="openai"\nmodel="gpt-4o"\n'
    p = Path(tempfile.mktemp(suffix=".toml"))
    p.write_text(toml_str)
    loaded = load_config(path=p)
    assert loaded.llm.provider == "openai"
    p.unlink(missing_ok=True)


def test_malformed_toml_raises_value_error(tmp_path: Path) -> None:
    # #503: TOML crash becomes a ValueError with path + cause.
    p = tmp_path / "cauterule.toml"
    p.write_text("[llm\nprovider = 'oops'\n")
    with pytest.raises(ValueError, match="invalid TOML"):
        load_config(path=p)


def test_env_overrides_new_vars(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # #503: numeric + threshold + extraction env vars honored.
    monkeypatch.chdir(tmp_path)
    (tmp_path / "cauterule.toml").write_text("")
    monkeypatch.setenv("CAUTERULE_LLM_TEMPERATURE", "0.7")
    monkeypatch.setenv("CAUTERULE_LLM_MAX_TOKENS", "2048")
    monkeypatch.setenv("CAUTERULE_LLM_TIMEOUT", "45")
    monkeypatch.setenv("CAUTERULE_LLM_MAX_RETRIES", "5")
    monkeypatch.setenv("CAUTERULE_THRESHOLD_PRECISION", "0.9")
    monkeypatch.setenv("CAUTERULE_THRESHOLD_RECALL", "0.6")
    monkeypatch.setenv("CAUTERULE_EXTRACTION_CONFIDENCE_THRESHOLD", "0.8")
    monkeypatch.setenv("CAUTERULE_EXTRACTION_PASSES", "5")
    monkeypatch.setenv("CAUTERULE_EXTRACTION_GATE_MODE", "relaxed")
    cfg = load_config()
    assert cfg.llm.temperature == 0.7
    assert cfg.llm.max_tokens == 2048
    assert cfg.llm.timeout == 45
    assert cfg.llm.max_retries == 5
    assert cfg.thresholds.precision == 0.9
    assert cfg.thresholds.recall == 0.6
    assert cfg.extraction.confidence_threshold == 0.8
    assert cfg.extraction.passes == 5
    assert cfg.extraction.gate_mode == "relaxed"


def test_env_invalid_numeric(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "cauterule.toml").write_text("")
    monkeypatch.setenv("CAUTERULE_LLM_TIMEOUT", "soon")
    with pytest.raises(ValueError, match="CAUTERULE_LLM_TIMEOUT"):
        load_config()


def test_defaults_agree_across_sources() -> None:
    # #503: dataclass defaults and from-dict fallbacks agree (docstring contract).
    from cauterule.config import (
        ExtractionConfig,
        ThresholdsConfig,
        _config_from_dict,
        _extraction_from_dict,
        _thresholds_from_dict,
    )

    assert ExtractionConfig().temperatures == (0.2, 0.5, 0.8)
    assert ExtractionConfig().confidence_threshold == 0.6
    assert ThresholdsConfig().precision == 0.8
    assert _extraction_from_dict({}).temperatures == (0.2, 0.5, 0.8)
    assert _extraction_from_dict({}).confidence_threshold == 0.6
    assert _thresholds_from_dict({}).precision == 0.8
    assert _config_from_dict(config_to_dict(Config())) == Config()
