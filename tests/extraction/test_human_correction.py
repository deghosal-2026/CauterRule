from cauterule.extraction.human_correction import parse_correction
from cauterule.models.trajectory import Step, Trajectory


def _traj() -> Trajectory:
    return Trajectory(id="T-001", timestamp="t", task="git push", steps=(Step(1, "bash", error="fail"),), success=False, failure_class="git/push")


def test_parse_next_time() -> None:
    c = parse_correction("next time do pull --rebase first", _traj())
    assert c is not None
    assert "pull --rebase" in c.do.directive
    assert "git/push" in c.when.trigger


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
