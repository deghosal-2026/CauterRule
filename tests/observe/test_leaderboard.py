"""Tests for failure-pattern leaderboard."""

from __future__ import annotations

from pathlib import Path

from cauterule.models.rule import (
    Provenance,
    ReplayEvidence,
    RuleDo,
    RuleWhen,
    StandingRule,
)
from cauterule.observe.leaderboard import get_leaderboard
from cauterule.store.manager import StoreManager


def _rule_with_evidence(
    rid: str,
    failures_prevented: tuple[str, ...] = (),
    successes_broken: tuple[str, ...] = (),
    precision: float = 0.0,
    recall: float = 0.0,
) -> StandingRule:
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
            replay_evidence=ReplayEvidence(
                failures_prevented=failures_prevented,
                successes_broken=successes_broken,
                precision=precision,
                recall=recall,
            ),
        ),
        status="active",
        promoted_at="2025-01-02T00:00:00",
    )


def test_leaderboard_most_prevented(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    store.add_rule(
        _rule_with_evidence("R-001", failures_prevented=("a", "b", "c"))
    )
    store.add_rule(_rule_with_evidence("R-002", failures_prevented=("d",)))

    lb = get_leaderboard(store)
    assert lb["most_prevented"][0]["id"] == "R-001"
    assert lb["most_prevented"][0]["count"] == 3


def test_leaderboard_most_broken(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    store.add_rule(_rule_with_evidence("R-001", successes_broken=("a", "b")))
    store.add_rule(_rule_with_evidence("R-002", successes_broken=("x", "y", "z")))

    lb = get_leaderboard(store)
    assert lb["most_broken"][0]["id"] == "R-002"
    assert lb["most_broken"][0]["count"] == 3


def test_leaderboard_top_gaps(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    store.add_rule(
        _rule_with_evidence("R-001", failures_prevented=("a",), recall=0.3)
    )
    store.add_rule(
        _rule_with_evidence("R-002", failures_prevented=("b",), recall=0.9)
    )

    lb = get_leaderboard(store)
    assert lb["top_gaps"][0]["id"] == "R-001"
    assert lb["top_gaps"][0]["recall"] == 0.3


def test_leaderboard_no_evidence(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    r = StandingRule(
        id="R-001",
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
    )
    store.add_rule(r)
    lb = get_leaderboard(store)
    assert lb["most_prevented"] == []
    assert lb["most_broken"] == []
    assert lb["top_gaps"] == []


def test_leaderboard_empty(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    lb = get_leaderboard(store)
    assert lb["most_prevented"] == []
    assert lb["most_broken"] == []
    assert lb["top_gaps"] == []
