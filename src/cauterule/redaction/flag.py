"""Redaction flag handling."""

from __future__ import annotations

from cauterule.models.trajectory import Trajectory


def mark_redacted(trajectory: Trajectory) -> Trajectory:
    """Return *trajectory* with ``redacted=True``.

    If already redacted, returns the same trajectory without modification.
    """
    if trajectory.redacted:
        return trajectory
    return Trajectory(
        id=trajectory.id,
        timestamp=trajectory.timestamp,
        task=trajectory.task,
        steps=trajectory.steps,
        success=trajectory.success,
        failure_point=trajectory.failure_point,
        failure_class=trajectory.failure_class,
        quality_label=trajectory.quality_label,
        domain=trajectory.domain,
        severity=trajectory.severity,
        tags=trajectory.tags,
        agent_config=trajectory.agent_config,
        environment=trajectory.environment,
        redacted=True,
    )


def is_redacted(trajectory: Trajectory) -> bool:
    """Return ``True`` if *trajectory* is flagged as redacted."""
    return trajectory.redacted
