"""Tests for the v0.3.0 reference corpora added by #698.

Closes the #690 reference-coverage gap for the agent/lifecycle/mcp target
domains and adds the paraphrase-diversity set (#689 validation).
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pytest

from cauterule.models.trajectory import Trajectory

_REPO = Path(__file__).resolve().parents[2]
_PUBLIC = _REPO / "corpus" / "public"

# (dir, required failure-class domain prefix)
_REFERENCE_SETS = {
    "adapters": "agent",
    "lifecycle": "lifecycle",
    "mcp": "mcp",
}


def _load(path: Path) -> list[dict[str, object]]:
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


@pytest.mark.parametrize("name,domain", _REFERENCE_SETS.items())
def test_reference_set_parses_and_balances(name: str, domain: str) -> None:
    records = _load(_PUBLIC / name / "reference.jsonl")
    trajectories = [Trajectory.from_dict(r) for r in records]
    assert len(trajectories) >= 3
    counts = Counter(t.success for t in trajectories)
    # #707: every source must carry both failure and success trajectories.
    assert counts[True] > 0 and counts[False] > 0
    failure_domains = {(t.failure_class or "").split("/")[0] for t in trajectories if not t.success}
    assert domain in failure_domains


def test_paraphrase_diversity_has_three_variants_per_class() -> None:
    records = _load(
        _PUBLIC / "reference-expansion" / "paraphrase-diversity" / "paraphrase-diversity.jsonl"
    )
    for record in records:
        Trajectory.from_dict(record)
    by_class: Counter[str] = Counter(str(r["failure_class"]) for r in records)
    assert len(by_class) >= 3
    assert all(count >= 3 for count in by_class.values()), by_class
