"""Vagueness check — detects generic triggers/directives."""

from __future__ import annotations

_VAGUE_PHRASES = frozenset({
    "be careful", "be more careful", "pay attention", "be mindful",
    "use common sense", "be reasonable", "be nice", "be good",
    "do better", "try harder", "be professional", "be smart",
    "be gentle", "be safe", "don't mess up", "don't break things",
})


def check_vagueness(text: str) -> list[str]:
    """Return warnings if *text* contains vague phrases."""
    lower = text.lower()
    return [f"vague: '{p}'" for p in _VAGUE_PHRASES if p in lower]