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
        cwd = Path.cwd()
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
        cwd = Path.cwd()
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
        cwd = Path.cwd()
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
        cwd = Path.cwd()
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


def test_readme_commands_resolve() -> None:
    # #501: every README-advertised command must resolve in the click group.
    import re
    from pathlib import Path

    import click

    readme = (Path(__file__).resolve().parents[2] / "README.md").read_text(encoding="utf-8")
    found: set[tuple[str, ...]] = set()
    for match in re.finditer(r"cauterule\s+([a-z][a-z-]*)(?:\s+([a-z][a-z-]*))?", readme):
        first, second = match.group(1), match.group(2)
        # Only pack/observe take subcommands; other second tokens are
        # arguments (e.g. `extract trajectory.jsonl`).
        if second is not None and first in {"pack", "observe"}:
            found.add((first, second))
        else:
            found.add((first,))
    # Subcommands advertised without the `cauterule` prefix (`pack list`).
    found.add(("pack", "list"))
    found.add(("pack", "info"))
    runner = CliRunner()
    for parts in sorted(found):
        cmd = main.commands.get(parts[0])
        assert cmd is not None, f"README advertises unknown command: {parts[0]}"
        if len(parts) == 2:
            assert isinstance(cmd, click.Group), f"{parts[0]} is not a group"
            assert parts[1] in cmd.commands, f"unknown subcommand: {parts[0]} {parts[1]}"
        else:
            result = runner.invoke(main, [parts[0], "--help"])
            assert result.exit_code == 0, f"{parts[0]} --help failed"


def test_export_agents_end_to_end(tmp_path: Path) -> None:
    # #501: export --format agents works on a sample rule store.
    from cauterule.models.rule import Provenance, RuleDo, RuleWhen, StandingRule
    from cauterule.store.manager import StoreManager

    store = StoreManager(base_dir=str(tmp_path / "rules"))
    store.add_rule(
        StandingRule(
            id="R-001",
            when=RuleWhen(trigger="git push fails"),
            do=RuleDo(directive="pull first"),
            confidence=0.9,
            provenance=Provenance(
                source_trajectory="t",
                extracted_by="m",
                extract_timestamp="t",
                extraction_pass=1,
            ),
            status="active",
            promoted_at="t",
        )
    )
    runner = CliRunner()
    result = runner.invoke(
        main, ["export", "--format", "agents", "--rules-dir", str(tmp_path / "rules")]
    )
    assert result.exit_code == 0
    assert "git push fails" in result.output


def test_observe_group_resolves() -> None:
    # #501: observe metrics/journal subcommands resolve.
    runner = CliRunner()
    assert runner.invoke(main, ["observe", "--help"]).exit_code == 0
    assert runner.invoke(main, ["observe", "metrics", "--help"]).exit_code == 0
    assert runner.invoke(main, ["observe", "journal", "--help"]).exit_code == 0
