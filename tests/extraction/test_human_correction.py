from cauterule.extraction.human_correction import DEFAULT_CORRECTION_CONFIDENCE, parse_correction
from cauterule.models.trajectory import Step, Trajectory


def _traj() -> Trajectory:
    return Trajectory(
        id="T-001",
        timestamp="t",
        task="git push",
        steps=(Step(1, "bash", error="fail"),),
        success=False,
        failure_class="git/push",
    )


def _traj_with_step_output() -> Trajectory:
    return Trajectory(
        id="T-002",
        timestamp="t",
        task="build",
        steps=(Step(1, "bash", output="compile error: undefined reference"),),
        success=False,
    )


def _traj_no_error() -> Trajectory:
    return Trajectory(
        id="T-003",
        timestamp="t",
        task="deploy",
        steps=(),
        success=False,
        failure_class="deploy/fail",
    )


def test_parse_next_time() -> None:
    c = parse_correction("next time do pull --rebase first", _traj())
    assert c is not None
    assert "pull --rebase" in c.do.directive
    # Trigger should come from step error, not failure_class
    assert "fail" in c.when.trigger


def test_parse_should_have() -> None:
    c = parse_correction("should have run tests first", _traj())
    assert c is not None
    assert "run tests" in c.do.directive


def test_parse_please() -> None:
    c = parse_correction("please verify branch is up to date", _traj())
    assert c is not None
    assert "verify" in c.do.directive


def test_parse_fallback() -> None:
    c = parse_correction("make sure to check preconditions before deploy", _traj())
    assert c is not None
    assert "check preconditions" in c.do.directive


def test_parse_short() -> None:
    assert parse_correction("hi", _traj()) is None
    assert parse_correction("   ", _traj()) is None
    assert parse_correction("", None) is None


def test_parse_no_trajectory() -> None:
    c = parse_correction("next time do X", None)
    assert c is not None
    assert "X" in c.do.directive
    assert c.when.trigger == "when task fails"


def test_parse_trigger_from_step_output() -> None:
    c = parse_correction("next time fix the compile error", _traj_with_step_output())
    assert c is not None
    assert "compile error" in c.when.trigger


def test_parse_trigger_from_failure_class_fallback() -> None:
    c = parse_correction("next time check connectivity", _traj_no_error())
    assert c is not None
    assert "deploy/fail" in c.when.trigger


def test_parse_confidence_default() -> None:
    c = parse_correction("next time do X", _traj())
    assert c is not None
    assert c.confidence == DEFAULT_CORRECTION_CONFIDENCE


def test_parse_confidence_custom() -> None:
    c = parse_correction("next time do X", _traj(), confidence=0.5)
    assert c is not None
    assert c.confidence == 0.5


def test_parse_confidence_clamped() -> None:
    c = parse_correction("next time do X", _traj(), confidence=1.5)
    assert c is not None
    assert c.confidence == 1.0
    c = parse_correction("next time do X", _traj(), confidence=-0.5)
    assert c is not None
    assert c.confidence == 0.0
