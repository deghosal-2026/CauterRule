"""End-to-end tests for the MCP HTTP (streamable-http) transport (#527).

These integration tests spin up the real ``CauteruleMCPServer`` on an
ephemeral port in a background thread and drive it with the official MCP
``ClientSession`` over ``streamable_http_client`` — the same path an
external agent (e.g. Claude Desktop, a custom MCP client) uses.

Marked ``@pytest.mark.slow`` because each test boots a uvicorn server.
"""

from __future__ import annotations

import socket
import threading
import time
from collections.abc import Iterator
from contextlib import contextmanager

import anyio
import pytest
from mcp.client.streamable_http import streamable_http_client

from cauterule.mcp.server import CauteruleMCPServer
from cauterule.models.rule import Provenance, RuleDo, RuleWhen, StandingRule
from cauterule.store.manager import StoreManager
from mcp import ClientSession

pytestmark = pytest.mark.slow


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _make_rule(rule_id: str = "rule-001") -> StandingRule:
    return StandingRule(
        id=rule_id,
        when=RuleWhen(trigger="empty response from tool"),
        do=RuleDo(directive="ask the user for clarification"),
        confidence=0.9,
        provenance=Provenance(
            source_trajectory="traj-foo",
            extracted_by="gpt-4o",
            extract_timestamp="2025-01-01T00:00:00Z",
            extraction_pass=1,
        ),
        status="active",
        promoted_at="2025-01-02T00:00:00Z",
    )


@contextmanager
def _running_server(tmp_path) -> Iterator[tuple[str, CauteruleMCPServer]]:
    """Start the MCP server on an ephemeral port; yield (base_url, server)."""
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]

    store = StoreManager(str(tmp_path / "rules"))
    store.add_rule(_make_rule())
    server = CauteruleMCPServer(store, host="127.0.0.1", port=port)

    thread = threading.Thread(target=server.run_http, daemon=True)
    thread.start()

    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.3):
                break
        except OSError:
            time.sleep(0.1)
    else:
        raise AssertionError("MCP HTTP server did not come up in time")

    try:
        yield f"http://127.0.0.1:{port}/mcp", server
    finally:
        # Server thread is daemonized; the client session will terminate it
        # via the DELETE request on close.
        pass


# ===========================================================================
# Tests
# ===========================================================================
def test_http_tools_listed(tmp_path) -> None:
    with _running_server(tmp_path) as (base_url, _server):

        async def _main() -> list[str]:
            async with (
                streamable_http_client(base_url) as (read, write, _),
                ClientSession(read, write) as session,
            ):
                await session.initialize()
                result = await session.list_tools()
                return [t.name for t in result.tools]

        names = anyio.run(_main)
        assert {
            "get_matching_rules_tool",
            "get_rule_tool",
            "list_rules_tool",
            "report_failure_tool",
        } <= set(names)


def test_http_call_tools_valid(tmp_path) -> None:
    with _running_server(tmp_path) as (base_url, _server):

        async def _main() -> None:
            async with (
                streamable_http_client(base_url) as (read, write, _),
                ClientSession(read, write) as session,
            ):
                await session.initialize()

                res = await session.call_tool("list_rules_tool", {})
                assert res.isError is False
                assert "rule-001" in (res.content[0].text if res.content else "")

                res = await session.call_tool("get_rule_tool", {"rule_id": "rule-001"})
                assert res.isError is False

                res = await session.call_tool(
                    "get_matching_rules_tool", {"task": "empty response"}
                )
                assert res.isError is False

                res = await session.call_tool(
                    "report_failure_tool",
                    {"trajectory_json": '{"steps": [{"action": "run"}]}'},
                )
                assert res.isError is False

        anyio.run(_main)


def test_http_invalid_args_schema_error(tmp_path) -> None:
    with _running_server(tmp_path) as (base_url, _server):

        async def _main() -> str:
            async with (
                streamable_http_client(base_url) as (read, write, _),
                ClientSession(read, write) as session,
            ):
                await session.initialize()
                res = await session.call_tool("list_rules_tool", {"status": 123})
                return res.content[0].text if res.content else ""

        text = anyio.run(_main)
        # Structured pydantic validation error, no traceback leak.
        assert "validation error" in text or "Error executing tool" in text
        assert "Traceback" not in text


def test_http_unknown_tool_no_traceback(tmp_path) -> None:
    with _running_server(tmp_path) as (base_url, _server):

        async def _main() -> str:
            async with (
                streamable_http_client(base_url) as (read, write, _),
                ClientSession(read, write) as session,
            ):
                await session.initialize()
                res = await session.call_tool("nope_tool", {})
                return res.content[0].text if res.content else ""

        text = anyio.run(_main)
        assert "Unknown tool" in text
        assert "Traceback" not in text


def test_http_unauthenticated_binding_posture(tmp_path) -> None:
    """Documented R6 posture: localhost bind, no server-side token auth.

    Unauthenticated HTTP requests are processed (the listener is bound to
    127.0.0.1 and production exposure requires a reverse proxy with its own
    auth). Pins the posture so a future auth change updates it deliberately.
    """
    with _running_server(tmp_path) as (base_url, _server):

        async def _main() -> bool:
            async with (
                streamable_http_client(base_url) as (read, write, _),
                ClientSession(read, write) as session,
            ):
                await session.initialize()
                res = await session.call_tool("list_rules_tool", {})
                return res.isError is False

        assert anyio.run(_main) is True
