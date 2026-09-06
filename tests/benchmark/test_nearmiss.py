"""Test 24.4: Near-miss precision >= 90%.

Near-miss scenarios (trigger partially matches but conditions aren't fully met)
should not trigger rule application."""

from __future__ import annotations

from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.models.trajectory import Step, Trajectory
from cauterule.replay.matcher import is_near_miss


def _cand(trigger: str, context: tuple[str, ...] = ()) -> CandidateRule:
    return CandidateRule(
        when=RuleWhen(trigger=trigger, context=context),
        do=RuleDo(directive="d"),
        confidence=0.9,
    )


def _traj(tid: str, task: str) -> Trajectory:
    return Trajectory(
        id=tid,
        timestamp="t",
        task=task,
        steps=(Step(1, "bash", output="ok"),),
        success=True,
    )


NEAR_MISS_SCENARIOS: list[tuple[CandidateRule, Trajectory]] = [
    (
        _cand("git push fails", ("shared branch",)),
        _traj("T1", "git push succeeds"),
    ),
    (
        _cand("docker build fails", ("linux",)),
        _traj("T2", "docker build succeeds"),
    ),
    (
        _cand("npm install fails", ("node 18",)),
        _traj("T3", "npm install succeeds"),
    ),
    (
        _cand("deploy fails", ("production",)),
        _traj("T4", "deploy succeeds"),
    ),
    (
        _cand("test fails", ("unit",)),
        _traj("T5", "test passes"),
    ),
]


def test_near_miss_not_triggered() -> None:
    triggered = 0
    for cand, traj in NEAR_MISS_SCENARIOS:
        if not is_near_miss(cand, traj):
            triggered += 1
    rate = triggered / len(NEAR_MISS_SCENARIOS)
    assert rate >= 0.90, f"Near-miss non-trigger rate {rate:.0%} < 90%"


def test_near_miss_empty_context() -> None:
    cand = _cand("git push fails")
    traj = _traj("T6", "git push succeeds")
    assert not is_near_miss(cand, traj)
