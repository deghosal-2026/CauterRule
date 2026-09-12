from cauterule.models.trajectory import Step, Trajectory
from cauterule.replay.whatif import what_if


def test_what_if() -> None:
    trajs = [
        Trajectory(
            id="T-1",
            timestamp="t",
            task="git push fails",
            steps=(Step(1, "bash", error="err"),),
            success=False,
        ),
        Trajectory(
            id="T-2",
            timestamp="t",
            task="docker fails",
            steps=(Step(1, "bash", error="err"),),
            success=False,
        ),
    ]
    result = what_if("test rule", "git push", "pull --rebase", trajs)
    assert result["task"] == "test rule"
    assert "T-1" in result["failures_prevented"]
    assert result["precision"] >= 0


def test_what_if_context() -> None:
    trajs = [
        Trajectory(
            id="T-1",
            timestamp="t",
            task="git push on shared branch",
            steps=(Step(1, "bash", error="err"),),
            success=False,
        )
    ]
    result = what_if("test", "git push", "d", trajs, context=("shared branch",))
    assert result["context"] == ["shared branch"]
