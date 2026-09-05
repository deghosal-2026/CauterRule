"""Tests for failure-class coverage."""

from __future__ import annotations

from pathlib import Path

from cauterule.models.rule import Provenance, RuleDo, RuleWhen, StandingRule
from cauterule.models.trajectory import Step, Trajectory
from cauterule.observe.class_coverage import class_coverage
from cauterule.store.manager import StoreManager


def _rule(
    rid: str, tags: tuple[str, ...] = (), taxonomy: str | None = None
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
        ),
        status="active",
        promoted_at="2025-01-02T00:00:00",
        tags=tags,
        taxonomy=taxonomy,
    )


def _trajectory(
    tid: str,
    success: bool = False,
    failure_class: str | None = None,
) -> Trajectory:
    return Trajectory(
        id=tid,
        timestamp="2025-01-01T00:00:00",
        task="test task",
        steps=(Step(step_number=1, tool="bash", output="ok"),),
        success=success,
        failure_class=failure_class,
    )


def test_class_coverage_empty_trajs(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    assert class_coverage(store, []) == {}


def test_class_coverage_recurring_covered_by_tag(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    store.add_rule(_rule("R-001", tags=("network_timeout",)))
    trajs = [
        _trajectory("T-1", failure_class="network_timeout"),
        _trajectory("T-2", failure_class="network_timeout"),
        _trajectory("T-3", failure_class="network_timeout"),
    ]
    cov = class_coverage(store, trajs)
    assert cov["network_timeout"] == 1.0


def test_class_coverage_recurring_uncovered(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    store.add_rule(_rule("R-001", tags=("git",)))
    trajs = [
        _trajectory("T-1", failure_class="docker_fail"),
        _trajectory("T-2", failure_class="docker_fail"),
    ]
    cov = class_coverage(store, trajs)
    assert cov["docker_fail"] == 0.0


def test_class_coverage_single_occurrence_ignored(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    trajs = [
        _trajectory("T-1", failure_class="rare_bug"),
    ]
    cov = class_coverage(store, trajs)
    assert cov == {}


def test_class_coverage_success_ignored(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    trajs = [
        _trajectory("T-1", success=True, failure_class="network"),
        _trajectory("T-2", success=True, failure_class="network"),
    ]
    cov = class_coverage(store, trajs)
    assert cov == {}


def test_class_coverage_covered_by_taxonomy(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    store.add_rule(_rule("R-001", taxonomy="auth_failure"))
    trajs = [
        _trajectory("T-1", failure_class="auth_failure"),
        _trajectory("T-2", failure_class="auth_failure"),
    ]
    cov = class_coverage(store, trajs)
    assert cov["auth_failure"] == 1.0
