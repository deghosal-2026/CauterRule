"""Tests for per-rule hit counter."""

from __future__ import annotations

from pathlib import Path

from cauterule.models.rule import Provenance, RuleDo, RuleWhen, StandingRule
from cauterule.observe.hits import get_hit_counts
from cauterule.store.manager import StoreManager


def _rule(rid: str, hit_count: int = 0) -> StandingRule:
    return StandingRule(
        id=rid,
        when=RuleWhen(trigger="test trigger"),
        do=RuleDo(directive="test directive", because="test"),
        confidence=0.8,
        provenance=Provenance(
            source_trajectory="T-1",
            extracted_by="test",
            extract_timestamp="2025-01-01T00:00:00",
            extraction_pass=1,
        ),
        status="active",
        promoted_at="2025-01-02T00:00:00",
        hit_count=hit_count,
    )


def test_get_hit_counts(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    store.add_rule(_rule("R-001", hit_count=5))
    store.add_rule(_rule("R-002", hit_count=0))
    store.add_rule(_rule("R-003", hit_count=12))

    counts = get_hit_counts(store)
    assert counts == {"R-001": 5, "R-002": 0, "R-003": 12}


def test_get_hit_counts_empty(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    assert get_hit_counts(store) == {}


def test_get_hit_counts_retired_included(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    store.add_rule(_rule("R-A", hit_count=3))
    retired = _rule("R-R", hit_count=1)
    from dataclasses import replace

    retired = replace(retired, status="retired")
    store.add_rule(retired)

    counts = get_hit_counts(store)
    assert "R-R" in counts
    assert counts["R-R"] == 1
