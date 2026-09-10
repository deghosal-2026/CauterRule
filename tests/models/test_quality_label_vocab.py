""""Tests for quality_label canonical vocabulary agreement (#612)."""

from __future__ import annotations

import pytest

from cauterule.models.trajectory import (
    Trajectory,
    Step,
    _VALID_QUALITY_LABELS,
)


def _traj(quality_label: str) -> Trajectory:
    return Trajectory(
        id="T-001",
        timestamp="t",
        task="task",
        steps=(Step(step_number=1, tool="bash", output="ok"),),
        success=False,
        quality_label=quality_label,  # type: ignore[arg-type]
    )


def test_canonical_vocabulary_has_all_doc_endorsed() -> None:
    # The canonical set must include every value the corpus docs endorse
    # (clear, noisy, ambiguous, multi-causal, misleading, open-ended) plus
    # operator-induced.
    assert _VALID_QUALITY_LABELS == {
        "clear",
        "noisy",
        "ambiguous",
        "multi-causal",
        "misleading",
        "operator-induced",
        "open-ended",
    }


def test_noisy_is_accepted() -> None:
    assert _traj("noisy").quality_label == "noisy"


def test_open_ended_is_accepted() -> None:
    assert _traj("open-ended").quality_label == "open-ended"


def test_operator_induced_is_accepted() -> None:
    assert _traj("operator-induced").quality_label == "operator-induced"


def test_success_rejected() -> None:
    with pytest.raises(ValueError, match="quality_label"):
        _traj("success")


def test_unlabeled_rejected() -> None:
    with pytest.raises(ValueError, match="quality_label"):
        _traj("unlabeled")