"""Test 24.10: Ablation studies — compare no clustering vs clustering, single-pass vs multi-pass."""

from __future__ import annotations

from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.models.trajectory import Step, Trajectory
from cauterule.replay.determinism import deterministic_replay


def _cand(trigger: str, confidence: float = 0.9) -> CandidateRule:
    return CandidateRule(
        when=RuleWhen(trigger=trigger),
        do=RuleDo(directive="d"),
        confidence=confidence,
    )


def _traj(tid: str, task: str, success: bool, error: str = "") -> Trajectory:
    steps = (Step(1, "bash", error=error),) if error else (Step(1, "bash", output="ok"),)
    return Trajectory(id=tid, timestamp="t", task=task, steps=steps, success=success)


def _no_clustering_rules() -> list[CandidateRule]:
    return [
        _cand("git push fails", 0.9),
        _cand("git merge conflict", 0.85),
        _cand("docker build fails", 0.8),
    ]


def _clustered_rules() -> list[CandidateRule]:
    return [
        _cand("git push fails", 0.88),
        _cand("docker build fails", 0.82),
    ]


def test_ablation_clustered_vs_unclustered_coverage() -> None:
    trajs = [
        _traj("F1", "git push fails", False, error="err"),
        _traj("F2", "git merge conflict", False, error="err"),
        _traj("F3", "git push fails again", False, error="err"),
        _traj("S1", "docker build succeeds", True),
    ]
    unclustered_prevented: set[str] = set()
    for rule in _no_clustering_rules():
        report = deterministic_replay(rule, trajs)
        unclustered_prevented.update(report.failures_prevented)

    clustered_prevented: set[str] = set()
    for rule in _clustered_rules():
        report = deterministic_replay(rule, trajs)
        clustered_prevented.update(report.failures_prevented)

    assert len(clustered_prevented) > 0
    assert len(unclustered_prevented) > 0


def test_ablation_single_pass_vs_multi_pass_coverage() -> None:
    trajs = [
        _traj("F1", "git push fails", False, error="err"),
        _traj("F2", "docker build fails", False, error="err"),
        _traj("F3", "npm install fails", False, error="err"),
        _traj("S1", "simple task", True),
    ]

    single_pass = [_cand("git push fails", 0.9)]
    multi_pass = [
        _cand("git push fails", 0.9),
        _cand("docker build fails", 0.8),
        _cand("npm install fails", 0.7),
    ]

    single_prevented: set[str] = set()
    for rule in single_pass:
        report = deterministic_replay(rule, trajs)
        single_prevented.update(report.failures_prevented)

    multi_prevented: set[str] = set()
    for rule in multi_pass:
        report = deterministic_replay(rule, trajs)
        multi_prevented.update(report.failures_prevented)

    assert len(multi_prevented) >= len(single_prevented)


def test_ablation_confidence_sensitivity() -> None:
    trajs = [
        _traj("F1", "git push fails", False, error="err"),
        _traj("F2", "git push conflict", False, error="err"),
        _traj("S1", "docker build", True),
    ]
    high_conf = deterministic_replay(_cand("git push fails", 0.95), trajs)
    low_conf = deterministic_replay(_cand("git push fails", 0.5), trajs)
    assert high_conf.precision >= low_conf.precision
