#!/usr/bin/env python3
"""Corpus replay root-cause diagnostics (#690).

Distinguishes, per corpus type, the three possible causes of a 0-pass result:

* **missing references** — ``reference_count`` is 0/under-covered, or the
  target's failure-class domains are absent from the reference set
  (``uncovered_domains``);
* **extraction rejected** — the candidate pre-filter funnel
  (``--results``) shows candidates dying as degenerate/generic rather than
  reaching scoring;
* **matcher threshold** — candidates reach scoring but still 0-pass (visible
  only from a full sweep's results).

Usage:
    python scripts/diagnose_corpus.py
    python scripts/diagnose_corpus.py --results field-test/results/0.3.0/otel/.../results.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.models.trajectory import Trajectory
from cauterule.replay.diagnostics import (
    candidate_funnel,
    diagnose_corpus,
    load_jsonl_trajectories,
)

_REPO = Path(__file__).resolve().parents[1]
_CORPUS = _REPO / "field-test" / "corpus"
_PUBLIC = _REPO / "corpus" / "public"
_V030_TARGETS = ("adapters", "lifecycle", "packs", "mcp", "otel")
_REFERENCE_BUCKETS = (
    "curated/failures/positive",
    "curated/failures/negative",
    "curated/successes",
    "curated/nearmiss",
    "curated/noisy",
    "curated/corrections",
)
# #698: public reference corpora covering the previously-uncovered domains.
# #704: lifecycle_infra extends lifecycle with terraform/infra failures.
# #705: browser extends coverage to WebArena/VisualWebArena browser-tool failures.
# #706: real-world python test failures (BugsInPy).
# #700/#702/#703/#707: success counterparts live in corpus/public/successes/.
_PUBLIC_REFERENCE_DIRS = (
    "adapters",
    "lifecycle",
    "lifecycle_infra",
    "mcp",
    "otel",
    "browser",
    "real-world/bugsinpy",
    "successes",
)


def _load_references() -> list[Trajectory]:
    references: list[Trajectory] = []
    for rel in _REFERENCE_BUCKETS:
        for path in sorted((_CORPUS / rel).glob("*.jsonl")):
            references.extend(load_jsonl_trajectories(path))
    for name in _PUBLIC_REFERENCE_DIRS:
        for path in sorted((_PUBLIC / name).glob("*.jsonl")):
            references.extend(load_jsonl_trajectories(path))
    return references


def _funnel_from_results(path: Path) -> dict[str, int]:
    candidates: list[CandidateRule] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        record: dict[str, Any] = json.loads(stripped)
        for entry in record.get("candidates", []):
            if not isinstance(entry, dict):
                continue
            # results.jsonl nests the extracted fields under "candidate":
            # {"candidate": {"when": <trigger>, "do": <directive>, ...}, ...}
            cand = entry.get("candidate", entry)
            if not isinstance(cand, dict) or not cand.get("when"):
                continue
            candidates.append(
                CandidateRule(
                    when=RuleWhen(
                        trigger=cand["when"], context=tuple(cand.get("context", []))
                    ),
                    do=RuleDo(directive=cand.get("do") or "unknown"),
                    confidence=float(cand.get("confidence", 0.5)),
                )
            )
    funnel = candidate_funnel(candidates)
    return {
        "total": funnel.total,
        "degenerate": funnel.degenerate,
        "generic": funnel.generic,
        "too_short": funnel.too_short,
        "scored": funnel.scored,
    }


def main() -> None:
    """Print reference-coverage diagnostics and an optional candidate funnel."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", action="append", choices=_V030_TARGETS)
    parser.add_argument(
        "--results",
        type=Path,
        default=None,
        help="A results.jsonl to compute the candidate pre-filter funnel for.",
    )
    args = parser.parse_args()

    references = _load_references()
    names = args.corpus or list(_V030_TARGETS)
    report: dict[str, Any] = {"reference_count_total": len(references), "corpora": {}}
    for name in names:
        targets = load_jsonl_trajectories(_CORPUS / name / f"{name}.jsonl")
        diag = diagnose_corpus(name, targets, references)
        report["corpora"][name] = {
            "target_count": diag.target_count,
            "reference_count": diag.reference_count,
            "reference_sufficient": diag.reference_sufficient,
            "uncovered_domains": list(diag.uncovered_domains),
            "reference_domains": diag.reference_domains,
        }
    if args.results is not None:
        report["candidate_funnel"] = _funnel_from_results(args.results)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
