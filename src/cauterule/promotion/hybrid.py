"""Hybrid mode — auto for high-confidence, review for low."""

from __future__ import annotations

from cauterule.linter.orchestrator import LinterResult
from cauterule.models.candidate import CandidateRule
from cauterule.models.conflict import ConflictReport
from cauterule.models.decision import PromotionDecision
from cauterule.models.evidence import EvidenceReport
from cauterule.promotion.auto import auto_promote
from cauterule.promotion.human import human_review


def hybrid_promote(
    candidate: CandidateRule,
    evidence_report: EvidenceReport,
    linter_result: LinterResult,
    conflict_reports: list[ConflictReport] | None = None,
    threshold: float = 0.8,
) -> PromotionDecision:
    """Decide promotion for *candidate* in hybrid mode.

    When the candidate's confidence is **at or above** *threshold* the
    decision delegates to :func:`auto_promote`.  Below the threshold it
    delegates to :func:`human_review`.

    Args:
        candidate: The candidate rule under review.
        evidence_report: Replay-evidence report for the candidate.
        linter_result: Linter result for the candidate.
        conflict_reports: Optional list of conflict reports.
        threshold: Confidence threshold for auto promotion (default 0.8).
            Must be in ``[0.0, 1.0]``.

    Returns:
        A :class:`PromotionDecision` based on the candidate's confidence.
    """
    if not 0.0 <= threshold <= 1.0:
        raise ValueError(f"threshold must be in [0.0, 1.0], got {threshold}")

    if candidate.confidence >= threshold:
        return auto_promote(candidate, linter_result, conflict_reports)

    return human_review(candidate, evidence_report, linter_result)