"""Tests for the Fix 8 recovery-exclusion re-run (§5.6, #491)."""

from __future__ import annotations

import pytest

from cauterule.measurement.recovery import recovery_exclusion


def _r(expected: str, silenced: bool) -> dict[str, object]:
    return {"expected_outcome": expected, "gate_is_silence": silenced}


def test_recovery_exclusion_rate() -> None:
    records = [
        _r("should_reject", True),
        _r("should_reject", False),
        _r("should_silence", True),
        _r("should_extract", False),
    ]
    report = recovery_exclusion(records)
    assert report.recovered_expected == 3
    assert report.excluded == 2
    assert report.exclusion_rate == pytest.approx(2 / 3)
    assert report.false_extractions == 1
    assert report.meets_target is True  # default target 0.5


def test_recovery_exclusion_below_target() -> None:
    records = [
        _r("should_reject", False),
        _r("should_reject", False),
    ]
    report = recovery_exclusion(records)
    assert report.exclusion_rate == 0.0
    assert report.meets_target is False


def test_recovery_exclusion_ignores_extract_expected() -> None:
    report = recovery_exclusion([_r("should_extract", False)])
    assert report.recovered_expected == 0
    assert report.exclusion_rate == 0.0
