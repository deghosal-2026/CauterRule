from __future__ import annotations

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
    runner = CliRunner()
    result = runner.invoke(main, ["init"])
    assert result.exit_code == 0
    assert "init" in result.output


def test_cli_demo() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["demo"])
    assert result.exit_code == 0
    assert "demo" in result.output


def test_cli_extract() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["extract", "traj.json"])
    assert result.exit_code == 0
    assert "extract" in result.output


def test_cli_extract_dry_run() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["extract", "traj.json", "--dry-run"])
    assert result.exit_code == 0
    assert "dry_run=True" in result.output


def test_cli_test() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["test", "R-001"])
    assert result.exit_code == 0
    assert "test" in result.output


def test_cli_test_ci() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["test", "R-001", "--ci"])
    assert result.exit_code == 0
    assert "ci=True" in result.output


def test_cli_promote() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["promote", "R-001"])
    assert result.exit_code == 0
    assert "promote" in result.output


def test_cli_inject() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["inject", "deploy"])
    assert result.exit_code == 0
    assert "inject" in result.output


def test_cli_inject_preflight() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["inject", "deploy", "--preflight"])
    assert result.exit_code == 0
    assert "preflight=True" in result.output


def test_cli_list() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["list"])
    assert result.exit_code == 0
    assert "list" in result.output


def test_cli_list_filters() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["list", "--status", "active", "--tag", "python"])
    assert result.exit_code == 0
    assert "list" in result.output


def test_cli_show() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["show", "R-001"])
    assert result.exit_code == 0
    assert "show" in result.output


def test_cli_search() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["search", "deployment"])
    assert result.exit_code == 0
    assert "search" in result.output


def test_cli_audit() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["audit", "R-001"])
    assert result.exit_code == 0
    assert "audit" in result.output


def test_cli_diff() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["diff", "R-001"])
    assert result.exit_code == 0
    assert "diff" in result.output


def test_cli_retire() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["retire", "R-001"])
    assert result.exit_code == 0
    assert "retire" in result.output


def test_cli_retire_with_reason() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["retire", "R-001", "--reason", "superseded"])
    assert result.exit_code == 0
    assert "superseded" in result.output


def test_cli_history() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["history"])
    assert result.exit_code == 0
    assert "history" in result.output


def test_cli_history_limit() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["history", "--limit", "10"])
    assert result.exit_code == 0
    assert "10" in result.output


def test_cli_conflicts() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["conflicts"])
    assert result.exit_code == 0
    assert "conflicts" in result.output


def test_cli_validate() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["validate"])
    assert result.exit_code == 0
    assert "validate" in result.output


def test_cli_health() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["health"])
    assert result.exit_code == 0
    assert "health" in result.output


def test_cli_counterfactual() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["counterfactual"])
    assert result.exit_code == 0
    assert "counterfactual" in result.output


def test_cli_story() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["story"])
    assert result.exit_code == 0
    assert "story" in result.output


def test_cli_story_format() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["story", "--format", "html"])
    assert result.exit_code == 0
    assert "html" in result.output


def test_cli_explain() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["explain", "R-001"])
    assert result.exit_code == 0
    assert "explain" in result.output


def test_cli_config_show() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["config", "--show"])
    assert result.exit_code == 0
    assert "config" in result.output


def test_cli_pack_list() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["pack", "list"])
    assert result.exit_code == 0
    assert "pack list" in result.output


def test_cli_pack_info() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["pack", "info", "core"])
    assert result.exit_code == 0
    assert "pack info" in result.output


def test_cli_metrics() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["metrics"])
    assert result.exit_code == 0
    assert "metrics" in result.output


def test_cli_report() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["report"])
    assert result.exit_code == 0
    assert "report" in result.output


def test_cli_report_with_output() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["report", "--format", "html", "-o", "report.html"])
    assert result.exit_code == 0
    assert "html" in result.output


def test_cli_unknown_command() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["nonesuch"])
    assert result.exit_code != 0
    assert "Error" in result.output
