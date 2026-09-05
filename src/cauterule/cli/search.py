from __future__ import annotations

import click


@click.command("search")
@click.argument("query")
def search(query: str) -> None:
    """Full-text search across rules."""
    click.echo(f"search: querying for {query}")
