from __future__ import annotations

import click

from cauterule.cli.audit import audit
from cauterule.cli.config import config
from cauterule.cli.conflicts import conflicts
from cauterule.cli.counterfactual import counterfactual
from cauterule.cli.demo import demo
from cauterule.cli.diff import diff
from cauterule.cli.explain import explain
from cauterule.cli.extract import extract
from cauterule.cli.health import health
from cauterule.cli.history import history
from cauterule.cli.init import init
from cauterule.cli.inject import inject
from cauterule.cli.list import list_rules
from cauterule.cli.metrics import metrics
from cauterule.cli.pack import pack
from cauterule.cli.promote import promote
from cauterule.cli.report import report
from cauterule.cli.retire import retire
from cauterule.cli.search import search
from cauterule.cli.show import show
from cauterule.cli.story import story
from cauterule.cli.test import test
from cauterule.cli.validate import validate
from cauterule.log import get_logger, setup_logging

log = get_logger(__name__)


@click.group(invoke_without_command=True)
@click.option("--verbose", is_flag=True, help="Enable debug logging.")
def main(verbose: bool) -> None:
    """CauterRule — automated standing-rule extraction from agent failures."""
    setup_logging(level="DEBUG" if verbose else "INFO")
    log.debug("cauterule cli invoked", extra={"verbose": verbose})


main.add_command(audit)
main.add_command(config)
main.add_command(conflicts)
main.add_command(counterfactual)
main.add_command(demo)
main.add_command(diff)
main.add_command(explain)
main.add_command(extract)
main.add_command(health)
main.add_command(history)
main.add_command(init)
main.add_command(inject)
main.add_command(list_rules)
main.add_command(metrics)
main.add_command(pack)
main.add_command(promote)
main.add_command(report)
main.add_command(retire)
main.add_command(search)
main.add_command(show)
main.add_command(story)
main.add_command(test)
main.add_command(validate)
