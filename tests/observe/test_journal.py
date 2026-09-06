"""Tests for learning journal generation."""

from __future__ import annotations

from pathlib import Path

from cauterule.models.rule import Provenance, RuleDo, RuleWhen, StandingRule
from cauterule.observe.journal import generate_journal
from cauterule.store.manager import StoreManager


def _rule(
    rid: str,
    trigger: str = "test trigger",
    directive: str = "test directive",
    tags: tuple[str, ...] = (),
) -> StandingRule:
    return StandingRule(
        id=rid,
        when=RuleWhen(trigger=trigger),
        do=RuleDo(directive=directive, because="test"),
        confidence=0.85,
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


def test_generate_journal_empty(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    journal = generate_journal(store)
    assert journal.startswith("# Learning Journal")


def test_generate_journal_single_rule(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    store.add_rule(_rule("R-001"))
    journal = generate_journal(store)
    assert "R-001" in journal
    assert "test trigger" in journal
    assert "test directive" in journal
    assert "0.85" in journal


def test_generate_journal_with_tags(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    store.add_rule(_rule("R-001", tags=("git", "push")))
    journal = generate_journal(store)
    assert "git, push" in journal


def test_generate_journal_multiple_rules(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    store.add_rule(_rule("R-001", trigger="push", directive="pull"))
    store.add_rule(_rule("R-002", trigger="merge", directive="rebase"))
    journal = generate_journal(store)
    assert "R-001" in journal
    assert "R-002" in journal
    assert "push" in journal
    assert "merge" in journal


def test_generate_journal_retired_included(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    from dataclasses import replace

    retired = replace(_rule("R-001"), status="retired")
    store.add_rule(retired)
    journal = generate_journal(store)
    assert "R-001" in journal
    assert "retired" in journal
