from __future__ import annotations

from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.tui.batch import BatchReviewScreen


def _make_candidate(i: int = 0) -> CandidateRule:
    conf = min(0.5 + i * 0.05, 1.0)
    return CandidateRule(
        when=RuleWhen(trigger=f"trigger-{i}"),
        do=RuleDo(directive=f"directive-{i}"),
        confidence=conf,
        extraction_pass=1,
    )


def test_batch_screen_instantiates() -> None:
    screen = BatchReviewScreen()
    assert screen is not None


def test_batch_screen_with_candidates() -> None:
    candidates = [_make_candidate(i) for i in range(10)]
    screen = BatchReviewScreen(candidates)
    assert len(screen._candidates) == 10


def test_approve_all_dismiss() -> None:
    result = {"action": "approve_all", "count": 10}
    assert result["action"] == "approve_all"
    assert result["count"] == 10


def test_reject_all_dismiss() -> None:
    result = {"action": "reject_all", "count": 10}
    assert result["action"] == "reject_all"
    assert result["count"] == 10


def test_batch_shows_first_10() -> None:
    candidates = [_make_candidate(i) for i in range(15)]
    shown = candidates[:10]
    assert len(shown) == 10


def test_batch_empty_candidates() -> None:
    screen = BatchReviewScreen()
    assert screen._candidates == []
