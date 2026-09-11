"""Verify docker compose orchestration — start services, run MCP, clean shutdown."""

from __future__ import annotations

import json
import subprocess
import time
from subprocess import CompletedProcess

import pytest

COMPOSE_FILE = "docker-compose.yaml"
PROJECT_NAME = "cauterule-field-test"

# v0.3.0 (#607): every service is profiled — activate all profiles explicitly.
ALL_PROFILES = [
    "--profile", "demo",
    "--profile", "test",
    "--profile", "mcp",
    "--profile", "mcp-http",
]

BASE_CMD: list[str] = ["docker", "compose", "-f", COMPOSE_FILE, "-p", PROJECT_NAME, *ALL_PROFILES]


def _compose(*args: str, input_data: str | None = None) -> CompletedProcess[str]:
    return subprocess.run(
        [*BASE_CMD, *args],
        capture_output=True,
        text=True,
        input=input_data,
    )


def _wait_for_service(service: str, running: bool = True, timeout: int = 180) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        ps = _compose("ps", "--format", "json")
        services: list[dict] = []
        try:
            parsed = json.loads(ps.stdout)
            if isinstance(parsed, list):
                services = [s for s in parsed if isinstance(s, dict)]
            elif isinstance(parsed, dict):
                services = [parsed]
        except json.JSONDecodeError:
            pass
        for svc in services:
            if svc.get("Service") == service:
                state = svc.get("State", "")
                if running and state == "running":
                    return True
                if not running and state in ("exited", "reloading"):
                    return True
        time.sleep(2)
    return False


@pytest.mark.docker
@pytest.mark.slow
def test_compose_start_demo() -> None:
    # Image is built by the suite start / hardening test — `up` reuses it.
    result = _compose("up", "cauterule-demo", "--abort-on-container-exit")
    assert result.returncode == 0, result.stderr
    assert "Seeded" in result.stdout
    assert "Extraction" in result.stdout
    assert "Promotion" in result.stdout
    _compose("down")


@pytest.mark.docker
@pytest.mark.slow
def test_compose_mcp_accepts() -> None:
    _compose("up", "-d", "cauterule-mcp")
    assert _wait_for_service("cauterule-mcp", running=True), "cauterule-mcp did not start"
    request = (
        json.dumps(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test", "version": "0.1.0"},
                },
            }
        )
        + "\n"
    )
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
        timeout=120,
    )
    assert result.returncode == 0, result.stderr
    resp = None
    for line in result.stdout.splitlines():
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict) and parsed.get("id") == 1:
            resp = parsed
            break
    assert resp is not None, f"no initialize response: {result.stdout!r}"
    assert resp.get("jsonrpc") == "2.0"
    _compose("down")


@pytest.mark.docker
@pytest.mark.slow
def test_compose_test_passes() -> None:
    result = _compose("up", "cauterule-test", "--abort-on-container-exit")
    assert result.returncode == 0, result.stderr
    _compose("down")


@pytest.mark.docker
@pytest.mark.slow
def test_compose_clean_shutdown() -> None:
    _compose("down")
    ps_result = _compose("ps", "-q")
    assert ps_result.stdout.strip() == ""


@pytest.mark.docker
@pytest.mark.slow
def test_compose_all_services() -> None:
    result = _compose("config", "--services")
    assert result.returncode == 0, result.stderr
    services = result.stdout.split()
    assert "cauterule-demo" in services
    assert "cauterule-test" in services
    assert "cauterule-mcp" in services
