from __future__ import annotations

import click

from cauterule.store.manager import StoreManager
from cauterule.serialization.rule_yaml import load_rules_from_dir


@click.group("pack")
def pack() -> None:
    """Manage rule packs."""


@pack.command("list")
def pack_list() -> None:
    """List available rule packs."""
    from pathlib import Path
    packs_dir = Path("rules")
    if not packs_dir.is_dir():
        click.echo("No packs directory found.")
        return
    click.echo("Available rule packs:")
    click.echo("  core: Core rules")


@pack.command("info")
@click.argument("name")
def pack_info(name: str) -> None:
    """Show information about a rule pack."""
    rules = load_rules_from_dir("rules")
    pack_rules = [r for r in rules if r.pack == name]
    click.echo(f"Pack: {name}")
    click.echo(f"Rules: {len(pack_rules)}")
    for r in pack_rules:
        click.echo(f"  {r.id}: {r.when.trigger}")