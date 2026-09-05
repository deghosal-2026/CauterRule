"""Extraction prompt builder."""

from __future__ import annotations

from cauterule.models.trajectory import Trajectory

TEMPLATE_INSTRUCTIONS: dict[str, str] = {
    "retry": "Suggest a retry-with-fix pattern.",
    "verify-then-act": "Suggest a verify-before-act pattern.",
    "check-preconditions": "Suggest a check-preconditions pattern.",
}


def build_extraction_prompt(trajectory: Trajectory, template: str | None = None) -> str:
    """Build an extraction prompt for *trajectory*.

    Args:
        trajectory: Trajectory to extract from.
        template: Optional template hint (retry, verify-then-act, check-preconditions).
    """
    steps_str = "\n".join(
        f"Step {s.step_number}: tool={s.tool} input={s.input or ''} output={s.output or ''} error={s.error or ''}"
        for s in trajectory.steps
    )
    template_hint = ""
    if template:
        hint = TEMPLATE_INSTRUCTIONS.get(template, template)
        template_hint = f"\nTemplate hint: {template} — {hint}"

    failure_point = trajectory.failure_point or "unknown"
    failure_class = trajectory.failure_class or "unknown"

    return (
        f"You are an expert at extracting actionable standing rules from agent failures.\n"
        f"Task: {trajectory.task}\n"
        f"Failure point: {failure_point}\n"
        f"Failure class: {failure_class}\n"
        f"Steps:\n{steps_str}\n"
        f"Tags: {', '.join(trajectory.tags) if trajectory.tags else 'none'}\n"
        f"{template_hint}\n"
        f"Produce a JSON object with keys: when (trigger, context), do (directive, because), "
        f"confidence (0.0-1.0), reasoning, template.\n"
        f"Example: {{\"when\": {{\"trigger\": \"when X\"}}, \"do\": {{\"directive\": \"do Y\"}}, \"confidence\": 0.85}}"
    )
