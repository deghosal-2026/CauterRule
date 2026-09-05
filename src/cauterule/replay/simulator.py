"""Outcome simulator."""

from __future__ import annotations

from typing import Literal

from cauterule.models.candidate import CandidateRule
from cauterule.models.trajectory import Trajectory
from cauterule.replay.matcher import is_near_miss, rule_matches

Outcome = Literal["prevented", "broken", "no_effect", "near_miss"]


def simulate(candidate: CandidateRule, trajectory: Trajectory) -> Outcome:
    """Simulate whether *candidate* would change *trajectory* outcome.

    Returns:
        - ``prevented`` if failure and matches (would have prevented)
        - ``broken`` if success and matches (would break success)
        - ``near_miss`` if partial context match
        - ``no_effect`` otherwise
    """
    if is_near_miss(candidate, trajectory):
        return "near_miss"
    matches = rule_matches(candidate, trajectory)
    if not matches:
        return "no_effect"
    if not trajectory.success:
        return "prevented"
    return "broken"
