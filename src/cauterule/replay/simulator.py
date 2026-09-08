"""Outcome simulator."""

from __future__ import annotations

from typing import Literal

from cauterule.models.candidate import CandidateRule
from cauterule.models.trajectory import Trajectory
from cauterule.replay.matcher import DEFAULT_THRESHOLD, is_near_miss, rule_matches

Outcome = Literal["prevented", "broken", "no_effect", "near_miss"]


def simulate(candidate: CandidateRule, trajectory: Trajectory, threshold: float = DEFAULT_THRESHOLD) -> Outcome:
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
    if not trajectory.success:
        return "prevented"
    # Success=True but has failure_class indicating recovery/nearmiss → not clean success
    if trajectory.success and (trajectory.failure_class or trajectory.failure_point):
        fc = (trajectory.failure_class or "").lower()
        if "temp" in fc or "near" in fc or "retry" in fc or "recover" in fc or "intermittent" in fc or "flaky" in fc:
            return "near_miss"
    return "broken"
