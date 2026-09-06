from __future__ import annotations

from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.tui.annotate import FAILURE_CATEGORIES, AnnotationScreen


def test_annotation_screen_instantiates() -> None:
    screen = AnnotationScreen()
    assert screen is not None


def test_annotation_screen_with_candidate() -> None:
    candidate = CandidateRule(
        when=RuleWhen(trigger="x fails"),
        do=RuleDo(directive="do y"),
        confidence=0.85,
    )
    screen = AnnotationScreen(candidate)
    assert screen._candidate is candidate


def test_failure_categories_defined() -> None:
    assert "logic_error" in FAILURE_CATEGORIES
    assert "missing_edge_case" in FAILURE_CATEGORIES
    assert "hallucination" in FAILURE_CATEGORIES
    assert "tool_misuse" in FAILURE_CATEGORIES
    assert "formatting" in FAILURE_CATEGORIES
    assert "other" in FAILURE_CATEGORIES


def test_tag_submission() -> None:
    screen = AnnotationScreen()
    screen._tags = ["python", "deploy"]
    screen._comment = "test comment"
    screen._category = "logic_error"
    result = screen._annotation_result()
    assert result["tags"] == ("python", "deploy")
    assert result["comment"] == "test comment"
    assert result["category"] == "logic_error"


def test_tag_submission_empty() -> None:
    screen = AnnotationScreen()
    screen._tags = []
    screen._comment = ""
    screen._category = ""
    result = screen._annotation_result()
    assert result["tags"] == ()
    assert result["comment"] == ""
