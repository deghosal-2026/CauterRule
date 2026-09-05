"""Field-level tests for the MCP tool surface.

These tests exercise the MCP tool functions (``get_matching_rules``,
``get_rule``, ``list_rules``, ``report_failure``) directly via the Python
API against a real fixture-loaded rule store.  They run locally (no Docker
subprocess) — the underlying MCP server protocol is covered by the unit
tests in ``tests/mcp``.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path

import pytest

from cauterule.mcp.tools import get_matching_rules, get_rule, list_rules, report_failure
from cauterule.store.manager import StoreManager

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"


@pytest.fixture
def store(tmp_path: Path) -> Iterator[StoreManager]:
    rules_src = FIXTURES / "rules"
    rules_dst = tmp_path / "rules"
    rules_dst.mkdir(parents=True)
    for f in rules_src.glob("*.yaml"):
        rules_dst.joinpath(f.name).write_bytes(f.read_bytes())
    yield StoreManager(base_dir=str(rules_dst))


# ======================================================================
# Tests
# ======================================================================


@pytest.mark.docker
def test_mcp_server_command_registered() -> None:
    """The ``cauterule mcp`` CLI command should be registered."""
    from click.testing import CliRunner

    from cauterule.cli.app import main

    result = CliRunner().invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "mcp" in result.output


@pytest.mark.docker
def test_get_matching_rules(store: StoreManager) -> None:
    rules = store.list_rules()
    matched = get_matching_rules("git push fails with non-fast-forward", rules)
    assert matched
    assert any(r.id == "R-001" for r in matched)


@pytest.mark.docker
def test_get_matching_rules_empty_task(store: StoreManager) -> None:
    rules = store.list_rules()
    assert get_matching_rules("", rules) == []


@pytest.mark.docker
def test_get_rule(store: StoreManager) -> None:
    rule = get_rule("R-001", store)
    assert rule is not None
    assert rule.id == "R-001"
    assert rule.provenance is not None
    assert rule.provenance.source_trajectory


@pytest.mark.docker
def test_get_rule_missing(store: StoreManager) -> None:
    assert get_rule("R-999", store) is None


@pytest.mark.docker
def test_list_rules(store: StoreManager) -> None:
    rules = list_rules(store=store)
    assert len(rules) >= 3
    ids = {r.id for r in rules}
    assert {"R-001", "R-002", "R-003"} <= ids


@pytest.mark.docker
def test_list_rules_status_filter(store: StoreManager) -> None:
    active = list_rules(status="active", store=store)
    assert all(r.status == "active" for r in active)
    assert any(r.id == "R-001" for r in active)


@pytest.mark.docker
def test_report_failure() -> None:
    trajectory = {
        "id": "T-001",
        "timestamp": "2025-01-01T00:00:00Z",
        "task": "deploy to prod",
        "steps": [
            {
                "step_number": 1,
                "tool": "deploy",
                "input": "deploy",
                "output": "",
                "error": "ENV not set",
            }
        ],
        "success": False,
    }
    result = report_failure(json.dumps(trajectory))
    assert result["accepted"] is True
    assert result["trajectory_length"] == 1


@pytest.mark.docker
def test_report_failure_invalid_json() -> None:
    result = report_failure("{not valid json}")
    assert result["accepted"] is False
    assert "Invalid JSON" in result["message"]


@pytest.mark.docker
def test_list_rules_no_store() -> None:
    assert list_rules(store=None) == []
