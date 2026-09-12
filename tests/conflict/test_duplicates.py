"""Tests for duplicate detection (#610)."""

from __future__ import annotations

from cauterule.conflict import detect_duplicates
from cauterule.conflict.duplicates import _jaccard
from cauterule.models.rule import Provenance, RuleDo, RuleWhen, StandingRule


def _rule(
    rid: str,
    trigger: str,
    directive: str,
    status: str = "active",
) -> StandingRule:
    return StandingRule(
        id=rid,
        when=RuleWhen(trigger=trigger),
        do=RuleDo(directive=directive),
        confidence=0.9,
        provenance=Provenance(
            source_trajectory="t.json",
            extracted_by="test",
            extract_timestamp="2025-01-01T00:00:00",
            extraction_pass=1,
        ),
        status=status,  # type: ignore[arg-type]
        promoted_at="2025-01-01T00:00:00",
    )


def test_exact_duplicate_detected() -> None:
    a = _rule("R-001", "git push fails", "run git pull --rebase")
    b = _rule("R-002", "git push fails", "run git pull --rebase")
    reports = detect_duplicates([a, b])
    assert len(reports) == 1
    assert reports[0].type == "duplicate"
    assert reports[0].rules == ("R-001", "R-002")


def test_paraphrase_duplicate_detected() -> None:
    a = _rule("R-001", "permission denied pushing to remote", "run git pull --rebase")
    b = _rule("R-002", "access denied pushing to remote", "run git pull --rebase")
    reports = detect_duplicates([a, b])
    assert any(r.type == "duplicate" for r in reports)


def test_distinct_rules_not_flagged() -> None:
    a = _rule("R-001", "git push fails", "pull --rebase")
    b = _rule("R-002", "docker build fails", "fix dockerfile")
    assert detect_duplicates([a, b]) == []


def test_threshold_boundary() -> None:
    a = _rule("R-001", "git push fails to remote", "pull --rebase")
    b = _rule("R-002", "git push fails to origin", "pull --rebase")
    assert detect_duplicates([a, b], threshold=0.99) == []
    assert len(detect_duplicates([a, b], threshold=0.6)) == 1


def test_contradiction_not_duplicate() -> None:
    # Same trigger, opposite directive: contradiction, not duplicate (#code-review).
    a = _rule("R-001", "service down", "restart service")
    b = _rule("R-002", "service down", "do not restart service")
    assert detect_duplicates([a, b]) == []


def test_subset_not_duplicate() -> None:
    # Generic fallback rule vs a more specific rule must not be a duplicate
    # (Jaccard avoids the subset-1.0 artifact) (#code-review).
    a = _rule("R-001", "error occurs", "notify")
    b = _rule("R-002", "compile error occurs in docker build", "notify if build fails")
    assert detect_duplicates([a, b]) == []


def test_inactive_rules_excluded() -> None:
    a = _rule("R-001", "git push fails", "pull --rebase")
    b = _rule("R-002", "git push fails", "pull --rebase", status="retired")
    assert detect_duplicates([a, b]) == []


def test_jaccard_identity() -> None:
    assert _jaccard({"a", "b"}, {"a", "b"}) == 1.0
    assert _jaccard({"a", "b"}, {"a", "c"}) == 1.0 / 3.0
    assert _jaccard(set(), {"a"}) == 0.0
