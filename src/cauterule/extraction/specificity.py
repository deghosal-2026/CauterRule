"""Trigger specificity scoring — penalize over-broad triggers.

Categories:
- specific: names a concrete tool, error, or condition
- moderate: names a domain or general condition
- generic: applies to almost anything
"""

from __future__ import annotations

import re
from typing import Literal

Specificity = Literal["specific", "moderate", "generic"]

# Degenerate trigger patterns — step identifiers, not failure descriptions.
_DEGENERATE_RE = re.compile(r"^step[_\s]*\d+$", re.IGNORECASE)

# Hyphenated or underscored error codes are strong specificity signals.
_SPECIFIC_RE = re.compile(r"[a-z]+[-_][a-z]+")

# Concrete error-condition markers (multi-word or hyphenated).
_CONCRETE_MARKERS: frozenset[str] = frozenset(
    {
        "non-fast-forward",
        "non fast forward",
        "merge conflict",
        "permission denied",
        "modulenotfounderror",
        "import error",
        "connection refused",
        "missing peer dependency",
    }
)

_STOPWORDS: frozenset[str] = frozenset(
    {
        "a",
        "an",
        "the",
        "and",
        "or",
        "but",
        "if",
        "then",
        "else",
        "when",
        "what",
        "which",
        "who",
        "whom",
        "this",
        "that",
        "these",
        "those",
        "am",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "having",
        "do",
        "does",
        "did",
        "doing",
        "will",
        "would",
        "shall",
        "should",
        "can",
        "could",
        "may",
        "might",
        "must",
        "ought",
        "to",
        "of",
        "in",
        "for",
        "on",
        "by",
        "with",
        "about",
        "into",
        "through",
        "during",
        "before",
        "after",
        "above",
        "below",
        "up",
        "down",
        "out",
        "off",
        "over",
        "under",
        "again",
        "further",
        "once",
        "here",
        "there",
        "all",
        "any",
        "both",
        "each",
        "few",
        "more",
        "most",
        "other",
        "some",
        "such",
        "only",
        "own",
        "same",
        "so",
        "than",
        "too",
        "very",
        "just",
        "also",
        "not",
        "no",
        "nor",
        "as",
        "at",
        "from",
        "it",
        "its",
        "you",
        "your",
        "we",
        "they",
    }
)


def _content_tokens(trigger: str) -> list[str]:
    lower = trigger.lower()
    # Keep hyphenated tokens as one unit for now; split on whitespace.
    tokens = [t.strip(".,;:!?\"'()[]{}") for t in lower.split()]
    return [t for t in tokens if t and t not in _STOPWORDS and len(t) > 1]


def score_specificity(trigger: str) -> Specificity:
    """Return specificity category for *trigger*."""
    lower = trigger.lower()
    tokens = _content_tokens(trigger)

    # Reject degenerate triggers (step identifiers like "step_1").
    if _DEGENERATE_RE.match(lower.strip()):
        return "generic"

    # Strong signal: hyphenated error code or concrete error phrase.
    if _SPECIFIC_RE.search(lower):
        return "specific"
    for phrase in _CONCRETE_MARKERS:
        if phrase in lower:
            return "specific"

    if len(tokens) >= 4:
        return "specific"
    if len(tokens) == 3:
        return "moderate"
    # 2-token triggers with a concrete tool name are moderate, not generic.
    if len(tokens) == 2 and any(
        t in {"git", "docker", "npm", "pip", "kubectl", "pytest"} for t in tokens
    ):
        return "moderate"
    return "generic"


def is_generic(trigger: str) -> bool:
    """Return True if *trigger* is generic (should be flagged)."""
    return score_specificity(trigger) == "generic"
