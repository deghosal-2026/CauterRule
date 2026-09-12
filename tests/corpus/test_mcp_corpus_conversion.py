"""Tests for the MCP reference-corpus gap converter (#703)."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

from cauterule.models.trajectory import Trajectory

_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "convert_mcp_issues_to_corpus.py"

_ISSUES = [
    {
        "number": 4598,
        "title": "Bearer JWT + JWKS for agent callers",
        "body": "Symptom\n```\n401 Unauthorized: missing bearer token on POST /tools/call\n```\nBearer token validation failed.",
    },
    {
        "number": 1788,
        "title": "StreamableHTTPClientTransport not passing headers",
        "body": "transport closed unexpectedly: StreamableHTTPClientTransport failed to pass Authorization header",
    },
    {
        "number": 4195,
        "title": "tools/list succeeds without initialize handshake",
        "body": "MCP lifecycle bypass: tools/list succeeds without initialize handshake, capability negotiation skipped",
    },
]


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("convert_mcp_issues", _SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_slug_helper() -> None:
    module = _load()
    assert module.slug("Bearer Token") == "bearer-token"
    assert module.slug("  Auth Failure!! ") == "auth-failure"


def test_classify_and_extract() -> None:
    module = _load()
    assert module.classify("401 Unauthorized missing bearer token") == "mcp/auth/bearer_token"
    assert module.classify("transport closed unexpectedly streamable http") == "mcp/transport/closed"
    assert module.classify("tools/list without initialize handshake") == "mcp/protocol/handshake"
    assert module.classify("nothing relevant") == "mcp/issue"
    error = module.extract_error("```\nERROR: bearer token failed\n```")
    assert "bearer token failed" in error.lower()


def test_convert_produces_schema_valid_and_balanced_records() -> None:
    module = _load()
    records = module.convert_mcp_issues(_ISSUES)
    for record in records:
        Trajectory.from_dict(record)
    failures = [r for r in records if not r["success"]]
    successes = [r for r in records if r["success"]]
    assert len(failures) == 3
    assert successes
    assert failures[0]["source_repo"] == "modelcontextprotocol/servers"
    assert failures[0]["expected_outcome"] == "should_extract"
    assert "bearer" in failures[0]["steps"][0]["error"].lower() or "unauthorized" in failures[0]["steps"][0]["error"].lower()
    # failure_class should be slug-like under mcp/
    assert failures[0]["failure_class"].startswith("mcp/")


def test_convert_respects_limit() -> None:
    module = _load()
    assert len([r for r in module.convert_mcp_issues(_ISSUES * 5, limit=2) if not r["success"]]) == 2


def test_cli_writes_failure_and_success_files(tmp_path: Path) -> None:
    module = _load()
    src = tmp_path / "issues.json"
    src.write_text(json.dumps(_ISSUES), encoding="utf-8")
    out = tmp_path / "mcp"
    succ = tmp_path / "successes"
    module.main(
        ["--issues", str(src), "--output", str(out), "--success-output", str(succ), "--limit", "2"]
    )
    failure_rows = [
        json.loads(line) for line in (out / "mcp-issues.jsonl").read_text(encoding="utf-8").splitlines() if line
    ]
    success_rows = [
        json.loads(line)
        for line in (succ / "mcp-successes.jsonl").read_text(encoding="utf-8").splitlines()
        if line
    ]
    assert len(failure_rows) == 2 and success_rows
    for record in failure_rows + success_rows:
        Trajectory.from_dict(record)
