"""Benchmark: pre-extraction gate + candidate quality checks (#605)."""

from __future__ import annotations

from benchmarks.conftest import make_trajectory

from cauterule.extraction.gate import run_gate
from cauterule.extraction.quality import check_quality
from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import RuleDo, RuleWhen


def test_gate_throughput(benchmark) -> None:
    """Gate decision latency over a trajectory batch."""
    trajs = [make_trajectory(i) for i in range(50)]

    def _run() -> None:
        for traj in trajs:
            run_gate(traj)

    benchmark(_run)


def test_quality_check_throughput(benchmark) -> None:
    """Candidate quality-gate latency."""
    cand = CandidateRule(
        when=RuleWhen(trigger="synthetic failure signature in git push"),
        do=RuleDo(directive="apply synthetic fix"),
        confidence=0.8,
    )
    traj = make_trajectory(0)

    def _run() -> None:
        for _ in range(50):
            check_quality(cand, traj)

    benchmark(_run)
