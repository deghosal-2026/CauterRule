from __future__ import annotations

import click

from cauterule.cli.journal import journal
from cauterule.cli.metrics import metrics


@click.group("observe")
def observe() -> None:
    """Observability metrics and learning journal."""


observe.add_command(metrics)
observe.add_command(journal)
