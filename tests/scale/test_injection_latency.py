"""Injection latency benchmarks.

p50 < 100ms, p95 < 500ms on small corpus.
"""

from __future__ import annotations

import time

from cauterule.injection.matcher import match_rules
from cauterule.models.rule import Provenance, RuleDo, RuleWhen, StandingRule


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


def _small_corpus() -> list[StandingRule]:
    return [_rule(f"R-{i:04d}", trigger=f"trigger {i}") for i in range(100)]


def test_injection_p50() -> None:
    rules = _small_corpus()
    times: list[float] = []
    for _ in range(50):
        start = time.perf_counter()
        match_rules("trigger 42", rules)
        elapsed = time.perf_counter() - start
        times.append(elapsed)
    times.sort()
    p50 = times[len(times) // 2]
    assert p50 < 0.1, f"p50 latency {p50 * 1000:.1f}ms (expected <100ms)"


def test_injection_p95() -> None:
    rules = _small_corpus()
    times: list[float] = []
    for _ in range(100):
        start = time.perf_counter()
        match_rules("trigger 42", rules)
        elapsed = time.perf_counter() - start
        times.append(elapsed)
    times.sort()
    p95 = times[int(len(times) * 0.95)]
    assert p95 < 0.5, f"p95 latency {p95 * 1000:.1f}ms (expected <500ms)"
