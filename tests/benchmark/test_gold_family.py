"""Test 24.2: Gold-family acceptance rate >= 85%.

Gold-family candidates are well-formed rules derived from clear failure
trajectories.  At least 85 % of them should receive a ``"pass"`` verdict."""

from __future__ import annotations

from cauterule.models.candidate import CandidateRule
from cauterule.models.evidence import EvidenceReport
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.models.trajectory import Step, Trajectory
from cauterule.replay.determinism import deterministic_replay


def _gold_candidate(trigger: str) -> CandidateRule:
    return CandidateRule(
        when=RuleWhen(trigger=trigger),
        do=RuleDo(directive="apply fix"),
        confidence=0.95,
        reasoning="clear failure pattern",
    )


def _failure_traj(tid: str, task: str, error: str) -> Trajectory:
    return Trajectory(
        id=tid,
        timestamp="t",
        task=task,
        steps=(Step(1, "bash", error=error),),
        success=False,
        failure_point="step1",
    )


def _success_traj(tid: str, task: str) -> Trajectory:
    return Trajectory(
        id=tid,
        timestamp="t",
        task=task,
        steps=(Step(1, "bash", output="ok"),),
        success=True,
    )


GOLD_RULES: list[tuple[CandidateRule, list[Trajectory]]] = [
    (
        _gold_candidate("git push fails"),
        [
            _failure_traj("F1", "git push fails non-fast-forward", "non-fast-forward"),
            _failure_traj("F2", "git push fails merge conflict", "merge conflict"),
            _success_traj("S1", "docker build succeeds"),
        ],
    ),
    (
        _gold_candidate("docker build fails"),
        [
            _failure_traj("F3", "docker build fails exit code 1", "exit 1"),
            _failure_traj("F4", "docker build fails layer cache", "layer cache"),
            _success_traj("S2", "git push succeeds"),
        ],
    ),
    (
        _gold_candidate("npm install fails"),
        [
            _failure_traj("F5", "npm install fails timeout", "timeout exceeded"),
            _failure_traj("F6", "npm install fails missing dep", "missing dependency"),
            _success_traj("S3", "git push succeeds"),
        ],
    ),
]


def test_gold_family_acceptance_rate() -> None:
    passed = 0
    for cand, trajs in GOLD_RULES:
        report: EvidenceReport = deterministic_replay(cand, trajs)
        if report.verdict == "pass":
            passed += 1
    rate = passed / len(GOLD_RULES)
    assert rate >= 0.85, f"Gold-family acceptance rate {rate:.0%} < 85%"


def test_gold_family_all_produce_evidence() -> None:
    for cand, trajs in GOLD_RULES:
        report = deterministic_replay(cand, trajs)
        assert report.precision >= 0.0
        assert report.recall >= 0.0
