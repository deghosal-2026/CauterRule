"""Tests for per-rule outcome tracking (#542)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import pytest

from cauterule.models.rule import Provenance, RuleDo, RuleWhen, StandingRule
from cauterule.observe.outcomes import (
    apply_report_outcomes,
    record_outcome,
    rule_outcome_summary,
    sparkline,
)
from cauterule.store.manager import StoreManager


def _rule(rid: str = "R-OUT") -> StandingRule:
    return StandingRule(
        id=rid,
        when=RuleWhen(trigger="git push fails"),
        do=RuleDo(directive="pull --rebase"),
        confidence=0.85,
        provenance=Provenance(
            source_trajectory="T-1",
            extracted_by="test",
            extract_timestamp="2025-01-01T00:00:00",
            extraction_pass=1,
        ),
        status="active",
        promoted_at="2025-01-02T00:00:00",
    )


def test_record_outcome_counts(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    store.add_rule(_rule("R-A"))
    record_outcome(store, "R-A", "prevented", trajectory_id="T-p1")
    record_outcome(store, "R-A", "broke", trajectory_id="T-b1")
    record_outcome(store, "R-A", "broke", trajectory_id="T-b2")
    record_outcome(store, "R-A", "neutral", trajectory_id="T-n1")
    rule = store.get_rule("R-A")
    assert rule is not None
    assert rule.prevented_count == 1
    assert rule.broke_count == 2
    assert rule.neutral_count == 1
    assert rule.last_outcome == "neutral"
    assert rule.outcome_trend == (1, -1, -1, 0)


def test_record_outcome_idempotent(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    store.add_rule(_rule("R-B"))
    record_outcome(store, "R-B", "prevented", trajectory_id="T-same")
    record_outcome(store, "R-B", "prevented", trajectory_id="T-same")
    rule = store.get_rule("R-B")
    assert rule is not None
    assert rule.prevented_count == 1  # no double count


def test_record_outcome_invalid(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    store.add_rule(_rule("R-C"))
    with pytest.raises(ValueError, match="outcome must be one of"):
        record_outcome(store, "R-C", "maybe")
    with pytest.raises(ValueError, match="not found"):
        record_outcome(store, "R-MISSING", "prevented")


def test_trend_capped(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    store.add_rule(_rule("R-D"))
    for i in range(60):
        record_outcome(store, "R-D", "prevented", trajectory_id=f"T-{i}")
    rule = store.get_rule("R-D")
    assert rule is not None
    assert len(rule.outcome_trend) == 50  # capped


def test_log_written_and_idempotent_across_reload(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    store.add_rule(_rule("R-E"))
    record_outcome(store, "R-E", "prevented", trajectory_id="T-x")
    # Reload the store from disk then re-record same trajectory: still 1.
    store2 = StoreManager(str(tmp_path / "rules"))
    record_outcome(store2, "R-E", "prevented", trajectory_id="T-x")
    rule = store2.get_rule("R-E")
    assert rule is not None
    assert rule.prevented_count == 1
    log = (tmp_path / "rules" / "outcomes" / "R-E.jsonl").read_text(encoding="utf-8")
    assert '"T-x"' in log


def test_apply_report_outcomes(tmp_path: Path) -> None:
    from types import SimpleNamespace

    store = StoreManager(str(tmp_path / "rules"))
    store.add_rule(_rule("R-F"))
    report = SimpleNamespace(
        replay_trace=(
            {"trajectory_id": "T-1", "outcome": "prevented"},
            {"trajectory_id": "T-2", "outcome": "broken"},
            {"trajectory_id": "T-3", "outcome": "no_effect"},
            {"trajectory_id": "T-1", "outcome": "prevented"},  # dup
        )
    )
    counts = apply_report_outcomes(store, "R-F", cast(Any, report))
    assert counts == {"prevented": 1, "broke": 1, "neutral": 1}
    rule = store.get_rule("R-F")
    assert rule is not None
    assert rule.prevented_count == 1
    assert rule.broke_count == 1
    assert rule.neutral_count == 1


def test_rule_outcome_summary(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    store.add_rule(_rule("R-G"))
    record_outcome(store, "R-G", "prevented", trajectory_id="T-a")
    record_outcome(store, "R-G", "prevented", trajectory_id="T-b")
    record_outcome(store, "R-G", "broke", trajectory_id="T-c")
    summary = rule_outcome_summary(store, "R-G")
    assert summary["prevented"] == 2
    assert summary["broke"] == 1
    assert summary["prevented_rate"] == round(2 / 3, 4)
    assert summary["trend"] == [1, 1, -1]


def test_sparkline() -> None:
    assert sparkline((1, 0, -1, 1)) == "█▄▁█"
    assert sparkline(()) == ""


def test_legacy_rule_defaults(tmp_path: Path) -> None:
    # A rule written before outcomes existed round-trips with zero counters.
    store = StoreManager(str(tmp_path / "rules"))
    store.add_rule(_rule("R-H"))
    rule = store.get_rule("R-H")
    assert rule is not None
    assert rule.prevented_count == 0
    assert rule.broke_count == 0
    assert rule.outcome_trend == ()
