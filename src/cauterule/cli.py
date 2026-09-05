"""Minimal CLI stub for CauterRule.

Full CLI (25+ commands) lands in M20-M22. This stub satisfies the
``cauterule`` entry point declared in ``pyproject.toml`` so that
``pip install -e .`` produces a working console script from M1 onward.
"""

from __future__ import annotations

import click

from cauterule.log import get_logger, setup_logging

log = get_logger(__name__)


@click.group(invoke_without_command=True)
@click.option("--verbose", is_flag=True, help="Enable debug logging.")
def main(verbose: bool) -> None:
    """CauterRule — automated standing-rule extraction from agent failures."""
    setup_logging(level="DEBUG" if verbose else "INFO")
    log.debug("cauterule cli invoked", extra={"verbose": verbose})


if __name__ == "__main__":  # pragma: no cover
    main()  # pragma: no cover
