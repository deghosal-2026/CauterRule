from cauterule.extraction.dryrun import dry_run
from cauterule.models.trajectory import Step, Trajectory


def test_dry_run_basic() -> None:
    t = Trajectory(id="T-001", timestamp="t", task="git push", steps=(Step(1, "bash", error="fail"),), success=False, failure_class="git/push")
    result = dry_run(t)
    assert result.when.trigger == "when git/push"
    assert result.do.directive == "apply fix based on trajectory"
    assert result.confidence == 0.0


def test_dry_run_template() -> None:
    t = Trajectory(id="T-002", timestamp="t", task="task", steps=(), success=False)
    result = dry_run(t, template="retry")
    assert result.template == "retry"
    assert result.reasoning is not None and "retry" in result.reasoning.lower()


def test_dry_run_no_failure_class() -> None:
    t = Trajectory(id="T-003", timestamp="t", task="my task", steps=(), success=False)
    result = dry_run(t)
    assert "my task" in result.when.trigger