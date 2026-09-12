#!/usr/bin/env python3
"""Convert MCP issue reports to a reference corpus (#703).

``modelcontextprotocol/servers`` (MIT) — and the adjacent
``modelcontextprotocol/python-sdk`` / ``typescript-sdk`` trackers — contain
genuine auth / bearer-token failures, transport errors (stdio, Streamable
HTTP, SSE, spawn ENOENT, timeouts), and protocol handshake / lifecycle /
capability-negotiation failures. Each issue becomes a failure reference
trajectory under ``corpus/public/mcp/`` with a failure class derived from
the error text; a small set of successful-handshake counterparts is emitted
for #707 balance.

Usage:
    python scripts/convert_mcp_issues_to_corpus.py
        --issues /tmp/mcp.json
        --output corpus/public/mcp
        --success-output corpus/public/successes
        --limit 20

Fetch sample with gh:
    gh api "search/issues?q=repo:modelcontextprotocol/servers+auth+type:issue&per_page=15"
        --jq '[.items[] | {number,title,body}]' > /tmp/mcp.json
    gh api "repos/modelcontextprotocol/servers/issues?state=all&per_page=20"
        --jq '[.[] | {number,title,body}]' > /tmp/mcp.json
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

_TS = "2026-09-11T00:00:00+00:00"
_SOURCE_REPO = "modelcontextprotocol/servers"
_ERROR_RE = re.compile(
    r"error|failed|refused|timeout|exception|unavailable|unauthorized|bearer|handshake|closed",
    re.IGNORECASE,
)

_CLASSIFIERS: tuple[tuple[str, str], ...] = (
    ("bearer token", "mcp/auth/bearer_token"),
    ("bearer", "mcp/auth/bearer_token"),
    ("jwt", "mcp/auth/bearer_token"),
    ("jwks", "mcp/auth/bearer_token"),
    ("unauthorized", "mcp/auth/bearer_token"),
    ("401", "mcp/auth/bearer_token"),
    ("oauth", "mcp/auth/oauth"),
    ("auth", "mcp/auth/failure"),
    ("initialize", "mcp/protocol/handshake"),
    ("handshake", "mcp/protocol/handshake"),
    ("capability", "mcp/protocol/handshake"),
    ("protocol version", "mcp/protocol/version"),
    ("lifecycle", "mcp/protocol/lifecycle"),
    ("tools/list", "mcp/protocol/handshake"),
    ("transport closed", "mcp/transport/closed"),
    ("streamable", "mcp/transport/streamable_http"),
    ("sse", "mcp/transport/sse"),
    ("stdio", "mcp/transport/stdio"),
    ("spawn", "mcp/transport/spawn"),
    ("enoent", "mcp/transport/spawn"),
    ("timeout", "mcp/transport/timeout"),
)


def slug(value: str) -> str:
    """Return a lowercase, hyphenated taxonomy segment."""
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "unspecified"


def classify(body: str) -> str:
    """Derive an MCP failure_class from issue body text."""
    lowered = body.lower()
    for needle, failure_class in _CLASSIFIERS:
        if needle in lowered:
            return failure_class
    return "mcp/issue"


def extract_error(body: str) -> str:
    """Extract the most error-like snippet from an issue body."""
    for block in re.findall(r"```(.*?)```", body, re.DOTALL):
        if _ERROR_RE.search(block):
            return str(block).strip()[:1000]
    for line in body.splitlines():
        if _ERROR_RE.search(line):
            return str(line).strip()[:1000]
    return str(body).strip()[:1000]


def _tool_for_body(body: str) -> str:
    lowered = body.lower()
    if "stdio" in lowered:
        return "mcp-stdio-client"
    if "streamable" in lowered or "sse" in lowered:
        return "mcp-http-client"
    return "mcp-client"


def _input_for_body(body: str) -> str:
    lowered = body.lower()
    if "initialize" in lowered or "handshake" in lowered:
        return "initialize"
    if "tools/list" in lowered:
        return "tools/list"
    if "bearer" in lowered or "auth" in lowered or "unauthorized" in lowered:
        return "POST /tools/call (Authorization: Bearer <token>)"
    return "call tool"


def _failure(issue: dict[str, Any], index: int, ts: str) -> dict[str, Any]:
    body = str(issue.get("body", ""))
    number = issue.get("number", index)
    tid = f"mcp-issue-{number}"
    task = str(issue.get("title", "")).strip() or f"MCP issue {number}"
    return {
        "trajectory_id": tid,
        "id": tid,
        "timestamp": ts,
        "task": task,
        "steps": [
            {
                "step_number": 1,
                "tool": _tool_for_body(body),
                "input": _input_for_body(body),
                "output": None,
                "error": extract_error(body),
            }
        ],
        "success": False,
        "redacted": False,
        "failure_point": "step_1",
        "failure_class": classify(body),
        "quality_label": "noisy",
        "domain": "devops",
        "severity": "medium",
        "tags": ["reference", "mcp", "servers"],
        "expected_outcome": "should_extract",
        "expected_outcome_rationale": (
            "Real MCP failure signature from the servers issue tracker."
        ),
        "expected_outcome_confidence": "medium",
        "source": "mcp-issues",
        "source_repo": _SOURCE_REPO,
    }


_SUCCESS_CASES = (
    "Call MCP tool over Streamable HTTP with valid bearer token",
    "Invoke MCP tool over stdio transport",
    "Complete MCP initialize handshake and list tools",
    "Call MCP tool with valid OAuth token via Streamable HTTP",
)


def _success(index: int, case: str, ts: str) -> dict[str, Any]:
    tid = f"mcp-success-{index:03d}"
    if "http" in case.lower() or "oauth" in case.lower():
        tool = "mcp-http-client"
    elif "stdio" in case.lower():
        tool = "mcp-stdio-client"
    else:
        tool = "mcp-client"
    return {
        "trajectory_id": tid,
        "id": tid,
        "timestamp": ts,
        "task": case,
        "steps": [
            {
                "step_number": 1,
                "tool": tool,
                "input": "tools/call" if "tool" in case.lower() else "initialize",
                "output": "tool executed successfully (200 OK)",
                "error": None,
            }
        ],
        "success": True,
        "redacted": False,
        "failure_point": None,
        "failure_class": None,
        "quality_label": "clear",
        "domain": "devops",
        "severity": "low",
        "tags": ["reference", "mcp", "success"],
        "expected_outcome": "should_silence",
        "expected_outcome_rationale": "Successful MCP counterpart (#707 balance).",
        "expected_outcome_confidence": "high",
        "source": "mcp-issues",
        "source_repo": _SOURCE_REPO,
    }


def convert_mcp_issues(
    issues: list[dict[str, Any]],
    *,
    limit: int | None = None,
    timestamp: str = _TS,
) -> list[dict[str, Any]]:
    """Return failure (issues) + success reference records."""
    records: list[dict[str, Any]] = []
    for i, issue in enumerate(issues):
        if limit is not None and i >= limit:
            break
        records.append(_failure(issue, i + 1, timestamp))
    for i, case in enumerate(_SUCCESS_CASES, start=1):
        records.append(_success(i, case, timestamp))
    return records


def main(argv: list[str] | None = None) -> None:
    """Convert MCP issues JSON and write failure + success corpus files."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--issues", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--success-output", type=Path, default=None)
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args(argv)

    issues = json.loads(args.issues.read_text(encoding="utf-8"))
    # Support both list and dict with items key (search API)
    if isinstance(issues, dict) and "items" in issues:
        issues = issues["items"]
    records = convert_mcp_issues(issues, limit=args.limit)
    failures = [r for r in records if not r["success"]]
    successes = [r for r in records if r["success"]]

    args.output.mkdir(parents=True, exist_ok=True)
    out = args.output / "mcp-issues.jsonl"
    out.write_text("\n".join(json.dumps(r) for r in failures) + "\n", encoding="utf-8")
    print(f"[convert] {len(failures)} failures -> {out}")

    if args.success_output is not None:
        args.success_output.mkdir(parents=True, exist_ok=True)
        success_out = args.success_output / "mcp-successes.jsonl"
        success_out.write_text(
            "\n".join(json.dumps(r) for r in successes) + "\n", encoding="utf-8"
        )
        print(f"[convert] {len(successes)} successes -> {success_out}")


if __name__ == "__main__":
    main()
