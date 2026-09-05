"""Tests for rule coverage score."""

from __future__ import annotations

from pathlib import Path

from cauterule.models.rule import (
    Provenance,
    ReplayEvidence,
    RuleDo,
    RuleWhen,
    StandingRule,
    Status,
)
from cauterule.observe.coverage_score import compute_coverage_score
from cauterule.store.manager import StoreManager


def _rule(
    rid: str,
    hit_count: int = 0,
    precision: float = 0.0,
    recall: float = 0.0,
    status: Status = "active",
) -> StandingRule:
    ev = (
        ReplayEvidence(
            failures_prevented=("f1",),
            successes_broken=(),
            precision=precision,
            recall=recall,
        )
        if precision > 0 or recall > 0
        else None
    )
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
            replay_evidence=ev,
        ),
        status=status,
        promoted_at="2025-01-02T00:00:00",
        hit_count=hit_count,
    )


def test_compute_coverage_score_empty(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    assert compute_coverage_score(store) == 0.0


def test_compute_coverage_score_all_hits(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    store.add_rule(_rule("R-001", hit_count=5, precision=0.9))
    store.add_rule(_rule("R-002", hit_count=3, precision=0.8))
    score = compute_coverage_score(store)
    # coverage_pct=1.0, precision_pct=0.85, non_stale_pct=1.0
    # 0.4*1.0 + 0.4*0.85 + 0.2*1.0 = 0.4 + 0.34 + 0.2 = 0.94
    assert score == 0.94


def test_compute_coverage_score_no_hits(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    store.add_rule(_rule("R-001", hit_count=0, precision=0.0))
    store.add_rule(_rule("R-002", hit_count=0, precision=0.0))
    score = compute_coverage_score(store)
    # coverage_pct=0.0, precision_pct=0.0, non_stale_pct=0.0
    # 0.4*0.0 + 0.4*0.0 + 0.2*0.0 = 0.0
    assert score == 0.0


def test_compute_coverage_score_retired_excluded(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    store.add_rule(_rule("R-001", hit_count=5, precision=0.9))
    store.add_rule(_rule("R-002", hit_count=0, status="retired"))
    score = compute_coverage_score(store)
    # Only active rules count: 1 active with hits
    # coverage_pct=1.0, precision_pct=0.9, non_stale_pct=1.0
    # 0.4*1.0 + 0.4*0.9 + 0.2*1.0 = 0.4 + 0.36 + 0.2 = 0.96
    assert score == 0.96


def test_compute_coverage_score_stale(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    store.add_rule(_rule("R-001", hit_count=5, precision=1.0))
    store.add_rule(_rule("R-002", hit_count=0, precision=0.0))
    store.add_rule(_rule("R-003", hit_count=0, precision=0.0))
    score = compute_coverage_score(store)
    # coverage_pct=1/3≈0.3333, precision_pct=1.0 (only R-001 has evidence), non_stale_pct=1/3≈0.3333
    # 0.4*0.3333 + 0.4*1.0 + 0.2*0.3333 = 0.1333 + 0.4 + 0.0667 = 0.6
    assert score == 0.6
