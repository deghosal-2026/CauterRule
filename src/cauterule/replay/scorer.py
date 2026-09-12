"""Evidence scorer with broad-trigger and near-miss penalty."""

from __future__ import annotations

from cauterule.models.evidence import Verdict


def compute_scores(
    prevented: int,
    broken: int,
    total_failures: int,
    total_successes: int,
    near_misses: int = 0,
) -> tuple[float, float, Verdict]:
    """Compute precision, recall, verdict.

    Broad-trigger penalty: if a trigger matches successes it would break,
    it is too broad. Triggers that break more successes than they prevent
    failures are "fail". Triggers that break some but still prevent more
    are "inconclusive" (broad, not dangerous).

    Near-miss penalty: if a trigger also matches near-miss references
    (recovered or ambiguous trajectories), it is over-broad. A candidate
    with ``near_misses > 0`` is downgraded from ``pass`` to ``inconclusive``
    — the trigger fires on trajectories that should not have produced a
    rule (v0.3.0 field-test fix: nearmiss corpus false passes at precision
    1.0 because near-misses were computed but never penalised).

    v0.3.0 field-test tuning: the penalty was zero-tolerance (any near-miss
    → inconclusive), which over-fired on legitimate candidates that prevent
    7 real failures and touch 1 near-miss. The tolerance band allows
    ``near_misses <= 2`` to still pass if precision ≥ 0.5 — a candidate
    that prevents more failures than it touches near-misses is a good rule.
    Above 2 near-misses, the trigger is too broad and stays inconclusive.

    Args:
        prevented: Failures prevented.
        broken: Successes broken.
        total_failures: Total failures in corpus.
        total_successes: Total successes in corpus.
        near_misses: Near-miss references matched (over-broad trigger).

    Returns:
        (precision, recall, verdict) where verdict is pass/fail/inconclusive.
    """
    denom = prevented + broken
    if denom == 0:
        precision = 0.0
    else:
        precision = prevented / denom

    recall = (prevented / total_failures) if total_failures > 0 else 0.0

    if prevented == 0 and broken == 0:
        verdict: Verdict = "inconclusive"
    elif broken > prevented:
        # More successes broken than failures prevented — dangerously broad
        verdict = "fail"
    elif broken > 0:
        # Some successes broken, but prevented more — broad but fixable
        verdict = "inconclusive"
    elif near_misses > 2:
        # No successes broken, but matched >2 near-miss references —
        # over-broad trigger. Downgrade from pass to inconclusive.
        verdict = "inconclusive"
    elif near_misses > 0 and precision < 0.5:
        # 1-2 near-misses but precision too low — still inconclusive.
        verdict = "inconclusive"
    else:
        # No successes broken, no near-misses — clean pass.
        # v0.3.0: lowered from 0.8 to 0.5. The domain-scoped reference pool
        # (#708) made precision more honest but rarely reaches 0.8 because
        # candidates match 1–3 relevant references out of 10–30. At 0.5 a
        # candidate that prevents more failures than it breaks still passes;
        # the near-miss penalty and broad-trigger check guard safety.
        if precision >= 0.5:
            verdict = "pass"
        elif precision >= 0.3:
            verdict = "inconclusive"
        else:
            verdict = "fail"

    return precision, recall, verdict
