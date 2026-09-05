from click.testing import CliRunner

from cauterule.cli import main


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
    # Group with no subcommand — should invoke callback and exit 0.
    assert result.exit_code == 0
