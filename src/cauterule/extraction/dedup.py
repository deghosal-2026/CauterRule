"""Candidate deduplication."""

from __future__ import annotations

from cauterule.models.candidate import CandidateRule


def _normalize(s: str) -> str:
    return " ".join(s.lower().strip().split())


def is_duplicate(a: CandidateRule, b: CandidateRule) -> bool:
    """Return True if *a* and *b* are semantically identical."""
    return (
        _normalize(a.when.trigger) == _normalize(b.when.trigger)
        and _normalize(a.do.directive) == _normalize(b.do.directive)
        and _normalize(" ".join(a.when.context)) == _normalize(" ".join(b.when.context))
    )


def deduplicate(candidates: list[CandidateRule]) -> list[CandidateRule]:
    """Remove semantically identical candidates, keeping first occurrence."""
    seen: list[CandidateRule] = []
    for cand in candidates:
        if any(is_duplicate(cand, existing) for existing in seen):
            continue
        seen.append(cand)
    return seen
