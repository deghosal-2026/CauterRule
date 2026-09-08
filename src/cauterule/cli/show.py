from __future__ import annotations

import click

from cauterule.store.manager import StoreManager


@click.command("show")
@click.argument("rule_id")
@click.option("--hits", is_flag=True, help="Show hit count and last match")
def show(rule_id: str, hits: bool) -> None:
    """Show full provenance view of a rule."""
    store = StoreManager()
    rule = store.get_rule(rule_id)
    if rule is None:
        click.echo(f"Rule {rule_id!r} not found.")
        return
    click.echo(f"ID: {rule.id}")
    click.echo(f"When: {rule.when.trigger}")
    if rule.when.context:
        click.echo(f"  Context: {', '.join(rule.when.context)}")
    click.echo(f"Do: {rule.do.directive}")
    if rule.do.because:
        click.echo(f"  Because: {rule.do.because}")
    click.echo(f"Confidence: {rule.confidence:.2f}")
    click.echo(f"Status: {rule.status}")
    click.echo(f"Promoted at: {rule.promoted_at}")
    click.echo(f"Hit count: {rule.hit_count}")
    if rule.last_match:
        click.echo(f"Last match: {rule.last_match}")
    elif hits:
        click.echo("Last match: never")
    click.echo(f"Tags: {', '.join(rule.tags) if rule.tags else 'none'}")
    if rule.taxonomy:
        click.echo(f"Taxonomy: {rule.taxonomy}")
    if rule.provenance.replay_evidence:
        ev = rule.provenance.replay_evidence
        click.echo(f"Failures prevented: {len(ev.failures_prevented)}")
        click.echo(f"Successes broken: {len(ev.successes_broken)}")
