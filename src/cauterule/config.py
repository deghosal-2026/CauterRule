"""Configuration for CauterRule.

Loads ``cauterule.toml`` and environment variables into typed dataclasses.

TOML layout (all sections optional, defaults shown):

```toml
[llm]
provider = "openai"
model = "gpt-4o"
api_key = ""
base_url = ""
temperature = 0.0
max_tokens = 4096

[paths]
rules = "rules"
trajectories = "trajectories"

[thresholds]
precision = 0.8
recall = 0.5

[promotion]
mode = "auto"  # auto | human-review | hybrid

[redaction]
patterns = []  # additional regex patterns

[extraction]
passes = 3
temperatures = [0.0, 0.7, 1.0]
confidence_threshold = 0.5
```
"""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class LLMConfig:
    """LLM provider settings."""

    provider: str = "openai"
    model: str = "gpt-4o"
    api_key: str = ""
    base_url: str = ""
    temperature: float = 0.0
    max_tokens: int = 4096
    timeout: int = 30


@dataclass(frozen=True)
class PathsConfig:
    """Filesystem paths."""

    rules: str = "rules"
    trajectories: str = "trajectories"


@dataclass(frozen=True)
class ThresholdsConfig:
    """Replay/promotion thresholds."""

    precision: float = 0.8
    recall: float = 0.5


@dataclass(frozen=True)
class PromotionConfig:
    """Promotion mode."""

    mode: str = "auto"  # auto | human-review | hybrid


@dataclass(frozen=True)
class RedactionConfig:
    """Redaction settings."""

    patterns: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ExtractionConfig:
    """Extraction settings."""

    passes: int = 3
    temperatures: tuple[float, ...] = (0.0, 0.7, 1.0)
    confidence_threshold: float = 0.5


@dataclass(frozen=True)
class Config:
    """Top-level configuration."""

    llm: LLMConfig = field(default_factory=LLMConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)
    thresholds: ThresholdsConfig = field(default_factory=ThresholdsConfig)
    promotion: PromotionConfig = field(default_factory=PromotionConfig)
    redaction: RedactionConfig = field(default_factory=RedactionConfig)
    extraction: ExtractionConfig = field(default_factory=ExtractionConfig)


def _parse_toml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    with path.open("rb") as f:
        data = tomllib.load(f)
    if not isinstance(data, dict):
        return {}
    return data


def _llm_from_dict(data: dict[str, Any]) -> LLMConfig:
    return LLMConfig(
        provider=str(data.get("provider", "openai")),
        model=str(data.get("model", "gpt-4o")),
        api_key=str(data.get("api_key", "")),
        base_url=str(data.get("base_url", "")),
        temperature=float(data.get("temperature", 0.0)),
        max_tokens=int(data.get("max_tokens", 4096)),
        timeout=int(data.get("timeout", 30)),
    )


def _paths_from_dict(data: dict[str, Any]) -> PathsConfig:
    return PathsConfig(
        rules=str(data.get("rules", "rules")),
        trajectories=str(data.get("trajectories", "trajectories")),
    )


def _thresholds_from_dict(data: dict[str, Any]) -> ThresholdsConfig:
    return ThresholdsConfig(
        precision=float(data.get("precision", 0.8)),
        recall=float(data.get("recall", 0.5)),
    )


def _promotion_from_dict(data: dict[str, Any]) -> PromotionConfig:
    mode = str(data.get("mode", "auto"))
    if mode not in {"auto", "human-review", "hybrid"}:
        raise ValueError(f"promotion.mode must be auto|human-review|hybrid, got {mode!r}")
    return PromotionConfig(mode=mode)


def _redaction_from_dict(data: dict[str, Any]) -> RedactionConfig:
    patterns = data.get("patterns", [])
    if not isinstance(patterns, list):
        raise ValueError("redaction.patterns must be a list")
    return RedactionConfig(patterns=tuple(str(p) for p in patterns))


def _extraction_from_dict(data: dict[str, Any]) -> ExtractionConfig:
    passes = int(data.get("passes", 3))
    if passes < 1:
        raise ValueError(f"extraction.passes must be >=1, got {passes}")
    temps_raw = data.get("temperatures", [0.0, 0.7, 1.0])
    if not isinstance(temps_raw, list):
        raise ValueError("extraction.temperatures must be a list")
    temps = tuple(float(t) for t in temps_raw)
    return ExtractionConfig(
        passes=passes,
        temperatures=temps,
        confidence_threshold=float(data.get("confidence_threshold", 0.5)),
    )


def _config_from_dict(data: dict[str, Any]) -> Config:
    return Config(
        llm=_llm_from_dict(data.get("llm", {})),
        paths=_paths_from_dict(data.get("paths", {})),
        thresholds=_thresholds_from_dict(data.get("thresholds", {})),
        promotion=_promotion_from_dict(data.get("promotion", {})),
        redaction=_redaction_from_dict(data.get("redaction", {})),
        extraction=_extraction_from_dict(data.get("extraction", {})),
    )


def _apply_env_overrides(config: Config) -> Config:
    """Apply ``CAUTERULE_*`` environment variables over *config*.

    Supported variables (all optional):
    - ``CAUTERULE_LLM_PROVIDER``
    - ``CAUTERULE_LLM_MODEL`` and ``CAUTERULE_MODEL`` (fallback)
    - ``CAUTERULE_LLM_API_KEY``
    - ``CAUTERULE_LLM_BASE_URL``
    - ``CAUTERULE_PROMOTION_MODE`` / ``CAUTERULE_MODE``
    - ``CAUTERULE_RULES_PATH`` / ``CAUTERULE_RULES``
    - ``CAUTERULE_TRAJECTORIES_PATH``
    """
    llm_provider = os.getenv("CAUTERULE_LLM_PROVIDER")
    llm_model = os.getenv("CAUTERULE_LLM_MODEL") or os.getenv("CAUTERULE_MODEL")
    llm_api_key = os.getenv("CAUTERULE_LLM_API_KEY")
    llm_base_url = os.getenv("CAUTERULE_LLM_BASE_URL")
    promotion_mode = os.getenv("CAUTERULE_PROMOTION_MODE") or os.getenv("CAUTERULE_MODE")
    rules_path = os.getenv("CAUTERULE_RULES_PATH") or os.getenv("CAUTERULE_RULES")
    trajectories_path = os.getenv("CAUTERULE_TRAJECTORIES_PATH") or os.getenv("CAUTERULE_TRAJECTORIES")

    # Rebuild only sections that have overrides, preserving frozen semantics.
    llm = config.llm
    if llm_provider is not None or llm_model is not None or llm_api_key is not None or llm_base_url is not None:
        llm = LLMConfig(
            provider=llm_provider if llm_provider is not None else llm.provider,
            model=llm_model if llm_model is not None else llm.model,
            api_key=llm_api_key if llm_api_key is not None else llm.api_key,
            base_url=llm_base_url if llm_base_url is not None else llm.base_url,
            temperature=llm.temperature,
            max_tokens=llm.max_tokens,
            timeout=llm.timeout,
        )

    paths = config.paths
    if rules_path is not None or trajectories_path is not None:
        paths = PathsConfig(
            rules=rules_path if rules_path is not None else paths.rules,
            trajectories=trajectories_path if trajectories_path is not None else paths.trajectories,
        )

    promotion = config.promotion
    if promotion_mode is not None:
        if promotion_mode not in {"auto", "human-review", "hybrid"}:
            raise ValueError(f"CAUTERULE_PROMOTION_MODE must be auto|human-review|hybrid, got {promotion_mode!r}")
        promotion = PromotionConfig(mode=promotion_mode)

    if llm is config.llm and paths is config.paths and promotion is config.promotion:
        return config

    return Config(
        llm=llm,
        paths=paths,
        thresholds=config.thresholds,
        promotion=promotion,
        redaction=config.redaction,
        extraction=config.extraction,
    )


def load_config(path: str | Path | None = None) -> Config:
    """Load configuration from ``cauterule.toml`` and environment.

    Args:
        path: Optional explicit path to ``cauterule.toml``. If ``None``,
            searches ``cauterule.toml`` in the current directory.
    """
    toml_path = Path(path) if path is not None else Path("cauterule.toml")
    data = _parse_toml(toml_path)
    config = _config_from_dict(data)
    return _apply_env_overrides(config)


def config_to_dict(config: Config) -> dict[str, Any]:
    """Serialize *config* to a TOML-compatible dict."""
    return {
        "llm": {
            "provider": config.llm.provider,
            "model": config.llm.model,
            "api_key": config.llm.api_key,
            "base_url": config.llm.base_url,
            "temperature": config.llm.temperature,
            "max_tokens": config.llm.max_tokens,
            "timeout": config.llm.timeout,
        },
        "paths": {"rules": config.paths.rules, "trajectories": config.paths.trajectories},
        "thresholds": {"precision": config.thresholds.precision, "recall": config.thresholds.recall},
        "promotion": {"mode": config.promotion.mode},
        "redaction": {"patterns": list(config.redaction.patterns)},
        "extraction": {
            "passes": config.extraction.passes,
            "temperatures": list(config.extraction.temperatures),
            "confidence_threshold": config.extraction.confidence_threshold,
        },
    }
