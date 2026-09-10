"""Tests for auto-promotion tuning (#545)."""

from __future__ import annotations

from cauterule.lifecycle.tune import (
    CEILING_MIN_QUALITY,
    FLOOR_MIN_QUALITY,
    MIN_EVIDENCE,
    PromotionCutoffs,
    cutoffs_for_corpus,
    learn_cutoffs,
)
from cauterule.models.rule import Provenance, RuleDo, RuleWhen, StandingRule


def _rule(
    rid: str,
    *,
    trigger: str = "git push fails permission denied",
    prevented: int = 0,
    broke: int = 0,
    specificity: float | None = 0.9,
) -> StandingRule:
    return StandingRule(
        id=rid,
        when=RuleWhen(trigger=trigger),
        do=RuleDo(directive="pull --rebase"),
        confidence=0.9,
        provenance=Provenance(
            source_trajectory="T",
            extracted_by="test",
            extract_timestamp="2025-01-01T00:00:00",
            extraction_pass=1,
        ),
        status="active",
        promoted_at="2025-01-02T00:00:00",
        prevented_count=prevented,
        broke_count=broke,
        specificity=specificity,
    )


def _corpus(prevented_total: int, n_rules: int = 40) -> list[StandingRule]:
    """Build a corpus with the given total prevented distribution."""
    per = prevented_total // n_rules
    rem = prevented_total % n_rules
    rules = []
    base_spec = 0.8 if prevented_total > n_rules else 0.3
    for i in range(n_rules):
        rules.append(
            _rule(
                f"R-{i:03d}",
                specificity=base_spec,
                prevented=per + (1 if i < rem else 0),
                broke=max(1, n_rules // 10),
            )
        )
    return rules


def test_cold_start_returns_default() -> None:
    # Zero-outcome corpus → source="default", behaves like static behavior.
    rules = [_rule("R-A", prevented=0, broke=0)]
    cutoffs = learn_cutoffs(rules, min_evidence=MIN_EVIDENCE)
    assert cutoffs.source == "default"
    assert cutoffs.min_quality == FLOOR_MIN_QUALITY


def test_thin_evidence_returns_default() -> None:
    # 6 outcomes < min_evidence(30) → default.
    rules = [
        _rule(f"R-{i}", specificity=0.9, prevented=1, broke=0)
        for i in range(6)
    ]
    cutoffs = cutoffs_for_corpus(rules, min_evidence=MIN_EVIDENCE)
    assert cutoffs.source == "default"


def test_high_precision_corpus_relaxes() -> None:
    # Corpus A: high prevented-rate → learned cutoffs <= static default.
    rules = _corpus(prevented_total=400, n_rules=40)  # ~10 prevented each
    cutoffs = learn_cutoffs(rules, min_evidence=10)
    assert cutoffs.source.startswith("learned")
    assert cutoffs.min_quality <= CEILING_MIN_QUALITY
    assert FLOOR_MIN_QUALITY <= cutoffs.min_quality <= CEILING_MIN_QUALITY


def test_low_precision_corpus_tightens() -> None:
    # Corpus B: low prevented-rate (mostly broke) → cutoff tightens toward
    # ceiling relative to corpus A (high precision).
    high = learn_cutoffs(_corpus(prevented_total=400, n_rules=40), min_evidence=10)
    low = learn_cutoffs(_corpus(prevented_total=40, n_rules=40), min_evidence=10)
    assert low.min_specificity >= high.min_specificity
    assert low.min_quality >= high.min_quality


def test_perfect_corpus_looser_than_broken() -> None:
    # The documented direction: a corpus whose LOW-specificity rules are also
    # accurate yields LOOSER cutoffs than a broken corpus (code-review).
    # Previously the implementation pinned to the ceiling and inverted this.
    perfect = learn_cutoffs(
        [
            _rule(f"R-{i}", specificity=(0.1 + 0.1 * (i % 8)), prevented=20, broke=0)
            for i in range(40)
        ],
        min_evidence=10,
    )
    broken = learn_cutoffs(
        [
            _rule(f"R-{i}", specificity=0.2, prevented=0, broke=20)
            for i in range(40)
        ],
        min_evidence=10,
    )
    assert perfect.min_quality <= broken.min_quality
    assert perfect.min_specificity <= broken.min_specificity


def test_floor_holds_under_all_broke_corpus() -> None:
    # Guardrail: an all-broke corpus never drops min_quality below floor.
    rules = [
        _rule(f"R-{i}", specificity=0.05, prevented=0, broke=10)
        for i in range(50)
    ]
    cutoffs = learn_cutoffs(rules, min_evidence=10)
    assert cutoffs.min_quality >= FLOOR_MIN_QUALITY
    assert cutoffs.min_specificity >= 0.0


def test_ceiling_holds_under_all_prevented_corpus() -> None:
    rules = [
        _rule(f"R-{i}", specificity=1.0, prevented=10, broke=0)
        for i in range(50)
    ]
    cutoffs = learn_cutoffs(rules, min_evidence=10)
    assert cutoffs.min_quality <= CEILING_MIN_QUALITY
    assert cutoffs.source.startswith("learned")


def test_guardrails_bound_learned_values() -> None:
    rules = _corpus(prevented_total=400, n_rules=40)
    cutoffs = learn_cutoffs(rules, min_evidence=10)
    assert FLOOR_MIN_QUALITY <= cutoffs.min_quality <= CEILING_MIN_QUALITY
    assert 0.0 <= cutoffs.min_specificity <= 1.0


def test_promotion_cutoffs_summarize() -> None:
    c = PromotionCutoffs(min_quality=0.7, min_specificity=0.3, source="learned(n=40)")
    s = c.summarize()
    assert "min_quality=0.70" in s
    assert "learned(n=40)" in s


def test_auto_promote_enforces_learned_cutoff() -> None:
    from cauterule.linter.orchestrator import LinterResult
    from cauterule.models.candidate import CandidateRule
    from cauterule.models.decision import PromotionDecision
    from cauterule.models.evidence import EvidenceReport
    from cauterule.models.rule import RuleDo, RuleWhen
    from cauterule.promotion.auto import auto_promote

    cand = CandidateRule(
        when=RuleWhen(trigger="git push fails"),
        do=RuleDo(directive="pull --rebase"),
        confidence=0.5,
    )
    evidence = EvidenceReport(
        failures_prevented=("T-1",), precision=1.0, recall=1.0, verdict="pass"
    )
    linter = LinterResult(passed=True, warnings=())

    # With a strict learned cutoff, a 0.5-confidence candidate is rejected.
    strict = PromotionCutoffs(min_quality=0.8, min_specificity=0.3, source="learned(n=40)")
    decision: PromotionDecision = auto_promote(
        cand, evidence, linter, cutoffs=strict
    )
    assert decision.verdict == "reject"
    assert "below learned cutoff" in decision.evidence_summary

    # With --force the learned cutoff is bypassed.
    forced: PromotionDecision = auto_promote(
        cand, evidence, linter, cutoffs=strict, force=True
    )
    assert forced.verdict == "promote"
