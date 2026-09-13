import pytest

from cauterule.extraction.ranking import rank_candidates
from cauterule.models.candidate import CandidateRule
from cauterule.models.evidence import EvidenceReport
from cauterule.models.rule import RuleDo, RuleWhen


def _cand(trigger: str, confidence: float) -> CandidateRule:
    return CandidateRule(
        when=RuleWhen(trigger=trigger), do=RuleDo(directive="d"), confidence=confidence
    )


def _ev(prec: float, rec: float) -> EvidenceReport:
    return EvidenceReport(precision=prec, recall=rec, verdict="pass")


def test_rank_prefers_recall() -> None:
    # #731: recall-weighted — (0.8, 0.9) outranks (0.9, 0.5).
    c1 = _cand("a", 0.9)
    c2 = _cand("b", 0.9)
    ev1 = _ev(0.9, 0.5)
    ev2 = _ev(0.8, 0.9)
    ranked = rank_candidates([c1, c2], [ev1, ev2])
    assert ranked[0].candidate == c2
    assert ranked[0].rank == 1
    assert ranked[1].rank == 2


def test_rank_tie_breaker_recall() -> None:
    c1 = _cand("a", 0.8)
    c2 = _cand("b", 0.8)
    ev1 = _ev(0.9, 0.5)
    ev2 = _ev(0.9, 0.9)
    ranked = rank_candidates([c1, c2], [ev1, ev2])
    assert ranked[0].candidate == c2


def test_rank_tie_breaker_confidence() -> None:
    c1 = _cand("a", 0.7)
    c2 = _cand("b", 0.9)
    ev = _ev(0.9, 0.9)
    ranked = rank_candidates([c1, c2], [ev, ev])
    assert ranked[0].candidate == c2


def test_rank_invalid_length() -> None:
    with pytest.raises(ValueError, match="same length"):
        rank_candidates([_cand("a", 0.9)], [])


def test_rank_specificity() -> None:
    c1 = CandidateRule(
        when=RuleWhen(trigger="a", context=("extra",)), do=RuleDo(directive="d"), confidence=0.9
    )
    c2 = _cand("a", 0.9)
    ev = _ev(0.9, 0.9)
    ranked = rank_candidates([c2, c1], [ev, ev])
    assert ranked[0].candidate == c1


def test_score_candidate_prefers_recall() -> None:
    # #731: the unsafe-004 shape (precision 1.0, recall 0.096) must not win.
    from cauterule.extraction.ranking import score_candidate

    assert score_candidate(0.9, 0.40) > score_candidate(1.0, 0.096)


def test_score_candidate_recall_floor() -> None:
    from cauterule.extraction.ranking import R_MIN_RECALL, score_candidate

    assert R_MIN_RECALL == 0.10
    assert score_candidate(1.0, 0.05) == 0.0


def test_rank_candidates_recall_floor_never_first() -> None:
    # #731: a recall below the floor can never be rank 1, even at precision 1.0.
    c1 = _cand("a", 0.9)  # precision 1.0, recall 0.05 -> below floor
    c2 = _cand("b", 0.9)  # precision 0.8, recall 0.30
    ranked = rank_candidates([c1, c2], [_ev(1.0, 0.05), _ev(0.8, 0.30)])
    assert ranked[0].candidate == c2
