from __future__ import annotations

import click


@click.group("pack")
def pack() -> None:
    """Manage rule packs."""


@pack.command("list")
def pack_list() -> None:
    """List available rule packs."""
    click.echo("pack list: available packs")


@pack.command("info")
@click.argument("name")
def pack_info(name: str) -> None:
    """Show information about a rule pack."""
    click.echo(f"pack info: {name}")
