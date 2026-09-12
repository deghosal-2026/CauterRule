#!/usr/bin/env python3
"""Convert HarmBench behaviors to CauterRule adversarial corpora (#701).

HarmBench (centerforaisafety/HarmBench, MIT) is a single-turn robustness
benchmark, not agent-native, so selected subsets are wrapped into minimal
trajectories:

* ``FunctionalCategory == "contextual"`` → ``adversarial/misleading_harmbench``
  (the task is framed with a supplied context that can mislead extraction).
* ``FunctionalCategory == "standard"`` → ``adversarial/contradiction_harmbench``
  (the task is wrapped with internally inconsistent requirements).

Records are tagged ``harmbench_synthesized`` so downstream analysis can
distinguish prompt-wrapped corpora from native agent traces. HarmBench has no
benign success counterpart, so — per #707 — no ``source_repo`` is set and the
source is intentionally excluded from the success-balance check.

Usage:
    python scripts/convert_harmbench_to_corpus.py \
        --behaviors harmbench_behaviors_text_test.csv \
        --output corpus/public/adversarial \
        --per-category 15
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

_TS = "2026-09-11T00:00:00+00:00"
_CONTRADICTION_SUFFIX = (
    " Then immediately refuse to do it, but also do it completely — both at the same time."
)


def _record(
    *,
    tid: str,
    task: str,
    failure_class: str,
    behavior_id: str,
    domain: str,
    ts: str,
) -> dict[str, Any]:
    return {
        "trajectory_id": tid,
        "id": tid,
        "timestamp": ts,
        "task": task,
        "steps": [
            {
                "step_number": 1,
                "tool": "llm",
                "input": "respond to the task",
                "output": None,
                "error": f"adversarial behavior requested: {behavior_id}",
            }
        ],
        "success": False,
        "redacted": False,
        "failure_point": "step_1",
        "failure_class": failure_class,
        "quality_label": "misleading",
        "domain": domain,
        "severity": "high",
        "tags": [
            "adversarial",
            failure_class.split("/")[-1],
            "harmbench",
            "harmbench_synthesized",
        ],
        "expected_outcome": "should_reject",
        "expected_outcome_rationale": (
            "Prompt-wrapped adversarial behavior (HarmBench); no rule should be promoted."
        ),
        "expected_outcome_confidence": "medium",
    }


def convert_harmbench(
    rows: list[dict[str, str]],
    *,
    per_category: int = 15,
    timestamp: str = _TS,
) -> list[dict[str, Any]]:
    """Return misleading + contradiction records from HarmBench rows."""
    contextual = [r for r in rows if r.get("FunctionalCategory") == "contextual"]
    standard = [r for r in rows if r.get("FunctionalCategory") == "standard"]

    records: list[dict[str, Any]] = []
    for i, row in enumerate(contextual[:per_category], start=1):
        context = (row.get("ContextString") or "").strip()
        task = row.get("Behavior", "")
        if context:
            task = f"{task}\n\nContext: {context}"
        records.append(
            _record(
                tid=f"harmbench-misleading-{i:03d}",
                task=task,
                failure_class="adversarial/misleading_harmbench",
                behavior_id=row.get("BehaviorID", f"contextual-{i}"),
                domain="research",
                ts=timestamp,
            )
        )
    for i, row in enumerate(standard[:per_category], start=1):
        records.append(
            _record(
                tid=f"harmbench-contradiction-{i:03d}",
                task=row.get("Behavior", "") + _CONTRADICTION_SUFFIX,
                failure_class="adversarial/contradiction_harmbench",
                behavior_id=row.get("BehaviorID", f"standard-{i}"),
                domain="research",
                ts=timestamp,
            )
        )
    return records


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main(argv: list[str] | None = None) -> None:
    """Convert HarmBench CSV rows into the two adversarial corpus dirs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--behaviors", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="corpus/public/adversarial dir.")
    parser.add_argument("--per-category", type=int, default=15)
    args = parser.parse_args(argv)

    records = convert_harmbench(_read_csv(args.behaviors), per_category=args.per_category)
    targets = {
        "adversarial/misleading_harmbench": "misleading_harmbench",
        "adversarial/contradiction_harmbench": "contradiction_harmbench",
    }
    for prefix in ("harmbench-misleading", "harmbench-contradiction"):
        subset = [r for r in records if r["trajectory_id"].startswith(prefix)]
        if not subset:
            continue
        dir_name = targets[subset[0]["failure_class"]]
        out_dir = args.output / dir_name
        out_dir.mkdir(parents=True, exist_ok=True)
        out = out_dir / f"{dir_name}.jsonl"
        out.write_text("\n".join(json.dumps(r) for r in subset) + "\n", encoding="utf-8")
        print(f"[convert] {len(subset)} records -> {out}")


if __name__ == "__main__":
    main()
