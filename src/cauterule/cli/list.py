from __future__ import annotations

import click

from cauterule.store.manager import StoreManager


@click.command("list")
@click.option("--status", help="Filter by status (active/retired/draft).")
@click.option("--tag", help="Filter by tag.")
def list_rules(status: str | None, tag: str | None) -> None:
    """List rules as a table with id, trigger, status, hits, tags."""
    store = StoreManager()
    rules = store.list_rules(status=status)
    if tag:
        rules = [r for r in rules if tag in [t.lower() for t in r.tags]]
    if not rules:
        click.echo("No rules found.")
        return
    for r in rules:
        tags = ",".join(r.tags) if r.tags else "-"
        click.echo(f"  {r.id:8s} {r.status:12s} hits={r.hit_count:3d} conf={r.confidence:.2f} tags=[{tags}] trigger=\"{r.when.trigger}\"")