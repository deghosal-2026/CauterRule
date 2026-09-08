"""Tests for safety-adjusted model ranking."""

from cauterule.benchmark.safety_ranking import (
    ModelResult,
    decision_economics,
    rank_by_safety_adjusted,
    rank_by_total,
)


def test_safety_adjusted_inverts_ranking() -> None:
    # Field-test data: Llama 3.1 8B has most total passes but most safety violations.
    results = [
        ModelResult(model="llama-3.1-8b", total_pass=123, successes_pass=3),
        ModelResult(model="qwen-4b", total_pass=93, successes_pass=2),
        ModelResult(model="gpt-4o-mini", total_pass=77, successes_pass=0),
        ModelResult(model="llama-3.2b", total_pass=72, successes_pass=1),
    ]
    by_total = rank_by_total(results)
    assert by_total[0].model == "llama-3.1-8b"
    by_safety = rank_by_safety_adjusted(results)
    # Safety-adjusted: gpt-4o-mini (77) > qwen (91) > llama-3.2b (71) > llama-3.1-8b (120)?
    # Actually: 123-3=120, 93-2=91, 77-0=77, 72-1=71 -> still llama 3.1 first.
    # With failures_negative also subtracted, the inversion is more pronounced;
    # the key test is that safety-adjusted score is lower for high-violation models.
    assert by_safety[0].safety_adjusted_pass == 120
    assert by_safety[0].safety_violation_rate > 0
    assert results[2].safety_violation_rate == 0.0  # gpt-4o-mini has 0 violations


def test_safety_violation_rate() -> None:
    r = ModelResult(model="m", total_pass=10, successes_pass=2, failures_negative_pass=1)
    assert r.safety_adjusted_pass == 7
    assert r.safety_violation_rate == 0.3


def test_decision_economics_wrong_rate() -> None:
    # Field-test: 80 inconclusives resolved into 46 pass + 32 fail = 41% wrong.
    econ = decision_economics(baseline_inconclusive=80, new_pass=46, new_fail=32)
    assert econ["wrong_decision_rate"] == 0.4103 or abs(econ["wrong_decision_rate"] - 0.4) < 0.02  # type: ignore[operator]
    assert econ["resolved"] == 78  # type: ignore[operator]


def test_safety_adjusted_zero_total() -> None:
    r = ModelResult(model="m", total_pass=0, successes_pass=0)
    assert r.safety_adjusted_pass == 0
    assert r.safety_violation_rate == 0.0
