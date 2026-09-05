from __future__ import annotations

from typing import Any

from cauterule.models.rule import (
    Provenance,
    ReplayEvidence,
    RuleDo,
    RuleWhen,
    StandingRule,
)
from cauterule.tui.confidence import ConfidenceCard


def _make_rule(
    confidence: float = 0.9,
    hit_count: int = 5,
    last_match: str | None = "2024-01-01",
    status: Any = "active",
    tags: tuple[str, ...] = ("python", "deploy"),
) -> StandingRule:
    return StandingRule(
        id="R-001",
        when=RuleWhen(trigger="x fails"),
        do=RuleDo(directive="do y"),
        confidence=confidence,
        hit_count=hit_count,
        last_match=last_match,
        status=status,
        tags=tags,
        promoted_at="2024-01-01",
        provenance=Provenance(
            source_trajectory="traj.json",
            extracted_by="extractor-v1",
            extract_timestamp="2024-01-01T00:00:00",
            extraction_pass=1,
            replay_evidence=ReplayEvidence(),
        ),
    )


def test_card_instantiates() -> None:
    card = ConfidenceCard()
    assert card is not None


def test_card_render_with_mock_rule() -> None:
    rule = _make_rule()
    card = ConfidenceCard()
    card.render_rule(rule)
    output = str(card.render())
    assert "Confidence: 0.90" in output
    assert "Hit count: 5" in output
    assert "Last hit: 2024-01-01" in output
    assert "Status: active" in output
    assert "python" in output
    assert "deploy" in output


def test_card_render_no_last_match() -> None:
    rule = _make_rule(last_match=None)
    card = ConfidenceCard()
    card.render_rule(rule)
    output = str(card.render())
    assert "Last hit: never" in output


def test_card_render_no_tags() -> None:
    rule = _make_rule(tags=())
    card = ConfidenceCard()
    card.render_rule(rule)
    output = str(card.render())
    assert "Tags: none" in output


def test_card_render_dict() -> None:
    card = ConfidenceCard()
    card.render_dict(0.5, 3, "2024-06-01", "retired", ("test",))
    output = str(card.render())
    assert "Confidence: 0.50" in output
    assert "Hit count: 3" in output
    assert "Status: retired" in output
    assert "test" in output


def test_card_initial_state() -> None:
    card = ConfidenceCard()
    assert card._rule is None
