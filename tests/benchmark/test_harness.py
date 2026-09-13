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
    check = check_candidate_range(
        candidates=7, corpus_name="golden", expected_min=5, expected_max=10
    )
    assert check.passed is True


def test_candidate_range_outside() -> None:
    check = check_candidate_range(
        candidates=3, corpus_name="golden", expected_min=5, expected_max=10
    )
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


# ── Rejection/safety corpora: gate-dropped silence must not fail the harness ─


def test_rejection_corpus_nearmiss_attempted_denominator_passes() -> None:
    """nearmiss: 27 gate-dropped + 23 attempted, all 23 parsed into candidates.

    Before the fix the parse rate was 23/50=46% -> false 'harness defect'.
    With the attempted denominator it is 23/23=100% -> PASS.
    """
    health = harness_health(
        parsed=23,
        total=50,
        candidates=43,
        trajectories=50,
        attempted=23,
        is_safety_corpus=True,
    )
    assert health.passed is True
    by_name = {c.name: c for c in health.checks}
    assert by_name["parse_rate"].passed is True
    assert by_name["parse_rate"].value == 1.0
    assert by_name["completion_ratio"].passed is True


def test_safety_corpus_full_gate_silence_attempted_zero_passes() -> None:
    """successes: everything gate-dropped (attempted=0) -> PASS via exemption."""
    health = harness_health(
        parsed=0,
        total=60,
        candidates=0,
        trajectories=60,
        attempted=0,
        is_safety_corpus=True,
    )
    assert health.passed is True


def test_extraction_corpus_real_parse_failure_still_fails() -> None:
    """A genuine parse failure on an extraction corpus must still FAIL."""
    health = harness_health(
        parsed=2,
        total=10,
        candidates=2,
        trajectories=10,
        attempted=10,
        is_safety_corpus=False,
    )
    assert health.passed is False


def test_attempted_defaults_to_total_for_back_compat() -> None:
    """No attempted arg -> behaves like before (parse over total)."""
    health = harness_health(parsed=3, total=10, candidates=3, trajectories=10)
    assert health.passed is False  # 30% parse
