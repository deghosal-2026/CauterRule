"""Incremental indexing benchmark — <1s per new rule at 1k rules."""

from __future__ import annotations

import time
from pathlib import Path

from cauterule.models.rule import Provenance, RuleDo, RuleWhen, StandingRule
from cauterule.store.index import IndexManager


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
    )


def _preload_index(idx: IndexManager, n: int) -> None:
    entries: dict[str, dict[str, object]] = {}
    for i in range(n):
        entries[f"R-PRE-{i:04d}"] = {"status": "active", "confidence": 0.9}
    idx.save_index(entries)


def test_indexing_single_rule(tmp_path: Path) -> None:
    idx = IndexManager(str(tmp_path / "rules"))
    rule = _rule("R-001")
    start = time.time()
    idx.add_entry(rule)
    elapsed = time.time() - start
    assert elapsed < 1.0, f"single index add took {elapsed:.2f}s (expected <1s)"


def test_indexing_at_1k_rules(tmp_path: Path) -> None:
    idx = IndexManager(str(tmp_path / "rules"))
    _preload_index(idx, 1000)
    rule = _rule("R-NEW-001")
    start = time.time()
    idx.add_entry(rule)
    elapsed = time.time() - start
    assert elapsed < 1.0, f"index add at 1k rules took {elapsed:.2f}s (expected <1s)"


def test_incremental_add_10_rules(tmp_path: Path) -> None:
    idx = IndexManager(str(tmp_path / "rules"))
    _preload_index(idx, 1000)
    times: list[float] = []
    for i in range(10):
        rule = _rule(f"R-INC-{i:04d}", trigger=f"trigger {i}")
        start = time.perf_counter()
        idx.add_entry(rule)
        elapsed = time.perf_counter() - start
        times.append(elapsed)
    max_time = max(times)
    avg_time = sum(times) / len(times)
    assert max_time < 1.0, f"max index add {max_time*1000:.1f}ms (expected <1s)"
    print(f"Incremental add: avg {avg_time*1000:.1f}ms, max {max_time*1000:.1f}ms")
