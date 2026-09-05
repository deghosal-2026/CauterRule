from __future__ import annotations

import click

from cauterule.store.manager import StoreManager
from cauterule.config import load_config
from cauterule.promotion.executor import execute_promotion


@click.command("promote")
@click.argument("rule")
def promote(rule: str) -> None:
    """Promote a tested rule to the active rule store."""
    store = StoreManager()
    candidate = store.get_rule(rule) if rule.startswith("R-") else None
    if candidate:
        click.echo(f"Cannot promote already-promoted rule {rule}. Use a candidate.")
        return
    click.echo(f"promote: promoting rule {rule}")
    click.echo("(candidate loading from draft store not yet implemented)")