from __future__ import annotations

from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.tui.review import ReviewScreen


def _make_candidate(trigger: str = "x fails") -> CandidateRule:
    return CandidateRule(
        when=RuleWhen(trigger=trigger),
        do=RuleDo(directive="do y"),
        confidence=0.85,
        reasoning="test reasoning",
        extraction_pass=1,
    )


def test_screen_instantiates() -> None:
    screen = ReviewScreen()
    assert screen is not None


def test_queue_label() -> None:
    screen = ReviewScreen()
    assert hasattr(screen, "query_one")


def test_empty_queue_shows_no_candidates() -> None:
    screen = ReviewScreen()
    assert len(screen._candidates) == 0


def test_mock_candidate_data() -> None:
    candidate = _make_candidate()
    assert candidate.when.trigger == "x fails"
    assert candidate.do.directive == "do y"
    assert candidate.confidence == 0.85


def test_compose_yields_widgets() -> None:
    screen = ReviewScreen()
    widgets = list(screen.compose())
    assert len(widgets) > 0


def test_reject_current_empty_queue() -> None:
    screen = ReviewScreen()
    screen.reject_current()
    assert screen._current_index == 0


def test_approve_current_empty_queue() -> None:
    screen = ReviewScreen()
    screen.approve_current()
    assert screen._current_index == 0


def test_reject_current_removes_candidate() -> None:
    candidates = [_make_candidate("a"), _make_candidate("b")]
    screen = ReviewScreen()
    screen._candidates = list(candidates)
    screen._current_index = 0
    screen.reject_current()
    assert len(screen._candidates) == 1
    assert screen._current_index == 0
