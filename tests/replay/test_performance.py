"""Performance benchmark for replay.

tiny corpus: <2s per candidate.
small corpus: <10s per candidate.
medium corpus: <60s per candidate.

These are timing benchmarks (not assert-heavy) that should be run explicitly.
"""

import time

from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.models.trajectory import Step, Trajectory
from cauterule.replay.report import build_evidence_report


def _make_trajs(n: int, success: bool = False) -> list[Trajectory]:
    return [
        Trajectory(
            id=f"T-{i}",
            timestamp="t",
            task=f"task {i}",
            steps=(Step(1, "bash", error=f"err {i}"),),
            success=success,
        )
        for i in range(n)
    ]


def test_performance_tiny() -> None:
    cand = CandidateRule(when=RuleWhen(trigger="task"), do=RuleDo(directive="fix"), confidence=0.9)
    trajs = _make_trajs(25)
    start = time.time()
    build_evidence_report(cand, trajs)
    elapsed = time.time() - start
    assert elapsed < 2.0, f"tiny corpus took {elapsed:.2f}s (expected <2s)"


def test_performance_benchmark() -> None:
    """Benchmark: 100 trajectories = small corpus."""
    cand = CandidateRule(when=RuleWhen(trigger="task"), do=RuleDo(directive="fix"), confidence=0.9)
    trajs = _make_trajs(100)
    start = time.time()
    build_evidence_report(cand, trajs)
    elapsed = time.time() - start
    print(f"Performance: 100 trajs took {elapsed:.3f}s")
