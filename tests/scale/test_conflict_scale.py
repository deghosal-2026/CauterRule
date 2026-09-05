"""Conflict detection at scale benchmarks.

100 / 1k / 10k rules, <5s at 1k.
"""

from __future__ import annotations

import time

from cauterule.conflict.contradiction import detect_contradictions
from cauterule.conflict.overlap import detect_overlaps
from cauterule.models.rule import Provenance, RuleDo, RuleWhen, StandingRule


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


def _seeded_rules(n: int) -> list[StandingRule]:
    rules: list[StandingRule] = []
    for i in range(n):
        trigger = f"trigger {i % 50}"
        directive = f"directive {i % 3}"
        rules.append(_rule(f"R-{i:04d}", trigger, directive))
    return rules


def test_conflict_100() -> None:
    rules = _seeded_rules(100)
    start = time.time()
    detect_contradictions(rules)
    detect_overlaps(rules)
    elapsed = time.time() - start
    assert elapsed < 5.0, f"100 rules took {elapsed:.2f}s (expected <5s)"


def test_conflict_1k() -> None:
    rules = _seeded_rules(1000)
    start = time.time()
    detect_contradictions(rules)
    detect_overlaps(rules)
    elapsed = time.time() - start
    assert elapsed < 5.0, f"1k rules took {elapsed:.2f}s (expected <5s)"


def test_conflict_10k() -> None:
    rules = _seeded_rules(10000)
    start = time.time()
    detect_contradictions(rules)
    detect_overlaps(rules)
    elapsed = time.time() - start
    print(f"Conflict 10k rules: {elapsed:.2f}s")
