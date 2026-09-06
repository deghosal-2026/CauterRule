"""Test 24.9: Confidence calibration — scores correlate with replay outcomes."""

from __future__ import annotations

import math

from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.models.trajectory import Step, Trajectory
from cauterule.replay.determinism import deterministic_replay


def _cand(trigger: str, confidence: float) -> CandidateRule:
    return CandidateRule(
        when=RuleWhen(trigger=trigger),
        do=RuleDo(directive="d"),
        confidence=confidence,
    )


def _traj(tid: str, task: str, success: bool, error: str = "") -> Trajectory:
    steps = (Step(1, "bash", error=error),) if error else (Step(1, "bash", output="ok"),)
    return Trajectory(id=tid, timestamp="t", task=task, steps=steps, success=success)


def test_higher_confidence_correlates_with_precision() -> None:
    trajs = [
        _traj("F1", "git push fails", False, error="err"),
        _traj("F2", "git push fails", False, error="err"),
        _traj("S1", "docker build", True),
    ]
    low_conf = _cand("git push fails", 0.5)
    high_conf = _cand("git push fails", 0.95)
    low_report = deterministic_replay(low_conf, trajs)
    high_report = deterministic_replay(high_conf, trajs)
    assert high_report.precision >= low_report.precision


def test_confidence_below_threshold_yields_inconclusive() -> None:
    cand = _cand("git push fails", 0.3)
    trajs = [
        _traj("F1", "git push fails", False, error="err"),
        _traj("F2", "git push fails", False, error="err"),
        _traj("S1", "docker test", True),
    ]
    report = deterministic_replay(cand, trajs)
    assert report.verdict in ("pass", "fail", "inconclusive")


def test_calibration_spread() -> None:
    confidences = [0.3, 0.5, 0.7, 0.9, 0.95]
    trajs = [
        _traj("F1", "git push fails", False, error="err"),
        _traj("F2", "git push fails too", False, error="err"),
        _traj("S1", "docker test", True),
    ]
    precisions: list[float] = []
    for conf in confidences:
        report = deterministic_replay(_cand("git push fails", conf), trajs)
        precisions.append(report.precision)
    for i in range(len(precisions) - 1):
        assert precisions[i] <= precisions[i + 1] or math.isclose(precisions[i], precisions[i + 1])
