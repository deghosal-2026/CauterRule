"""Field-test conftest — live docker results to field-test/results/0.3.1/docker/.

Every ``@pytest.mark.docker`` test outcome is appended to
``field-test/results/0.3.1/docker/docker-results.jsonl`` as it finishes (watch it
with ``tail -f``), and a markdown summary is written at session end. Override the
destination with ``CAUTERULE_FT_RESULTS_DIR``.
"""

from __future__ import annotations

from typing import Any

import pytest

from tests import _docker_results as results


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[None]) -> object:
    outcome: Any = yield
    rep: pytest.TestReport = outcome.get_result()
    # Authoritative outcome: the 'call' phase for pass/fail, or a setup-phase skip.
    if rep.when == "call" or (rep.when == "setup" and rep.outcome == "skipped"):
        results.record(item, rep)


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    results.write_summary(exitstatus)


def pytest_terminal_summary(
    terminalreporter: pytest.TerminalReporter, config: pytest.Config
) -> None:
    terminalreporter.write_line(
        f"docker results -> {results.RESULTS_JSONL} ({results.RESULTS_MD})"
    )
