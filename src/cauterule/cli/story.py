from __future__ import annotations

import click


@click.command("story")
@click.option("--format", "fmt", default="markdown", help="Output format (markdown/html).")
def story(fmt: str) -> None:
    """Generate a narrative blog post of the learning journey."""
    click.echo(f"story: generating {fmt} narrative")
