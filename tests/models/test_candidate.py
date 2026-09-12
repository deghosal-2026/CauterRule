import pytest

from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import RuleDo, RuleWhen


def test_candidate_valid() -> None:
    c = CandidateRule(
        when=RuleWhen(trigger="git push fails"),
        do=RuleDo(directive="pull --rebase"),
        confidence=0.9,
        reasoning="remote ahead",
        extraction_pass=2,
        template="retry",
    )
    assert c.confidence == 0.9
    d = c.to_dict()
    assert d["reasoning"] == "remote ahead"
    assert CandidateRule.from_dict(d) == c
    # minimal
    c2 = CandidateRule(when=RuleWhen(trigger="t"), do=RuleDo(directive="d"), confidence=0.5)
    assert "reasoning" not in c2.to_dict()


def test_candidate_validation() -> None:
    with pytest.raises(ValueError, match="confidence"):
        CandidateRule(when=RuleWhen(trigger="t"), do=RuleDo(directive="d"), confidence=1.5)
    with pytest.raises(ValueError, match="extraction_pass"):
        CandidateRule(
            when=RuleWhen(trigger="t"), do=RuleDo(directive="d"), confidence=0.5, extraction_pass=0
        )
    with pytest.raises(ValueError, match="reasoning"):
        CandidateRule(
            when=RuleWhen(trigger="t"), do=RuleDo(directive="d"), confidence=0.5, reasoning="   "
        )
    with pytest.raises(ValueError, match="template"):
        CandidateRule(
            when=RuleWhen(trigger="t"), do=RuleDo(directive="d"), confidence=0.5, template="   "
        )
