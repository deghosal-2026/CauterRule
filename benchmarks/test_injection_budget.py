"""Benchmark: injection ordering + budget optimizer (#605)."""

from __future__ import annotations

from cauterule.injection.budget import optimize_budget
from cauterule.injection.ordering import order_by_specificity


def test_ordering_vs_store_size(benchmark, rule_store) -> None:
    """Specificity ordering latency as the store grows."""

    def _run() -> None:
        order_by_specificity(list(rule_store))

    benchmark(_run)


def test_budget_optimizer(benchmark, rule_store) -> None:
    """Budget optimizer latency at the largest store size."""
    rules = rule_store
    if len(rules) < 300:
        from benchmarks.conftest import make_rule

        rules = [make_rule(i) for i in range(300)]

    def _run() -> None:
        optimize_budget(rules, max_tokens=2000)

    benchmark(_run)
