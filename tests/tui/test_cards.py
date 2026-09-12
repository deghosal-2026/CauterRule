from __future__ import annotations

from cauterule.models.rule import ReplayEvidence
from cauterule.tui.cards import EvidenceCard


def test_card_instantiates() -> None:
    card = EvidenceCard()
    assert card is not None


def test_card_render_with_mock_evidence() -> None:
    evidence = ReplayEvidence(
        failures_prevented=("F-1", "F-2"),
        successes_broken=("S-1",),
        precision=1.0,
        recall=0.5,
    )
    card = EvidenceCard()
    card.render_evidence(evidence)
    output = str(card.render())
    assert "Prevented 2 failures" in output
    assert "broke 1 successes" in output
    assert "Precision: 1.00" in output
    assert "Recall: 0.50" in output


def test_card_render_no_evidence() -> None:
    evidence = ReplayEvidence()
    card = EvidenceCard()
    card.render_evidence(evidence)
    output = str(card.render())
    assert "Prevented 0 failures" in output
    assert "broke 0 successes" in output


def test_card_render_dict() -> None:
    card = EvidenceCard()
    card.render_dict(
        {
            "failures_prevented": ["F-1"],
            "successes_broken": [],
            "precision": 0.75,
            "recall": 0.25,
        }
    )
    output = str(card.render())
    assert "Prevented 1 failures" in output
    assert "broke 0 successes" in output
    assert "Precision: 0.75" in output


def test_card_initial_state() -> None:
    card = EvidenceCard()
    assert card._evidence is None
