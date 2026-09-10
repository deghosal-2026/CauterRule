"""Evidence scorer with broad-trigger penalty."""

from __future__ import annotations

from cauterule.models.evidence import Verdict


def compute_scores(
    prevented: int,
    broken: int,
    total_failures: int,
    total_successes: int,
) -> tuple[float, float, Verdict]:
    """Compute precision, recall, verdict.

    Broad-trigger penalty: if a trigger matches successes it would break,
    it is too broad. Triggers that break more successes than they prevent
    failures are "fail". Triggers that break some but still prevent more
    are "inconclusive" (broad, not dangerous).

    Args:
        prevented: Failures prevented.
        broken: Successes broken.
        total_failures: Total failures in corpus.
        total_successes: Total successes in corpus.

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
    else:
        # No successes broken
        if precision >= 0.8:
            verdict = "pass"
        elif precision >= 0.5:
            verdict = "inconclusive"
        else:
            verdict = "fail"

    return precision, recall, verdict
