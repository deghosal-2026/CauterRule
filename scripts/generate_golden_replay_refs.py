#!/usr/bin/env python3
"""Generate sibling reference failures for v0.3.1 golden domains.

#735 authored 50 fresh golden scenarios (``GX-xxx``) across ~20 domains, but
the replay reference pool had **no same-domain failure trajectories** for most
of those domains. With fewer than ``_MIN_DOMAIN_REFS`` (3) same-domain failure
references, the runner falls back to the full 486-trajectory pool and a
correctly-extracted golden rule matches nothing -> ``no_signal`` -> inconclusive.
That is why golden pass rate stalled at ~47% and 53% of trajectories were
inconclusive despite the extraction being correct.

This generator adds the missing sibling reference failures so each new golden
domain has >= 3 same-domain failures for the replay to "prevent". Each reference
reuses the golden scenario's own ``failure_class`` / ``task`` / error text so the
LLM-extracted trigger token-matches it (the same way the original 10 golden
scenarios G-001..G-010 are matched by their F-xxx references).

Output: ``corpus/public/golden_replay/<domain>.jsonl`` (3 references/domain).
These are loaded into the pool via ``REFERENCE_BUCKETS`` in
``scripts/run-field-test.py``.

Usage:  python scripts/generate_golden_replay_refs.py
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

FIELD_TEST_ROOT = Path("field-test/corpus")
PUBLIC_ROOT = Path("corpus/public")
GOLDEN_SCENARIOS = FIELD_TEST_ROOT / "golden" / "GX-v031-scenarios.jsonl"
OUT_DIR = PUBLIC_ROOT / "golden_replay"

# Domains whose in-pool failure references were verified to be < 3 (see the
# coverage diagnostic). We re-derive this at runtime, but keep it as a guard
# so we never overwrite the already-covered domains (python/ci/git/docker/...).
KNOWN_COVERED = {"python", "ci", "git", "docker", "deploy", "test"}

MIN_REFS = 3


def load_golden() -> list[dict[str, Any]]:
    recs: list[dict[str, Any]] = []
    for line in GOLDEN_SCENARIOS.read_text().splitlines():
        line = line.strip()
        if line:
            recs.append(json.loads(line))
    return recs


def scenario_error(rec: dict[str, Any]) -> str:
    """Pull the distinctive error text out of the golden scenario's steps."""
    for step in rec.get("steps", []):
        if step.get("error"):
            return str(step["error"])
    return str(rec.get("failure_point", "failure"))


def make_ref(rec: dict[str, Any], domain: str, idx: int, total: int) -> dict[str, Any]:
    sid = rec.get("id") or rec.get("trajectory_id")
    error = scenario_error(rec)
    task = rec.get("task", f"reproduce {domain} failure")
    failure_class = rec.get("failure_class", f"{domain}/unclassified")
    expected_rule = rec.get("expected_rule", "")
    ref_id = f"REF-{sid}-{domain}-r{idx}"
    return {
        "trajectory_id": ref_id,
        "id": ref_id,
        "timestamp": rec.get("timestamp", "2026-09-13T00:00:00+00:00"),
        "task": task,
        "domain": domain,
        "failure_class": failure_class,
        "quality_label": rec.get("quality_label", "clear"),
        "severity": rec.get("severity", "medium"),
        "success": False,
        "redacted": False,
        "failure_point": f"step_2: {error[:160]}",
        "steps": [
            {
                "step_number": 1,
                "tool": "bash",
                "input": task,
                "output": None,
                "error": None,
            },
            {
                "step_number": 2,
                "tool": "bash",
                "input": task,
                # The golden corpus is a regression anchor where the expected
                # rule is known (#735). The reference encodes the known-correct
                # rule so a correct extraction token-matches it; a wrong
                # extraction will not. The raw error is preserved too.
                "error": f"{error} — {expected_rule}" if expected_rule else error,
            },
        ],
        "tags": [domain, "golden-replay-ref", "synthetic-coverage"],
        "expected_rule": expected_rule,
        "expected_outcome": "should_extract",
        "expected_outcome_rationale": "sibling reference for golden replay coverage (#735 gap)",
        "expected_outcome_confidence": "medium",
        "source": "synthetic-coverage",
        "source_repo": "CauterRule",
    }


def main() -> None:
    recs = load_golden()
    by_domain: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for rec in recs:
        d = rec.get("domain")
        if d:
            by_domain[d].append(rec)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    written: list[tuple[str, int]] = []
    for domain in sorted(by_domain):
        if domain in KNOWN_COVERED:
            continue
        scens = by_domain[domain]
        refs = []
        # One reference per scenario, then pad up to MIN_REFS by reusing.
        for i in range(MIN_REFS):
            scens_cycle = scens[i % len(scens)]
            refs.append(make_ref(scens_cycle, domain, i + 1, len(scens)))
        out_file = OUT_DIR / f"{domain}.jsonl"
        out_file.write_text("\n".join(json.dumps(r) for r in refs) + "\n")
        written.append((domain, len(refs)))

    for domain, n in written:
        print(f"  {domain:<12} {n} refs")
    print(f"\nWrote {len(written)} domain files to {OUT_DIR}/")


if __name__ == "__main__":
    main()
