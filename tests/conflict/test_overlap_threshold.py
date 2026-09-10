"""Tests for overlap threshold behavior (#609)."""

from __future__ import annotations

from cauterule.conflict.overlap import detect_overlaps
from cauterule.models.rule import Provenance, RuleDo, RuleWhen, StandingRule


def _rule(rid: str, trigger: str, directive: str) -> StandingRule:
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
        status="active",  # type: ignore[arg-type]
        promoted_at="2025-01-01T00:00:00",
    )


def test_single_shared_token_fp_rejected() -> None:
    # "git push to remote" vs "push to branch" share only "push" — must NOT report.
    a = _rule("R-001", "git push to remote", "pull --rebase")
    b = _rule("R-002", "push to branch", "create branch")
    assert detect_overlaps([a, b]) == []


def test_stop_word_only_fp_rejected() -> None:
    a = _rule("R-001", "deploy to prod", "run deploy")
    b = _rule("R-002", "build the image", "run build")
    assert detect_overlaps([a, b]) == []


def test_real_overlap_accepted() -> None:
    a = _rule("R-001", "deploy to prod", "run smoke tests")
    b = _rule("R-002", "deploy to staging prod", "run e2e")
    reports = detect_overlaps([a, b])
    assert len(reports) == 1
    assert reports[0].type == "overlap"


def test_overlap_fraction_in_resolution() -> None:
    a = _rule("R-001", "git push fails auth", "pull --rebase")
    b = _rule("R-002", "git push fails network", "fetch --all")
    reports = detect_overlaps([a, b])
    assert len(reports) == 1
    assert "overlap=" in (reports[0].resolution or "")
