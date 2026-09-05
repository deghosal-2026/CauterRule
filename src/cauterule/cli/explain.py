from __future__ import annotations

import click


@click.command("explain")
@click.argument("rule_id")
def explain(rule_id: str) -> None:
    """LLM explains why a rule fires."""
    click.echo(f"explain: generating explanation for rule {rule_id}")
