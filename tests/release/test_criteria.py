"""Tests for release criteria thresholds."""

from cauterule.release.criteria import check_release_criteria


def test_release_gate_blocks_on_successes() -> None:
    verdict = check_release_criteria(successes_pass_rate=0.05)
    assert verdict.passed is False
    assert any("successes" in f.lower() for f in verdict.failures)


def test_release_gate_passes_when_all_met() -> None:
    verdict = check_release_criteria(
        successes_pass_rate=0.0,
        failures_negative_pass_rate=0.0,
        nearmiss_precision=0.95,
        golden_pass_rate=0.8,
        failures_positive_pass_rate=0.6,
        inconclusive_curated_rate=0.10,
        inconclusive_raw_rate=0.30,
    )
    assert verdict.passed is True
    assert verdict.failures == []


def test_release_gate_nearmiss_precision() -> None:
    verdict = check_release_criteria(nearmiss_precision=0.8)
    assert verdict.passed is False
    assert any("nearmiss" in f.lower() for f in verdict.failures)


def test_release_gate_golden_threshold() -> None:
    verdict = check_release_criteria(golden_pass_rate=0.5)
    assert verdict.passed is False


def test_release_gate_inconclusive_curated() -> None:
    verdict = check_release_criteria(inconclusive_curated_rate=0.20)
    assert verdict.passed is False
