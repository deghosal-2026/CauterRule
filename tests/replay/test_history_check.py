from cauterule.models.trajectory import Trajectory
from cauterule.replay.history_check import check_history, history_verdict


def test_sufficient() -> None:
    trajs = [Trajectory(id=f"T-{i}", timestamp="t", task="t", steps=(), success=True) for i in range(5)]
    ok, msg = check_history(trajs, min_count=3)
    assert ok
    assert msg == "ok"


def test_insufficient() -> None:
    trajs = [Trajectory(id="T-1", timestamp="t", task="t", steps=(), success=True)]
    ok, msg = check_history(trajs, min_count=3)
    assert not ok
    assert "insufficient" in msg


def test_empty() -> None:
    ok, _msg = check_history([], min_count=3)
    assert not ok


def test_history_verdict() -> None:
    assert history_verdict([Trajectory(id="T-1", timestamp="t", task="t", steps=(), success=True)]) == "inconclusive"
    assert history_verdict([Trajectory(id=f"T-{i}", timestamp="t", task="t", steps=(), success=True) for i in range(3)]) == "ok"
