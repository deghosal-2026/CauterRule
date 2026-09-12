"""Benchmark: observe coverage scoring (#605)."""

from __future__ import annotations

from benchmarks.conftest import make_rule

from cauterule.observe.coverage_score import compute_coverage_score
from cauterule.serialization.rule_yaml import dump_rule_to_file
from cauterule.store.manager import StoreManager


def test_coverage_score(benchmark, tmp_path) -> None:
    """Coverage-score latency over a synthetic store."""
    store = tmp_path / "rules"
    store.mkdir()
    for i in range(100):
        dump_rule_to_file(make_rule(i), store / f"R-B{i:04d}.yaml")
    manager = StoreManager(base_dir=str(store))

    def _run() -> None:
        compute_coverage_score(manager)

    benchmark(_run)
