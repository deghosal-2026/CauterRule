from __future__ import annotations

import click


@click.command("history")
@click.option("--limit", default=20, help="Number of entries to show.")
def history(limit: int) -> None:
    """Timeline of promotions and retirements."""
    click.echo(f"history: showing last {limit} events")
