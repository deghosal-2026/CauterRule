"""Comprehensive tests for the MCP server and tool modules."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from cauterule.mcp.launch import launch_mcp
from cauterule.mcp.server import CauteruleMCPServer
from cauterule.mcp.tools import get_matching_rules, get_rule, list_rules, report_failure
from cauterule.models.rule import (
    Provenance,
    RuleDo,
    RuleWhen,
    StandingRule,
    Status,
)
from cauterule.store.manager import StoreManager


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
def _make_rule(
    rule_id: str = "rule-001",
    trigger: str = "agent produces empty response",
    directive: str = "ask the user for clarification",
    status: Status = "active",
    tags: tuple[str, ...] = ("output",),
) -> StandingRule:
    return StandingRule(
        id=rule_id,
        when=RuleWhen(trigger=trigger),
        do=RuleDo(directive=directive),
        confidence=0.85,
        provenance=Provenance(
            source_trajectory="traj-foo",
            extracted_by="gpt-4o",
            extract_timestamp="2025-01-01T00:00:00Z",
            extraction_pass=1,
        ),
        status=status,
        promoted_at="2025-01-02T00:00:00Z",
        tags=tags,
    )


def _mock_store(rules: list[StandingRule] | None = None) -> MagicMock:
    store = MagicMock(spec=StoreManager)
    store.list_rules.return_value = rules or []
    store.get_rule.return_value = rules[0] if rules else None
    return store


# ======================================================================
# get_matching_rules
# ======================================================================
class TestGetMatchingRules:
    def test_matches_trigger(self) -> None:
        rule = _make_rule(trigger="empty response from tool")
        result = get_matching_rules("empty response", [rule])
        assert result == [rule]

    def test_case_insensitive(self) -> None:
        rule = _make_rule(trigger="EMPTY RESPONSE")
        result = get_matching_rules("empty", [rule])
        assert result == [rule]

    def test_matches_tag(self) -> None:
        rule = _make_rule(tags=("output", "critical"))
        result = get_matching_rules("critical", [rule])
        assert result == [rule]

    def test_skips_non_active_rules(self) -> None:
        retired = _make_rule(rule_id="r1", status="retired")
        active = _make_rule(rule_id="r2", trigger="empty response")
        result = get_matching_rules("empty", [retired, active])
        assert result == [active]

    def test_no_match_returns_empty(self) -> None:
        rule = _make_rule(trigger="something else")
        result = get_matching_rules("no match here", [rule])
        assert result == []

    def test_empty_task_returns_nothing(self) -> None:
        rule = _make_rule()
        result = get_matching_rules("", [rule])
        assert result == []

    def test_empty_rules_list(self) -> None:
        result = get_matching_rules("anything", [])
        assert result == []


# ======================================================================
# get_rule
# ======================================================================
class TestGetRule:
    def test_existing_rule(self) -> None:
        rule = _make_rule()
        store = _mock_store([rule])
        result = get_rule("rule-001", store)
        assert result is rule
        store.get_rule.assert_called_once_with("rule-001")

    def test_missing_rule(self) -> None:
        store = _mock_store([])
        result = get_rule("nonexistent", store)
        assert result is None

    def test_provenance_included(self) -> None:
        rule = _make_rule()
        store = _mock_store([rule])
        result = get_rule("rule-001", store)
        assert result is not None
        assert result.provenance.source_trajectory == "traj-foo"
        assert result.provenance.extracted_by == "gpt-4o"


# ======================================================================
# list_rules
# ======================================================================
class TestListRules:
    def test_no_filters(self) -> None:
        rules = [_make_rule(rule_id="a"), _make_rule(rule_id="b")]
        store = _mock_store(rules)
        result = list_rules(store=store)
        assert result == rules
        store.list_rules.assert_called_once_with(status=None)

    def test_filter_by_status(self) -> None:
        rules = [_make_rule(rule_id="a", status="active")]
        store = _mock_store(rules)
        result = list_rules(status="active", store=store)
        assert result == rules
        store.list_rules.assert_called_once_with(status="active")

    def test_filter_by_tag(self) -> None:
        r1 = _make_rule(rule_id="a", tags=("output",))
        r2 = _make_rule(rule_id="b", tags=("security",))
        store = _mock_store([r1, r2])
        store.list_rules.return_value = [r1, r2]
        result = list_rules(tag="output", store=store)
        assert result == [r1]

    def test_filter_by_tag_case_insensitive(self) -> None:
        r1 = _make_rule(rule_id="a", tags=("Output",))
        store = _mock_store([r1])
        store.list_rules.return_value = [r1]
        result = list_rules(tag="output", store=store)
        assert result == [r1]

    def test_filter_by_status_and_tag(self) -> None:
        r1 = _make_rule(rule_id="a", status="active", tags=("output",))
        r2 = _make_rule(rule_id="b", status="active", tags=("security",))
        r3 = _make_rule(rule_id="c", status="retired", tags=("output",))
        store = _mock_store([r1, r2, r3])
        store.list_rules.return_value = [r1, r2]
        result = list_rules(status="active", tag="output", store=store)
        assert result == [r1]

    def test_no_tag_match_returns_empty(self) -> None:
        r1 = _make_rule(tags=("output",))
        store = _mock_store([r1])
        store.list_rules.return_value = [r1]
        result = list_rules(tag="nonexistent", store=store)
        assert result == []

    def test_none_store_returns_empty(self) -> None:
        result = list_rules(store=None)
        assert result == []


# ======================================================================
# report_failure
# ======================================================================
class TestReportFailure:
    def test_valid_trajectory(self) -> None:
        result = report_failure('{"steps": [{"action": "run"}, {"action": "fail"}]}')
        assert result["accepted"] is True
        assert result["trajectory_length"] == 2

    def test_trajectory_without_steps(self) -> None:
        result = report_failure('{"foo": "bar"}')
        assert result["accepted"] is True
        assert result["trajectory_length"] == 0

    def test_empty_object(self) -> None:
        result = report_failure("{}")
        assert result["accepted"] is True
        assert result["trajectory_length"] == 0

    def test_invalid_json(self) -> None:
        result = report_failure("not json")
        assert result["accepted"] is False
        assert result["trajectory_length"] == 0
        assert "Invalid JSON" in result["message"]

    def test_non_dict_json(self) -> None:
        result = report_failure('"just a string"')
        assert result["accepted"] is False
        assert result["trajectory_length"] == 0
        assert "must be a JSON object" in result["message"]

    def test_steps_is_not_a_list(self) -> None:
        result = report_failure('{"steps": "not a list"}')
        assert result["accepted"] is True
        assert result["trajectory_length"] == 0


# ======================================================================
# CauteruleMCPServer
# ======================================================================
class TestCauteruleMCPServer:
    def test_constructs_with_store(self) -> None:
        store = _mock_store()
        server = CauteruleMCPServer(store)
        assert server.store is store
        assert server._mcp is not None

    def test_run_stdio_invokes_mcp_run(self) -> None:
        store = _mock_store()
        server = CauteruleMCPServer(store)
        with patch.object(server._mcp, "run") as mock_run:
            server.run_stdio()
        mock_run.assert_called_once_with(transport="stdio")

    def test_run_http_invokes_mcp_run(self) -> None:
        store = _mock_store()
        server = CauteruleMCPServer(store, host="0.0.0.0", port=9001)
        with patch.object(server._mcp, "run") as mock_run:
            server.run_http()
        mock_run.assert_called_once_with(transport="streamable-http")

    def test_run_http_defaults(self) -> None:
        store = _mock_store()
        server = CauteruleMCPServer(store)
        with patch.object(server._mcp, "run") as mock_run:
            server.run_http()
        mock_run.assert_called_once_with(transport="streamable-http")


# ======================================================================
# launch_mcp
# ======================================================================
class TestLaunchMcp:
    def test_launch_stdio(self) -> None:
        with patch(
            "cauterule.mcp.launch.CauteruleMCPServer"
        ) as mock_server_cls, patch(
            "cauterule.mcp.launch.StoreManager"
        ) as mock_store_cls:
            instance = mock_server_cls.return_value
            launch_mcp(transport="stdio")
        mock_store_cls.assert_called_once()
        mock_server_cls.assert_called_once()
        instance.run_stdio.assert_called_once()

    def test_launch_http(self) -> None:
        with patch(
            "cauterule.mcp.launch.CauteruleMCPServer"
        ) as mock_server_cls, patch(
            "cauterule.mcp.launch.StoreManager"
        ) as mock_store_cls:
            instance = mock_server_cls.return_value
            launch_mcp(transport="http", host="0.0.0.0", port=8080)
        mock_store_cls.assert_called_once()
        _, kwargs = mock_server_cls.call_args
        assert kwargs["host"] == "0.0.0.0"
        assert kwargs["port"] == 8080
        assert kwargs["auth_mode"] == "none"
        assert "rate_limiter" in kwargs
        instance.run_http.assert_called_once_with()

    def test_invalid_transport(self) -> None:
        with pytest.raises(ValueError, match="Unknown transport"):
            launch_mcp(transport="ws")
