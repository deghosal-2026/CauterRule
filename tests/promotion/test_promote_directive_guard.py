"""End-to-end promotion guard for destructive directives (#762 Phase 1).

A destructive directive that passes the (trigger-only) replay gate must not be
auto-promoted.
"""

from __future__ import annotations

from cauterule.linter.orchestrator import lint_rule
from cauterule.models.candidate import CandidateRule
from cauterule.models.evidence import EvidenceReport
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.promotion.auto import auto_promote

_TRIGGER = "when git push fails with non-fast-forward"


def _candidate(directive: str) -> CandidateRule:
    return CandidateRule(
        when=RuleWhen(trigger=_TRIGGER),
        do=RuleDo(directive=directive),
        confidence=0.9,
    )


def _passing_evidence() -> EvidenceReport:
    return EvidenceReport(
        failures_prevented=("F1",),
        verdict="pass",
        precision=1.0,
        recall=1.0,
    )


def test_destructive_directive_not_auto_promoted() -> None:
    cand = _candidate("delete the remote branch and recreate it from scratch")
    lint = lint_rule(cand.when.trigger, cand.do.directive)
    decision = auto_promote(cand, _passing_evidence(), lint)
    assert decision.verdict != "promote"


def test_correct_directive_auto_promoted() -> None:
    cand = _candidate("pull latest changes before pushing")
    lint = lint_rule(cand.when.trigger, cand.do.directive)
    decision = auto_promote(cand, _passing_evidence(), lint)
    assert decision.verdict == "promote"
