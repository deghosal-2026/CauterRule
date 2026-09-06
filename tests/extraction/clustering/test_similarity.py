from cauterule.extraction.clustering.similarity import similarity
from cauterule.models.trajectory import Step, Trajectory


def _traj(failure_class: str | None, tool: str, error: str | None) -> Trajectory:
    steps = (Step(step_number=1, tool=tool, error=error),) if error or tool else ()
    return Trajectory(
        id="T-001",
        timestamp="t",
        task="task",
        steps=steps,
        success=False,
        failure_class=failure_class,
    )


def test_similarity_identical() -> None:
    a = _traj("git/push", "bash", "non-fast-forward")
    b = _traj("git/push", "bash", "non-fast-forward")
    assert similarity(a, b) == 1.0


def test_similarity_same_prefix() -> None:
    a = _traj("git/push/non-fast-forward", "bash", "error")
    b = _traj("git/push", "bash", "error")
    s = similarity(a, b)
    assert 0.7 < s < 1.0


def test_similarity_different_class() -> None:
    a = _traj("git/push", "bash", "error")
    b = _traj("python/import", "python", "import error")
    assert similarity(a, b) < 0.6


def test_similarity_tool_jaccard() -> None:
    a = Trajectory(
        id="T-1", timestamp="t", task="t", steps=(Step(1, "bash"), Step(2, "read")), success=False, failure_class="git/push"
    )
    b = Trajectory(
        id="T-2", timestamp="t", task="t", steps=(Step(1, "bash"), Step(2, "write")), success=False, failure_class="git/push"
    )
    s = similarity(a, b)
    assert 0.5 < s < 1.0


def test_similarity_error_overlap() -> None:
    a = _traj("git/push", "bash", "non-fast-forward rejected")
    b = _traj("git/push", "bash", "rejected non-fast-forward")
    assert similarity(a, b) > 0.8


def test_similarity_empty() -> None:
    a = Trajectory(id="T-1", timestamp="t", task="t", steps=(), success=False)
    b = Trajectory(id="T-2", timestamp="t", task="t", steps=(), success=False)
    assert similarity(a, b) == 1.0


def test_similarity_no_failure_class() -> None:
    a = _traj(None, "bash", "error")
    b = _traj(None, "bash", "error")
    assert similarity(a, b) > 0.5
    c = _traj("git/push", "bash", "error")
    assert similarity(a, c) < similarity(a, b)
