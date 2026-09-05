"""Determinism guarantee."""

from __future__ import annotations

import hashlib
import json

from cauterule.models.candidate import CandidateRule
from cauterule.models.evidence import EvidenceReport
from cauterule.models.trajectory import Trajectory
from cauterule.replay.report import build_evidence_report


def _corpus_hash(trajectories: list[Trajectory]) -> str:
    # Deterministic hash: sorted ids + sorted task strings
    ids = sorted(t.id for t in trajectories)
    return hashlib.sha256(json.dumps(ids).encode()).hexdigest()[:8]


def deterministic_replay(
    candidate: CandidateRule,
    trajectories: list[Trajectory],
) -> EvidenceReport:
    """Replay with determinism guarantee.

    Same candidate + same corpus (by ids) = same report (no randomness).
    Achieved by sorting trajectories by id and using deterministic scorer.
    """
    # Sort for determinism
    sorted_trajs = sorted(trajectories, key=lambda t: t.id)
    _ = _corpus_hash(sorted_trajs)  # hash used for caching key (future)
    return build_evidence_report(candidate, sorted_trajs)
