"""Verify docker compose orchestration — start services, run MCP, clean shutdown."""

from __future__ import annotations

import json
import subprocess
from subprocess import CompletedProcess

import pytest

COMPOSE_FILE = "docker-compose.yaml"
PROJECT_NAME = "cauterule-field-test"

BASE_CMD: list[str] = ["docker", "compose", "-f", COMPOSE_FILE, "-p", PROJECT_NAME]


def _compose(*args: str, input_data: str | None = None) -> CompletedProcess[str]:
    return subprocess.run(
        [*BASE_CMD, *args],
        capture_output=True,
        text=True,
        input=input_data,
    )


@pytest.mark.docker
@pytest.mark.slow
def test_compose_start_demo() -> None:
    result = _compose("up", "cauterule-demo", "--abort-on-container-exit")
    assert result.returncode == 0, result.stderr
    assert "demo" in result.stdout
    assert "rule" in result.stdout
    assert "promoted" in result.stdout


@pytest.mark.docker
@pytest.mark.slow
def test_compose_mcp_accepts() -> None:
    _compose("up", "-d", "cauterule-mcp")
    request = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "get_matching_rules",
            "arguments": {"task": "git push failure"},
        },
    })
    result = subprocess.run(
        [
            *BASE_CMD,
            "exec",
            "-i",
            "cauterule-mcp",
            "cauterule",
            "mcp",
            "--transport",
            "stdio",
        ],
        capture_output=True,
        text=True,
        input=request,
    )
    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)
    assert response.get("jsonrpc") == "2.0"
    assert "result" in response


@pytest.mark.docker
@pytest.mark.slow
def test_compose_test_passes() -> None:
    result = _compose("up", "cauterule-test", "--abort-on-container-exit")
    assert result.returncode == 0, result.stderr


@pytest.mark.docker
@pytest.mark.slow
def test_compose_clean_shutdown() -> None:
    _compose("down")
    ps_result = _compose("ps", "-q")
    assert ps_result.stdout.strip() == ""


@pytest.mark.docker
@pytest.mark.slow
def test_compose_all_services() -> None:
    _compose("up", "-d")
    result = _compose("ps", "--format", "json")
    services = json.loads(result.stdout)
    for svc in services:
        assert svc.get("State") == "running", f"{svc.get('Service')} not running"
        assert svc.get("Health") == "healthy", f"{svc.get('Service')} not healthy"
    _compose("down")
