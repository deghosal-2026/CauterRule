"""Edge/validation coverage for models touched in v0.3.1 (#681)."""

from __future__ import annotations

import pytest

from cauterule.models.evidence import EvidenceReport
from cauterule.models.rule import Provenance, RuleDo, RuleWhen, StandingRule


def _prov() -> Provenance:
    return Provenance(
        source_trajectory="T", extracted_by="e", extract_timestamp="t", extraction_pass=1
    )


# --- EvidenceReport (#720 outcome fields + existing validation) ---


def test_evidence_outcome_round_trip() -> None:
    ev = EvidenceReport(precision=0.5, recall=0.5, outcome_precision=0.9, outcome_verdict="pass")
    d = ev.to_dict()
    assert d["outcome_precision"] == 0.9
    assert d["outcome_verdict"] == "pass"
    restored = EvidenceReport.from_dict(d)
    assert restored.outcome_precision == 0.9
    assert restored.outcome_verdict == "pass"


def test_evidence_outcome_optional_absent() -> None:
    ev = EvidenceReport(precision=0.5, recall=0.5)
    assert "outcome_precision" not in ev.to_dict()
    assert EvidenceReport.from_dict(ev.to_dict()).outcome_precision is None


@pytest.mark.parametrize("bad", [-0.1, 1.1])
def test_evidence_outcome_precision_range(bad: float) -> None:
    with pytest.raises(ValueError, match="outcome_precision"):
        EvidenceReport(outcome_precision=bad)


def test_evidence_outcome_verdict_valid() -> None:
    with pytest.raises(ValueError, match="outcome_verdict"):
        EvidenceReport(outcome_verdict="maybe")  # type: ignore[arg-type]


def test_evidence_precision_range() -> None:
    with pytest.raises(ValueError, match="precision"):
        EvidenceReport(precision=2.0)


def test_evidence_recall_range() -> None:
    with pytest.raises(ValueError, match="recall"):
        EvidenceReport(recall=-1.0)


def test_evidence_verdict_valid() -> None:
    with pytest.raises(ValueError, match="verdict"):
        EvidenceReport(verdict="maybe")  # type: ignore[arg-type]


def test_evidence_inconclusive_reason_valid() -> None:
    with pytest.raises(ValueError, match="inconclusive_reason"):
        EvidenceReport(inconclusive_reason="whatever")  # type: ignore[arg-type]


# --- RuleWhen.signature (#725) ---


def test_rule_when_signature_blank_rejected() -> None:
    with pytest.raises(ValueError, match="signature"):
        RuleWhen(trigger="t", signature="  ")


# --- StandingRule validation branches ---


def test_standing_rule_invalid_last_outcome() -> None:
    with pytest.raises(ValueError, match="last_outcome"):
        StandingRule(
            id="R-1",
            when=RuleWhen(trigger="t"),
            do=RuleDo(directive="d"),
            confidence=0.9,
            provenance=_prov(),
            status="active",
            promoted_at="t",
            last_outcome="exploded",
        )


def test_standing_rule_invalid_outcome_trend() -> None:
    with pytest.raises(ValueError, match="outcome_trend"):
        StandingRule(
            id="R-1",
            when=RuleWhen(trigger="t"),
            do=RuleDo(directive="d"),
            confidence=0.9,
            provenance=_prov(),
            status="active",
            promoted_at="t",
            outcome_trend=(1, 5),
        )


def test_standing_rule_invalid_specificity() -> None:
    with pytest.raises(ValueError, match="specificity"):
        StandingRule(
            id="R-1",
            when=RuleWhen(trigger="t"),
            do=RuleDo(directive="d"),
            confidence=0.9,
            provenance=_prov(),
            status="active",
            promoted_at="t",
            specificity=1.5,
        )


def test_standing_rule_invalid_hit_count() -> None:
    with pytest.raises(ValueError, match="hit_count"):
        StandingRule(
            id="R-1",
            when=RuleWhen(trigger="t"),
            do=RuleDo(directive="d"),
            confidence=0.9,
            provenance=_prov(),
            status="active",
            promoted_at="t",
            hit_count=-1,
        )


def test_standing_rule_invalid_status() -> None:
    with pytest.raises(ValueError, match="status"):
        StandingRule(
            id="R-1",
            when=RuleWhen(trigger="t"),
            do=RuleDo(directive="d"),
            confidence=0.9,
            provenance=_prov(),
            status="archived",  # type: ignore[arg-type]
            promoted_at="t",
        )


def test_standing_rule_blank_tag() -> None:
    with pytest.raises(ValueError, match="tags"):
        StandingRule(
            id="R-1",
            when=RuleWhen(trigger="t"),
            do=RuleDo(directive="d"),
            confidence=0.9,
            provenance=_prov(),
            status="active",
            promoted_at="t",
            tags=("",),
        )
