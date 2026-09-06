from cauterule.models.trajectory import Trajectory
from cauterule.redaction.flag import is_redacted, mark_redacted


def test_mark_redacted() -> None:
    t = Trajectory(id="T-001", timestamp="t", task="task", steps=(), success=True, redacted=False)
    assert not is_redacted(t)
    redacted = mark_redacted(t)
    assert is_redacted(redacted)
    assert redacted.redacted is True
    # original unchanged
    assert not t.redacted


def test_mark_already_redacted() -> None:
    t = Trajectory(id="T-002", timestamp="t", task="task", steps=(), success=True, redacted=True)
    same = mark_redacted(t)
    assert same is t  # returns same object when already redacted


def test_is_redacted() -> None:
    t = Trajectory(id="T-003", timestamp="t", task="task", steps=(), success=True, redacted=False)
    assert not is_redacted(t)
    t2 = Trajectory(id="T-004", timestamp="t", task="task", steps=(), success=True, redacted=True)
    assert is_redacted(t2)
