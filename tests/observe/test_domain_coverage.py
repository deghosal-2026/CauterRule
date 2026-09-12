"""Tests for domain-level coverage score."""

from __future__ import annotations

from pathlib import Path

from cauterule.models.rule import Provenance, RuleDo, RuleWhen, StandingRule
from cauterule.observe.domain_coverage import domain_coverage
from cauterule.store.manager import StoreManager


def _rule(rid: str, hit_count: int = 0, tags: tuple[str, ...] = ()) -> StandingRule:
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
        tags=tags,
    )


def test_domain_coverage_empty(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    assert domain_coverage(store) == {}


def test_domain_coverage_single_domain(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    store.add_rule(_rule("R-001", hit_count=5, tags=("git",)))
    store.add_rule(_rule("R-002", hit_count=0, tags=("git",)))
    cov = domain_coverage(store)
    assert cov["git"] == 0.5


def test_domain_coverage_multiple_domains(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    store.add_rule(_rule("R-001", hit_count=3, tags=("git",)))
    store.add_rule(_rule("R-002", hit_count=0, tags=("docker",)))
    store.add_rule(_rule("R-003", hit_count=1, tags=("docker",)))
    cov = domain_coverage(store)
    assert cov["git"] == 1.0
    assert cov["docker"] == 0.5


def test_domain_coverage_all_covered(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    store.add_rule(_rule("R-001", hit_count=5, tags=("git",)))
    store.add_rule(_rule("R-002", hit_count=3, tags=("git",)))
    cov = domain_coverage(store)
    assert cov["git"] == 1.0


def test_domain_coverage_retired_excluded(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    from dataclasses import replace

    retired = replace(_rule("R-001", hit_count=5, tags=("git",)), status="retired")
    store.add_rule(retired)
    store.add_rule(_rule("R-002", hit_count=0, tags=("git",)))
    cov = domain_coverage(store)
    assert cov["git"] == 0.0
