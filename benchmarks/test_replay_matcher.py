"""Benchmark: replay matcher O(N x M) scaling (#605)."""

from __future__ import annotations

from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.models.trajectory import Step, Trajectory
from cauterule.replay import embeddings
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


class _FakeEmbedder:
    """Cheap deterministic embedder so the semantic blend can be benchmarked."""

    def encode(self, texts: list[str]) -> list[list[float]]:
        return [[float(len(t) % 7), 1.0, 0.0] for t in texts]


def test_matcher_semantic_path_latency(benchmark) -> None:
    """Match latency with the embedding blend enabled (#689)."""
    cand = CandidateRule(
        when=RuleWhen(trigger="database connection dropped"),
        do=RuleDo(directive="d"),
        confidence=0.9,
    )
    trajs = [
        Trajectory(
            id=f"T-{i}",
            timestamp="t",
            task="run migration",
            steps=(Step(1, "bash", error=f"lost connection to postgres {i}"),),
            success=False,
        )
        for i in range(10)
    ]
    embeddings.set_embedder_for_testing(_FakeEmbedder())
    try:
        benchmark(lambda: [match_score(cand, traj) for traj in trajs])
    finally:
        embeddings.reset_embedder()
