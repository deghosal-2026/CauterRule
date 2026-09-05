from __future__ import annotations

import click


@click.command("counterfactual")
@click.option("--days", default=7, help="Lookback window in days.")
def counterfactual(days: int) -> None:
    """Show failures that would have been avoided with current rules."""
    click.echo(f"counterfactual: analyzing last {days} days")
