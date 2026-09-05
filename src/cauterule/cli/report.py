from __future__ import annotations

import click


@click.command("report")
@click.option("--format", "fmt", default="markdown", help="Output format (markdown/html/pdf).")
@click.option("--output", "-o", help="Output file path.")
def report(fmt: str, output: str | None) -> None:
    """Generate a markdown report for sharing."""
    click.echo(f"report: generating {fmt} report (output={output})")
