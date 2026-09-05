from __future__ import annotations

import click


@click.command("review")
def review() -> None:
    """Launch the TUI review interface (Textual)."""
    from cauterule.tui.app import CauterRuleApp

    app = CauterRuleApp()
    app.run()