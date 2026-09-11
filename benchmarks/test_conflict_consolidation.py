"""Benchmark: conflict consolidation O(N^2) scaling (#605)."""

from __future__ import annotations

from cauterule.conflict.consolidation import consolidate


def test_consolidate_vs_store_size(benchmark, rule_store) -> None:
    """Pairwise consolidation latency as the store grows."""

    def _run() -> None:
        consolidate(list(rule_store))

    benchmark(_run)
