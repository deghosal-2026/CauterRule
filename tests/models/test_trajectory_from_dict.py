"""Strict from_dict tests for Trajectory/Step (#594, #595)."""

from typing import Any

import pytest

from cauterule.models.trajectory import Step, Trajectory


def _base(**overrides: Any) -> dict[str, Any]:
    d = {
        "trajectory_id": "T-1",
        "timestamp": "2026-01-01T00:00:00Z",
        "task": "x",
        "steps": [],
        "success": True,
    }
    d.update(overrides)
    return d


def test_missing_success_raises() -> None:
    # #594: absent success must not silently label a success as failure.
    d = _base()
    del d["success"]
    with pytest.raises(ValueError, match="success"):
        Trajectory.from_dict(d)


def test_none_success_raises() -> None:
    d = _base(success=None)
    with pytest.raises(ValueError, match="success"):
        Trajectory.from_dict(d)


def test_steps_missing_step_number_do_not_collide() -> None:
    # #595: auto-number by position instead of collapsing to 1.
    d = _base(
        success=False,
        steps=[
            {"tool": "bash", "input": "a"},
            {"tool": "bash", "input": "b"},
            {"tool": "bash", "input": "c"},
        ],
    )
    traj = Trajectory.from_dict(d)
    assert [s.step_number for s in traj.steps] == [1, 2, 3]


def test_steps_explicit_step_number_preserved() -> None:
    d = _base(
        success=False,
        steps=[
            {"step_number": 5, "tool": "bash"},
            {"step_number": 7, "tool": "bash"},
        ],
    )
    traj = Trajectory.from_dict(d)
    assert [s.step_number for s in traj.steps] == [5, 7]


def test_step_from_dict_missing_without_hint_raises() -> None:
    # #595: bare Step.from_dict with no position hint fails loud.
    with pytest.raises(ValueError, match="step_number"):
        Step.from_dict({"tool": "bash"})


def test_steps_auto_number_logs_warning(caplog: pytest.LogCaptureFixture) -> None:
    # Review: the auto-number fallback is observable.
    import logging

    d = _base(success=False, steps=[{"tool": "bash"}, {"tool": "bash"}])
    with caplog.at_level(logging.WARNING, logger="cauterule.models.trajectory"):
        traj = Trajectory.from_dict(d)
    assert [s.step_number for s in traj.steps] == [1, 2]
    assert "auto-numbering" in caplog.text
