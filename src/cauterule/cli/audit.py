from __future__ import annotations

import click


@click.command("audit")
@click.argument("rule_id")
def audit(rule_id: str) -> None:
    """Show full provenance trail for a rule."""
    click.echo(f"audit: provenance trail for rule {rule_id}")
