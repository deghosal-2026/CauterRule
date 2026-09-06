from __future__ import annotations

import click

from cauterule.store.manager import StoreManager
from cauterule.injection.matcher import match_rules


@click.command("inject")
@click.argument("task")
@click.option("--preflight", is_flag=True, help="Dry-run: show rules without injecting.")
def inject(task: str, preflight: bool) -> None:
    """Inject relevant rules into a task context."""
    store = StoreManager()
    rules = store.list_rules(status="active")
    matched = match_rules(task, rules)
    if not matched:
        click.echo("No matching rules found.")
        return
    click.echo(f"Found {len(matched)} matching rule(s):")
    for r in matched:
        click.echo(f"  {r.id}: when \"{r.when.trigger}\" → {r.do.directive}")
    if not preflight:
        click.echo("[injection not yet implemented]")