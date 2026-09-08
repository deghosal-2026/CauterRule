from __future__ import annotations

import click

from cauterule.store.manager import StoreManager


@click.command("promote")
@click.argument("rule")
@click.option(
    "--force",
    "force_promote",
    is_flag=True,
    help="Force promotion despite safety warnings (audit logged).",
)
def promote(rule: str, force_promote: bool) -> None:
    """Promote a tested rule to the active rule store."""
    if force_promote:
        click.echo("WARNING: --force: safety warnings will be overridden (audit logged).")
    store = StoreManager()
    candidate = store.get_rule(rule) if rule.startswith("R-") else None
    if candidate:
        click.echo(f"Cannot promote already-promoted rule {rule}. Use a candidate.")
        return
    click.echo(f"promote: promoting rule {rule}")
    click.echo("(candidate loading from draft store not yet implemented)")
