from __future__ import annotations

import click
from pathlib import Path

from cauterule.store.health import health_report


@click.command("report")
@click.option("--format", "fmt", default="markdown", help="Output format (markdown/html/pdf).")
@click.option("--output", "-o", help="Output file path.")
def report(fmt: str, output: str | None) -> None:
    """Generate a markdown report for sharing."""
    report_data = health_report()
    lines = [
        "# CauterRule Report",
        "",
        f"- **Total rules**: {report_data['total_rules']}",
        f"- **By status**: {report_data['by_status']}",
        f"- **Avg confidence**: {report_data['avg_confidence']}",
        f"- **Avg effectiveness**: {report_data['avg_effectiveness']}",
        f"- **Conflict count**: {report_data['conflict_count']}",
        "",
    ]
    if report_data['stale_rules']:
        lines.append(f"**Stale rules**: {', '.join(report_data['stale_rules'])}")

    body = "\n".join(lines)
    if output:
        Path(output).write_text(body, encoding="utf-8")
        click.echo(f"Report written to {output}")
    else:
        click.echo(body)