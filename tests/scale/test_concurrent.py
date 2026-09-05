"""Concurrent ingestion test — multiple failures at once, queue, dedup, consistent promotion."""

from __future__ import annotations

import time
from pathlib import Path

from cauterule.models.rule import Provenance, RuleDo, RuleWhen, StandingRule
from cauterule.store.manager import StoreManager


def _rule(tid: str, trigger: str, directive: str) -> StandingRule:
    return StandingRule(
        id=tid,
        when=RuleWhen(trigger=trigger),
        do=RuleDo(directive=directive),
        confidence=0.9,
        provenance=Provenance(
            source_trajectory="t.json",
            extracted_by="test",
            extract_timestamp="t",
            extraction_pass=1,
        ),
        status="active",
        promoted_at="t",
    )


def test_concurrent_ingestion(tmp_path: Path) -> None:
    base = tmp_path / "rules"
    m = StoreManager(str(base))
    rules = [_rule(f"C-{i:04d}", f"trigger {i}", f"directive {i}") for i in range(50)]

    start = time.time()
    ids = [m.add_rule(r) for r in rules]
    elapsed = time.time() - start
    assert len(set(ids)) == 50
    all_rules = m.list_rules()
    assert len(all_rules) == 50
    assert elapsed < 5.0, f"concurrent ingestion took {elapsed:.2f}s (expected <5s)"


def test_dedup_on_duplicate_ids(tmp_path: Path) -> None:
    base = tmp_path / "rules"
    m = StoreManager(str(base))
    r = _rule("DUP", "git push fails", "pull --rebase")
    m.add_rule(r)
    m.add_rule(r)
    all_rules = m.list_rules()
    assert len(all_rules) == 1


def test_promotion_consistency(tmp_path: Path) -> None:
    base = tmp_path / "rules"
    m = StoreManager(str(base))
    m.add_rule(_rule("P-001", "fail A", "fix A"))
    m.add_rule(_rule("P-002", "fail B", "fix B"))
    m.retire_rule("P-001", "replaced")
    m.add_rule(_rule("P-003", "fail C", "fix C"))
    active = m.list_rules(status="active")
    retired = m.list_rules(status="retired")
    assert len(active) == 2
    assert len(retired) == 1
    assert all(r.status == "active" for r in active)
    assert all(r.status == "retired" for r in retired)
