"""Tests for coverage gap detector."""

from __future__ import annotations

from pathlib import Path

from cauterule.models.rule import Provenance, RuleDo, RuleWhen, StandingRule
from cauterule.models.trajectory import Step, Trajectory
from cauterule.observe.coverage_gap import find_coverage_gaps
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


def _trajectory(
    tid: str,
    success: bool = True,
    domain: str | None = None,
) -> Trajectory:
    return Trajectory(
        id=tid,
        timestamp="2025-01-01T00:00:00",
        task="test task",
        steps=(Step(step_number=1, tool="bash", output="ok"),),
        success=success,
        domain=domain,
    )


def test_find_coverage_gaps_empty(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    assert find_coverage_gaps(store, []) == []


def test_find_coverage_gaps_no_gaps(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    store.add_rule(_rule("R-001", tags=("git",)))
    trajs = [
        _trajectory("T-1", success=False, domain="git"),
        _trajectory("T-2", success=False, domain="git"),
    ]
    assert find_coverage_gaps(store, trajs) == []


def test_find_coverage_gaps_domain_gap(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    store.add_rule(_rule("R-001", tags=("git",)))
    trajs = [
        _trajectory("T-1", success=False, domain="docker"),
        _trajectory("T-2", success=False, domain="docker"),
        _trajectory("T-3", success=False, domain="docker"),
    ]
    gaps = find_coverage_gaps(store, trajs)
    assert len(gaps) == 1
    assert gaps[0]["domain"] == "docker"
    assert gaps[0]["failure_count"] == 3


def test_find_coverage_gaps_single_failure_not_gap(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    store.add_rule(_rule("R-001", tags=("git",)))
    trajs = [
        _trajectory("T-1", success=False, domain="docker"),
    ]
    gaps = find_coverage_gaps(store, trajs)
    assert gaps == []


def test_find_coverage_gaps_success_ignored(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    trajs = [
        _trajectory("T-1", success=True, domain="docker"),
        _trajectory("T-2", success=False, domain="docker"),
    ]
    gaps = find_coverage_gaps(store, trajs)
    assert gaps == []
