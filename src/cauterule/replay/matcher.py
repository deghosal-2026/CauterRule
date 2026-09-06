"""Rule matcher."""

from __future__ import annotations

from cauterule.models.candidate import CandidateRule
from cauterule.models.trajectory import Trajectory

# Triggers shorter than this are considered too generic to match reliably.
# Set to 1 to allow single-word triggers like "docker" or "deploy" while still
# providing a floor for truly empty or meaningless triggers.
_MIN_TRIGGER_WORDS = 1


def _tokenize(text: str) -> set[str]:
    """Return lowercase word tokens from *text*."""
    return {w for w in text.lower().split() if len(w) > 1}


def rule_matches(candidate: CandidateRule, trajectory: Trajectory) -> bool:
    """Return True if *candidate* matches *trajectory*.

    Matching strategy:
    1. Build a haystack from task, failure_class, and step input/output/error.
    2. Check trigger: either substring match OR significant token overlap.
    3. Check all context items: substring match in haystack.
    4. Reject overly generic triggers (1 word) unless context disambiguates.

    Case-insensitive throughout.
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

    trigger_words = _tokenize(trigger)
    haystack_words = _tokenize(haystack)

    # Reject 1-word triggers as too generic unless context narrows them
    if len(trigger_words) < _MIN_TRIGGER_WORDS and not candidate.when.context:
        return False

    # Match: substring match preferred. For longer triggers (>=4 words),
    # fall back to token overlap as a tolerance for small model output variation.
    # Require >=75% overlap to avoid false positives from short generic triggers.
    trigger_match = trigger in haystack
    if not trigger_match and len(trigger_words) >= 4:
        overlap = len(trigger_words & haystack_words)
        if overlap < max(3, len(trigger_words) // 2):
            return False
    elif not trigger_match:
        return False

    # All context items must substring-match
    for ctx in candidate.when.context:
        if ctx.lower().strip() not in haystack:
            return False

    return True


def is_near_miss(candidate: CandidateRule, trajectory: Trajectory) -> bool:
    """Return True if trigger matches but not all context (partial)."""
    haystack_parts: list[str] = [trajectory.task]
    if trajectory.failure_class:
        haystack_parts.append(trajectory.failure_class)
    for step in trajectory.steps:
        if step.error:
            haystack_parts.append(step.error)
        if step.output:
            haystack_parts.append(step.output)
    haystack = " ".join(haystack_parts).lower()

    trigger = candidate.when.trigger.lower().strip()
    if not trigger:
        return False

    trigger_words = _tokenize(trigger)
    haystack_words = _tokenize(haystack)

    trigger_match = trigger in haystack
    if not trigger_match and trigger_words:
        overlap = len(trigger_words & haystack_words)
        if overlap < max(1, len(trigger_words) // 2):
            return False
    elif not trigger_match:
        return False

    # If context exists and not all context matches, it's near miss.
    if candidate.when.context:
        matched_ctx = sum(1 for ctx in candidate.when.context if ctx.lower().strip() in haystack)
        if 0 < matched_ctx < len(candidate.when.context):
            return True
    return False
