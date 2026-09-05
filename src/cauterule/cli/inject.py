from __future__ import annotations

import click


@click.command("inject")
@click.argument("task")
@click.option("--preflight", is_flag=True, help="Dry-run: show rules without injecting.")
def inject(task: str, preflight: bool) -> None:
    """Inject relevant rules into a task context."""
    click.echo(f"inject: checking rules for task {task} (preflight={preflight})")
