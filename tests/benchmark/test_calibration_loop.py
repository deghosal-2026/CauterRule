"""Test 24.12: Calibration feedback loop adjusts promotion thresholds."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from cauterule.benchmark.calibration_loop import feed_calibration_data
from cauterule.promotion.thresholds import get_thresholds


@pytest.fixture(autouse=True)
def _isolate_calibration_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Keep calibration history and threshold presets out of the repo (#801)."""
    from cauterule.benchmark import calibration_loop
    from cauterule.promotion import thresholds as thresholds_module

    monkeypatch.setattr(
        calibration_loop,
        "_CALIBRATION_FILE",
        str(tmp_path / "calibration_history.json"),
    )
    monkeypatch.setattr(
        thresholds_module,
        "_THRESHOLD_PRESETS",
        {mode: dict(preset) for mode, preset in thresholds_module._THRESHOLD_PRESETS.items()},
    )


def _data(min_precision: float) -> dict[str, float | int]:
    return {
        "min_confidence": 0.70,
        "min_precision": min_precision,
        "min_recall": 0.75,
        "linter_warning_limit": 1,
        "conflict_tolerance": 0,
    }


def test_feed_calibration_data_returns_adjusted_thresholds() -> None:
    result = feed_calibration_data(
        {
            "min_confidence": 0.85,
            "min_precision": 0.80,
            "min_recall": 0.75,
            "linter_warning_limit": 1,
            "conflict_tolerance": 0,
        }
    )
    assert isinstance(result, dict)
    for mode in ("conservative", "balanced", "aggressive"):
        assert mode in result
        assert "min_confidence" in result[mode]
        assert "precision" in result[mode]


def test_feed_calibration_returns_current_presets() -> None:
    data = {
        "min_confidence": 0.85,
        "min_precision": 0.80,
        "min_recall": 0.75,
        "linter_warning_limit": 1,
        "conflict_tolerance": 0,
    }
    result = feed_calibration_data(data)
    assert result["conservative"]["min_confidence"] == 0.85
    assert result["balanced"]["min_confidence"] == 0.70
    assert result["aggressive"]["min_confidence"] == 0.50


def test_feed_calibration_missing_key_raises() -> None:
    with pytest.raises(ValueError, match="Missing required threshold keys"):
        feed_calibration_data({"min_confidence": 0.85})


def test_feed_calibration_invalid_confidence_raises() -> None:
    with pytest.raises(ValueError, match="min_confidence must be in"):
        feed_calibration_data(
            {
                "min_confidence": 2.0,
                "min_precision": 0.8,
                "min_recall": 0.75,
                "linter_warning_limit": 1,
                "conflict_tolerance": 0,
            }
        )


def test_feed_calibration_negative_limit_raises() -> None:
    with pytest.raises(ValueError, match="linter_warning_limit must be non-negative"):
        feed_calibration_data(
            {
                "min_confidence": 0.8,
                "min_precision": 0.8,
                "min_recall": 0.75,
                "linter_warning_limit": -1,
                "conflict_tolerance": 0,
            }
        )


def test_feed_calibration_non_int_limit_raises() -> None:
    with pytest.raises(ValueError, match="linter_warning_limit must be non-negative"):
        feed_calibration_data(
            {
                "min_confidence": 0.8,
                "min_precision": 0.8,
                "min_recall": 0.75,
                "linter_warning_limit": 0.5,
                "conflict_tolerance": 0,
            }
        )


def test_low_precision_escalates_after_three_feeds() -> None:
    # #801: three consecutive low-precision feeds must trip the >=3 branch
    # and tighten by the larger 0.05 step, not the 0.02 default.
    feed_calibration_data(_data(0.50))
    feed_calibration_data(_data(0.50))
    after_two = get_thresholds("balanced")["min_confidence"]
    feed_calibration_data(_data(0.50))
    after_three = get_thresholds("balanced")["min_confidence"]

    third_step = after_three - after_two
    assert third_step == pytest.approx(0.05)
    assert third_step > 0.02


def test_legacy_flat_history_counts_toward_escalation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # #801: pre-existing flat-dict history files must keep contributing to the
    # low-precision count (backward compatibility).
    from cauterule.benchmark import calibration_loop

    legacy = tmp_path / "legacy_history.json"
    legacy.write_text(
        json.dumps(
            {
                "min_confidence": 0.70,
                "min_precision": 0.50,
                "min_recall": 0.75,
                "linter_warning_limit": 1,
                "conflict_tolerance": 0,
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(calibration_loop, "_CALIBRATION_FILE", str(legacy))

    # Legacy entry + two new low-precision entries == 3 -> escalate.
    feed_calibration_data(_data(0.50))
    feed_calibration_data(_data(0.50))

    # 0.70 + 0.02 (feed 1) + 0.05 (feed 2, escalated) == 0.77
    assert get_thresholds("balanced")["min_confidence"] == pytest.approx(0.77)
