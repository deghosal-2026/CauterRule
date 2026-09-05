"""Redaction engine."""

from __future__ import annotations

import re
from typing import Any

from cauterule.models.trajectory import Step, Trajectory
from cauterule.redaction.patterns import get_builtin_patterns

_REDACTED = "[REDACTED]"


def _compile_extra(patterns: list[str] | tuple[str, ...] | None) -> list[re.Pattern[str]]:
    if not patterns:
        return []
    compiled: list[re.Pattern[str]] = []
    for p in patterns:
        try:
            compiled.append(re.compile(p))
        except re.error:
            # Invalid regex: treat as literal substring.
            compiled.append(re.compile(re.escape(p)))
    return compiled


def redact_text(text: str, extra_patterns: list[str] | tuple[str, ...] | None = None) -> str:
    """Redact secrets in *text* using built-in and *extra_patterns*.

    Args:
        text: Input text.
        extra_patterns: Additional regex patterns for custom secrets.
    """
    if not text:
        return text
    redacted = text
    for pat in get_builtin_patterns():
        redacted = pat.sub(_REDACTED, redacted)
    for pat in _compile_extra(extra_patterns):
        redacted = pat.sub(_REDACTED, redacted)
    return redacted


def _redact_value(value: Any, extra_patterns: list[str] | tuple[str, ...] | None) -> Any:
    if isinstance(value, str):
        return redact_text(value, extra_patterns)
    if isinstance(value, dict):
        return {k: _redact_value(v, extra_patterns) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        redacted_list = [_redact_value(v, extra_patterns) for v in value]
        return type(value)(redacted_list) if isinstance(value, tuple) else redacted_list
    return value


def redact_trajectory(
    trajectory: Trajectory,
    extra_patterns: list[str] | tuple[str, ...] | None = None,
) -> Trajectory:
    """Return a new :class:`Trajectory` with secrets redacted.

    Redacts ``task``, ``failure_class``, and all step ``input``/``output``/``error``/``state``.
    Sets ``redacted`` to ``True``.
    """
    # Check if already redacted: no-op to avoid double processing, but still ensure flag.
    # We still redact even if already redacted (idempotent).

    redacted_steps: list[Step] = []
    for step in trajectory.steps:
        redacted_state = None
        if step.state is not None:
            redacted_state = _redact_value(step.state, extra_patterns)
        redacted_steps.append(
            Step(
                step_number=step.step_number,
                tool=step.tool,  # tool name not redacted (not a secret)
                input=redact_text(step.input, extra_patterns) if step.input is not None else None,
                output=redact_text(step.output, extra_patterns) if step.output is not None else None,
                error=redact_text(step.error, extra_patterns) if step.error is not None else None,
                state=redacted_state,
            )
        )

    # Redact top-level fields.
    redacted_task = redact_text(trajectory.task, extra_patterns)
    redacted_failure_class = (
        redact_text(trajectory.failure_class, extra_patterns) if trajectory.failure_class else None
    )

    return Trajectory(
        id=trajectory.id,
        timestamp=trajectory.timestamp,
        task=redacted_task,
        steps=tuple(redacted_steps),
        success=trajectory.success,
        failure_point=trajectory.failure_point,
        failure_class=redacted_failure_class,
        quality_label=trajectory.quality_label,
        domain=trajectory.domain,
        severity=trajectory.severity,
        tags=trajectory.tags,
        agent_config=trajectory.agent_config,
        environment=trajectory.environment,
        redacted=True,
    )


def contains_secret(text: str, extra_patterns: list[str] | tuple[str, ...] | None = None) -> bool:
    """Return ``True`` if *text* contains a secret pattern."""
    if not text:
        return False
    for pat in get_builtin_patterns():
        if pat.search(text):
            return True
    for pat in _compile_extra(extra_patterns):
        if pat.search(text):
            return True
    return False
