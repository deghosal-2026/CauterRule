"""Tests for ``cauterule corpus`` CLI (#606)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from cauterule.cli.app import main

GOOD = {
    "trajectory_id": "T-1",
    "timestamp": "2026-09-01T00:00:00Z",
    "task": "do thing",
    "steps": [{"step_number": 1, "tool": "git", "input": "x", "output": "", "error": "boom"}],
    "success": False,
    "failure_class": "git/push",
    "quality_label": "clear",
    "domain": "git",
}


@pytest.fixture
def workspace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    return tmp_path


class TestCorpusCli:
    def test_help_lists_subcommands(self, workspace: Path) -> None:
        result = CliRunner().invoke(main, ["corpus", "--help"])
        assert result.exit_code == 0
        for sub in ("add", "list", "validate", "lint", "build", "export"):
            assert sub in result.output

    def test_add_list_export_round_trip(self, workspace: Path) -> None:
        src = workspace / "in.jsonl"
        src.write_text(json.dumps(GOOD) + "\n", encoding="utf-8")
        runner = CliRunner()
        result = runner.invoke(main, ["corpus", "add", str(src), "--domain", "git"])
        assert result.exit_code == 0, result.output
        assert "Ingested 1 trajectories" in result.output
        result = runner.invoke(main, ["corpus", "list", "--domain", "git"])
        assert "in.jsonl" in result.output
        result = runner.invoke(main, ["corpus", "export", "--format", "jsonl", "--domain", "git"])
        assert result.exit_code == 0
        assert "T-1" in result.output

    def test_validate_rejects_malformed(self, workspace: Path) -> None:
        bad = workspace / "corpus" / "public" / "git" / "bad.jsonl"
        bad.parent.mkdir(parents=True)
        bad.write_text("{not json}\n", encoding="utf-8")
        result = CliRunner().invoke(main, ["corpus", "validate", str(bad)])
        assert result.exit_code != 0
        assert "FAIL" in result.output

    def test_lint_flags_missing_provenance(self, workspace: Path) -> None:
        thin = dict(GOOD)
        del thin["failure_class"]
        path = workspace / "corpus" / "public" / "git" / "thin.jsonl"
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps(thin) + "\n", encoding="utf-8")
        result = CliRunner().invoke(main, ["corpus", "lint", str(path)])
        assert result.exit_code == 0
        assert "missing failure_class" in result.output

    def test_build_consolidates(self, workspace: Path) -> None:
        src = workspace / "in.jsonl"
        src.write_text(json.dumps(GOOD) + "\n", encoding="utf-8")
        runner = CliRunner()
        runner.invoke(main, ["corpus", "add", str(src), "--domain", "git"])
        result = runner.invoke(main, ["corpus", "build"])
        assert result.exit_code == 0, result.output
        assert (workspace / "corpus" / "store.jsonl").is_file()

    def test_export_csv(self, workspace: Path) -> None:
        src = workspace / "in.jsonl"
        src.write_text(json.dumps(GOOD) + "\n", encoding="utf-8")
        runner = CliRunner()
        runner.invoke(main, ["corpus", "add", str(src), "--domain", "git"])
        result = runner.invoke(main, ["corpus", "export", "--format", "csv", "--domain", "git"])
        assert result.exit_code == 0
        assert "trajectory_id" in result.output
