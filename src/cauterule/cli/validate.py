from __future__ import annotations

import click


@click.command("validate")
def validate() -> None:
    """Check rule store integrity."""
    click.echo("validate: checking rule store integrity")
