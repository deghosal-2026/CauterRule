"""Human correction capture."""

from __future__ import annotations

import re

from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.models.trajectory import Trajectory

_CORRECTION_PATTERNS = [
    re.compile(r"next time (?:do|try|use)\s+(.+)", re.IGNORECASE),
    re.compile(r"should have\s+(.+)", re.IGNORECASE),
    re.compile(r"please\s+(.+)", re.IGNORECASE),
]


def parse_correction(text: str, trajectory: Trajectory | None = None) -> CandidateRule | None:
    """Parse a human correction like \"next time do X\" into a candidate.

    Args:
        text: Human correction text.
        trajectory: Optional trajectory for context (used to infer when trigger).

    Returns:
        :class:`CandidateRule` if parsing succeeds, else ``None``.
    """
    text = text.strip()
    if not text:
        return None

    directive: str | None = None
    for pat in _CORRECTION_PATTERNS:
        m = pat.search(text)
        if m:
            directive = m.group(1).strip().rstrip(".")
            break

    if directive is None:
        # Fallback: treat whole text as directive if it looks like an action.
        if len(text.split()) >= 3:
            directive = text
        else:
            return None

    # Infer trigger from trajectory failure class or task
    trigger = "when task fails"
    if trajectory is not None:
        if trajectory.failure_class:
            trigger = f"when {trajectory.failure_class} fails"
        elif trajectory.task:
            trigger = f"when {trajectory.task[:60]} fails"

    return CandidateRule(
        when=RuleWhen(trigger=trigger),
        do=RuleDo(directive=directive),
        confidence=0.8,
        reasoning=f"human correction: {text[:100]}",
        extraction_pass=1,
        template=None,
    )
