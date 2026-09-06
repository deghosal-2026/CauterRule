"""Contradiction check — detects conflicting existing rules."""

from __future__ import annotations

from cauterule.models.rule import StandingRule


def _normalize(s: str) -> str:
    return " ".join(s.lower().strip().split())


def check_contradiction(candidate_trigger: str, candidate_directive: str, existing_rules: list[StandingRule]) -> list[str]:
    """Return warnings if candidate contradicts an existing rule (same trigger, opposite directive)."""
    ct = _normalize(candidate_trigger)
    cd = _normalize(candidate_directive)
    for rule in existing_rules:
        if _normalize(rule.when.trigger) != ct:
            continue
        rd = _normalize(rule.do.directive)
        if cd != rd:
            return [f"contradiction: conflicts with {rule.id} ('{rule.do.directive}' vs '{candidate_directive}')"]
    return []