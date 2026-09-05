from __future__ import annotations

import click

from cauterule.store.health import health_report


@click.command("health")
def health() -> None:
    """Rule store health report."""
    report = health_report()
    click.echo(f"Total rules: {report['total_rules']}")
    click.echo(f"By status: {report['by_status']}")
    click.echo(f"Avg confidence: {report['avg_confidence']}")
    click.echo(f"Avg effectiveness: {report['avg_effectiveness']}")
    click.echo(f"Conflict count: {report['conflict_count']}")
    if report['stale_rules']:
        click.echo(f"Stale rules: {', '.join(report['stale_rules'])}")