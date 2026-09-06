"""Parallel replay — run N candidates in parallel for draft tournament."""

from __future__ import annotations

import concurrent.futures
from typing import Any

from cauterule.models.candidate import CandidateRule
from cauterule.models.evidence import EvidenceReport
from cauterule.models.trajectory import Trajectory
from cauterule.replay.cache import ReplayCache


def run_parallel(
    candidates: list[CandidateRule],
    trajectories: list[Trajectory],
    max_workers: int = 4,
    cache: ReplayCache | None = None,
) -> list[EvidenceReport]:
    """Run replay for all *candidates* in parallel.

    Args:
        candidates: Candidates to test.
        trajectories: Historical trajectories.
        max_workers: Max parallel workers.
        cache: Optional cache to reuse.

    Returns:
        List of evidence reports (same order as candidates).
    """
    if cache is None:
        cache = ReplayCache()

    def _replay(cand: CandidateRule) -> EvidenceReport:
        return cache.get(cand, trajectories)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(_replay, candidates))
    return results