"""Tests for the behavioral outcome signal (#720)."""

from __future__ import annotations

from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.models.trajectory import Step, Trajectory
from cauterule.replay.matcher import is_grounded
from cauterule.replay.outcome import build_outcome_report, simulate_outcome

_TRIGGER = "git push fails with non-fast-forward"


def _cand(trigger: str = _TRIGGER, signature: str | None = None) -> CandidateRule:
    return CandidateRule(
        when=RuleWhen(trigger=trigger, signature=signature),
        do=RuleDo(directive="pull latest changes before pushing"),
        confidence=0.9,
    )


def _fail(id: str, error: str, failure_class: str | None = None) -> Trajectory:
    return Trajectory(
        id=id,
        timestamp="t",
        task="git push",
        steps=(Step(1, "bash", error=error),),
        success=False,
        failure_class=failure_class,
    )


def _success(id: str, task: str) -> Trajectory:
    return Trajectory(id=id, timestamp="t", task=task, steps=(), success=True)


def test_is_grounded_signature() -> None:
    cand = _cand(signature="non-fast-forward")
    traj = _fail("F", "rejected: non-fast-forward", "git/push/non-fast-forward")
    assert is_grounded(cand, traj)


def test_is_grounded_distinctive_phrase() -> None:
    cand = _cand()  # no structured signature
    traj = _fail("F", "error: failed to push some refs (non-fast-forward)")
    assert is_grounded(cand, traj)


def test_is_grounded_vague_false() -> None:
    cand = _cand(trigger="command failed")
    traj = _fail("F", "exit status 1")
    assert not is_grounded(cand, traj)


def test_simulate_outcome_grounded_prevented() -> None:
    cand = _cand(signature="non-fast-forward")
    traj = _fail("F", "rejected: non-fast-forward", "git/push/non-fast-forward")
    assert simulate_outcome(cand, traj) == "prevented"


def test_simulate_outcome_grounded_broken() -> None:
    # A success whose failure signature matches the rule -> verified broken.
    cand = _cand(signature="non-fast-forward")
    traj = Trajectory(
        id="S",
        timestamp="t",
        task="git push fails with non-fast-forward",
        steps=(),
        success=True,
        failure_class="git/push/non-fast-forward",
    )
    assert simulate_outcome(cand, traj) == "broken"


def test_simulate_outcome_ungrounded_is_unverified() -> None:
    # Matches lexically but is not anchored to the failure -> unverified.
    cand = _cand()
    traj = _success("S", "git push fails with non-fast-forward but succeeded")
    assert simulate_outcome(cand, traj) == "unverified"


def test_build_outcome_report_precision() -> None:
    cand = _cand(signature="non-fast-forward")
    trajs = [
        _fail(f"F{i}", "rejected: non-fast-forward", "git/push/non-fast-forward") for i in range(5)
    ] + [
        _success(f"S{i}", "git push fails with non-fast-forward but succeeded") for i in range(3)
    ]
    report = build_outcome_report(cand, trajs)
    assert len(report.verified_prevented) == 5
    assert len(report.verified_broken) == 0
    assert len(report.unverified) == 3
    assert report.precision == 1.0


def test_build_outcome_report_property() -> None:
    cand = _cand()
    trajs = [
        _fail("F1", "rejected: non-fast-forward", "git/push"),
        _success("S1", "git push fails with non-fast-forward but succeeded"),
        _success("S2", "git push fails with non-fast-forward but local branch was reset"),
    ]
    report = build_outcome_report(cand, trajs)
    total = len(report.verified_prevented) + len(report.verified_broken) + len(report.unverified)
    assert total == len(trajs)
    assert 0.0 <= report.precision <= 1.0
