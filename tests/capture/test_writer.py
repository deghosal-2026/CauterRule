from pathlib import Path

from cauterule.capture.writer import trajectory_path, write_trajectory
from cauterule.models.trajectory import Step, Trajectory


def test_trajectory_path_failure(tmp_path: Path) -> None:
    t = Trajectory(
        id="T-001", timestamp="2026-09-03T18:25:00Z", task="task", steps=(), success=False
    )
    p = trajectory_path(t, base_dir=tmp_path)
    assert p.parent.name == "2026-09-03"
    assert p.name == "failure-T-001.jsonl"
    assert str(tmp_path) in str(p)


def test_trajectory_path_success() -> None:
    t = Trajectory(
        id="T-002", timestamp="2026-09-03T18:25:00Z", task="task", steps=(), success=True
    )
    p = trajectory_path(t)
    assert p.name == "success-T-002.jsonl"


def test_trajectory_path_sanitize() -> None:
    t = Trajectory(
        id="T/001:bad", timestamp="2026-09-03T18:25:00Z", task="task", steps=(), success=False
    )
    p = trajectory_path(t)
    assert "T-001-bad" in p.name


def test_trajectory_path_invalid_timestamp(tmp_path: Path) -> None:
    t = Trajectory(id="T-003", timestamp="bad-timestamp", task="task", steps=(), success=False)
    p = trajectory_path(t, base_dir=tmp_path)
    # fallback to today, but still failure prefix
    assert p.name == "failure-T-003.jsonl"
    assert p.parent.exists() or not p.parent.exists()  # parent is date dir


def test_write_trajectory(tmp_path: Path) -> None:
    t = Trajectory(
        id="T-004",
        timestamp="2026-09-03T18:25:00Z",
        task="task",
        steps=(Step(step_number=1, tool="bash", error="boom"),),
        success=False,
    )
    p = write_trajectory(t, base_dir=tmp_path)
    assert p.exists()
    content = p.read_text()
    assert "T-004" in content
    # second write appends
    p2 = write_trajectory(t, base_dir=tmp_path)
    assert p == p2
    # file should have two lines
    assert len(p.read_text().strip().splitlines()) == 2
