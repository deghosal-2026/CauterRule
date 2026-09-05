"""Auto-promote mode — pass + clean linter + no conflicts → promoted."""

from __future__ import annotations

from cauterule.linter.orchestrator import LinterResult
from cauterule.models.candidate import CandidateRule
from cauterule.models.conflict import ConflictReport
from cauterule.models.decision import PromotionDecision


def auto_promote(
    candidate: CandidateRule,
    linter_result: LinterResult,
    conflict_reports: list[ConflictReport] | None = None,
) -> PromotionDecision:
    """Decide promotion for *candidate* in auto mode.

    Auto-promotion requires all three gates to pass:
    - Clean linter (no warnings).
    - Zero unresolved conflicts.
    - The candidate's confidence is already validated upstream.

    Args:
        candidate: The candidate rule under review.
        linter_result: Result from the linter orchestrator.
        conflict_reports: Optional list of conflict reports; defaults to
            empty.

    Returns:
        A :class:`PromotionDecision` with verdict ``"promote"`` if all
        checks pass, or ``"reject"`` otherwise.
    """
    conflicts = conflict_reports or []
    conflict_warnings: list[str] = []

    for c in conflicts:
        conflict_warnings.append(f"{c.type}: rules {list(c.rules)}")

    if linter_result.passed and not conflicts:
        return PromotionDecision(
            verdict="promote",
            evidence_summary=f"Auto-promote: linter clean, no conflicts; candidate confidence={candidate.confidence}",
            approver="auto",
        )

    return PromotionDecision(
        verdict="reject",
        evidence_summary=(
            f"Auto-reject: confidence={candidate.confidence:.2f}, "
            f"linter_passed={linter_result.passed}, "
            f"conflicts={len(conflicts)}"
        ),
        approver="auto",
        linter_warnings=linter_result.warnings,
        conflicts=tuple(conflict_warnings),
    )