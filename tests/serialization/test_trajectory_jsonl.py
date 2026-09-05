from pathlib import Path

import pytest

from cauterule.models.trajectory import AgentConfig, Environment, Step, Trajectory
from cauterule.serialization.trajectory_jsonl import (
    append_trajectory,
    dump_trajectories,
    dump_trajectory,
    load_trajectories,
    load_trajectory,
)


def _valid_trajectory() -> Trajectory:
    return Trajectory(
        id="T-003",
        timestamp="2026-09-03T18:25:00Z",
        task="Deploy to staging",
        steps=(Step(step_number=1, tool="bash", input="git push", output="rejected"),),
        success=False,
        failure_point="step_1",
        failure_class="git/push",
        quality_label="clear",
        domain="git",
        severity="medium",
        tags=("git",),
        agent_config=AgentConfig(model="gpt-4o", tools=("bash",)),
        environment=Environment(os="linux", ci=True),
        redacted=True,
    )


def test_dump_load_roundtrip() -> None:
    t = _valid_trajectory()
    line = dump_trajectory(t)
    assert "T-003" in line
    loaded = load_trajectory(line)
    assert loaded == t


def test_minimal_roundtrip() -> None:
    t = Trajectory(id="T-001", timestamp="t", task="task", steps=(), success=True)
    assert load_trajectory(dump_trajectory(t)) == t


def test_load_invalid_jsonl() -> None:
    with pytest.raises(ValueError, match="mapping"):
        load_trajectory("123")
    with pytest.raises(ValueError, match="mapping"):
        load_trajectory("[1,2,3]")


def test_dump_load_trajectories(tmp_path: Path) -> None:
    t1 = _valid_trajectory()
    t2 = Trajectory(id="T-004", timestamp="t", task="task2", steps=(), success=True)
    p = tmp_path / "trajectories.jsonl"
    dump_trajectories([t1, t2], p)
    assert p.exists()
    loaded = list(load_trajectories(p))
    assert loaded == [t1, t2]
    # blank lines skipped
    # append with blank line
    with p.open("a", encoding="utf-8") as f:
        f.write("\n\n")
    assert len(list(load_trajectories(p))) == 2


def test_append_trajectory(tmp_path: Path) -> None:
    t = _valid_trajectory()
    p = tmp_path / "append.jsonl"
    append_trajectory(t, p)
    assert p.exists()
    assert list(load_trajectories(p)) == [t]
    # append second
    t2 = Trajectory(id="T-005", timestamp="t", task="task", steps=(), success=True)
    append_trajectory(t2, p)
    assert len(list(load_trajectories(p))) == 2
    # nested dir creation
    nested = tmp_path / "nested" / "file.jsonl"
    append_trajectory(t, nested)
    assert nested.exists()


def test_dump_trajectories_empty(tmp_path: Path) -> None:
    p = tmp_path / "empty.jsonl"
    dump_trajectories([], p)
    assert p.read_text() == ""
    assert list(load_trajectories(p)) == []
