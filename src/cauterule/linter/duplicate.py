"""Duplicate check — detects semantically identical existing rules."""

from __future__ import annotations

from cauterule.models.rule import StandingRule


def _normalize(s: str) -> str:
    return " ".join(s.lower().strip().split())


def check_duplicate(candidate_trigger: str, candidate_directive: str, existing_rules: list[StandingRule]) -> list[str]:
    """Return warnings if a rule with same trigger+directive exists."""
    ct = _normalize(candidate_trigger)
    cd = _normalize(candidate_directive)
    for rule in existing_rules:
        if _normalize(rule.when.trigger) == ct and _normalize(rule.do.directive) == cd:
            return [f"duplicate: matches existing rule {rule.id}"]
    return []