"""Dry-run mode."""

from __future__ import annotations

from cauterule.extraction.prompt import build_extraction_prompt
from cauterule.models.trajectory import Trajectory


def dry_run(trajectory: Trajectory, template: str | None = None) -> dict[str, str]:
    """Show what would be extracted without an LLM call.

    Returns a dict with ``prompt`` and ``would_extract`` stub.

    Args:
        trajectory: Trajectory that would be extracted from.
        template: Optional template hint.
    """
    prompt = build_extraction_prompt(trajectory, template=template)
    # Stub extraction: echo back a would-be candidate based on failure class
    when_trigger = f"when {trajectory.failure_class or trajectory.task[:50]}"
    do_directive = "apply fix based on trajectory"
    return {
        "prompt": prompt,
        "would_extract_when": when_trigger,
        "would_extract_do": do_directive,
        "note": "dry-run: no LLM call, pattern-based stub",
    }
