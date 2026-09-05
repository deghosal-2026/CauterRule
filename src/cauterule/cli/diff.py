from __future__ import annotations

import click


@click.command("diff")
@click.argument("rule_id")
def diff(rule_id: str) -> None:
    """Show changes between rule versions."""
    click.echo(f"diff: showing version history for rule {rule_id}")
