"""Tests for safety-first promotion gate."""

from cauterule.linter.orchestrator import LinterResult
from cauterule.models.candidate import CandidateRule
from cauterule.models.evidence import EvidenceReport
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.promotion.auto import auto_promote
from cauterule.promotion.safety import check_safety


def _cand() -> CandidateRule:
    return CandidateRule(when=RuleWhen(trigger="git push fails"), do=RuleDo(directive="pull first"), confidence=0.9)


def _evidence(verdict: str = "pass", prevented: int = 1, broken: int = 0) -> EvidenceReport:
    return EvidenceReport(
        failures_prevented=tuple(f"F{i}" for i in range(prevented)),
        successes_broken=tuple(f"S{i}" for i in range(broken)),
        verdict=verdict,  # type: ignore[arg-type]
        precision=1.0 if verdict == "pass" else 0.0,
    )


def test_safety_blocks_successes_pass() -> None:
    ev = _evidence(verdict="pass", prevented=1)
    warnings = check_safety(ev, corpus_name="successes")
    assert len(warnings) > 0
    assert any("successes" in w.lower() for w in warnings)


def test_safety_blocks_failures_negative_pass() -> None:
    ev = _evidence(verdict="pass", prevented=1)
    warnings = check_safety(ev, corpus_name="failures/negative")
    assert len(warnings) > 0


def test_safety_no_block_without_corpus() -> None:
    ev = _evidence(verdict="pass", prevented=1)
    assert check_safety(ev, corpus_name=None) == []
    assert check_safety(ev, corpus_name="failures/positive") == []


def test_safety_nearmiss_low_precision() -> None:
    ev = EvidenceReport(failures_prevented=("F1",), successes_broken=(), verdict="pass", precision=0.5)
    warnings = check_safety(ev, corpus_name="nearmiss")
    assert len(warnings) > 0


def test_auto_promote_blocks_on_successes() -> None:
    cand = _cand()
    ev = _evidence(verdict="pass", prevented=1)
    linter = LinterResult(warnings=())
    decision = auto_promote(cand, ev, linter, corpus_name="successes")
    assert decision.verdict == "reject"


def test_auto_promote_force_overrides_safety() -> None:
    cand = _cand()
    ev = _evidence(verdict="pass", prevented=1)
    linter = LinterResult(warnings=())
    decision = auto_promote(cand, ev, linter, corpus_name="successes", force=True)
    assert decision.verdict == "promote"
    assert decision.evidence_summary is not None
    assert "safety overridden" in decision.evidence_summary.lower()


def test_auto_promote_blocks_on_failures_negative() -> None:
    cand = _cand()
    ev = _evidence(verdict="pass", prevented=1)
    linter = LinterResult(warnings=())
    decision = auto_promote(cand, ev, linter, corpus_name="failures/negative")
    assert decision.verdict == "reject"


def test_auto_promote_passes_on_positive_corpus() -> None:
    cand = _cand()
    ev = _evidence(verdict="pass", prevented=1)
    linter = LinterResult(warnings=())
    decision = auto_promote(cand, ev, linter, corpus_name="failures/positive")
    assert decision.verdict == "promote"
