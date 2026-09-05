"""Replay caching — cache replay results for same candidate + corpus hash."""

from __future__ import annotations

import hashlib
import json

from cauterule.models.candidate import CandidateRule
from cauterule.models.evidence import EvidenceReport
from cauterule.models.trajectory import Trajectory
from cauterule.replay.determinism import deterministic_replay


class ReplayCache:
    """Cache replay results keyed by candidate + corpus hash."""

    def __init__(self) -> None:
        self._cache: dict[str, EvidenceReport] = {}

    def _key(self, candidate: CandidateRule, trajectories: list[Trajectory]) -> str:
        ids = sorted(t.id for t in trajectories)
        corpus_hash = hashlib.sha256(json.dumps(ids).encode()).hexdigest()[:16]
        cand_hash = hashlib.sha256(
            json.dumps(
                {
                    "trigger": candidate.when.trigger,
                    "directive": candidate.do.directive,
                    "context": list(candidate.when.context),
                },
                sort_keys=True,
            ).encode()
        ).hexdigest()[:16]
        return f"{cand_hash}:{corpus_hash}"

    def get(self, candidate: CandidateRule, trajectories: list[Trajectory]) -> EvidenceReport:
        """Return cached or computed replay result."""
        key = self._key(candidate, trajectories)
        if key in self._cache:
            return self._cache[key]
        report = deterministic_replay(candidate, trajectories)
        self._cache[key] = report
        return report

    def clear(self) -> None:
        """Clear the cache."""
        self._cache.clear()

    def __len__(self) -> int:
        return len(self._cache)