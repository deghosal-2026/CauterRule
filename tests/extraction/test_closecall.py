from cauterule.extraction.closecall import get_close_call_candidates, is_close_call
from cauterule.extraction.ranking import RankedCandidate
from cauterule.models.candidate import CandidateRule
from cauterule.models.evidence import EvidenceReport
from cauterule.models.rule import RuleDo, RuleWhen


def _ranked(precisions: list[float]) -> list[RankedCandidate]:
    ranked: list[RankedCandidate] = []
    for i, p in enumerate(precisions):
        cand = CandidateRule(when=RuleWhen(trigger=f"t{i}"), do=RuleDo(directive="d"), confidence=0.9)
        ev = EvidenceReport(precision=p, recall=0.5, verdict="pass")
        ranked.append(RankedCandidate(candidate=cand, evidence=ev, rank=i + 1))
    return ranked


def test_is_close_call_true() -> None:
    ranked = _ranked([0.9, 0.88])
    assert is_close_call(ranked, threshold=0.05)
    assert not is_close_call(ranked, threshold=0.01)


def test_is_close_call_false() -> None:
    ranked = _ranked([0.9, 0.7])
    assert not is_close_call(ranked)


def test_is_close_call_single() -> None:
    assert not is_close_call(_ranked([0.9]))
    assert not is_close_call([])


def test_get_close_call_candidates() -> None:
    ranked = _ranked([0.9, 0.88, 0.5])
    assert len(get_close_call_candidates(ranked, threshold=0.05)) == 2
    assert len(get_close_call_candidates(ranked, threshold=0.01)) == 1
    assert get_close_call_candidates([]) == []
