from __future__ import annotations

import click


@click.command("promote")
@click.argument("rule")
def promote(rule: str) -> None:
    """Promote a tested rule to the active rule store."""
    click.echo(f"promote: promoting rule {rule}")
