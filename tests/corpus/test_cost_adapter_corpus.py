"""Tests for the v0.3.0 cost + adapter corpus targets (#635/#653/#486).

The field-test plan requires:
  - ``field-test/corpus/adapters/`` — 20 trajectories per framework (3 = 60)
    so the §6.1 "adapter capture rate 3/3 frameworks" gate has enough sample.
  - ``field-test/corpus/cost/`` — a *fixed* 1,000-trajectory mixed sample used
    for ``$/1k``/``cost_per_candidate``/``cost_per_promoted_rule`` (§5.4/§7.4).
    The sample must not drift between model sweeps.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pytest

from cauterule.models.trajectory import Trajectory

_REPO = Path(__file__).resolve().parents[2]
_CORPUS = _REPO / "field-test" / "corpus"

_ADAPTER_FRAMEWORKS = ("langgraph", "crewai", "pydanticai")
_ADAPTERS_PER_FRAMEWORK = 20
_COST_SIZE = 1000
_COST_MIX = {
    "success": 300,
    "failure-positive": 300,
    "failure-negative": 200,
    "raw-mixed": 200,
}


def _load(path: Path) -> list[dict[str, object]]:
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def test_adapter_corpus_has_20_per_framework() -> None:
    records = _load(_CORPUS / "adapters" / "adapters.jsonl")
    by_framework = Counter(str(r.get("framework")) for r in records)
    for framework in _ADAPTER_FRAMEWORKS:
        assert by_framework[framework] == _ADAPTERS_PER_FRAMEWORK, by_framework
    assert sum(by_framework.values()) == len(_ADAPTER_FRAMEWORKS) * _ADAPTERS_PER_FRAMEWORK
    # Every adapter trajectory must parse and be an extractable failure.
    for record in records:
        traj = Trajectory.from_dict(record)
        assert traj.success is False
        assert record["expected_outcome"] == "should_extract"


def test_cost_corpus_is_fixed_size_and_mixed() -> None:
    records = _load(_CORPUS / "cost" / "cost.jsonl")
    assert len(records) == _COST_SIZE
    by_kind = Counter(str(r.get("cost_kind")) for r in records)
    assert dict(by_kind) == _COST_MIX, by_kind
    # Mixed expected outcomes drive the $/1k + safety-adjusted accounting.
    by_outcome = Counter(str(r.get("expected_outcome")) for r in records)
    assert by_outcome["should_extract"] > 0
    assert by_outcome["should_silence"] > 0
    assert by_outcome["should_reject"] > 0


@pytest.mark.parametrize("kind", sorted(_COST_MIX))
def test_cost_corpus_records_parse(kind: str) -> None:
    records = [r for r in _load(_CORPUS / "cost" / "cost.jsonl") if r.get("cost_kind") == kind]
    assert records
    for record in records:
        Trajectory.from_dict(record)
