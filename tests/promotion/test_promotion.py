"""Tests for the promotion gate module."""

from __future__ import annotations

from pathlib import Path

from cauterule.linter.orchestrator import LinterResult
from cauterule.models.candidate import CandidateRule
from cauterule.models.conflict import ConflictReport
from cauterule.models.evidence import EvidenceReport
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.promotion.auto import auto_promote
from cauterule.promotion.executor import execute_promotion
from cauterule.promotion.human import human_review
from cauterule.promotion.hybrid import hybrid_promote
from cauterule.promotion.thresholds import get_thresholds

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _candidate(confidence: float = 0.95) -> CandidateRule:
    return CandidateRule(
        when=RuleWhen(trigger="git push fails"),
        do=RuleDo(directive="run pull --rebase first"),
        confidence=confidence,
        reasoning="Prevents divergent history",
    )


def _clean_linter() -> LinterResult:
    return LinterResult(warnings=())


def _dirty_linter() -> LinterResult:
    return LinterResult(warnings=("vague: 'be careful'",))


def _empty_conflict_list() -> list[ConflictReport]:
    return []


def _conflict_report() -> list[ConflictReport]:
    return [ConflictReport(type="duplicate", rules=("R-001",), trigger="git push fails")]


def _passing_evidence() -> EvidenceReport:
    return EvidenceReport(
        failures_prevented=("F-001",),
        successes_broken=(),
        precision=0.9,
        recall=0.8,
        verdict="pass",
    )


def _failing_evidence() -> EvidenceReport:
    return EvidenceReport(
        failures_prevented=(),
        successes_broken=("S-001",),
        precision=0.3,
        recall=0.2,
        verdict="fail",
    )


# ---------------------------------------------------------------------------
# thresholds
# ---------------------------------------------------------------------------

def test_get_thresholds_conservative() -> None:
    t = get_thresholds("conservative")
    assert t["min_confidence"] == 0.85
    assert t["linter_warning_limit"] == 0
    assert t["precision"] == 1.0


def test_get_thresholds_balanced() -> None:
    t = get_thresholds("balanced")
    assert t["min_confidence"] == 0.7
    assert t["precision"] == 1.0


def test_get_thresholds_aggressive() -> None:
    t = get_thresholds("aggressive")
    assert t["min_confidence"] == 0.5
    assert t["precision"] == 1.0
    assert t["recall"] == 0


def test_get_thresholds_invalid_mode() -> None:
    import pytest
    with pytest.raises(ValueError, match="unknown threshold mode"):
        get_thresholds("invalid")


# ---------------------------------------------------------------------------
# auto_promote
# ---------------------------------------------------------------------------

def test_auto_promote_clean() -> None:
    result = auto_promote(_candidate(), _passing_evidence(), _clean_linter(), _empty_conflict_list())
    assert result.verdict == "promote"
    assert result.approver == "auto"
    assert result.linter_warnings == ()


def test_auto_promote_linter_warnings() -> None:
    result = auto_promote(_candidate(), _passing_evidence(), _dirty_linter(), _empty_conflict_list())
    assert result.verdict == "reject"
    assert result.evidence_summary is not None
    assert "linter_passed=False" in result.evidence_summary
    assert result.linter_warnings == ("vague: 'be careful'",)


def test_auto_promote_conflicts() -> None:
    result = auto_promote(_candidate(), _passing_evidence(), _clean_linter(), _conflict_report())
    assert result.verdict == "reject"
    assert len(result.conflicts) == 1


def test_auto_promote_empty_conflict_none() -> None:
    result = auto_promote(_candidate(), _passing_evidence(), _clean_linter(), None)
    assert result.verdict == "promote"


def test_auto_promote_failing_evidence_rejected() -> None:
    result = auto_promote(_candidate(), _failing_evidence(), _clean_linter(), None)
    assert result.verdict == "reject"
    assert result.evidence_summary is not None
    assert "evidence_verdict=fail" in result.evidence_summary


# ---------------------------------------------------------------------------
# human_review
# ---------------------------------------------------------------------------

def test_human_review_always_needs_review() -> None:
    result = human_review(_candidate(), _passing_evidence(), _clean_linter())
    assert result.verdict == "needs_review"
    assert result.approver == "human"


def test_human_review_evidence_summary() -> None:
    result = human_review(_candidate(), _passing_evidence(), _clean_linter())
    assert result.evidence_summary is not None
    s = result.evidence_summary
    assert "git push fails" in s
    assert "pull --rebase" in s
    assert "Precision:" in s


def test_human_review_failing_evidence() -> None:
    result = human_review(_candidate(), _failing_evidence(), _clean_linter())
    assert result.verdict == "needs_review"
    assert result.evidence_summary is not None
    assert "Precision: 0.30" in result.evidence_summary


def test_human_review_linter_warnings_in_summary() -> None:
    result = human_review(_candidate(), _passing_evidence(), _dirty_linter())
    assert result.evidence_summary is not None
    assert "vague" in result.evidence_summary
    assert result.linter_warnings == ("vague: 'be careful'",)


def test_human_review_includes_reasoning() -> None:
    result = human_review(_candidate(), _passing_evidence(), _clean_linter())
    assert result.evidence_summary is not None
    assert "Extraction reasoning" in result.evidence_summary
    assert "divergent history" in result.evidence_summary


# ---------------------------------------------------------------------------
# hybrid_promote
# ---------------------------------------------------------------------------

def test_hybrid_high_confidence_clean() -> None:
    c = _candidate(confidence=0.95)
    result = hybrid_promote(c, _passing_evidence(), _clean_linter(), None, threshold=0.8)
    assert result.verdict == "promote"


def test_hybrid_high_confidence_dirty() -> None:
    c = _candidate(confidence=0.95)
    result = hybrid_promote(c, _passing_evidence(), _dirty_linter(), None, threshold=0.8)
    assert result.verdict == "reject"


def test_hybrid_low_confidence() -> None:
    c = _candidate(confidence=0.50)
    result = hybrid_promote(c, _failing_evidence(), _clean_linter(), None, threshold=0.8)
    assert result.verdict == "needs_review"
    assert result.approver == "human"


def test_hybrid_exact_threshold() -> None:
    c = _candidate(confidence=0.80)
    result = hybrid_promote(c, _passing_evidence(), _clean_linter(), None, threshold=0.8)
    assert result.verdict == "promote"


def test_hybrid_invalid_threshold() -> None:
    import pytest
    c = _candidate()
    with pytest.raises(ValueError, match="threshold must be in"):
        hybrid_promote(c, _passing_evidence(), _clean_linter(), None, threshold=1.5)


# ---------------------------------------------------------------------------
# execute_promotion
# ---------------------------------------------------------------------------

def test_execute_promotion_creates_rule_yaml(tmp_path: Path) -> None:
    rules_dir = tmp_path / "rules"
    config = {
        "rules_dir": str(rules_dir),
        "source_trajectory": "traj-001",
        "extracted_by": "extractor-m1",
        "extract_timestamp": "2025-01-01T00:00:00Z",
        "extraction_pass": 1,
        "promotion_mode": "auto",
        "status": "active",
    }
    rule_id = execute_promotion(_candidate(), config)
    assert rule_id == "R-001"
    rule_path = rules_dir / "R-001.yaml"
    assert rule_path.exists()
    content = rule_path.read_text(encoding="utf-8")
    assert "git push fails" in content
    assert "pull --rebase" in content


def test_execute_promotion_increments_id(tmp_path: Path) -> None:
    rules_dir = tmp_path / "rules"
    config = {
        "rules_dir": str(rules_dir),
        "source_trajectory": "traj-001",
        "extracted_by": "extractor-m1",
        "extract_timestamp": "2025-01-01T00:00:00Z",
        "extraction_pass": 1,
        "promotion_mode": "auto",
        "status": "active",
    }
    r1 = execute_promotion(_candidate(), config)
    r2 = execute_promotion(_candidate(), config)
    assert r1 == "R-001"
    assert r2 == "R-002"


def test_execute_promotion_writes_index(tmp_path: Path) -> None:
    import yaml

    rules_dir = tmp_path / "rules"
    config = {
        "rules_dir": str(rules_dir),
        "source_trajectory": "traj-001",
        "extracted_by": "extractor-m1",
        "extract_timestamp": "2025-01-01T00:00:00Z",
        "extraction_pass": 1,
        "promotion_mode": "auto",
        "status": "active",
    }
    execute_promotion(_candidate(), config)
    index_path = rules_dir / "index.yaml"
    assert index_path.exists()
    entries = yaml.safe_load(index_path.read_text(encoding="utf-8"))
    assert isinstance(entries, dict)
    assert "rules" in entries
    assert entries["rules"][0]["id"] == "R-001"


def test_execute_promotion_missing_config_key() -> None:
    import pytest
    with pytest.raises(KeyError):
        execute_promotion(_candidate(), {})
