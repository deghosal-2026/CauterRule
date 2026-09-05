from __future__ import annotations

import click


@click.command("init")
@click.option("--dir", default=".", help="Target directory for scaffolding.")
def init(dir: str) -> None:
    """Scaffold cauterule.toml, rules/, .gitignore, example agent, and first rule."""
    click.echo(f"init: scaffold CauterRule project in {dir}")
