"""Tests for human review sampling workflow."""

from cauterule.models.candidate import CandidateRule
from cauterule.models.evidence import EvidenceReport
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.review.sampling import (
    HumanScore,
    agreement_rate,
    requires_human_approval,
    sample_candidates,
)


def _cand(trigger: str) -> CandidateRule:
    return CandidateRule(when=RuleWhen(trigger=trigger), do=RuleDo(directive="d"), confidence=0.9)


def _ev(verdict: str) -> EvidenceReport:
    return EvidenceReport(verdict=verdict)  # type: ignore[arg-type]


def test_sample_reproducible() -> None:
    cands = [
        (_cand(f"t{i}"), _ev(v))
        for i, v in enumerate(["pass", "pass", "fail", "fail", "inconclusive", "inconclusive"] * 2)
    ]
    s1 = sample_candidates(cands, n_per_bucket=1)
    s2 = sample_candidates(cands, n_per_bucket=1)
    assert s1.sampled == s2.sampled
    assert s1.by_verdict["pass"] == 1
    assert s1.by_verdict["fail"] == 1
    assert s1.by_verdict["inconclusive"] == 1


def test_agreement_rate() -> None:
    scores = [
        HumanScore(candidate_id="1", replay_verdict="pass", human_verdict="pass"),
        HumanScore(candidate_id="2", replay_verdict="pass", human_verdict="fail"),
        HumanScore(candidate_id="3", replay_verdict="fail", human_verdict="fail"),
    ]
    assert agreement_rate(scores) == 0.6667
    assert agreement_rate([]) == 0.0


def test_requires_approval() -> None:
    assert requires_human_approval(0.5) is True
    assert requires_human_approval(0.9) is False
    assert requires_human_approval(0.8) is False
    assert requires_human_approval(0.79) is True
