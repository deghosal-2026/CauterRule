"""Tests for coverage frontier suggestion."""

from __future__ import annotations

from pathlib import Path

from cauterule.models.rule import Provenance, RuleDo, RuleWhen, StandingRule
from cauterule.models.trajectory import Step, Trajectory
from cauterule.observe.coverage_frontier import suggest_next_frontier
from cauterule.store.manager import StoreManager


def _rule(rid: str, tags: tuple[str, ...] = ()) -> StandingRule:
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
        tags=tags,
    )


def _trajectory(tid: str, success: bool = False, domain: str | None = None) -> Trajectory:
    return Trajectory(
        id=tid,
        timestamp="2025-01-01T00:00:00",
        task="test task",
        steps=(Step(step_number=1, tool="bash", output="ok"),),
        success=success,
        domain=domain,
    )


def test_suggest_next_frontier_uncovered_domain(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    store.add_rule(_rule("R-001", tags=("git",)))
    trajs = [
        _trajectory("T-1", domain="docker"),
        _trajectory("T-2", domain="docker"),
        _trajectory("T-3", domain="docker"),
    ]
    suggestion = suggest_next_frontier(store, trajs)
    assert "docker" in suggestion
    assert "3" in suggestion


def test_suggest_next_frontier_all_covered(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    store.add_rule(_rule("R-001", tags=("git",)))
    trajs = [
        _trajectory("T-1", domain="git"),
        _trajectory("T-2", domain="git"),
    ]
    suggestion = suggest_next_frontier(store, trajs)
    assert "All domains are covered" in suggestion


def test_suggest_next_frontier_empty_trajs(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    suggestion = suggest_next_frontier(store, [])
    assert "All domains are covered" in suggestion


def test_suggest_next_frontier_no_rules(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    trajs = [
        _trajectory("T-1", domain="docker"),
        _trajectory("T-2", domain="docker"),
    ]
    suggestion = suggest_next_frontier(store, trajs)
    assert "docker" in suggestion


def test_suggest_next_frontier_multiple_gaps(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    store.add_rule(_rule("R-001", tags=("git",)))
    trajs = [
        _trajectory("T-1", domain="docker"),
        _trajectory("T-2", domain="docker"),
        _trajectory("T-3", domain="docker"),
        _trajectory("T-4", domain="kubernetes"),
    ]
    suggestion = suggest_next_frontier(store, trajs)
    assert "docker" in suggestion
