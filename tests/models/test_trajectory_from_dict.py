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


@pytest.mark.parametrize("value", ["false", "true", 0, 1, False, True])
def test_success_accepts_real_booleans(value: Any) -> None:
    # #769: numeric/string booleans are coerced; string "false" must not
    # become True via bool().
    traj = Trajectory.from_dict(_base(success=value))
    assert traj.success is bool(value in (True, 1, "true"))


@pytest.mark.parametrize("value", ["yes", "no", 2, -1, [], {}, 3.14])
def test_success_rejects_non_boolean(value: Any) -> None:
    # #769: fail loud instead of silently coercing arbitrary truthy values.
    with pytest.raises(ValueError, match="success"):
        Trajectory.from_dict(_base(success=value))


def test_optional_boolean_fields_strict() -> None:
    # #769: redacted/injection_signal get the same strict coercion.
    traj = Trajectory.from_dict(_base(success=False, redacted="false", injection_signal="false"))
    assert traj.redacted is False
    assert traj.injection_signal is False
    traj2 = Trajectory.from_dict(_base(success=False, redacted="true", injection_signal=1))
    assert traj2.redacted is True
    assert traj2.injection_signal is True
    with pytest.raises(ValueError, match="redacted"):
        Trajectory.from_dict(_base(success=False, redacted="maybe"))
    with pytest.raises(ValueError, match="injection_signal"):
        Trajectory.from_dict(_base(success=False, injection_signal=2))


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


def test_scalar_tags_rejected() -> None:
    # #771: scalar tags must not split into characters.
    with pytest.raises(ValueError, match="tags"):
        Trajectory.from_dict(_base(success=False, tags="git"))


def test_scalar_agent_tools_rejected() -> None:
    with pytest.raises(ValueError, match="tools"):
        Trajectory.from_dict(_base(success=False, agent_config={"tools": "bash"}))
