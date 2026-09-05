from __future__ import annotations

import click


@click.command("retire")
@click.argument("rule_id")
@click.option("--reason", default="", help="Reason for retirement.")
def retire(rule_id: str, reason: str) -> None:
    """Retire a rule with an optional reason."""
    click.echo(f"retire: retiring rule {rule_id} (reason={reason})")
