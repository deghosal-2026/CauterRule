from __future__ import annotations

import click


@click.command("demo")
@click.option("--failures", default=5, help="Number of seeded failures.")
def demo(failures: int) -> None:
    """Seeded failure history with a full narrated loop walkthrough."""
    click.echo(f"demo: walkthrough with {failures} seeded failures")
