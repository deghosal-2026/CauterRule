from __future__ import annotations

import click


@click.command("extract")
@click.argument("trajectory")
@click.option("--dry-run", is_flag=True, help="Show candidates without persisting.")
def extract(trajectory: str, dry_run: bool) -> None:
    """Extract candidate rules from a failure trajectory."""
    click.echo(f"extract: processing trajectory {trajectory} (dry_run={dry_run})")
