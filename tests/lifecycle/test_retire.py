"""Tests for automated retirement policy (#543)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, cast

from cauterule.lifecycle.retire import (
    RetirementPolicy,
    apply_candidates,
    evaluate,
)
from cauterule.models.rule import Provenance, RuleDo, RuleWhen, StandingRule
from cauterule.store.manager import StoreManager


def _rule(
    rid: str,
    *,
    trigger: str = "git push fails",
    status: str = "active",
    prevented: int = 0,
    broke: int = 0,
    neutral: int = 0,
    hit_count: int = 0,
    last_match: str | None = None,
    last_outcome_at: str | None = None,
    superseded_by: str | None = None,
) -> StandingRule:
    return StandingRule(
        id=rid,
        when=RuleWhen(trigger=trigger),
        do=RuleDo(directive="pull --rebase"),
        confidence=0.85,
        provenance=Provenance(
            source_trajectory="T-1",
            extracted_by="test",
            extract_timestamp="2025-01-01T00:00:00",
            extraction_pass=1,
        ),
        status=cast(Any, status),
        promoted_at="2025-01-02T00:00:00",
        hit_count=hit_count,
        last_match=last_match,
        prevented_count=prevented,
        broke_count=broke,
        neutral_count=neutral,
        last_outcome_at=last_outcome_at,
        superseded_by=superseded_by,
    )


def _old_timestamp(days: int) -> str:
    ts = datetime.now(UTC) - timedelta(days=days)
    return ts.strftime("%Y-%m-%dT%H:%M:%SZ")


def test_harmful_rule_detected() -> None:
    rules = [_rule("R-H", trigger="fails", broke=15, prevented=2)]
    cands = evaluate(rules)
    assert len(cands) == 1
    assert cands[0].rule_id == "R-H"
    assert cands[0].reason == "auto:harmful"


def test_harmful_requires_min_evidence() -> None:
    # 1-for-1 new rule is never retired (#543 acceptance).
    rules = [_rule("R-N", broke=1, prevented=1)]
    assert evaluate(rules) == []


def test_stale_rule_detected() -> None:
    rules = [
        _rule(
            "R-S",
            trigger="fails",  # low specificity
            hit_count=1,
            last_match=_old_timestamp(200),
            last_outcome_at=_old_timestamp(200),
        )
    ]
    cands = evaluate(rules)
    assert len(cands) == 1
    assert cands[0].reason == "auto:stale"


def test_stale_requires_low_specificity() -> None:
    # A specific rule, even old, is NOT stale (needs breadth too).
    rules = [
        _rule(
            "R-SPEC",
            trigger="git push fails permission denied",
            hit_count=1,
            last_match=_old_timestamp(200),
            last_outcome_at=_old_timestamp(200),
        )
    ]
    assert evaluate(rules) == []


def test_healthy_rule_not_candidate() -> None:
    rules = [
        _rule(
            "R-OK",
            trigger="git push fails permission denied",
            prevented=10,
            broke=1,
            hit_count=5,
            last_match=_old_timestamp(1),
            last_outcome_at=_old_timestamp(1),
        )
    ]
    assert evaluate(rules) == []


def test_dry_run_default_mutates_nothing(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    store.add_rule(_rule("R-STALE", trigger="fails", hit_count=0, last_match=None))
    rules_before = store.list_rules()
    cands = evaluate(rules_before)
    assert cands  # candidate exists
    # No mutation: the rule file is byte-identical after dry-run.
    path = tmp_path / "rules" / "R-STALE.yaml"
    before = path.read_bytes()
    # evaluate is pure; no mutation occurs
    assert path.read_bytes() == before
    assert cast(Any, store.get_rule("R-STALE")).status == "active"


def test_apply_candidates_retires(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    store.add_rule(_rule("R-STALE", trigger="fails", hit_count=0, last_match=None))
    store.add_rule(_rule("R-HARM", trigger="fails", broke=12, prevented=1))
    store.add_rule(_rule("R-OK", trigger="git push fails permission denied", prevented=5))
    cands = evaluate(store.list_rules())
    retired = apply_candidates(store, cands, audit_log=True)
    assert set(retired) == {"R-STALE", "R-HARM"}
    stale = store.get_rule("R-STALE")
    assert stale is not None
    assert stale.status == "retired"
    assert stale.retirement_reason == "auto:stale"
    assert cast(Any, store.get_rule("R-OK")).status == "active"
    # audit log written
    log = (tmp_path / "rules" / "outcomes" / "retirements.jsonl").read_text(encoding="utf-8")
    assert "R-STALE" in log and "R-HARM" in log


def test_superseded_rule_never_retired() -> None:
    rules = [_rule("R-MID", trigger="fails", broke=20, superseded_by="R-NEW")]
    assert evaluate(rules) == []


def test_policy_overrides() -> None:
    # With stale_days=1, a rule idle for 5 days with a VAGUE trigger qualifies.
    rules = [_rule("R-IDLE", trigger="fails", hit_count=1, last_match=_old_timestamp(5))]
    policy = RetirementPolicy(stale_days=1, stale_specificity=0.3)
    cands = evaluate(rules, policy)
    assert len(cands) == 1
    assert cands[0].reason == "auto:stale"
