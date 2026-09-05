"""Tests for last-match timestamp updates."""

from __future__ import annotations

from pathlib import Path

import pytest

from cauterule.models.rule import Provenance, RuleDo, RuleWhen, StandingRule
from cauterule.observe.timestamps import update_last_match
from cauterule.store.manager import StoreManager


def _rule(rid: str, last_match: str | None = None) -> StandingRule:
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
        last_match=last_match,
    )


def test_update_last_match_provided(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    store.add_rule(_rule("R-001"))
    update_last_match(store, "R-001", timestamp="2026-01-01T00:00:00")
    rule = store.get_rule("R-001")
    assert rule is not None
    assert rule.last_match == "2026-01-01T00:00:00"


def test_update_last_match_default(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    store.add_rule(_rule("R-001"))
    update_last_match(store, "R-001")
    rule = store.get_rule("R-001")
    assert rule is not None
    assert rule.last_match is not None
    assert "T" in rule.last_match


def test_update_last_match_overwrites(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    store.add_rule(_rule("R-001", last_match="2025-06-01T00:00:00"))
    update_last_match(store, "R-001", timestamp="2026-01-01T00:00:00")
    rule = store.get_rule("R-001")
    assert rule is not None
    assert rule.last_match == "2026-01-01T00:00:00"


def test_update_last_match_missing_rule(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    with pytest.raises(ValueError, match="not found"):
        update_last_match(store, "R-MISSING")
