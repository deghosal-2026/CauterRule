"""Duplicate check — detects semantically identical existing rules."""

from __future__ import annotations

from cauterule.models.rule import StandingRule

# Overlap-coefficient threshold for near-duplicates (#504): |A∩B| / min(|A|,|B|).
_NEAR_DUPLICATE_THRESHOLD = 0.6


def _normalize(s: str) -> str:
    return " ".join(s.lower().strip().split())


def _tokens(s: str) -> set[str]:
    return set(_normalize(s).split())


def _overlap(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / min(len(a), len(b))


def check_duplicate(
    candidate_trigger: str, candidate_directive: str, existing_rules: list[StandingRule]
) -> list[str]:
    """Return warnings if a rule with same trigger+directive exists.

    Exact normalized matches warn as duplicates; paraphrases with high
    token overlap on BOTH trigger and directive warn as near-duplicates.
    """
    ct = _normalize(candidate_trigger)
    cd = _normalize(candidate_directive)
    ct_tokens = _tokens(candidate_trigger)
    cd_tokens = _tokens(candidate_directive)
    for rule in existing_rules:
        if _normalize(rule.when.trigger) == ct and _normalize(rule.do.directive) == cd:
            return [f"duplicate: matches existing rule {rule.id}"]
        if (
            _overlap(ct_tokens, _tokens(rule.when.trigger)) >= _NEAR_DUPLICATE_THRESHOLD
            and _overlap(cd_tokens, _tokens(rule.do.directive)) >= _NEAR_DUPLICATE_THRESHOLD
        ):
            return [f"near-duplicate: paraphrases existing rule {rule.id}"]
    return []
