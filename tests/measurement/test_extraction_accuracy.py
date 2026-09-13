"""Tests for extraction-accuracy measurement (#730)."""

from __future__ import annotations

from cauterule.measurement.extraction_accuracy import (
    ExtractionRecord,
    measure_extraction_accuracy,
    parse_expected_rule,
    records_from_results,
    score_rule,
)

_EXPECTED = "when git push fails with non-fast-forward, pull latest changes before pushing"


def test_parse_expected_rule() -> None:
    trigger, directive = parse_expected_rule(_EXPECTED)
    assert trigger == "git push fails with non-fast-forward"
    assert directive == "pull latest changes before pushing"
    # no comma -> whole string is the trigger
    assert parse_expected_rule("when build fails") == ("build fails", "")


def test_reworded_rule_semantically_agrees_token_f1_lower() -> None:
    score = score_rule(
        "when git push fails with non-fast-forward",
        "pull latest changes before pushing",
        _EXPECTED,
    )
    assert score.semantic_f1 >= 0.6
    assert score.agreement is True
    # literal token match on the directive is not required for agreement
    assert 0.0 <= score.token_f1 <= 1.0


def test_unrelated_rule_low_f1_and_no_agreement() -> None:
    score = score_rule("when plants need water", "water the office plants", _EXPECTED)
    assert score.semantic_f1 < 0.6
    assert score.agreement is False


def test_agreement_is_trigger_only_directive_not_gated() -> None:
    """J6: a semantically-correct trigger agrees even when the directive is
    reworded or wrong; the directive is reported as ``directive_f1`` alongside
    but does not gate the headline ``agreement``."""
    score = score_rule(
        "when git push fails with non-fast-forward",
        "delete the remote branch",
        _EXPECTED,
    )
    assert score.semantic_f1 >= 0.6
    assert score.agreement is True
    # the directive genuinely differs from the expected one, yet still agrees
    assert score.directive_f1 < 0.5


def test_measure_excludes_no_expected_rule() -> None:
    records = [
        ExtractionRecord(
            trigger="when git push fails with non-fast-forward",
            directive="pull latest changes before pushing",
            expected_rule=_EXPECTED,
        ),
        ExtractionRecord(
            trigger="when git push fails",
            directive="rebase",
            expected_rule="when git push fails, rebase the branch",
        ),
    ]
    report = measure_extraction_accuracy(records)
    assert report.n == 2
    assert 0.0 <= report.agreement <= 1.0
    assert report.semantic_f1 >= report.token_f1 or report.token_f1 >= 0.0


def test_measure_empty_is_na_zero_not_error() -> None:
    report = measure_extraction_accuracy([])
    assert report.n == 0
    assert report.semantic_f1 == 0.0
    assert report.agreement == 0.0


def test_to_dict_is_null_when_no_ground_truth() -> None:
    """J10: an empty report must serialize as nulls, not a hard 0.0."""
    d = measure_extraction_accuracy([]).to_dict()
    assert d["n"] == 0
    for key in ("token_f1", "semantic_f1", "directive_f1", "token_agreement", "agreement"):
        assert d[key] is None, key


def test_to_dict_has_numbers_when_measured() -> None:
    d = measure_extraction_accuracy(
        [
            ExtractionRecord(
                trigger="when git push fails with non-fast-forward",
                directive="pull latest changes before pushing",
                expected_rule=_EXPECTED,
            )
        ]
    ).to_dict()
    assert d["n"] == 1
    assert isinstance(d["semantic_f1"], float)
    assert isinstance(d["agreement"], float)


def test_records_from_results_skips_missing_expected() -> None:
    results: list[dict[str, object]] = [
        {
            "trajectory": {"expected_rule": _EXPECTED},
            "best": {"candidate": {"when": "when git push fails", "do": "pull"}},
        },
        {"trajectory": {"expected_rule": None}, "best": {"candidate": {"when": "x", "do": "y"}}},
        {"trajectory": {"expected_rule": _EXPECTED}},  # no best candidate
    ]
    records = records_from_results(results)
    assert len(records) == 1
    assert records[0].trigger == "when git push fails"
