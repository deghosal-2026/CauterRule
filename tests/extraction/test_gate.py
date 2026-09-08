"""Tests for the pre-extraction null-hypothesis gate."""

from cauterule.extraction.gate import (
    SILENCE_REASON_NO_FAILURE,
    GateResult,
    run_gate,
)
from cauterule.models.trajectory import Step, Trajectory


def _success_traj() -> Trajectory:
    return Trajectory(
        id="T-success",
        timestamp="t",
        task="run tests",
        steps=(Step(step_number=1, tool="bash", output="ok"),),
        success=True,
    )


def _failure_traj() -> Trajectory:
    return Trajectory(
        id="T-fail",
        timestamp="t",
        task="git push fails",
        steps=(Step(step_number=1, tool="bash", error="non-fast-forward"),),
        success=False,
        failure_class="git/push",
    )


def test_success_without_signal_is_silence() -> None:
    result = run_gate(_success_traj(), mode="strict")
    assert result.should_extract is False
    assert result.reason == SILENCE_REASON_NO_FAILURE
    assert result.is_silence is True
    assert result.failure_signals == ()


def test_failure_with_error_proceeds() -> None:
    result = run_gate(_failure_traj(), mode="strict")
    assert result.should_extract is True
    assert result.reason is None
    assert result.is_silence is False
    assert len(result.failure_signals) > 0


def test_nonzero_exit_code_is_signal() -> None:
    traj = Trajectory(
        id="T-exit",
        timestamp="t",
        task="run script",
        steps=(Step(step_number=1, tool="bash", state={"exit_code": 1}),),
        success=True,
    )
    result = run_gate(traj, mode="strict")
    assert result.should_extract is True
    assert any("exit code" in s for s in result.failure_signals)


def test_zero_exit_code_is_not_signal() -> None:
    traj = Trajectory(
        id="T-zero",
        timestamp="t",
        task="run script",
        steps=(Step(step_number=1, tool="bash", state={"exit_code": 0}),),
        success=True,
    )
    result = run_gate(traj, mode="strict")
    assert result.should_extract is False
    assert result.reason == SILENCE_REASON_NO_FAILURE


def test_failed_assertion_is_signal() -> None:
    traj = Trajectory(
        id="T-assert",
        timestamp="t",
        task="run tests",
        steps=(Step(step_number=1, tool="pytest", state={"assertion_failed": "x == y"}),),
        success=True,
    )
    result = run_gate(traj, mode="strict")
    assert result.should_extract is True
    assert any("assertion" in s for s in result.failure_signals)


def test_schema_violation_is_signal() -> None:
    traj = Trajectory(
        id="T-schema",
        timestamp="t",
        task="validate",
        steps=(Step(step_number=1, tool="validator", state={"schema_violation": "missing field"}),),
        success=True,
    )
    result = run_gate(traj, mode="strict")
    assert result.should_extract is True
    assert any("schema" in s for s in result.failure_signals)


def test_failure_class_is_signal_even_when_success() -> None:
    traj = Trajectory(
        id="T-class",
        timestamp="t",
        task="something",
        steps=(Step(step_number=1, tool="bash", output="ok"),),
        success=True,
        failure_class="git/push",
    )
    result = run_gate(traj, mode="strict")
    assert result.should_extract is True
    assert any("failure_class" in s for s in result.failure_signals)


def test_relaxed_mode_always_proceeds() -> None:
    result = run_gate(_success_traj(), mode="relaxed")
    assert result.should_extract is True
    assert result.reason is None
    assert isinstance(result, GateResult)


def test_blank_error_is_not_signal() -> None:
    traj = Trajectory(
        id="T-blank",
        timestamp="t",
        task="run",
        steps=(Step(step_number=1, tool="bash", error="   "),),
        success=True,
    )
    result = run_gate(traj, mode="strict")
    assert result.should_extract is False
    assert result.reason == SILENCE_REASON_NO_FAILURE
