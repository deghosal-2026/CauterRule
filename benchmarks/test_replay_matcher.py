"""Benchmark: replay matcher O(N x M) scaling (#605)."""

from __future__ import annotations

from cauterule.models.candidate import CandidateRule
from cauterule.replay.matcher import match_score


def test_matcher_vs_store_size(benchmark, rule_store, trajectories) -> None:
    """Match latency as the rule store grows (10/100/300)."""
    cands = [
        CandidateRule(when=r.when, do=r.do, confidence=r.confidence) for r in rule_store
    ]
    trajs = trajectories[:5]

    def _run() -> None:
        for cand in cands:
            for traj in trajs:
                match_score(cand, traj)

    benchmark(_run)
