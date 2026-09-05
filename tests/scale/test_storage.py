"""Storage churn benchmark — YAML + git manageable after frequent promote/retire."""

from __future__ import annotations

import shutil
import time
from pathlib import Path

from cauterule.models.rule import Provenance, RuleDo, RuleWhen, StandingRule
from cauterule.store.manager import StoreManager


def _rule(tid: str, status: str = "active") -> StandingRule:
    return StandingRule(
        id=tid,
        when=RuleWhen(trigger="git push fails"),
        do=RuleDo(directive="pull --rebase"),
        confidence=0.9,
        provenance=Provenance(
            source_trajectory="t.json",
            extracted_by="test",
            extract_timestamp="t",
            extraction_pass=1,
        ),
        status=status,
        promoted_at="t",
    )


def test_storage_churn(tmp_path: Path) -> None:
    base = tmp_path / "rules"
    m = StoreManager(str(base))
    for i in range(100):
        m.add_rule(_rule(f"R-{i:04d}"))
    start = time.time()
    for i in range(50):
        m.retire_rule(f"R-{i:04d}", "retired for test")
    for i in range(50, 100):
        m.add_rule(_rule(f"R-NEW-{i:04d}"))
    for i in range(50):
        m.add_rule(_rule(f"R-REP-{i:04d}"))
    elapsed = time.time() - start
    rules = m.list_rules()
    assert len(rules) == 200
    assert elapsed < 5.0, f"storage churn took {elapsed:.2f}s (expected <5s)"
    shutil.rmtree(base)


def test_storage_yaml_consistency(tmp_path: Path) -> None:
    base = tmp_path / "rules"
    m = StoreManager(str(base))
    for i in range(50):
        m.add_rule(_rule(f"R-F{i:04d}"))
    for i in range(25):
        m.retire_rule(f"R-F{i:04d}", "cleanup")
    active = m.list_rules(status="active")
    retired = m.list_rules(status="retired")
    assert len(active) == 25
    assert len(retired) == 25
