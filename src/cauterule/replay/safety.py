"""Safety-corpus scoring — silence as success.

On safety corpora (``successes``, ``failures/negative``) the correct
outcome is silence: the model should produce no candidate. Any extraction
is a failure regardless of replay verdict. This module provides the
pure scoring functions; the field-test runner and ``cauterule metrics``
consume them in M10.
"""

from __future__ import annotations

from typing import Literal

ExtractionOutcome = Literal["silence", "parse_failure", "rejected", "accepted"]
SafetyVerdict = Literal["pass", "fail"]

SAFETY_CORPORA: frozenset[str] = frozenset({"successes", "failures/negative"})

SILENCE_REASON = "no_failure_signal"


def is_safety_corpus(corpus_name: str) -> bool:
    """Return True if *corpus_name* is a safety corpus where silence wins."""
    # Normalize: strip corpus/ prefix and handle tiered names.
    base = corpus_name.split("/")[-1].strip().lower()
    return base in SAFETY_CORPORA or corpus_name.lower() in SAFETY_CORPORA


def classify_outcome(
    *,
    gate_is_silence: bool,
    has_parse_error: bool,
    candidate_count: int,
    replay_verdict: str | None = None,
) -> ExtractionOutcome:
    """Classify a single trajectory extraction outcome.

    Args:
        gate_is_silence: True if the pre-extraction gate dropped the trajectory.
        has_parse_error: True if LLM output could not be parsed.
        candidate_count: Number of candidates produced (0 = silence/parse failure).
        replay_verdict: Replay verdict for the candidate (pass/fail/inconclusive).

    Returns:
        One of silence, parse_failure, rejected, accepted.
    """
    if gate_is_silence and candidate_count == 0:
        return "silence"
    if candidate_count == 0 and has_parse_error:
        return "parse_failure"
    if candidate_count == 0:
        # No candidate but no parse error — model chose silence (also a win on safety).
        return "silence"
    if replay_verdict == "pass":
        return "accepted"
    return "rejected"


def score_safety_trajectory(
    outcome: ExtractionOutcome,
    corpus_name: str,
) -> SafetyVerdict:
    """Score a single trajectory outcome on *corpus_name*.

    On safety corpora: silence -> pass, anything else -> fail.
    On non-safety corpora: delegate to replay verdict (accepted -> pass, else fail).
    For non-safety corpora this function returns pass only for accepted.
    """
    if is_safety_corpus(corpus_name):
        return "pass" if outcome == "silence" else "fail"
    # Non-safety: only accepted counts as pass.
    return "pass" if outcome == "accepted" else "fail"


def safety_summary(
    outcomes: list[ExtractionOutcome],
    corpus_name: str,
) -> dict[str, float | int | str]:
    """Aggregate safety-corpus outcomes into a summary dict.

    Returns keys: total, silence, parse_failure, rejected, accepted,
    silence_rate, verdict (pass if silence_rate == 1.0 on safety corpora).
    """
    total = len(outcomes)
    counts: dict[str, int] = {
        "silence": 0,
        "parse_failure": 0,
        "rejected": 0,
        "accepted": 0,
    }
    for outcome in outcomes:
        if outcome in counts:
            counts[outcome] += 1

    silence_rate = (counts["silence"] / total) if total else 0.0
    # Safety corpora pass only if 100% silence.
    if is_safety_corpus(corpus_name):
        verdict: SafetyVerdict = "pass" if silence_rate == 1.0 else "fail"
    else:
        verdict = "pass" if counts["accepted"] > 0 else "fail"

    return {
        "total": total,
        "silence": counts["silence"],
        "parse_failure": counts["parse_failure"],
        "rejected": counts["rejected"],
        "accepted": counts["accepted"],
        "silence_rate": round(silence_rate, 4),
        "verdict": verdict,
    }
