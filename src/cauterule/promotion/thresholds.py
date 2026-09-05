"""Threshold configuration for the promotion gate.

Provides conservative / balanced / aggressive presets that control how the
promotion gate evaluates confidence, linter warnings, and conflict reports.
"""

from __future__ import annotations

from typing import Any

_THRESHOLD_PRESETS: dict[str, dict[str, float]] = {
    "conservative": {
        "min_confidence": 0.95,
        "min_precision": 0.90,
        "min_recall": 0.80,
        "linter_warning_limit": 0,
        "conflict_tolerance": 0,
    },
    "balanced": {
        "min_confidence": 0.80,
        "min_precision": 0.75,
        "min_recall": 0.70,
        "linter_warning_limit": 1,
        "conflict_tolerance": 0,
    },
    "aggressive": {
        "min_confidence": 0.60,
        "min_precision": 0.50,
        "min_recall": 0.50,
        "linter_warning_limit": 3,
        "conflict_tolerance": 1,
    },
}

_VALID_MODES: frozenset[str] = frozenset({"conservative", "balanced", "aggressive"})


def get_thresholds(mode: str) -> dict[str, Any]:
    """Return threshold dict for the given *mode*.

    Args:
        mode: One of ``"conservative"``, ``"balanced"``, or ``"aggressive"``.

    Returns:
        A dict with keys ``min_confidence``, ``min_precision``,
        ``min_recall``, ``linter_warning_limit``, ``conflict_tolerance``.

    Raises:
        ValueError: If *mode* is not recognised.
    """
    if mode not in _VALID_MODES:
        raise ValueError(f"unknown threshold mode {mode!r}; choose one of {sorted(_VALID_MODES)}")
    return dict(_THRESHOLD_PRESETS[mode])