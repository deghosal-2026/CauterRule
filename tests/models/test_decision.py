import pytest

from cauterule.models.decision import PromotionDecision


def test_decision_valid() -> None:
    d = PromotionDecision(
        verdict="promote",
        evidence_summary="3 failures prevented, 0 broken",
        approver="human",
        linter_warnings=("vague",),
        conflicts=("R-001 vs R-002",),
    )
    assert d.verdict == "promote"
    out = d.to_dict()
    assert out["approver"] == "human"
    assert PromotionDecision.from_dict(out) == d
    # minimal
    d2 = PromotionDecision(verdict="reject")
    assert "evidence_summary" not in d2.to_dict()


def test_decision_validation() -> None:
    with pytest.raises(ValueError, match="verdict"):
        PromotionDecision(verdict="bad")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="evidence_summary"):
        PromotionDecision(verdict="promote", evidence_summary="   ")


def test_scalar_warning_lists_rejected() -> None:
    # #771: scalar string lists must not split into characters.
    with pytest.raises(ValueError, match="linter_warnings"):
        PromotionDecision.from_dict({"verdict": "promote", "linter_warnings": "vague"})
    with pytest.raises(ValueError, match="conflicts"):
        PromotionDecision.from_dict({"verdict": "promote", "conflicts": "R-001"})
    with pytest.raises(ValueError, match="safety_warnings"):
        PromotionDecision.from_dict({"verdict": "promote", "safety_warnings": "x"})
