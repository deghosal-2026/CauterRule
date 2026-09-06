"""Calibration feedback loop — adjusts promotion thresholds from benchmark data."""

from __future__ import annotations

from typing import Any

from cauterule.promotion.thresholds import get_thresholds


def feed_calibration_data(thresholds: dict[str, Any]) -> dict[str, Any]:
    """Feed calibration data back into the promotion threshold system.

    Args:
        thresholds: A dict with keys like ``"min_confidence"``, ``"min_precision"``,
            ``"min_recall"``, ``"linter_warning_limit"``, ``"conflict_tolerance"``.

    Returns:
        A dict mapping preset names to thresholds that were adjusted. For now,
        returns the current preset thresholds unmodified (pass-through).
    """
    _validate_thresholds(thresholds)
    adjusted: dict[str, Any] = {}
    for mode in ("conservative", "balanced", "aggressive"):
        current = get_thresholds(mode)
        adjusted[mode] = dict(current)
    return adjusted


def _validate_thresholds(thresholds: dict[str, Any]) -> None:
    required_keys = {
        "min_confidence", "min_precision", "min_recall",
        "linter_warning_limit", "conflict_tolerance",
    }
    missing = required_keys - set(thresholds.keys())
    if missing:
        raise ValueError(f"Missing required threshold keys: {missing}")
    for key in ("min_confidence", "min_precision", "min_recall"):
        val = thresholds.get(key, 0.0)
        if not isinstance(val, (int, float)) or not 0.0 <= val <= 1.0:
            raise ValueError(f"{key} must be in [0.0, 1.0], got {val}")
    for key in ("linter_warning_limit", "conflict_tolerance"):
        val = thresholds.get(key, 0)
        if not isinstance(val, int) or val < 0:
            raise ValueError(f"{key} must be non-negative int, got {val}")
