from pathlib import Path

import pytest

from cauterule.adapter.decorator import watch


def test_watch_success(tmp_path: Path) -> None:
    @watch(base_dir=str(tmp_path))
    def my_agent(x: int) -> int:
        return x * 2

    result = my_agent(21)
    assert result == 42
    # should have written one trajectory
    files = list((tmp_path).rglob("*.jsonl"))
    assert len(files) == 1
    content = files[0].read_text()
    assert "my_agent" in content
    assert "success" in files[0].name


def test_watch_failure(tmp_path: Path) -> None:
    @watch(base_dir=str(tmp_path))
    def failing_agent() -> None:
        raise ValueError("boom")

    with pytest.raises(ValueError, match="boom"):
        failing_agent()
    files = list(tmp_path.rglob("*.jsonl"))
    assert len(files) == 1
    assert "failure" in files[0].name
    assert "boom" in files[0].read_text()


def test_watch_capture_success_false(tmp_path: Path) -> None:
    @watch(base_dir=str(tmp_path), capture_success=False)
    def my_agent() -> int:
        return 1

    result = my_agent()
    assert result == 1
    files = list(tmp_path.rglob("*.jsonl"))
    assert len(files) == 0

    @watch(capture_success=False, base_dir=str(tmp_path))
    def failing() -> None:
        raise RuntimeError("fail")

    with pytest.raises(RuntimeError):
        failing()
    files = list(tmp_path.rglob("*.jsonl"))
    assert len(files) == 1


def test_watch_without_call_parens(tmp_path: Path) -> None:
    # Use as @watch without parentheses — base_dir defaults to trajectories
    # We test the decorator factory handles callable correctly, but avoid writing to real dir
    # So we patch by using tmp_path via direct decorator
    @watch
    def simple() -> int:
        return 5

    # simple should be wrapped; calling it will try to write to "trajectories"
    # we don't call it to avoid file creation, just check it's callable
    assert callable(simple)
    # Also test @watch(base_dir=...) returns decorator
    dec = watch(base_dir=str(tmp_path))
    assert callable(dec)

    @dec
    def another() -> int:
        return 6

    assert another() == 6
    files = list(tmp_path.rglob("*.jsonl"))
    assert len(files) == 1
