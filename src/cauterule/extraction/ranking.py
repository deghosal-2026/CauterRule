"""Tournament ranking."""

from __future__ import annotations

from dataclasses import dataclass

from cauterule.models.candidate import CandidateRule
from cauterule.models.evidence import EvidenceReport


@dataclass(frozen=True)
class RankedCandidate:
    """Candidate with its evidence and rank."""

    candidate: CandidateRule
    evidence: EvidenceReport
    rank: int


def rank_candidates(
    candidates: list[CandidateRule],
    evidences: list[EvidenceReport],
) -> list[RankedCandidate]:
    """Rank candidates by precision > recall > confidence > specificity.

    Args:
        candidates: List of candidates.
        evidences: Parallel list of evidence reports (same order).

    Returns:
        Ranked list sorted best first, with rank 1..N.
    """
    if len(candidates) != len(evidences):
        raise ValueError("candidates and evidences must be same length")

    paired = list(zip(candidates, evidences, strict=True))

    def sort_key(pair: tuple[CandidateRule, EvidenceReport]) -> tuple[float, float, float, int]:
        cand, ev = pair
        # Specificity proxy: length of trigger + context
        specificity = len(cand.when.trigger) + sum(len(c) for c in cand.when.context)
        return (ev.precision, ev.recall, cand.confidence, specificity)

    paired.sort(key=sort_key, reverse=True)

    return [
        RankedCandidate(candidate=cand, evidence=ev, rank=idx)
        for idx, (cand, ev) in enumerate(paired, start=1)
    ]
