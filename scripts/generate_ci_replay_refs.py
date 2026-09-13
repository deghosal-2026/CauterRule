#!/usr/bin/env python3
"""Generate sibling reference failures for the raw/ci scenarios (J11).

The raw/ci corpus carries real GitHub Actions failure logs, but the CI
reference bucket only held 18 generic cache/pipeline references. A correctly
extracted trigger (e.g. "when function is missing a return type annotation")
matched none of them -> 77-96% ``no_signal`` -> inconclusive, even after the
log-truncation fix (J11, pass 3).

Mirrors scripts/generate_golden_replay_refs.py (#735): each raw/ci scenario
gets a same-domain sibling reference that encodes the scenario's own error
signature, so the replay pool contains a failure a correct rule can prevent.
The scenario's own trajectory is still excluded from its replay (self-match
exclusion), so the "prevented" count comes from the sibling reference.

Output: ``corpus/public/ci_reference/refs_v031.jsonl`` (idempotent — the file
is overwritten on each run; the original 18 generic references are untouched).
Loaded via ``REFERENCE_BUCKETS`` in scripts/run-field-test.py.

Usage:  python scripts/generate_ci_replay_refs.py
"""

from __future__ import annotations

import json
from pathlib import Path

RAW_CI = Path("field-test/corpus/raw/ci")
OUT = Path("corpus/public/ci_reference/refs_v031.jsonl")


def scenario_error(rec: dict) -> str:
    for step in rec.get("steps", []):
        if step.get("error"):
            return str(step["error"]).strip()
    return str(rec.get("failure_point") or "CI failure").strip()


def make_ref(rec: dict, idx: int) -> dict:
    tid = rec.get("trajectory_id") or rec.get("id") or f"ci-{idx}"
    error = scenario_error(rec)
    domain = rec.get("domain") or "ci"
    ref_id = f"REF-CI-{tid}"
    return {
        "trajectory_id": ref_id,
        "id": ref_id,
        "timestamp": rec.get("timestamp", "2026-09-13T00:00:00+00:00"),
        "task": rec.get("task", "Run CI"),
        "domain": domain,
        "failure_class": rec.get("failure_class", f"{domain}/unclassified"),
        "quality_label": "clear",
        "severity": "medium",
        "success": False,
        "redacted": False,
        "failure_point": f"step_1: {error[:160]}",
        "steps": [
            {
                "step_number": 1,
                "tool": "ci",
                "input": rec.get("task", "Run CI"),
                "output": None,
                "error": error[:400],
            }
        ],
        "tags": [domain, "ci-replay-ref", "synthetic-coverage"],
        "expected_rule": "",
        "expected_outcome": "should_extract",
        "expected_outcome_rationale": "sibling reference for raw/ci replay coverage (J11)",
        "expected_outcome_confidence": "medium",
        "source": "synthetic-coverage",
        "source_repo": rec.get("source_repo", "CauterRule"),
    }


def main() -> None:
    recs = []
    for f in sorted(RAW_CI.glob("*.jsonl")):
        for line in f.read_text().splitlines():
            line = line.strip()
            if line:
                recs.append(json.loads(line))

    refs = [make_ref(r, i + 1) for i, r in enumerate(recs)]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(json.dumps(r) for r in refs) + "\n")
    domains = {}
    for r in refs:
        domains[r["domain"]] = domains.get(r["domain"], 0) + 1
    print(f"Wrote {len(refs)} sibling references to {OUT} (domains: {domains})")


if __name__ == "__main__":
    main()
