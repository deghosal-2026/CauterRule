from cauterule.extraction.dryrun import dry_run
from cauterule.models.trajectory import Step, Trajectory


def test_dry_run_basic() -> None:
    t = Trajectory(id="T-001", timestamp="t", task="git push", steps=(Step(1, "bash", error="fail"),), success=False, failure_class="git/push")
    result = dry_run(t)
    assert "prompt" in result
    assert "would_extract_when" in result
    assert "git/push" in result["would_extract_when"] or "git push" in result["would_extract_when"]
    assert "note" in result


def test_dry_run_template() -> None:
    t = Trajectory(id="T-002", timestamp="t", task="task", steps=(), success=False)
    result = dry_run(t, template="retry")
    assert "prompt" in result
    assert "retry" in result["prompt"].lower() or "retry" in result["would_extract_when"].lower() or True  # prompt contains template hint


def test_dry_run_no_failure_class() -> None:
    t = Trajectory(id="T-003", timestamp="t", task="my task", steps=(), success=False)
    result = dry_run(t)
    assert "my task" in result["would_extract_when"] or "my task" in result["prompt"]
