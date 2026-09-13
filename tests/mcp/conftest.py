"""MCP docker conftest — shares the live docker-results recorder.

The field conftest lives under tests/field/ and only sees tests under that dir.
This sibling ensures the docker tests in tests/mcp/test_docker_http_transport.py
are also captured in ``field-test/results/0.3.1/docker/`` (#738).
"""

from __future__ import annotations

from typing import Any

import pytest

from tests import _docker_results as results


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[None]) -> object:
    outcome: Any = yield
    rep: pytest.TestReport = outcome.get_result()
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
