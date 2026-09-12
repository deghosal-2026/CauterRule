"""Strict from_dict tests for StandingRule (#593)."""

from typing import Any

import pytest

from cauterule.models.rule import StandingRule


def _valid_rule_dict(**overrides: Any) -> dict[str, Any]:
    d = {
        "id": "R-001",
        "when": {"trigger": "git push fails", "context": []},
        "do": {"directive": "pull --rebase", "because": "remote ahead"},
        "confidence": 0.9,
        "provenance": {
            "source_trajectory": "t.jsonl",
            "extracted_by": "test",
            "extract_timestamp": "2026-01-01T00:00:00Z",
            "extraction_pass": 1,
        },
        "status": "retired",
        "promoted_at": "2026-01-01T00:00:00Z",
        "hit_count": 0,
    }
    d.update(overrides)
    return d


def test_missing_status_raises() -> None:
    # #593: absent status must not silently resurrect a rule as active.
    d = _valid_rule_dict()
    del d["status"]
    with pytest.raises(ValueError, match="status"):
        StandingRule.from_dict(d)


def test_none_status_raises() -> None:
    # Review: explicit null status is also missing, not active.
    with pytest.raises(ValueError, match="status"):
        StandingRule.from_dict(_valid_rule_dict(status=None))


def test_retired_rule_roundtrip_stays_retired() -> None:
    rule = StandingRule.from_dict(_valid_rule_dict(status="retired"))
    assert rule.status == "retired"
    assert StandingRule.from_dict(rule.to_dict()).status == "retired"


def test_invalid_status_rejected() -> None:
    with pytest.raises(ValueError, match="status"):
        StandingRule.from_dict(_valid_rule_dict(status="archived"))
