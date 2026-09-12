from cauterule.extraction.patterns import detect_repeated_failures, extract_stronger_rule
from cauterule.models.trajectory import Trajectory


def _traj(id: str, failure_class: str) -> Trajectory:
    return Trajectory(
        id=id, timestamp="t", task="task", steps=(), success=False, failure_class=failure_class
    )


def test_detect_repeated() -> None:
    trajs = [_traj(f"T-{i}", "git/push") for i in range(5)] + [
        _traj(f"T-{i}", "python/import") for i in range(2)
    ]
    repeated = detect_repeated_failures(trajs, min_count=3)
    assert len(repeated) == 1
    assert repeated[0][0] == "git/push"
    assert repeated[0][1] == 5


def test_detect_no_repeated() -> None:
    trajs = [_traj(f"T-{i}", f"class-{i}") for i in range(3)]
    assert detect_repeated_failures(trajs, min_count=2) == []


def test_detect_sorted() -> None:
    trajs = [
        _traj("T-1", "a"),
        _traj("T-2", "a"),
        _traj("T-3", "a"),
        _traj("T-4", "b"),
        _traj("T-5", "b"),
        _traj("T-6", "b"),
        _traj("T-7", "b"),
    ]
    repeated = detect_repeated_failures(trajs, min_count=2)
    assert repeated[0][0] == "b"  # 4 > 3


def test_extract_stronger_rule() -> None:
    rule = extract_stronger_rule("git/push", [], count=3)
    assert "git/push" in rule.when.trigger
    assert "3 times" in rule.when.trigger
    assert rule.template == "check-preconditions"
    assert "3" in (rule.reasoning or "")
