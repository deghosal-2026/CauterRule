"""Test 24.12: Calibration feedback loop adjusts promotion thresholds."""

from __future__ import annotations

import pytest

from cauterule.benchmark.calibration_loop import feed_calibration_data


def test_feed_calibration_data_returns_adjusted_thresholds() -> None:
    result = feed_calibration_data(
        {"min_confidence": 0.85, "min_precision": 0.80, "min_recall": 0.75, "linter_warning_limit": 1, "conflict_tolerance": 0}
    )
    assert isinstance(result, dict)
    for mode in ("conservative", "balanced", "aggressive"):
        assert mode in result
        assert "min_confidence" in result[mode]
        assert "min_precision" in result[mode]


def test_feed_calibration_returns_current_presets() -> None:
    data = {"min_confidence": 0.85, "min_precision": 0.80, "min_recall": 0.75, "linter_warning_limit": 1, "conflict_tolerance": 0}
    result = feed_calibration_data(data)
    assert result["conservative"]["min_confidence"] == 0.95
    assert result["balanced"]["min_confidence"] == 0.80
    assert result["aggressive"]["min_confidence"] == 0.60


def test_feed_calibration_missing_key_raises() -> None:
    with pytest.raises(ValueError, match="Missing required threshold keys"):
        feed_calibration_data({"min_confidence": 0.85})


def test_feed_calibration_invalid_confidence_raises() -> None:
    with pytest.raises(ValueError, match="min_confidence must be in"):
        feed_calibration_data(
            {"min_confidence": 2.0, "min_precision": 0.8, "min_recall": 0.75, "linter_warning_limit": 1, "conflict_tolerance": 0}
        )


def test_feed_calibration_negative_limit_raises() -> None:
    with pytest.raises(ValueError, match="linter_warning_limit must be non-negative"):
        feed_calibration_data(
            {"min_confidence": 0.8, "min_precision": 0.8, "min_recall": 0.75, "linter_warning_limit": -1, "conflict_tolerance": 0}
        )


def test_feed_calibration_non_int_limit_raises() -> None:
    with pytest.raises(ValueError, match="linter_warning_limit must be non-negative"):
        feed_calibration_data(
            {"min_confidence": 0.8, "min_precision": 0.8, "min_recall": 0.75, "linter_warning_limit": 0.5, "conflict_tolerance": 0}
        )
