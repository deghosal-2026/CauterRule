"""Tests for harness health assertions."""

from cauterule.benchmark.harness import (
    check_candidate_range,
    check_completion_ratio,
    check_parse_rate,
    harness_health,
)


def test_parse_rate_pass() -> None:
    check = check_parse_rate(parsed=8, total=10, threshold=0.7)
    assert check.passed is True


def test_parse_rate_fail() -> None:
    check = check_parse_rate(parsed=3, total=10, threshold=0.7)
    assert check.passed is False
    assert "harness defect" in check.message.lower()


def test_completion_zero_candidates_is_failure() -> None:
    health = harness_health(parsed=10, total=10, candidates=0, trajectories=10)
    assert health.passed is False
    assert any("harness failure" in c.message.lower() for c in health.checks)


def test_completion_healthy() -> None:
    health = harness_health(parsed=10, total=10, candidates=10, trajectories=10)
    assert health.passed is True


def test_candidate_range_within() -> None:
    check = check_candidate_range(candidates=7, corpus_name="golden", expected_min=5, expected_max=10)
    assert check.passed is True


def test_candidate_range_outside() -> None:
    check = check_candidate_range(candidates=3, corpus_name="golden", expected_min=5, expected_max=10)
    assert check.passed is False
    assert "HARNESS_FAILURE" in check.message


def test_harness_health_with_ranges() -> None:
    health = harness_health(
        parsed=10,
        total=10,
        candidates=10,
        trajectories=10,
        corpus_ranges={"golden": (5, 10), "successes": (0, 0)},
        candidate_counts={"golden": 7, "successes": 0},
    )
    assert health.passed is True


def test_harness_health_low_parse_rate_fails() -> None:
    health = harness_health(parsed=3, total=10, candidates=3, trajectories=10, parse_threshold=0.7)
    assert health.passed is False


def test_completion_ratio_helper() -> None:
    assert check_completion_ratio(candidates=5, trajectories=10).passed is False
    assert check_completion_ratio(candidates=9, trajectories=10, threshold=0.9).passed is True
