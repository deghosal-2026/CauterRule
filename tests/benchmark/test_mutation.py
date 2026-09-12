"""Test 24.8: Rule mutation testing — perturbed rules degrade replay quality."""

from __future__ import annotations

from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.models.trajectory import Step, Trajectory
from cauterule.replay.determinism import deterministic_replay


def _traj(tid: str, task: str, success: bool, error: str = "") -> Trajectory:
    steps = (Step(1, "bash", error=error),) if error else (Step(1, "bash", output="ok"),)
    return Trajectory(id=tid, timestamp="t", task=task, steps=steps, success=success)


def test_mutation_good_rule_passes() -> None:
    good = CandidateRule(
        when=RuleWhen(trigger="git push fails"),
        do=RuleDo(directive="run pull --rebase first"),
        confidence=0.95,
    )
    trajs = [
        _traj("F1", "git push fails non-fast-forward", False, error="non-fast-forward"),
        _traj("F2", "git push fails merge conflict", False, error="merge conflict"),
        _traj("S1", "docker build succeeds", True),
    ]
    report = deterministic_replay(good, trajs)
    assert report.verdict == "pass" or len(report.failures_prevented) > 0


def test_mutation_bad_rule_trigger_shift() -> None:
    good = CandidateRule(
        when=RuleWhen(trigger="git push fails"),
        do=RuleDo(directive="run pull --rebase"),
        confidence=0.95,
    )
    bad = CandidateRule(
        when=RuleWhen(trigger="git push fails non-fast-forward"),
        do=RuleDo(directive="run pull --rebase"),
        confidence=0.95,
    )
    trajs = [
        _traj("F1", "git push fails non-fast-forward", False, error="non-fast-forward"),
        _traj("F2", "git push fails merge conflict", False, error="merge conflict"),
        _traj("S1", "docker build succeeds", True),
    ]
    good_report = deterministic_replay(good, trajs)
    bad_report = deterministic_replay(bad, trajs)
    assert len(good_report.failures_prevented) >= len(bad_report.failures_prevented)


def test_mutation_multiple_perturbations() -> None:
    original = CandidateRule(
        when=RuleWhen(trigger="npm install fails"),
        do=RuleDo(directive="run npm cache clean"),
        confidence=0.95,
    )
    perturbations = [
        CandidateRule(
            when=RuleWhen(trigger="npm install fails", context=("wrong context",)),
            do=RuleDo(directive="x"),
            confidence=0.95,
        ),
        CandidateRule(
            when=RuleWhen(trigger="docker build fails"), do=RuleDo(directive="x"), confidence=0.95
        ),
        CandidateRule(when=RuleWhen(trigger="npm"), do=RuleDo(directive="x"), confidence=0.95),
    ]
    trajs = [
        _traj("F1", "npm install fails timeout", False, error="timeout"),
        _traj("F2", "npm install fails missing dep", False, error="missing dep"),
        _traj("S1", "npm install succeeds", True),
    ]
    orig_report = deterministic_replay(original, trajs)
    degraded = sum(
        1 for p in perturbations if deterministic_replay(p, trajs).precision < orig_report.precision
    )
    assert degraded >= 2
