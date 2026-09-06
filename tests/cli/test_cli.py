from __future__ import annotations

import os
import tempfile
from pathlib import Path

from click.testing import CliRunner

from cauterule.cli.app import main


def test_cli_help() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "CauterRule" in result.output


def test_cli_verbose_flag() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["--verbose"])
    assert result.exit_code == 0


def test_cli_no_args() -> None:
    runner = CliRunner()
    result = runner.invoke(main, [])
    assert result.exit_code == 0


def test_cli_init() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        runner = CliRunner()
        result = runner.invoke(main, ["init", "--dir", tmp])
        assert result.exit_code == 0
        assert "Scaffolded" in result.output
        assert (Path(tmp) / "cauterule.toml").is_file()
        assert (Path(tmp) / "rules").is_dir()
        assert (Path(tmp) / "trajectories").is_dir()


def test_cli_demo() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["demo", "--failures", "3"])
    assert result.exit_code == 0
    assert "Seeded" in result.output
    assert "Extraction phase" in result.output


def test_cli_extract_dry_run() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        traj_path = Path(tmp) / "traj.json"
        traj_path.write_text(
            '{"id": "T-1", "timestamp": "2024-01-01T00:00:00Z", "task": "deploy to prod", "steps": [{"step_number": 1, "tool": "deploy", "input": "deploy", "output": "", "error": "ENV not set"}], "success": false}',
            encoding="utf-8",
        )
        cwd = os.getcwd()
        try:
            os.chdir(tmp)
            runner = CliRunner()
            result = runner.invoke(main, ["extract", str(traj_path), "--dry-run"])
            assert result.exit_code == 0
            assert "dry-run" in result.output
        finally:
            os.chdir(cwd)


def test_cli_validate_empty_store() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "rules").mkdir(parents=True, exist_ok=True)
        cwd = os.getcwd()
        try:
            os.chdir(tmp)
            runner = CliRunner()
            result = runner.invoke(main, ["validate"])
            assert result.exit_code == 0
        finally:
            os.chdir(cwd)


def test_cli_health_empty_store() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "rules").mkdir(parents=True, exist_ok=True)
        cwd = os.getcwd()
        try:
            os.chdir(tmp)
            runner = CliRunner()
            result = runner.invoke(main, ["health"])
            assert result.exit_code == 0
            assert "Total rules" in result.output
        finally:
            os.chdir(cwd)


def test_cli_metrics() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["metrics"])
    assert result.exit_code == 0
    assert result.output


def test_cli_list() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["list"])
    assert result.exit_code == 0


def test_cli_search() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["search", "deployment"])
    assert result.exit_code == 0


def test_cli_show_not_found() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["show", "R-999"])
    assert result.exit_code == 0
    assert "not found" in result.output


def test_cli_explain_not_found() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["explain", "R-999"])
    assert result.exit_code == 0
    assert "not found" in result.output


def test_cli_audit_not_found() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["audit", "R-999"])
    assert result.exit_code == 0
    assert "not found" in result.output


def test_cli_diff_not_found() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["diff", "R-999"])
    assert result.exit_code == 0


def test_cli_retire_not_found() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["retire", "R-999"])
    assert result.exit_code != 0 or "Error" in result.output or "not found" in result.output


def test_cli_config_show() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["config", "--show"])
    assert result.exit_code == 0


def test_cli_pack_list() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["pack", "list"])
    assert result.exit_code == 0


def test_cli_report() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["report"])
    assert result.exit_code == 0
    assert "CauterRule Report" in result.output


def test_cli_story() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["story"])
    assert result.exit_code == 0
    assert "CauterRule Learning Journey" in result.output


def test_cli_counterfactual() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["counterfactual"])
    assert result.exit_code == 0


def test_cli_history() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "rules").mkdir(parents=True, exist_ok=True)
        cwd = os.getcwd()
        try:
            os.chdir(tmp)
            runner = CliRunner()
            result = runner.invoke(main, ["history"])
            assert result.exit_code == 0
        finally:
            os.chdir(cwd)


def test_cli_inject() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["inject", "deploy"])
    assert result.exit_code == 0


def test_cli_inject_preflight() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["inject", "deploy", "--preflight"])
    assert result.exit_code == 0


def test_cli_unknown_command() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["nonesuch"])
    assert result.exit_code != 0
    assert "Error" in result.output