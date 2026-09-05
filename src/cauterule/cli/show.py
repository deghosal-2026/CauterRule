from __future__ import annotations

import click


@click.command("show")
@click.argument("rule_id")
def show(rule_id: str) -> None:
    """Show full provenance view of a rule."""
    click.echo(f"show: displaying rule {rule_id}")
