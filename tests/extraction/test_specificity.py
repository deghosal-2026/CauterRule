"""Tests for trigger specificity scoring."""

from cauterule.extraction.specificity import is_generic, score_specificity
from cauterule.linter.orchestrator import lint_rule
from cauterule.linter.specificity import check_specificity


def test_specific_trigger() -> None:
    assert score_specificity("when git push fails with non-fast-forward") == "specific"
    assert score_specificity("when docker build fails with permission denied") == "specific"
    assert score_specificity("when npm install fails due to missing peer dependency") == "specific"


def test_generic_trigger() -> None:
    assert score_specificity("when a command fails") == "generic"
    assert score_specificity("when an error occurs") == "generic"
    assert is_generic("when a command fails") is True


def test_moderate_trigger() -> None:
    assert score_specificity("when a git command fails") == "moderate"
    assert score_specificity("when docker fails to start") == "moderate"


def test_hyphenated_generic_phrase_not_specific() -> None:
    # #784: plain-letter hyphenation is just a word separator, not an error code.
    assert score_specificity("does not work") == "generic"
    assert score_specificity("does-not-work") == "generic"
    assert score_specificity("does_not_work") == "generic"


def test_hyphenated_code_like_still_specific() -> None:
    # #784: genuine codes keep their specificity credit.
    assert score_specificity("non-fast-forward") == "specific"
    assert score_specificity("error-123") == "specific"
    assert score_specificity("exit_code") == "specific"


def test_linter_flags_hyphenated_generic() -> None:
    # #784: the hyphenated form of the golden broad trigger must be flagged.
    result = lint_rule("does-not-work", "restart the service")
    assert not result.passed
    assert any("generic trigger" in w.lower() for w in result.warnings)


def test_linter_rejects_generic() -> None:
    warnings = check_specificity("when a command fails")
    assert len(warnings) == 1
    assert "generic trigger" in warnings[0].lower()


def test_linter_passes_specific() -> None:
    assert check_specificity("when git push fails with non-fast-forward") == []


def test_lint_rule_rejects_generic_trigger() -> None:
    result = lint_rule("when a command fails", "do something")
    assert not result.passed
    assert any("generic trigger" in w.lower() for w in result.warnings)


def test_lint_rule_passes_specific_trigger() -> None:
    result = lint_rule("when git push fails with non-fast-forward", "run pull --rebase first")
    # May have other warnings, but not generic trigger
    assert not any("generic trigger" in w.lower() for w in result.warnings)
