"""Evidence scorer."""

from __future__ import annotations


def compute_scores(
    prevented: int,
    broken: int,
    total_failures: int,
    total_successes: int,  # noqa: ARG001
) -> tuple[float, float, str]:
    """Compute precision, recall, verdict.

    Args:
        prevented: Failures prevented.
        broken: Successes broken.
        total_failures: Total failures in corpus.
        total_successes: Total successes (unused for now, but kept for API).

    Returns:
        (precision, recall, verdict) where verdict is pass/fail/inconclusive.
    """
    _ = total_successes
    denom = prevented + broken
    if denom == 0:
        precision = 1.0 if prevented == 0 and broken == 0 else 0.0
        # If no matches at all, treat as inconclusive unless there were no failures to prevent
        if prevented == 0 and broken == 0:
            precision = 0.0
    else:
        precision = prevented / denom

    recall = (prevented / total_failures) if total_failures > 0 else 0.0

    if prevented == 0 and broken == 0:
        verdict = "inconclusive"
    elif broken > 0:
        # If any success broken, verdict is fail regardless of precision (conservative)
        verdict = "fail"
    else:
        # No successes broken
        if precision >= 0.8:
            verdict = "pass"
        elif precision >= 0.5:
            verdict = "inconclusive"
        else:
            verdict = "fail"

    return precision, recall, verdict
