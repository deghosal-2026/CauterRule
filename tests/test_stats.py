"""Tests for Wilson confidence-interval helpers (#695)."""

import pytest

from cauterule.stats import rate_with_ci, wilson_ci


def test_wilson_ci_zero_of_ten_upper_below_30_percent() -> None:
    low, high = wilson_ci(0, 10)
    assert low == 0.0
    assert 0.25 < high < 0.30  # ~0.2775 — a 0/10 result does NOT imply ~0%


def test_wilson_ci_one_of_ten_brackets_ten_percent() -> None:
    low, high = wilson_ci(1, 10)
    assert low < 0.10 < high
    assert 0.01 < low < 0.03
    assert 0.35 < high < 0.45


def test_wilson_ci_37_of_50_brackets_74_percent() -> None:
    low, high = wilson_ci(37, 50)
    assert low < 0.74 < high
    assert 0.58 < low < 0.63
    assert 0.83 < high < 0.87


def test_wilson_ci_all_successes_upper_is_one() -> None:
    low, high = wilson_ci(10, 10)
    assert high == 1.0
    assert low < 1.0


def test_wilson_ci_is_symmetric() -> None:
    low_fail, high_fail = wilson_ci(2, 10)
    low_pass, high_pass = wilson_ci(8, 10)
    assert low_fail == pytest.approx(1.0 - high_pass, abs=1e-9)
    assert high_fail == pytest.approx(1.0 - low_pass, abs=1e-9)


def test_wilson_ci_zero_total_is_maximally_uncertain() -> None:
    assert wilson_ci(0, 0) == (0.0, 1.0)


def test_wilson_ci_higher_confidence_is_wider() -> None:
    low90, high90 = wilson_ci(5, 10, confidence=0.90)
    low99, high99 = wilson_ci(5, 10, confidence=0.99)
    assert low99 <= low90
    assert high99 >= high90


def test_wilson_ci_invalid_counts_raise() -> None:
    with pytest.raises(ValueError, match="invalid counts"):
        wilson_ci(11, 10)
    with pytest.raises(ValueError, match="invalid counts"):
        wilson_ci(-1, 10)


def test_wilson_ci_invalid_confidence_raises() -> None:
    with pytest.raises(ValueError, match="confidence"):
        wilson_ci(1, 10, confidence=1.5)


def test_rate_with_ci_shape() -> None:
    result = rate_with_ci(0, 10)
    assert result["n"] == 10
    assert result["rate"] == 0.0
    assert result["ci_low"] == 0.0
    assert 0.25 < result["ci_high"] < 0.30
