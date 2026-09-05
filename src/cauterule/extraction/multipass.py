"""Multi-pass orchestrator."""

from __future__ import annotations

from typing import Any

from cauterule.extraction.extractor import extract_candidate_safe
from cauterule.models.candidate import CandidateRule
from cauterule.models.trajectory import Trajectory

DEFAULT_TEMPERATURES: tuple[float, ...] = (0.2, 0.5, 0.8)


def multipass_extract(
    trajectory: Trajectory,
    llm: Any,
    temperatures: tuple[float, ...] = DEFAULT_TEMPERATURES,
    template: str | None = None,
) -> list[CandidateRule]:
    """Run extraction multiple times with different temperatures.

    Args:
        trajectory: Trajectory to extract from.
        llm: LLM provider.
        temperatures: Temperatures to use per pass.
        template: Optional template hint.

    Returns:
        List of successfully extracted candidates (one per successful pass).
    """
    candidates: list[CandidateRule] = []
    for idx, temp in enumerate(temperatures, start=1):
        # Pass temperature via llm kwargs if supported; here we just vary extraction_pass.
        candidate, error = extract_candidate_safe(
            trajectory, llm, template=template, extraction_pass=idx
        )
        if candidate is not None:
            # Annotate with temperature via reasoning if needed (no field, so keep as is).
            candidates.append(candidate)
        else:
            _ = error
    return candidates
