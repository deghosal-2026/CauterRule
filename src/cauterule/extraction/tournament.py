"""Draft tournament runner."""

from __future__ import annotations

from typing import Any

from cauterule.extraction.ranking import RankedCandidate, rank_candidates
from cauterule.models.candidate import CandidateRule
from cauterule.models.evidence import EvidenceReport
from cauterule.models.trajectory import Trajectory


def _mock_evidence(candidate: CandidateRule, trajectories: list[Trajectory]) -> EvidenceReport:
    """Mock replay evidence for tournament (uses simple matching).

    In M8, full replay engine (M9) is not yet available, so we simulate:
    - failures_prevented: trajectories where candidate trigger appears in task
    - successes_broken: none for mock
    """
    prevented: list[str] = []
    for t in trajectories:
        if not t.success and candidate.when.trigger.lower() in t.task.lower():
            prevented.append(t.id)
    precision = 1.0 if prevented else 0.0
    recall = len(prevented) / max(1, len([t for t in trajectories if not t.success]))
    verdict = "pass" if precision >= 0.5 else "fail"
    return EvidenceReport(
        failures_prevented=tuple(prevented),
        successes_broken=(),
        precision=precision,
        recall=recall,
        verdict=verdict,  # type: ignore[arg-type]
    )


def run_tournament(
    candidates: list[CandidateRule],
    trajectories: list[Trajectory],
    scorer: Any | None = None,
) -> list[RankedCandidate]:
    """Replay-test all candidates and rank them.

    Args:
        candidates: Candidates from multi-pass.
        trajectories: Historical trajectories for replay.
        scorer: Optional custom scorer (unused in mock, reserved for M9 integration).

    Returns:
        Ranked candidates best first.
    """
    _ = scorer
    evidences = [_mock_evidence(c, trajectories) for c in candidates]
    return rank_candidates(candidates, evidences)
