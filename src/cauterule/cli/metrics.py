from __future__ import annotations

import click

from cauterule.store.health import health_report


@click.command("metrics")
def metrics() -> None:
    """CLI summary: rules, precision, repeat-failure rate, store size."""
    report = health_report()
    click.echo(f"Total rules: {report['total_rules']}")
    click.echo(f"By status: {report['by_status']}")
    click.echo(f"Avg confidence: {report['avg_confidence']}")
    click.echo(f"Avg effectiveness: {report['avg_effectiveness']}")
    if report['stale_rules']:
        click.echo(f"Stale rules ({len(report['stale_rules'])}): {', '.join(report['stale_rules'])}")