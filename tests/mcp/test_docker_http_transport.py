"""Docker test: MCP HTTP transport end-to-end in-container (#676).

Mirrors the host-side proof in ``tests/mcp/test_http_transport.py`` but drives
the server from *outside* the container the way a deployed agent would: starts
``cauterule mcp --transport http`` in a container that binds 8025, maps it to
the host, and exercises initialize / list_tools / call_tool / schema-rejection
/ unknown-tool over the official MCP ``streamable_http_client``.

Results are recorded to ``field-test/results/0.3.0/docker/`` by the field conftest
(this module also marks tests ``docker`` so they are picked up there).

Skipped gracefully where no Docker daemon is available.
"""

from __future__ import annotations

import shutil
import subprocess
import time
from pathlib import Path

import anyio
import pytest
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

DOCKER_TAG = "cauterule:field-test"
MCP_PORT = "8025"
CONTAINER_NAME = "mcp-http-v030-it"
FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"

pytestmark = [pytest.mark.docker, pytest.mark.slow]


def _docker_available() -> bool:
    try:
        subprocess.run(["docker", "info"], capture_output=True, timeout=10, check=False)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False
    return True


skip_no_docker = pytest.mark.skipif(not _docker_available(), reason="docker daemon not available")


def _wait_http(host_port: str, timeout: int = 40) -> None:
    """Poll until the container's HTTP endpoint answers — TCP accept alone is
    not enough (the streamable-http session manager resets early clients)."""
    import subprocess as sp
    deadline = time.time() + timeout
    url = f"http://127.0.0.1:{host_port}/mcp"
    while time.time() < deadline:
        r = sp.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
             "-X", "POST", url,
             "-H", "Content-Type: application/json",
             "-H", "Accept: application/json, text/event-stream",
             "-d", '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"t","version":"0"}}}'],
            capture_output=True, text=True, timeout=10,
        )
        if r.stdout.strip().isdigit() and int(r.stdout.strip()) > 0:
            return
        time.sleep(0.5)
    raise AssertionError(f"HTTP endpoint on port {host_port} never answered in {timeout}s")


@pytest.fixture
def mcp_http_container(tmp_path: Path):
    """Start the MCP HTTP server in a container with a seeded store; yield base_url."""
    # Seed a rule store on the host to mount into the container.
    store = tmp_path / "rules"
    store.mkdir()
    for f in (FIXTURES / "rules").glob("*.yaml"):
        shutil.copy(f, store)

    started = subprocess.run(
        ["docker", "run", "--rm", "-d",
         "--name", CONTAINER_NAME,
         "-p", f"0:{MCP_PORT}",
         "-v", f"{store}:/app/rules",
         DOCKER_TAG,
         "mcp", "--transport", "http", "--host", "0.0.0.0", "--port", MCP_PORT],
        capture_output=True, text=True, timeout=60,
    )
    if started.returncode != 0:
        pytest.skip(f"could not start mcp http container: {started.stderr}")

    port_out = subprocess.run(
        ["docker", "port", CONTAINER_NAME, MCP_PORT],
        capture_output=True, text=True, timeout=20,
    )
    host_port = port_out.stdout.strip().split(":")[-1]
    try:
        assert host_port, f"no port mapping: {port_out.stdout}"
        _wait_http(host_port, 40)
        yield f"http://127.0.0.1:{host_port}/mcp"
    finally:
        subprocess.run(["docker", "rm", "-f", CONTAINER_NAME], capture_output=True, timeout=20)


# ===========================================================================
# Tests — same client pattern as tests/mcp/test_http_transport.py
# ===========================================================================
@skip_no_docker
def test_docker_http_tools_listed(mcp_http_container: str) -> None:
    base_url = mcp_http_container

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


@skip_no_docker
def test_docker_http_call_tools_valid(mcp_http_container: str) -> None:
    base_url = mcp_http_container

    async def _main() -> None:
        async with (
            streamable_http_client(base_url) as (read, write, _),
            ClientSession(read, write) as session,
        ):
            await session.initialize()
            res = await session.call_tool("list_rules_tool", {})
            assert res.isError is False
            # The seeded store has R-001/R-002/R-003 — at least one rule listed.
            text = res.content[0].text if res.content else ""
            assert "R-0" in text, text

    anyio.run(_main)


@skip_no_docker
def test_docker_http_invalid_args_schema_error(mcp_http_container: str) -> None:
    base_url = mcp_http_container

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


@skip_no_docker
def test_docker_http_unknown_tool_no_traceback(mcp_http_container: str) -> None:
    base_url = mcp_http_container

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
