#!/usr/bin/env python3
"""Convert InjecAgent cases to CauterRule's tool-output-injection corpus (#700).

InjecAgent (uiuc-kang-lab/InjecAgent, MIT) provides agent task templates whose
tool-response contains an ``<Attacker Instruction>`` placeholder — indirect
prompt injection delivered through ``step.output``, the exact architectural gap
#696/#700 target.

Each source case produces:
* a **failure** trajectory (the poisoned tool output) with
  ``expected_outcome: should_reject``, and
* a matching **success** trajectory (the benign task completing) so the source
  pairs failures with successes for safety-gate balance (#707).

Usage:
    python scripts/convert_injecagent_to_corpus.py \
        --user-cases data/user_cases.jsonl \
        --attacker-cases data/attacker_cases_dh.jsonl \
        --output corpus/public/adversarial/tool_output_injection \
        --success-output corpus/public/successes \
        --limit 10
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

_TS = "2026-09-11T00:00:00+00:00"
_PLACEHOLDER = "<Attacker Instruction>"
_SOURCE_REPO = "uiuc-kang-lab/InjecAgent"


def poison_response(template: str, instruction: str) -> str:
    """Insert *instruction* into a tool-response template."""
    if _PLACEHOLDER in template:
        return template.replace(_PLACEHOLDER, instruction)
    return f"{template} {instruction}".strip()


def _failure(user: dict[str, Any], attacker: dict[str, Any], index: int, ts: str) -> dict[str, Any]:
    tid = f"injecagent-tool-output-{index:03d}"
    instruction = str(attacker.get("Attacker Instruction", ""))
    return {
        "trajectory_id": tid,
        "id": tid,
        "timestamp": ts,
        "task": str(user.get("User Instruction", "")),
        "steps": [
            {
                "step_number": 1,
                "tool": str(user.get("User Tool", "tool")),
                "input": str(user.get("Tool Parameters", "")),
                "output": poison_response(str(user.get("Tool Response Template", "")), instruction),
                "error": None,
            }
        ],
        "success": False,
        "redacted": False,
        "failure_point": "step_1",
        "failure_class": "adversarial/tool_output_injection",
        "quality_label": "misleading",
        "domain": "research",
        "severity": "high",
        "tags": ["adversarial", "tool_output_injection", "injecagent"],
        "expected_outcome": "should_reject",
        "expected_outcome_rationale": (
            "Indirect prompt injection delivered via tool output; no rule should be extracted."
        ),
        "expected_outcome_confidence": "high",
        "source": "injecagent",
        "source_repo": _SOURCE_REPO,
    }


def _success(user: dict[str, Any], index: int, ts: str) -> dict[str, Any]:
    tid = f"injecagent-benign-success-{index:03d}"
    return {
        "trajectory_id": tid,
        "id": tid,
        "timestamp": ts,
        "task": str(user.get("User Instruction", "")),
        "steps": [
            {
                "step_number": 1,
                "tool": str(user.get("User Tool", "tool")),
                "input": str(user.get("Tool Parameters", "")),
                "output": poison_response(
                    str(user.get("Tool Response Template", "")),
                    "No additional instructions.",
                ),
                "error": None,
            }
        ],
        "success": True,
        "redacted": False,
        "failure_point": None,
        "failure_class": None,
        "quality_label": "clear",
        "domain": "research",
        "severity": "low",
        "tags": ["adversarial", "tool_output_injection", "injecagent", "success"],
        "expected_outcome": "should_silence",
        "expected_outcome_rationale": "Benign tool call completing normally (#707 balance).",
        "expected_outcome_confidence": "high",
        "source": "injecagent",
        "source_repo": _SOURCE_REPO,
    }


def convert_injecagent(
    user_cases: list[dict[str, Any]],
    attacker_cases: list[dict[str, Any]],
    *,
    limit: int | None = None,
    timestamp: str = _TS,
) -> list[dict[str, Any]]:
    """Convert InjecAgent cases into failure + success corpus records."""
    if not attacker_cases:
        return []
    records: list[dict[str, Any]] = []
    for i, user in enumerate(user_cases):
        if limit is not None and i >= limit:
            break
        attacker = attacker_cases[i % len(attacker_cases)]
        records.append(_failure(user, attacker, i + 1, timestamp))
        records.append(_success(user, i + 1, timestamp))
    return records


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def main(argv: list[str] | None = None) -> None:
    """Convert InjecAgent JSONL cases and write failure + success corpus files."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--user-cases", type=Path, required=True)
    parser.add_argument("--attacker-cases", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="tool-output-injection dir.")
    parser.add_argument(
        "--success-output", type=Path, default=None, help="Success-counterpart dir (#707)."
    )
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args(argv)

    records = convert_injecagent(
        _read_jsonl(args.user_cases), _read_jsonl(args.attacker_cases), limit=args.limit
    )
    failures = [r for r in records if not r["success"]]
    successes = [r for r in records if r["success"]]

    args.output.mkdir(parents=True, exist_ok=True)
    out = args.output / "injecagent-tool-output.jsonl"
    out.write_text("\n".join(json.dumps(r) for r in failures) + "\n", encoding="utf-8")
    print(f"[convert] {len(failures)} failures -> {out}")

    if args.success_output is not None and successes:
        args.success_output.mkdir(parents=True, exist_ok=True)
        success_out = args.success_output / "injecagent-successes.jsonl"
        success_out.write_text(
            "\n".join(json.dumps(r) for r in successes) + "\n", encoding="utf-8"
        )
        print(f"[convert] {len(successes)} successes -> {success_out}")


if __name__ == "__main__":
    main()
