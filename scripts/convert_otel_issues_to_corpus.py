#!/usr/bin/env python3
"""Convert OpenTelemetry Demo issue reports to a reference corpus (#702).

``open-telemetry/opentelemetry-demo`` (Apache-2.0) issues contain genuine
span-export failures, collector errors, and exporter connection problems —
real failure text rather than hand-authored approximations. Each issue becomes
a failure reference trajectory under ``corpus/public/otel/`` with a failure
class derived from the error text; a small set of successful-export
counterparts is emitted for #707 balance.

Usage:
    python scripts/convert_otel_issues_to_corpus.py \
        --issues otel_issues.json \
        --output corpus/public/otel \
        --success-output corpus/public/successes \
        --limit 20
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

_TS = "2026-09-11T00:00:00+00:00"
_SOURCE_REPO = "open-telemetry/opentelemetry-demo"
_ERROR_RE = re.compile(r"error|failed|refused|timeout|exception|unavailable", re.IGNORECASE)

_CLASSIFIERS: tuple[tuple[str, str], ...] = (
    ("connection refused", "otel/exporter/connection_refused"),
    ("dial tcp", "otel/exporter/connection_refused"),
    ("context deadline exceeded", "otel/exporter/timeout"),
    ("unavailable", "otel/exporter/unavailable"),
    ("out-of-order exemplar", "otel/prometheus/exemplar"),
    ("connection leak", "otel/grpc/connection-leak"),
    ("collector", "otel/collector/pipeline"),
)


def classify(body: str) -> str:
    """Derive an otel failure_class from issue body text."""
    lowered = body.lower()
    for needle, failure_class in _CLASSIFIERS:
        if needle in lowered:
            return failure_class
    return "otel/issue"


def extract_error(body: str) -> str:
    """Extract the most error-like snippet from an issue body."""
    for block in re.findall(r"```(.*?)```", body, re.DOTALL):
        if _ERROR_RE.search(block):
            return str(block).strip()[:1000]
    for line in body.splitlines():
        if _ERROR_RE.search(line):
            return str(line).strip()[:1000]
    return str(body).strip()[:1000]


def _failure(issue: dict[str, Any], index: int, ts: str) -> dict[str, Any]:
    body = str(issue.get("body", ""))
    number = issue.get("number", index)
    tid = f"otel-issue-{number}"
    return {
        "trajectory_id": tid,
        "id": tid,
        "timestamp": ts,
        "task": str(issue.get("title", "")),
        "steps": [
            {
                "step_number": 1,
                "tool": "otel-collector",
                "input": "export spans",
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
        "tags": ["reference", "otel", "opentelemetry-demo"],
        "expected_outcome": "should_extract",
        "expected_outcome_rationale": (
            "Real OpenTelemetry failure signature from the demo issue tracker."
        ),
        "expected_outcome_confidence": "medium",
        "source": "opentelemetry-demo-issues",
        "source_repo": _SOURCE_REPO,
    }


_SUCCESS_CASES = (
    "Export trace spans via OTLP exporter",
    "Collect metrics from the checkout service",
    "Propagate context across the frontend and cart services",
)


def _success(index: int, case: str, ts: str) -> dict[str, Any]:
    tid = f"otel-success-{index:03d}"
    return {
        "trajectory_id": tid,
        "id": tid,
        "timestamp": ts,
        "task": case,
        "steps": [
            {
                "step_number": 1,
                "tool": "otel-collector",
                "input": "export batch",
                "output": "spans exported successfully (200 OK)",
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
        "tags": ["reference", "otel", "success"],
        "expected_outcome": "should_silence",
        "expected_outcome_rationale": "Successful export counterpart (#707 balance).",
        "expected_outcome_confidence": "high",
        "source": "opentelemetry-demo-issues",
        "source_repo": _SOURCE_REPO,
    }


def convert_otel_issues(
    issues: list[dict[str, Any]],
    *,
    limit: int | None = None,
    timestamp: str = _TS,
) -> list[dict[str, Any]]:
    """Return failure (issues) + success (export) reference records."""
    records: list[dict[str, Any]] = []
    for i, issue in enumerate(issues):
        if limit is not None and i >= limit:
            break
        records.append(_failure(issue, i + 1, timestamp))
    for i, case in enumerate(_SUCCESS_CASES, start=1):
        records.append(_success(i, case, timestamp))
    return records


def main(argv: list[str] | None = None) -> None:
    """Convert OTel issues JSON and write failure + success corpus files."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--issues", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--success-output", type=Path, default=None)
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args(argv)

    issues = json.loads(args.issues.read_text(encoding="utf-8"))
    records = convert_otel_issues(issues, limit=args.limit)
    failures = [r for r in records if not r["success"]]
    successes = [r for r in records if r["success"]]

    args.output.mkdir(parents=True, exist_ok=True)
    out = args.output / "otel-issues.jsonl"
    out.write_text("\n".join(json.dumps(r) for r in failures) + "\n", encoding="utf-8")
    print(f"[convert] {len(failures)} failures -> {out}")

    if args.success_output is not None:
        args.success_output.mkdir(parents=True, exist_ok=True)
        success_out = args.success_output / "otel-successes.jsonl"
        success_out.write_text(
            "\n".join(json.dumps(r) for r in successes) + "\n", encoding="utf-8"
        )
        print(f"[convert] {len(successes)} successes -> {success_out}")


if __name__ == "__main__":
    main()
