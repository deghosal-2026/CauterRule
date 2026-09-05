from __future__ import annotations

import click


@click.command("list")
@click.option("--status", help="Filter by status (active/retired/draft).")
@click.option("--tag", help="Filter by tag.")
def list_rules(status: str | None, tag: str | None) -> None:
    """List rules as a table with id, trigger, status, hits, tags."""
    click.echo(f"list: listing rules (status={status}, tag={tag})")
