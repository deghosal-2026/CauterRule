"""YAML serialization for StandingRule.

Provides round-trip ``StandingRule`` ↔ YAML via ``to_dict``/``from_dict``.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from cauterule.models.rule import StandingRule


def dump_rule(rule: StandingRule) -> str:
    """Serialize *rule* to a YAML string."""
    return yaml.safe_dump(rule.to_dict(), sort_keys=False, allow_unicode=True)


def load_rule(yaml_str: str) -> StandingRule:
    """Deserialize a YAML string to a :class:`StandingRule`."""
    data = yaml.safe_load(yaml_str)
    if not isinstance(data, dict):
        raise ValueError("YAML must decode to a mapping")
    return StandingRule.from_dict(data)


def dump_rule_to_file(rule: StandingRule, path: str | Path) -> None:
    """Write *rule* to *path* as YAML.

    Creates parent directories as needed.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(dump_rule(rule), encoding="utf-8")


def load_rule_from_file(path: str | Path) -> StandingRule:
    """Load a :class:`StandingRule` from a YAML file at *path*."""
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    return load_rule(text)


def load_rules_from_dir(directory: str | Path) -> list[StandingRule]:
    """Load all ``*.yaml``/``*.yml`` rules from *directory* (non-recursive)."""
    d = Path(directory)
    rules: list[StandingRule] = []
    if not d.is_dir():
        return rules
    for pattern in ("*.yaml", "*.yml"):
        for p in d.glob(pattern):
            if p.stem == "index":
                continue
            if p.is_file():
                rules.append(load_rule_from_file(p))
    return rules
