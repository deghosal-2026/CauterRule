from __future__ import annotations

import click

from cauterule.store.manager import StoreManager


@click.command("audit")
@click.argument("rule_id")
def audit(rule_id: str) -> None:
    """Show full provenance trail for a rule."""
    store = StoreManager()
    rule = store.get_rule(rule_id)
    if rule is None:
        click.echo(f"Rule {rule_id!r} not found.")
        return
    prov = rule.provenance
    click.echo(f"Rule: {rule.id}")
    click.echo(f"  Status: {rule.status}")
    click.echo(f"  Source trajectory: {prov.source_trajectory}")
    click.echo(f"  Extracted by: {prov.extracted_by}")
    click.echo(f"  Extract timestamp: {prov.extract_timestamp}")
    click.echo(f"  Extraction pass: {prov.extraction_pass}")
    click.echo(f"  Promotion commit: {prov.promotion_commit}")
    click.echo(f"  Promotion mode: {prov.promotion_mode}")
    if prov.draft_tournament_rank is not None:
        click.echo(f"  Tournament rank: {prov.draft_tournament_rank}")