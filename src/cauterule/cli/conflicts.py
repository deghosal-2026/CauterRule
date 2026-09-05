from __future__ import annotations

import click


@click.command("conflicts")
def conflicts() -> None:
    """List detected conflicts between active rules."""
    click.echo("conflicts: scanning for rule conflicts")
