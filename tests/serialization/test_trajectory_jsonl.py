from pathlib import Path

import pytest

from cauterule.models.trajectory import AgentConfig, Environment, Step, Trajectory
from cauterule.serialization.trajectory_jsonl import (
    append_trajectory,
    dump_trajectories,
    dump_trajectory,
    load_trajectories,
    load_trajectories_result,
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


def test_load_trajectories_skips_bad_lines(tmp_path: Path) -> None:
    # #597: one corrupt line must not kill the other 499.
    import json as _json

    p = tmp_path / "corpus.jsonl"
    good = _valid_trajectory()
    with p.open("w", encoding="utf-8") as f:
        f.write(dump_trajectory(good) + "\n")
        f.write("{not valid json\n")
        f.write(_json.dumps({"id": "T-bad", "task": "no success field"}) + "\n")
        f.write(dump_trajectory(good) + "\n")
    skipped: list[tuple[int, str]] = []
    loaded = list(load_trajectories(p, on_skip=lambda ln, err: skipped.append((ln, err))))
    assert loaded == [good, good]
    assert [ln for ln, _ in skipped] == [2, 3]


def test_load_trajectories_strict_raises(tmp_path: Path) -> None:
    # #597: strict=True re-enables fail-fast for CI.
    p = tmp_path / "corpus.jsonl"
    with p.open("w", encoding="utf-8") as f:
        f.write(dump_trajectory(_valid_trajectory()) + "\n")
        f.write("{not valid json\n")
    with pytest.raises(ValueError, match="skipping bad JSONL line"):
        list(load_trajectories(p, strict=True))


def test_load_trajectories_result_reports_skips(tmp_path: Path) -> None:
    # #597: skip count exposed via LoadResult.
    p = tmp_path / "corpus.jsonl"
    with p.open("w", encoding="utf-8") as f:
        f.write(dump_trajectory(_valid_trajectory()) + "\n")
        f.write("boom\n")
    result = load_trajectories_result(p)
    assert len(result.loaded) == 1
    assert result.skipped == 1
    assert len(result.errors) == 1


def test_load_trajectories_result_error_content(tmp_path: Path) -> None:
    # Review: errors carry file line numbers.
    p = tmp_path / "corpus.jsonl"
    with p.open("w", encoding="utf-8") as f:
        f.write(dump_trajectory(_valid_trajectory()) + "\n")
        f.write("{bad\n")
    result = load_trajectories_result(p)
    assert result.skipped == 1
    assert result.errors[0].startswith("line 2:")


def test_load_trajectories_strict_ignores_blank_lines(tmp_path: Path) -> None:
    # Review: blank lines never raise, even in strict mode.
    p = tmp_path / "corpus.jsonl"
    with p.open("w", encoding="utf-8") as f:
        f.write("\n")
        f.write(dump_trajectory(_valid_trajectory()) + "\n")
        f.write("\n")
    assert len(list(load_trajectories(p, strict=True))) == 1


def test_load_trajectories_multiline_objects(tmp_path: Path) -> None:
    # #490: multi-line pretty-printed JSON objects load correctly.
    multi = """{
  "trajectory_id": "T-multi",
  "timestamp": "t",
  "task": "multi-line test",
  "steps": [
    {
      "step_number": 1,
      "tool": "bash",
      "input": "echo hello"
    }
  ],
  "success": false
}"""
    p = tmp_path / "corpus.jsonl"
    with p.open("w", encoding="utf-8") as f:
        f.write(dump_trajectory(_valid_trajectory()) + "\n")
        f.write(multi + "\n")
        f.write(dump_trajectory(_valid_trajectory()) + "\n")
    loaded = list(load_trajectories(p))
    assert len(loaded) == 3
    assert loaded[1].id == "T-multi"
    assert loaded[1].success is False


def test_load_trajectories_truncated_multiline_strict_raises(tmp_path: Path) -> None:
    # #773: a multi-line record truncated at EOF must fail loud in strict mode.
    p = tmp_path / "corpus.jsonl"
    p.write_text(
        dump_trajectory(_valid_trajectory())
        + '\n{\n  "trajectory_id": "T-trunc",\n  "task": "x",\n',
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="truncated"):
        list(load_trajectories(p, strict=True))


def test_load_trajectories_truncated_multiline_non_strict_skips(tmp_path: Path) -> None:
    # #773: non-strict mode reports the truncation instead of dropping silently.
    p = tmp_path / "corpus.jsonl"
    p.write_text(
        dump_trajectory(_valid_trajectory())
        + '\n{\n  "trajectory_id": "T-trunc",\n  "task": "x",\n',
        encoding="utf-8",
    )
    result = load_trajectories_result(p)
    assert len(result.loaded) == 1
    assert result.skipped == 1
    assert any("truncated" in e for e in result.errors)


def test_load_trajectories_multiline_with_braces_in_strings(tmp_path: Path) -> None:
    # #490: braces inside JSON string values must not confuse depth counter.
    multi = """{
  "trajectory_id": "T-brace",
  "timestamp": "t",
  "task": "test with {brace} in task",
  "steps": [
    {
      "step_number": 1,
      "tool": "bash",
      "error": "expected { in format string"
    }
  ],
  "success": false
}"""
    p = tmp_path / "corpus.jsonl"
    with p.open("w", encoding="utf-8") as f:
        f.write(dump_trajectory(_valid_trajectory()) + "\n")
        f.write(multi + "\n")
    loaded = list(load_trajectories(p))
    assert len(loaded) == 2
    assert loaded[1].id == "T-brace"
