from pathlib import Path

from cauterule.models.trajectory import Trajectory
from cauterule.replay.loader import load_corpus, load_from_dir, load_from_file
from cauterule.serialization.trajectory_jsonl import dump_trajectory


def test_load_from_file(tmp_path: Path) -> None:
    t = Trajectory(id="T-001", timestamp="t", task="task", steps=(), success=True)
    p = tmp_path / "traj.jsonl"
    with p.open("w") as f:
        f.write(dump_trajectory(t) + "\n")
    loaded = load_from_file(p)
    assert len(loaded) == 1
    assert loaded[0].id == "T-001"
    # missing file
    assert load_from_file(tmp_path / "nope.jsonl") == []


def test_load_from_dir(tmp_path: Path) -> None:
    t1 = Trajectory(id="T-001", timestamp="t", task="t", steps=(), success=True)
    t2 = Trajectory(id="T-002", timestamp="t", task="t", steps=(), success=True)
    sub = tmp_path / "sub"
    sub.mkdir()
    with (tmp_path / "a.jsonl").open("w") as f:
        f.write(dump_trajectory(t1) + "\n")
    with (sub / "b.jsonl").open("w") as f:
        f.write(dump_trajectory(t2) + "\n")
    loaded = load_from_dir(tmp_path)
    assert len(loaded) == 2
    assert loaded[0].id == "T-001"
    assert loaded[1].id == "T-002"
    # non-existent dir
    assert load_from_dir(tmp_path / "nope") == []


def test_load_corpus(tmp_path: Path) -> None:
    t = Trajectory(id="T-001", timestamp="t", task="t", steps=(), success=True)
    p = tmp_path / "t.jsonl"
    with p.open("w") as f:
        f.write(dump_trajectory(t) + "\n")
    loaded = load_corpus([p, tmp_path / "nope"])
    assert len(loaded) == 1
    # dir
    loaded2 = load_corpus([tmp_path])
    assert len(loaded2) == 1
