from __future__ import annotations

import click


@click.command("test")
@click.argument("rule")
@click.option("--ci", is_flag=True, help="Output JUnit XML.")
def test(rule: str, ci: bool) -> None:
    """Replay-test a candidate rule against historical failures."""
    click.echo(f"test: replay-testing rule {rule} (ci={ci})")
