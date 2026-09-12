"""Test 24.5: Success-regression catch rate >= 95%.

Rules that would break previously successful trajectories should be caught."""

from __future__ import annotations

from cauterule.models.candidate import CandidateRule
from cauterule.models.evidence import EvidenceReport
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.models.trajectory import Step, Trajectory
from cauterule.replay.determinism import deterministic_replay


def _breaking_rule(trigger: str) -> CandidateRule:
    return CandidateRule(
        when=RuleWhen(trigger=trigger),
        do=RuleDo(directive="interrupt the flow"),
        confidence=0.9,
    )


def _success_traj(tid: str, task: str) -> Trajectory:
    return Trajectory(
        id=tid,
        timestamp="t",
        task=task,
        steps=(Step(1, "bash", output="ok"),),
        success=True,
    )


def _failure_traj(tid: str, task: str) -> Trajectory:
    return Trajectory(
        id=tid,
        timestamp="t",
        task=task,
        steps=(Step(1, "bash", error="err"),),
        success=False,
    )


BREAKING_RULES: list[tuple[CandidateRule, list[Trajectory]]] = [
    (
        _breaking_rule("git push"),
        [
            _success_traj("S1", "git push succeeds"),
            _success_traj("S2", "git push works"),
            _failure_traj("F1", "docker fails"),
        ],
    ),
    (
        _breaking_rule("npm install"),
        [
            _success_traj("S3", "npm install works"),
            _success_traj("S4", "npm install passes"),
            _failure_traj("F2", "test fails"),
        ],
    ),
    (
        _breaking_rule("docker build"),
        [
            _success_traj("S5", "docker build ok"),
            _success_traj("S6", "docker build done"),
            _failure_traj("F3", "deploy fails"),
        ],
    ),
    (
        _breaking_rule("deploy"),
        [
            _success_traj("S7", "deploy success"),
            _success_traj("S8", "deploy completed"),
            _failure_traj("F4", "config error"),
        ],
    ),
]


def test_regression_catch_rate() -> None:
    caught = 0
    for cand, trajs in BREAKING_RULES:
        report: EvidenceReport = deterministic_replay(cand, trajs)
        if report.verdict == "fail" or len(report.successes_broken) > 0:
            caught += 1
    rate = caught / len(BREAKING_RULES)
    assert rate >= 0.95, f"Regression catch rate {rate:.0%} < 95%"


def test_regression_reports_broken_successes() -> None:
    for cand, trajs in BREAKING_RULES:
        report = deterministic_replay(cand, trajs)
        assert len(report.successes_broken) > 0
