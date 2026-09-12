"""Tests for ``cauterule benchmark`` CLI (#606). Subprocess mocked."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from cauterule.cli.app import main


@pytest.fixture
def bench_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    benchmarks = tmp_path / "benchmarks"
    benchmarks.mkdir()
    (benchmarks / "test_replay_matcher.py").write_text("def test_x(): pass\n")
    (benchmarks / "test_extraction.py").write_text("def test_y(): pass\n")
    return tmp_path


class TestBenchmarkCli:
    def test_help(self, bench_dir: Path) -> None:
        result = CliRunner().invoke(main, ["benchmark", "--help"])
        assert result.exit_code == 0
        assert "run" in result.output and "list" in result.output

    def test_list(self, bench_dir: Path) -> None:
        result = CliRunner().invoke(main, ["benchmark", "list"])
        assert result.exit_code == 0, result.output
        assert "replay_matcher" in result.output
        assert "extraction" in result.output

    def test_list_leaderboard_format(self, bench_dir: Path) -> None:
        result = CliRunner().invoke(main, ["benchmark", "list", "--format", "leaderboard"])
        assert result.exit_code == 0, result.output
        assert "replay_matcher" in result.output
        assert "|" in result.output

    def test_list_empty(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        result = CliRunner().invoke(main, ["benchmark", "list"])
        assert "No benchmarks found" in result.output

    def test_run_single(self, bench_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        import subprocess

        calls: list[list[str]] = []

        class _Done:
            returncode = 0
            stdout = "1 passed\n"
            stderr = ""

        def _fake(cmd: list[str], **kwargs: object) -> _Done:
            calls.append(cmd)
            return _Done()

        monkeypatch.setattr(subprocess, "run", _fake)
        result = CliRunner().invoke(main, ["benchmark", "run", "extraction"])
        assert result.exit_code == 0, result.output
        assert any("test_extraction.py" in c for c in calls[0])

    def test_run_unknown(self, bench_dir: Path) -> None:
        result = CliRunner().invoke(main, ["benchmark", "run", "nope"])
        assert result.exit_code != 0
        assert "unknown benchmark" in result.output
