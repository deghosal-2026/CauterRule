"""Test 24.3: Counterexample rejection rate >= 90%.

Plausible-looking but wrong rules should be rejected by replay.
These rules match too broadly and break successes, or fail to match
the right failure patterns, earning a ``"fail"`` verdict."""

from __future__ import annotations

from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.models.trajectory import Step, Trajectory
from cauterule.replay.determinism import deterministic_replay


def _bad_candidate(trigger: str) -> CandidateRule:
    return CandidateRule(
        when=RuleWhen(trigger=trigger),
        do=RuleDo(directive="do something unrelated"),
        confidence=0.95,
        reasoning="plausible but wrong",
    )


def _traj(tid: str, task: str, success: bool, error: str = "") -> Trajectory:
    steps = (Step(1, "bash", error=error),) if error else (Step(1, "bash", output="ok"),)
    return Trajectory(id=tid, timestamp="t", task=task, steps=steps, success=success)


BAD_RULES: list[tuple[CandidateRule, list[Trajectory]]] = [
    (
        _bad_candidate("git push"),
        [
            _traj("F1", "git push fails non-fast-forward", False, error="non-fast-forward"),
            _traj("S1", "git push succeeds", True),
            _traj("S2", "git push succeeds again", True),
        ],
    ),
    (
        _bad_candidate("npm install"),
        [
            _traj("F3", "npm install fails timeout", False, error="timeout"),
            _traj("S3", "npm install succeeds", True),
            _traj("S4", "npm install completes", True),
        ],
    ),
    (
        _bad_candidate("docker"),
        [
            _traj("F5", "docker build fails exit 1", False, error="exit 1"),
            _traj("S5", "docker build succeeds", True),
            _traj("S6", "docker test passes", True),
        ],
    ),
    (
        _bad_candidate("deploy"),
        [
            _traj("F7", "deploy fails timeout", False, error="timeout"),
            _traj("S7", "deploy succeeds", True),
            _traj("S8", "deploy completes", True),
        ],
    ),
]


def test_counterexample_rejection_rate() -> None:
    rejected = 0
    for cand, trajs in BAD_RULES:
        report = deterministic_replay(cand, trajs)
        if report.verdict == "fail":
            rejected += 1
    rate = rejected / len(BAD_RULES)
    assert rate >= 0.90, f"Counterexample rejection rate {rate:.0%} < 90%"


def test_bad_rules_break_successes() -> None:
    for cand, trajs in BAD_RULES:
        report = deterministic_replay(cand, trajs)
        assert len(report.successes_broken) > 0
