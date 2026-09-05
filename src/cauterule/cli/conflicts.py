from __future__ import annotations

import click

from cauterule.store.manager import StoreManager
from cauterule.serialization.rule_yaml import load_rules_from_dir
from cauterule.conflict import detect_contradictions, detect_overlaps


@click.command("conflicts")
def conflicts() -> None:
    """List detected conflicts between active rules."""
    rules = load_rules_from_dir("rules")
    if not rules:
        click.echo("No rules found in store.")
        return
    contradictions = detect_contradictions(rules)
    overlaps = detect_overlaps(rules)
    if not contradictions and not overlaps:
        click.echo("No conflicts detected.")
        return
    for c in contradictions:
        click.echo(f"CONTRADICTION: {c.rules[0]} vs {c.rules[1]} — {c.resolution}")
    for o in overlaps:
        click.echo(f"OVERLAP: {o.rules[0]} vs {o.rules[1]} — {o.resolution}")