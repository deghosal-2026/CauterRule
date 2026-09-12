#!/usr/bin/env python3
"""Convert AgentHarm cases to CauterRule's adversarial/unsafe corpus (#699).

AgentHarm (Hugging Face ``ai-safety-institute/AgentHarm``) is a purpose-built
benchmark of genuinely harmful agent tasks with target tool functions. Its
``harmful`` config becomes ``adversarial/unsafe_realistic`` failure
trajectories (``expected_outcome: should_reject``); its ``harmless_benign``
config supplies matching success trajectories so the source is balanced (#707).

Labels are derived from AgentHarm's own harm category and MUST be spot-checked
before being treated as ground truth (the ticket's human-labeling caveat).

Usage:
    python scripts/convert_agentharm_to_corpus.py \
        --harmful agentharm_harmful.jsonl \
        --benign agentharm_harmless_benign.jsonl \
        --output corpus/public/adversarial/unsafe_realistic \
        --success-output corpus/public/successes \
        --limit 20
"""

from __future__ import annotations

import argparse
import ast
import json
import re
from pathlib import Path
from typing import Any

_TS = "2026-09-11T00:00:00+00:00"
_SOURCE_REPO = "ai-safety-institute/AgentHarm"


def slug(value: str) -> str:
    """Return a lowercase, hyphenated taxonomy segment."""
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "unspecified"


def parse_targets(value: object) -> list[str]:
    """Parse AgentHarm's ``target_functions`` (list or stringified list)."""
    if isinstance(value, list):
        return [str(v) for v in value]
    if not isinstance(value, str):
        return []
    try:
        parsed = ast.literal_eval(value)
    except (ValueError, SyntaxError):
        return []
    return [str(v) for v in parsed] if isinstance(parsed, list) else []


def _steps(targets: list[str], *, error: str | None) -> list[dict[str, Any]]:
    if not targets:
        return [
            {
                "step_number": 1,
                "tool": "agent",
                "input": "invoke task",
                "output": None,
                "error": error,
            }
        ]
    steps: list[dict[str, Any]] = []
    for i, tool in enumerate(targets, start=1):
        last = i == len(targets)
        steps.append(
            {
                "step_number": i,
                "tool": tool,
                "input": "invoke",
                "output": None if (error and last) else f"{tool} acknowledged",
                "error": error if (error and last) else None,
            }
        )
    return steps


def _failure(row: dict[str, Any], index: int, ts: str) -> dict[str, Any]:
    category = str(row.get("category", "unspecified"))
    tid = f"agentharm-unsafe-{index:03d}"
    targets = parse_targets(row.get("target_functions"))
    return {
        "trajectory_id": tid,
        "id": tid,
        "timestamp": ts,
        "task": str(row.get("prompt", "")),
        "steps": _steps(targets, error=f"unsafe task requested: {row.get('name', category)}"),
        "success": False,
        "redacted": False,
        "failure_point": "step_1",
        "failure_class": f"adversarial/unsafe/{slug(category)}",
        "quality_label": "misleading",
        "domain": "research",
        "severity": "high",
        "tags": ["adversarial", "unsafe_realistic", "agentharm"],
        "expected_outcome": "should_reject",
        "expected_outcome_rationale": (
            "Genuinely harmful agent task (AgentHarm); no rule should be promoted."
        ),
        "expected_outcome_confidence": "medium",
        "source": "agentharm",
        "source_repo": _SOURCE_REPO,
    }


def _success(row: dict[str, Any], index: int, ts: str) -> dict[str, Any]:
    tid = f"agentharm-benign-{index:03d}"
    targets = parse_targets(row.get("target_functions"))
    return {
        "trajectory_id": tid,
        "id": tid,
        "timestamp": ts,
        "task": str(row.get("prompt", "")),
        "steps": _steps(targets, error=None),
        "success": True,
        "redacted": False,
        "failure_point": None,
        "failure_class": None,
        "quality_label": "clear",
        "domain": "research",
        "severity": "low",
        "tags": ["adversarial", "unsafe_realistic", "agentharm", "success"],
        "expected_outcome": "should_silence",
        "expected_outcome_rationale": "Benign counterpart task completing normally (#707 balance).",
        "expected_outcome_confidence": "high",
        "source": "agentharm",
        "source_repo": _SOURCE_REPO,
    }


def convert_agentharm(
    harmful: list[dict[str, Any]],
    benign: list[dict[str, Any]],
    *,
    limit: int | None = None,
    timestamp: str = _TS,
) -> list[dict[str, Any]]:
    """Return failure (harmful) + success (benign) corpus records."""
    records: list[dict[str, Any]] = []
    for i, row in enumerate(harmful):
        if limit is not None and i >= limit:
            break
        records.append(_failure(row, i + 1, timestamp))
    for i, row in enumerate(benign):
        if limit is not None and i >= limit:
            break
        records.append(_success(row, i + 1, timestamp))
    return records


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def main(argv: list[str] | None = None) -> None:
    """Convert AgentHarm JSONL cases and write the corpus files."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--harmful", type=Path, required=True)
    parser.add_argument("--benign", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--success-output", type=Path, default=None)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args(argv)

    records = convert_agentharm(
        _read_jsonl(args.harmful), _read_jsonl(args.benign), limit=args.limit
    )
    failures = [r for r in records if not r["success"]]
    successes = [r for r in records if r["success"]]

    args.output.mkdir(parents=True, exist_ok=True)
    out = args.output / "agentharm-unsafe.jsonl"
    out.write_text("\n".join(json.dumps(r) for r in failures) + "\n", encoding="utf-8")
    print(f"[convert] {len(failures)} failures -> {out}")

    if args.success_output is not None and successes:
        args.success_output.mkdir(parents=True, exist_ok=True)
        success_out = args.success_output / "agentharm-successes.jsonl"
        success_out.write_text("\n".join(json.dumps(r) for r in successes) + "\n", encoding="utf-8")
        print(f"[convert] {len(successes)} successes -> {success_out}")


if __name__ == "__main__":
    main()
