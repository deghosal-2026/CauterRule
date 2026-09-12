from typing import Any, cast

import pytest

from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.models.trajectory import Step, Trajectory
from cauterule.replay.report import build_evidence_report


def _cand(trigger: str) -> CandidateRule:
    return CandidateRule(when=RuleWhen(trigger=trigger), do=RuleDo(directive="d"), confidence=0.9)


def _traj(id: str, task: str, success: bool, error: str = "") -> Trajectory:
    steps = (Step(1, "bash", error=error),) if error else ()
    return Trajectory(id=id, timestamp="t", task=task, steps=steps, success=success)


def test_report_prevented() -> None:
    cand = _cand("git push")
    trajs = [
        _traj("T-1", "git push fails", False, error="non-fast-forward"),
        _traj("T-2", "docker", False, error="err"),
    ]
    report = build_evidence_report(cand, trajs)
    assert "T-1" in report.failures_prevented
    assert report.precision > 0
    assert report.verdict in ("pass", "inconclusive", "fail")


def test_report_broken() -> None:
    cand = _cand("git push")
    # Need >= 3 trajectories to avoid inconclusive verdict
    trajs = [
        _traj("T-1", "git push succeeds", True),
        _traj("T-2", "git push succeeds", True),
        _traj("T-3", "git push succeeds", True),
    ]
    report = build_evidence_report(cand, trajs)
    assert "T-1" in report.successes_broken
    assert report.verdict == "fail"


def test_report_no_effect() -> None:
    cand = _cand("docker")
    trajs = [_traj("T-1", "git push", False, error="non-fast-forward")]
    report = build_evidence_report(cand, trajs)
    assert len(report.failures_prevented) == 0
    assert report.verdict == "inconclusive"


def test_report_insufficient_history() -> None:
    cand = _cand("git push")
    trajs = [_traj("T-1", "git push", False, "err")]
    report = build_evidence_report(cand, trajs)
    assert report.verdict == "inconclusive"  # < 3 trajectories


def test_report_trace() -> None:
    cand = _cand("git push")
    trajs = [_traj("T-1", "git push fails", False, "err")]
    report = build_evidence_report(cand, trajs)
    assert len(report.replay_trace) == 1
    assert report.replay_trace[0]["trajectory_id"] == "T-1"


def test_min_sample_override_surfaced() -> None:
    # #521: 2-trajectory all-prevented input yields inconclusive + a reason
    # string naming the min-sample policy and the computed verdict, with the
    # underlying data (failures_prevented, precision) untouched.
    cand = _cand("git push")
    trajs = [
        _traj("T-1", "git push fails", False, "non-fast-forward"),
        _traj("T-2", "git push fails", False, "non-fast-forward"),
    ]
    report = build_evidence_report(cand, trajs)
    assert report.verdict == "inconclusive"
    assert report.verdict_reason is not None
    assert "min_sample" in report.verdict_reason
    assert len(report.failures_prevented) == 2
    assert report.precision > 0


def test_frozen_report_cannot_mutate() -> None:
    import dataclasses

    cand = _cand("git push")
    trajs = [_traj("T-1", "git push fails", False, "err")]
    report = build_evidence_report(cand, trajs)
    with pytest.raises(dataclasses.FrozenInstanceError):
        cast(Any, report).verdict = "pass"


def test_report_surfaces_blocked_by_broken() -> None:
    # #724: the true blocking reason is recorded on the report.
    cand = _cand("git push")
    trajs = [_traj(f"T-{i}", "git push succeeds", True) for i in range(3)]
    report = build_evidence_report(cand, trajs)
    assert report.verdict == "fail"
    assert report.verdict_reason == "blocked_by_broken"


def test_report_near_miss_branch() -> None:
    # #723: a recovery success is counted as near_miss, not prevented/broken.
    cand = _cand("git push")
    trajs = [
        _traj("N-1", "git push retry", True),
        _traj("F-1", "git push fails", False, error="non-fast-forward"),
        _traj("F-2", "git push fails", False, error="non-fast-forward"),
    ]
    report = build_evidence_report(cand, trajs)
    assert "N-1" in report.near_misses


def test_report_surfaces_outcome_precision() -> None:
    # #720: behavioral (grounded) outcome is reported alongside the text verdict.
    cand = _cand("git push fails with non-fast-forward")
    trajs = [
        _traj(f"F{i}", "git push", False, error="rejected: non-fast-forward") for i in range(3)
    ]
    report = build_evidence_report(cand, trajs)
    assert report.outcome_precision == 1.0
    assert report.outcome_verdict == "pass"
    # round-trips through serialization
    from cauterule.models.evidence import EvidenceReport

    restored = EvidenceReport.from_dict(report.to_dict())
    assert restored.outcome_precision == 1.0
