"""Tests for monthly learning report."""

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
from cauterule.observe.monthly_report import generate_monthly_report
from cauterule.store.manager import StoreManager


def _rule(
    rid: str,
    hit_count: int = 0,
    confidence: float = 0.8,
    tags: tuple[str, ...] = (),
    failures_prevented: tuple[str, ...] = (),
    successes_broken: tuple[str, ...] = (),
    precision: float = 0.0,
    recall: float = 0.0,
    status: Status = "active",
) -> StandingRule:
    ev = (
        ReplayEvidence(
            failures_prevented=failures_prevented,
            successes_broken=successes_broken,
            precision=precision,
            recall=recall,
        )
        if failures_prevented or successes_broken
        else None
    )
    return StandingRule(
        id=rid,
        when=RuleWhen(trigger="test trigger"),
        do=RuleDo(directive="test directive", because="test"),
        confidence=confidence,
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
        tags=tags,
    )


def test_generate_monthly_report_empty(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    report = generate_monthly_report(store)
    assert report.startswith("# Monthly Learning Report")
    assert "Total Rules" in report


def test_generate_monthly_report_active_rules(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    store.add_rule(_rule("R-001", hit_count=10, confidence=0.95, tags=("git",)))
    store.add_rule(_rule("R-002", hit_count=5, confidence=0.80, tags=("git",)))
    report = generate_monthly_report(store)
    assert "2" in report  # Total Rules
    assert "git" in report
    assert "Coverage Score" in report


def test_generate_monthly_report_with_retired(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    store.add_rule(_rule("R-001", hit_count=10, tags=("git",)))
    from dataclasses import replace

    retired = replace(_rule("R-002"), status="retired")
    store.add_rule(retired)
    report = generate_monthly_report(store)
    assert "2" in report  # Total Rules
    assert "1" in report  # Active


def test_generate_monthly_report_leaderboard(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    store.add_rule(
        _rule(
            "R-001",
            hit_count=10,
            failures_prevented=("a", "b", "c"),
            precision=0.9,
            recall=0.8,
        )
    )
    report = generate_monthly_report(store)
    assert "Most Prevented Failures" in report
    assert "R-001" in report
    assert "Top Coverage Gaps" in report


def test_generate_monthly_report_includes_sections(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    store.add_rule(_rule("R-001", hit_count=3))
    report = generate_monthly_report(store)
    assert "## Overview" in report
    assert "## Domain Coverage" in report
    assert "## Most Prevented Failures" in report
    assert "## Top Coverage Gaps" in report
