"""Test 24.1: Replay determinism — same input always produces same output."""

from __future__ import annotations

from cauterule.models.candidate import CandidateRule
from cauterule.models.evidence import EvidenceReport
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.models.trajectory import Step, Trajectory
from cauterule.replay.determinism import deterministic_replay


def _cand(trigger: str, context: tuple[str, ...] = ()) -> CandidateRule:
    return CandidateRule(
        when=RuleWhen(trigger=trigger, context=context),
        do=RuleDo(directive="d"),
        confidence=0.9,
    )


def _traj(tid: str, success: bool) -> Trajectory:
    steps = (Step(1, "bash", error="err"),) if not success else (Step(1, "bash", output="ok"),)
    return Trajectory(id=tid, timestamp="t", task="some task", steps=steps, success=success)


def test_replay_determinism_identical_inputs() -> None:
    cand = _cand("git push fails")
    trajs = [_traj("T-1", False), _traj("T-2", False), _traj("T-3", True)]
    r1: EvidenceReport = deterministic_replay(cand, trajs)
    r2: EvidenceReport = deterministic_replay(cand, trajs)
    assert r1 == r2


def test_replay_determinism_across_multiple_fields() -> None:
    cand = _cand("docker fails")
    trajs = [_traj("A-1", False), _traj("B-1", False), _traj("C-1", True), _traj("D-1", True)]
    r1 = deterministic_replay(cand, trajs)
    r2 = deterministic_replay(cand, trajs)
    assert r1.precision == r2.precision
    assert r1.recall == r2.recall
    assert r1.verdict == r2.verdict
    assert r1.failures_prevented == r2.failures_prevented
    assert r1.successes_broken == r2.successes_broken
    assert r1.replay_trace == r2.replay_trace


def test_replay_determinism_reordering_same_result() -> None:
    cand = _cand("git merge")
    trajs = [_traj("T-2", False), _traj("T-1", True), _traj("T-3", False)]
    r1 = deterministic_replay(cand, trajs)
    r2 = deterministic_replay(cand, list(reversed(trajs)))
    assert r1 == r2
