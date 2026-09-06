"""Replay latency benchmarks.

tiny corpus: <2s per candidate.
small corpus: <10s per candidate.
medium corpus: <60s per candidate.
"""

from __future__ import annotations

import time

from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.models.trajectory import Step, Trajectory
from cauterule.replay.report import build_evidence_report


def _make_trajs(n: int) -> list[Trajectory]:
    return [
        Trajectory(
            id=f"T-{i}",
            timestamp="t",
            task=f"task {i}",
            steps=(Step(1, "bash", error=f"err {i}"),),
            success=False,
        )
        for i in range(n)
    ]


def _candidate() -> CandidateRule:
    return CandidateRule(when=RuleWhen(trigger="task"), do=RuleDo(directive="fix"), confidence=0.9)


def test_replay_tiny() -> None:
    cand = _candidate()
    trajs = _make_trajs(25)
    start = time.time()
    build_evidence_report(cand, trajs)
    elapsed = time.time() - start
    assert elapsed < 2.0, f"tiny corpus took {elapsed:.2f}s (expected <2s)"


def test_replay_small() -> None:
    cand = _candidate()
    trajs = _make_trajs(100)
    start = time.time()
    build_evidence_report(cand, trajs)
    elapsed = time.time() - start
    assert elapsed < 10.0, f"small corpus took {elapsed:.2f}s (expected <10s)"


def test_replay_medium() -> None:
    cand = _candidate()
    trajs = _make_trajs(500)
    start = time.time()
    build_evidence_report(cand, trajs)
    elapsed = time.time() - start
    assert elapsed < 60.0, f"medium corpus took {elapsed:.2f}s (expected <60s)"
