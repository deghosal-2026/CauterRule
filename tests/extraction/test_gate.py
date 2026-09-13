"""Tests for the pre-extraction null-hypothesis gate."""

from cauterule.extraction.gate import (
    SILENCE_REASON_NEARMISS,
    SILENCE_REASON_NO_FAILURE,
    SILENCE_REASON_NO_SIGNAL_AND_FAILURE,
    GateResult,
    _detect_nearmiss_recovery,
    _step_shows_success,
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


def test_relaxed_mode_silences_clean_success() -> None:
    # #709: a clean success (success=True, no failure signals) must not be
    # extracted even in relaxed mode — otherwise non-failure corpora (otel span
    # events) get extracted and then break reference successes.
    result = run_gate(_success_traj(), mode="relaxed")
    assert result.should_extract is False
    assert result.reason == SILENCE_REASON_NO_FAILURE
    assert isinstance(result, GateResult)


def test_relaxed_mode_proceeds_for_success_with_failure_signal() -> None:
    traj = Trajectory(
        id="T-success-sig",
        timestamp="t",
        task="recovered run",
        steps=(Step(step_number=1, tool="bash", error="transient boom"),),
        success=True,
    )
    result = run_gate(traj, mode="relaxed")
    assert result.should_extract is True


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


# ------------------------------------------------------------------
# #518 — zero-signal failures + state-only recovery
# ------------------------------------------------------------------
def test_failure_without_signals_is_silence() -> None:
    traj = Trajectory(
        id="T-nosig",
        timestamp="t",
        task="do thing",
        steps=(Step(step_number=1, tool="bash", output=""),),
        success=False,
    )
    result = run_gate(traj, mode="strict")
    assert result.should_extract is False
    assert result.reason == SILENCE_REASON_NO_SIGNAL_AND_FAILURE


def test_failure_without_signals_proceeds_relaxed() -> None:
    traj = Trajectory(
        id="T-nosig-relaxed",
        timestamp="t",
        task="do thing",
        steps=(Step(step_number=1, tool="bash", output=""),),
        success=False,
    )
    result = run_gate(traj, mode="relaxed")
    assert result.should_extract is True


def test_state_only_recovery_is_nearmiss() -> None:
    traj = Trajectory(
        id="T-state-rec",
        timestamp="t",
        task="retry",
        steps=(
            Step(step_number=1, tool="bash", error="perm denied", state={"exit_code": 1}),
            Step(step_number=2, tool="bash", output="", state={"exit_code": 0}),
        ),
        success=True,
    )
    result = run_gate(traj, mode="strict")
    assert result.should_extract is False
    assert result.reason == SILENCE_REASON_NEARMISS


def test_state_only_early_failure_is_nearmiss() -> None:
    # #772: an early step that failed only via state (exit_code=1, no error
    # text) followed by a state recovery is a near-miss and must be dropped.
    traj = Trajectory(
        id="T-state-only",
        timestamp="t",
        task="retry",
        steps=(
            Step(step_number=1, tool="bash", state={"exit_code": 1}),
            Step(step_number=2, tool="bash", state={"exit_code": 0}),
        ),
        success=True,
    )
    result = run_gate(traj, mode="strict")
    assert result.should_extract is False
    assert result.reason == SILENCE_REASON_NEARMISS


# ------------------------------------------------------------------
# #692 — recovery keyword must match whole tokens, not substrings
# ------------------------------------------------------------------
def test_recovery_keyword_does_not_match_substring_false_positive() -> None:
    # "template_injection" contains "temp" as a substring but is a real,
    # unresolved failure class — must NOT be gate-dropped as a near-miss.
    traj = Trajectory(
        id="T-substr",
        timestamp="t",
        task="render user template",
        steps=(
            Step(step_number=1, tool="render", output="starting template engine"),
            Step(step_number=2, tool="render", output="completed"),
        ),
        success=True,
        failure_class="template_injection",
    )
    result = run_gate(traj, mode="strict")
    assert result.should_extract is True


def test_recovery_keyword_matches_whole_token() -> None:
    # A genuine whole-word recovery token must still gate-drop.
    traj = Trajectory(
        id="T-token",
        timestamp="t",
        task="retry push",
        steps=(Step(step_number=1, tool="bash", output="ok"),),
        success=True,
        failure_class="git/near-miss/recovered",
    )
    result = run_gate(traj, mode="strict")
    assert result.should_extract is False
    assert result.reason == SILENCE_REASON_NEARMISS


def test_recovery_keyword_ignores_unrelated_substring_classes() -> None:
    for failure_class in ("nearline_storage_corruption", "temperature_sensor_timeout"):
        traj = Trajectory(
            id=f"T-{failure_class}",
            timestamp="t",
            task="do work",
            steps=(
                Step(step_number=1, tool="bash", output="start"),
                Step(step_number=2, tool="bash", output="done"),
            ),
            success=True,
            failure_class=failure_class,
        )
        assert _detect_nearmiss_recovery(traj) is False, failure_class


# ------------------------------------------------------------------
# #693 — output presence is not a success signal
# ------------------------------------------------------------------
def test_step_shows_success_false_positive_on_error_text_in_output() -> None:
    step = Step(
        step_number=1, tool="bash", output="Error: connection refused", error=None, state={}
    )
    assert _step_shows_success(step) is False


def test_step_shows_success_respects_nonzero_exit_code_over_output_text() -> None:
    step = Step(step_number=1, tool="bash", output="some log line", state={"exit_code": 1})
    assert _step_shows_success(step) is False


def test_detect_nearmiss_recovery_rejects_still_failing_later_step() -> None:
    traj = Trajectory(
        id="T-still-failing",
        timestamp="t",
        task="retry fetch",
        steps=(
            Step(step_number=1, tool="bash", error="connection refused"),
            Step(step_number=2, tool="bash", output="Error: connection refused", error=None),
        ),
        success=True,
    )
    assert _detect_nearmiss_recovery(traj) is False
    result = run_gate(traj, mode="strict")
    assert result.should_extract is True
