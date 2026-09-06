"""Memory footprint benchmark — <1GB RAM on small corpus."""

from __future__ import annotations

import tracemalloc
from pathlib import Path

from cauterule.models.rule import Provenance, RuleDo, RuleWhen, StandingRule
from cauterule.store.manager import StoreManager


def _rule(tid: str, trigger: str = "git push fails") -> StandingRule:
    return StandingRule(
        id=tid,
        when=RuleWhen(trigger=trigger),
        do=RuleDo(directive="pull --rebase"),
        confidence=0.9,
        provenance=Provenance(
            source_trajectory="t.json",
            extracted_by="test",
            extract_timestamp="t",
            extraction_pass=1,
        ),
        status="active",
        promoted_at="t",
        tags=("git",),
    )


def test_memory_small_corpus(tmp_path: Path) -> None:
    tracemalloc.start()
    base = str(tmp_path / "rules")
    m = StoreManager(base)
    for i in range(100):
        m.add_rule(_rule(f"R-{i:04d}", trigger=f"trigger {i}"))
    rules = m.list_rules()
    _current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    peak_mb = peak / 1024 / 1024
    assert peak_mb < 1024, f"peak memory {peak_mb:.1f}MB (expected <1024MB)"
    assert len(rules) == 100
    print(f"Peak memory: {peak_mb:.1f}MB for 100 rules")


def test_memory_load_large(tmp_path: Path) -> None:
    base = str(tmp_path / "rules")
    m = StoreManager(base)
    for i in range(500):
        m.add_rule(_rule(f"R-BIG-{i:04d}", trigger=f"long trigger string {i}" * 10))
    tracemalloc.start()
    rules = m.list_rules()
    _current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    peak_mb = peak / 1024 / 1024
    assert peak_mb < 1024, f"peak memory {peak_mb:.1f}MB (expected <1024MB)"
    assert len(rules) == 500
    print(f"Peak memory for 500 complex rules: {peak_mb:.1f}MB")
