"""Throughput benchmark for replay.

>=6 candidates/minute on small corpus.
"""

import time

from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.models.trajectory import Step, Trajectory
from cauterule.replay.report import build_evidence_report


def test_throughput_small() -> None:
    """Measure throughput: candidates per minute on small corpus."""
    trajs = [
        Trajectory(
            id=f"T-{i}",
            timestamp="t",
            task=f"task {i}",
            steps=(Step(1, "bash", error=f"err {i}"),),
            success=False,
        )
        for i in range(100)
    ]
    candidates = [
        CandidateRule(when=RuleWhen(trigger=f"task {i}"), do=RuleDo(directive="fix"), confidence=0.9)
        for i in range(10)
    ]
    start = time.time()
    for cand in candidates:
        build_evidence_report(cand, trajs)
    elapsed = time.time() - start
    candidates_per_minute = (len(candidates) / elapsed) * 60 if elapsed > 0 else float("inf")
    print(f"Throughput: {candidates_per_minute:.1f} candidates/min on 100-trajs corpus")
    assert candidates_per_minute >= 6, f"throughput {candidates_per_minute:.1f} < 6"
