from __future__ import annotations

import click


@click.command("config")
@click.option("--show", is_flag=True, help="Show current configuration.")
@click.option("--set", "set_key", help="Set a config key (key=value).")
def config(show: bool, set_key: str | None) -> None:
    """View or edit CauterRule configuration."""
    click.echo(f"config: show={show}, set={set_key}")
