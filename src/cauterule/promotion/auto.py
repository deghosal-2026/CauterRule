"""Auto-promote mode — pass + clean linter + no conflicts → promoted."""

from __future__ import annotations

from cauterule.linter.orchestrator import LinterResult
from cauterule.models.candidate import CandidateRule
from cauterule.models.conflict import ConflictReport
from cauterule.models.decision import PromotionDecision
from cauterule.models.evidence import EvidenceReport
from cauterule.promotion.safety import check_safety


def auto_promote(
    candidate: CandidateRule,
    evidence: EvidenceReport,
    linter_result: LinterResult,
    conflict_reports: list[ConflictReport] | None = None,
    corpus_name: str | None = None,
    force: bool = False,
) -> PromotionDecision:
    """Decide promotion for *candidate* in auto mode.

    Auto-promotion requires all gates to pass:
    - Clean linter (no warnings).
    - Zero unresolved conflicts.
    - Evidence verdict pass with at least one failure prevented.
    - Safety gate: no safety-corpus violations (unless force=True).

    Args:
        candidate: The candidate rule under review.
        evidence: Replay-evidence report for the candidate.
        linter_result: Result from the linter orchestrator.
        conflict_reports: Optional list of conflict reports; defaults to
            empty.
        corpus_name: Source corpus for safety checks (e.g. successes).
            If None, safety gate is skipped.
        force: If True, promote despite safety warnings (audit logged).

    Returns:
        A :class:`PromotionDecision` with verdict ``"promote"`` if all
        checks pass, or ``"reject"`` otherwise.
    """
    conflicts = conflict_reports or []
    conflict_warnings: list[str] = []

    for c in conflicts:
        conflict_warnings.append(f"{c.type}: rules {list(c.rules)}")

    evidence_ok = evidence.verdict == "pass" and len(evidence.failures_prevented) >= 1

    safety_warnings = check_safety(evidence, corpus_name=corpus_name)
    safety_ok = not safety_warnings or force

    if linter_result.passed and not conflicts and evidence_ok and safety_ok:
        summary = f"Auto-promote: linter clean, no conflicts, evidence={evidence.verdict}; candidate confidence={candidate.confidence}"
        if safety_warnings and force:
            summary += f" (safety overridden: {'; '.join(safety_warnings)})"
        return PromotionDecision(
            verdict="promote",
            evidence_summary=summary,
            approver="auto",
            safety_warnings=tuple(safety_warnings),
        )

    all_warnings = list(linter_result.warnings) + safety_warnings
    return PromotionDecision(
        verdict="reject",
        evidence_summary=(
            f"Auto-reject: confidence={candidate.confidence:.2f}, "
            f"linter_passed={linter_result.passed}, "
            f"conflicts={len(conflicts)}, "
            f"evidence_verdict={evidence.verdict}"
            + (f", safety_warnings={safety_warnings}" if safety_warnings else "")
        ),
        approver="auto",
        linter_warnings=tuple(all_warnings),
        conflicts=tuple(conflict_warnings),
        safety_warnings=tuple(safety_warnings),
    )