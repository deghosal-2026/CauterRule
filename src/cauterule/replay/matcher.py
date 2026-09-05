"""Rule matcher."""

from __future__ import annotations

from cauterule.models.candidate import CandidateRule
from cauterule.models.trajectory import Trajectory


def rule_matches(candidate: CandidateRule, trajectory: Trajectory) -> bool:
    """Return True if *candidate* matches *trajectory*.

    Matching: trigger substring in task or any step error/output, and all context
    items substring in same haystack. Case-insensitive.
    """
    haystack_parts: list[str] = [trajectory.task]
    if trajectory.failure_class:
        haystack_parts.append(trajectory.failure_class)
    for step in trajectory.steps:
        if step.error:
            haystack_parts.append(step.error)
        if step.output:
            haystack_parts.append(step.output)
        if step.input:
            haystack_parts.append(step.input)
    haystack = " ".join(haystack_parts).lower()

    trigger = candidate.when.trigger.lower().strip()
    if not trigger:
        return False
    if trigger not in haystack:
        return False

    for ctx in candidate.when.context:
        if ctx.lower().strip() not in haystack:
            return False

    # Optional tag check: if candidate has tags, require at least one tag in trajectory tags
    # For now, tags are not strict; they are for filtering, not matching.
    return True


def is_near_miss(candidate: CandidateRule, trajectory: Trajectory) -> bool:
    """Return True if trigger matches but not all context (partial)."""
    haystack_parts: list[str] = [trajectory.task]
    for step in trajectory.steps:
        if step.error:
            haystack_parts.append(step.error)
        if step.output:
            haystack_parts.append(step.output)
    haystack = " ".join(haystack_parts).lower()

    trigger = candidate.when.trigger.lower().strip()
    if trigger not in haystack:
        return False

    # If context exists and not all context matches, it's near miss.
    if candidate.when.context:
        matched_ctx = sum(1 for ctx in candidate.when.context if ctx.lower().strip() in haystack)
        if 0 < matched_ctx < len(candidate.when.context):
            return True
    return False
