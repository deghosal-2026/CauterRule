from __future__ import annotations

import click


@click.command("health")
def health() -> None:
    """Rule store health report."""
    click.echo("health: generating health report")
