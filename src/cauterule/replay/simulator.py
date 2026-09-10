"""Outcome simulator."""

from __future__ import annotations

from typing import Literal

from cauterule.models.candidate import CandidateRule
from cauterule.models.trajectory import Trajectory
from cauterule.replay.matcher import DEFAULT_THRESHOLD, check_domain_mismatch, is_near_miss, rule_matches

Outcome = Literal["prevented", "broken", "no_effect", "near_miss"]

# Recovery signals matched as EXACT slash-delimited taxonomy segments.
# Substring matching here caused semantic inversion (#616): "unrecoverable"
# matched "recover", "retry budget exhausted" matched "retry", "template"
# matched "temp", and every "nearmiss/*" label circularly matched "near".
# Bare "temp" is excluded (temperature/template collide); "nearmiss" is
# excluded (corpus category label, not a recovery signal — see #616).
RECOVERY_CLASS_TOKENS = frozenset(
    {
        "temporary",
        "retry",
        "recovered",
        "recovery",
        "intermittent",
        "flaky",
        "near_miss",
    }
)


def is_recovery_class(failure_class: str | None) -> bool:
    """Return True if *failure_class* denotes a genuine recovery.

    Matches whole ``/``-separated segments only — never substrings.
    Non-string inputs (possible from unvalidated JSONL) return False.
    """
    if not isinstance(failure_class, str):
        return False
    segments = [seg.strip().lower() for seg in failure_class.split("/")]
    return any(seg in RECOVERY_CLASS_TOKENS for seg in segments)


def simulate(
    candidate: CandidateRule, trajectory: Trajectory, threshold: float = DEFAULT_THRESHOLD
) -> Outcome:
    """Simulate whether *candidate* would change *trajectory* outcome.

    Args:
        candidate: The candidate rule to test.
        trajectory: The trajectory to test against.
        threshold: Matcher threshold (default 0.6). Use corpus-aware
            :func:`threshold_for_corpus` for per-corpus tuning.

    Returns:
        - ``prevented`` if failure and matches (would have prevented)
        - ``broken`` if success and matches (would break success)
        - ``near_miss`` if partial context match or recovery trajectory
        - ``no_effect`` otherwise
    """
    if is_near_miss(candidate, trajectory):
        return "near_miss"
    matches = rule_matches(candidate, trajectory, threshold=threshold)
    if not matches:
        return "no_effect"
    # Domain mismatch: trigger names a different domain than the reference
    # trajectory's failure_class. This is typically a "wrong failure" scenario
    # where the match is coincidental (e.g. both trajectories involve bash but
    # one is a git failure and the other is a docker failure). Rather than
    # counting as "prevented", downgrade to no_effect (#487).
    if not trajectory.success and check_domain_mismatch(candidate, trajectory):
        return "no_effect"
    if not trajectory.success:
        return "prevented"
    # Success=True but has failure_class indicating recovery/nearmiss → not clean success
    if trajectory.success and (trajectory.failure_class or trajectory.failure_point):
        if is_recovery_class(trajectory.failure_class):
            return "near_miss"
    return "broken"
