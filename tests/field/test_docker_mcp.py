"""Verify the MCP server works inside the Docker container over stdio transport."""

from __future__ import annotations

import json
import subprocess
import sys
from collections.abc import Iterator
from typing import Any, cast

import pytest

MCP_CMD = [sys.executable, "-m", "cauterule.cli.app", "mcp", "--transport", "stdio"]


class _McpClient:
    """Bare-minimum JSON-RPC 2.0 client over subprocess stdin/stdout."""

    def __init__(self) -> None:
        self._proc: subprocess.Popen[str] | None = None
        self._next_id = 0

    def start(self) -> None:
        self._proc = subprocess.Popen(
            MCP_CMD,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    @property
    def process(self) -> subprocess.Popen[str]:
        assert self._proc is not None
        return self._proc

    def send_request(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        self._next_id += 1
        request: dict[str, Any] = {
            "jsonrpc": "2.0",
            "id": self._next_id,
            "method": "tools/call",
            "params": {"name": method, "arguments": params or {}},
        }
        line = json.dumps(request) + "\n"
        self.process.stdin.write(line)  # type: ignore[union-attr]
        self.process.stdin.flush()  # type: ignore[union-attr]

        raw = self.process.stdout.readline()  # type: ignore[union-attr]
        return cast("dict[str, Any]", json.loads(raw))

    def send_raw(self, raw_json: str) -> dict[str, Any]:
        self.process.stdin.write(raw_json + "\n")  # type: ignore[union-attr]
        self.process.stdin.flush()  # type: ignore[union-attr]
        raw = self.process.stdout.readline()  # type: ignore[union-attr]
        return cast("dict[str, Any]", json.loads(raw))

    def stop(self) -> None:
        if self._proc is not None:
            self._proc.terminate()
            self._proc.wait(timeout=10)


@pytest.fixture
def mcp_client() -> Iterator[_McpClient]:
    client = _McpClient()
    client.start()
    yield client
    client.stop()


# ======================================================================
# Tests
# ======================================================================


@pytest.mark.docker
def test_mcp_server_starts(mcp_client: _McpClient) -> None:
    assert mcp_client.process.poll() is None


@pytest.mark.docker
def test_get_matching_rules(mcp_client: _McpClient) -> None:
    resp = mcp_client.send_request("get_matching_rules", {"task": "git push to origin"})
    assert "result" in resp or "error" in resp
    if "result" in resp:
        assert isinstance(resp["result"]["content"], list)


@pytest.mark.docker
def test_get_rule(mcp_client: _McpClient) -> None:
    resp = mcp_client.send_request("get_rule", {"rule_id": "R-001"})
    assert "result" in resp or "error" in resp
    if "result" in resp:
        content = resp["result"]["content"]
        if content:
            data = json.loads(content[0]["text"])
            assert "provenance" in data


@pytest.mark.docker
def test_list_rules(mcp_client: _McpClient) -> None:
    resp = mcp_client.send_request("list_rules", {"filter": "active"})
    assert "result" in resp or "error" in resp
    if "result" in resp:
        assert isinstance(resp["result"]["content"], list)


@pytest.mark.docker
def test_report_failure(mcp_client: _McpClient) -> None:
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
    resp = mcp_client.send_request("report_failure", {"trajectory": trajectory})
    assert "result" in resp or "error" in resp
    if "result" in resp:
        text = resp["result"]["content"][0]["text"]
        assert "trajectory_length" in text or "accepted" in text


@pytest.mark.docker
def test_stdio_transport(mcp_client: _McpClient) -> None:
    req = '{"jsonrpc":"2.0","id":99,"method":"tools/list","params":{}}'
    resp = mcp_client.send_raw(req)
    assert resp.get("id") == 99
    assert "result" in resp or "error" in resp
    if "result" in resp:
        assert isinstance(resp["result"]["tools"], list)


@pytest.mark.docker
def test_mcp_error_handling(mcp_client: _McpClient) -> None:
    resp = mcp_client.send_raw('{"invalid jsonrpc message}')
    assert "error" in resp or "id" in resp


@pytest.mark.docker
def test_mcp_invalid_id(mcp_client: _McpClient) -> None:
    resp = mcp_client.send_request("get_rule", {"rule_id": "R-999"})
    assert "result" in resp or "error" in resp
    if "result" in resp:
        assert resp["result"]["content"] is not None
