"""Tests for corpus validation and trajectory annotations."""

from cauterule.corpus.validation import (
    corpus_size_report,
    validate_annotations,
    validate_corpus_sizes,
)
from cauterule.models.trajectory import Step, Trajectory


def test_validate_corpus_sizes_below_minimum() -> None:
    warnings = validate_corpus_sizes({"successes": 20, "failures/negative": 10, "nearmiss": 14})
    assert len(warnings) == 3
    assert any("successes" in w for w in warnings)


def test_validate_corpus_sizes_meets_minimum() -> None:
    warnings = validate_corpus_sizes({"successes": 50, "failures/negative": 50, "nearmiss": 50})
    assert warnings == []


def test_corpus_size_report() -> None:
    report = corpus_size_report({"successes": 50, "failures/negative": 50, "nearmiss": 50})
    assert report["all_ok"] is True
    report2 = corpus_size_report({"successes": 20, "failures/negative": 50, "nearmiss": 50})
    assert report2["all_ok"] is False


def test_trajectory_expected_outcome() -> None:
    traj = Trajectory(
        id="T-001",
        timestamp="t",
        task="do thing",
        steps=(Step(1, "bash", error="fail"),),
        success=False,
        expected_outcome="should_extract",
        expected_outcome_rationale="clear failure should produce rule",
    )
    assert traj.expected_outcome == "should_extract"
    d = traj.to_dict()
    assert d["expected_outcome"] == "should_extract"
    restored = Trajectory.from_dict(d)
    assert restored.expected_outcome == "should_extract"


def test_validate_annotations() -> None:
    trajs = [
        Trajectory(
            id="T-001",
            timestamp="t",
            task="a",
            steps=(Step(1, "bash", output="ok"),),
            success=True,
            expected_outcome="should_silence",
        ),
        Trajectory(
            id="T-002", timestamp="t", task="b", steps=(Step(1, "bash", output="ok"),), success=True
        ),
    ]
    warnings = validate_annotations(trajs)
    assert len(warnings) == 1
    assert "T-002" in warnings[0]
