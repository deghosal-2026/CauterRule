from __future__ import annotations

import click


@click.command("metrics")
def metrics() -> None:
    """CLI summary: rules, precision, repeat-failure rate, store size."""
    click.echo("metrics: generating summary")
