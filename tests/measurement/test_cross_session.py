"""Tests for cross-session repeat-failure measurement (§5.2/§7.3, #663/#496)."""

from __future__ import annotations

import pytest

from cauterule.measurement.cross_session import (
    CrossSessionReport,
    cross_session_delta,
    repeat_failure_rate,
)


def _rec(session: int, failure_class: str, *, success: bool = False) -> dict[str, object]:
    return {"session": session, "failure_class": failure_class, "success": success}


def test_repeat_failure_rate_counts_recurring_classes() -> None:
    records = [
        _rec(1, "git/non-ff"),
        _rec(1, "python/import"),
        _rec(2, "git/non-ff"),  # repeat of session 1
        _rec(2, "docker/build"),
        _rec(2, "git/non-ff"),  # repeat within session 2
    ]
    # 5 failures; git/non-ff occurs 3x (2 are repeats), others once each.
    assert repeat_failure_rate(records) == pytest.approx(2 / 5)


def test_repeat_failure_rate_ignores_successes() -> None:
    records = [
        _rec(1, "git/non-ff"),
        _rec(1, "git/non-ff", success=True),
    ]
    assert repeat_failure_rate(records) == 0.0


def test_cross_session_delta_reduces_with_intervention() -> None:
    baseline = [
        _rec(1, "git/non-ff"),
        _rec(1, "git/non-ff"),
        _rec(2, "git/non-ff"),
        _rec(2, "git/non-ff"),
    ]
    intervention = [
        _rec(1, "git/non-ff"),
        _rec(2, "python/import"),
    ]
    report = cross_session_delta(baseline, intervention)
    assert isinstance(report, CrossSessionReport)
    assert report.baseline_repeat_rate == pytest.approx(3 / 4)
    assert report.intervention_repeat_rate == pytest.approx(0.0)
    assert report.reduction == pytest.approx(1.0)
    assert report.meets_target is True


def test_cross_session_delta_late_sessions_window() -> None:
    baseline = [_rec(s, "git/non-ff") for s in range(1, 6)] + [_rec(5, "git/non-ff")]
    intervention = [_rec(s, "git/non-ff") for s in range(1, 5)]
    report = cross_session_delta(baseline, intervention, late_sessions={4, 5})
    # baseline late {4,5}: session 4 (1) + session 5 (2) = 3 failures
    assert report.baseline_failures == 3
    assert report.intervention_failures == 1  # session 4
    assert report.baseline_repeat_rate == pytest.approx(2 / 3)
    assert report.intervention_repeat_rate == pytest.approx(0.0)
    assert report.meets_target is True


def test_cross_session_delta_no_baseline_failures_is_safe() -> None:
    report = cross_session_delta([], [_rec(1, "git/non-ff")])
    assert report.baseline_repeat_rate == 0.0
    assert report.reduction == 0.0
    assert report.meets_target is False
