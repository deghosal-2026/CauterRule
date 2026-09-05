"""Test 24.11: Human vs LLM comparison — compare manual vs extracted rules."""

from __future__ import annotations

from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.models.trajectory import Step, Trajectory
from cauterule.replay.determinism import deterministic_replay


def _manual_rule() -> CandidateRule:
    return CandidateRule(
        when=RuleWhen(trigger="git push fails"),
        do=RuleDo(directive="run git pull --rebase before pushing", because="remote has commits"),
        confidence=0.95,
        reasoning="human-crafted: common git workflow",
    )


def _llm_extracted_rule() -> CandidateRule:
    return CandidateRule(
        when=RuleWhen(trigger="git push fails"),
        do=RuleDo(directive="pull --rebase"),
        confidence=0.85,
        reasoning="auto-extracted from trajectory",
    )


def _traj(tid: str, task: str, success: bool, error: str = "", failure_class: str | None = None) -> Trajectory:
    steps = (Step(1, "bash", error=error),) if error else (Step(1, "bash", output="ok"),)
    return Trajectory(id=tid, timestamp="t", task=task, steps=steps, success=success, failure_class=failure_class)


def test_human_rule_at_least_as_good_as_llm() -> None:
    trajs = [
        _traj("F1", "git push fails due to remote ahead", False, error="non-fast-forward"),
        _traj("F2", "git push fails due to merge", False, error="merge conflict"),
        _traj("S1", "docker build succeeds", True),
    ]
    manual_report = deterministic_replay(_manual_rule(), trajs)
    llm_report = deterministic_replay(_llm_extracted_rule(), trajs)
    assert manual_report.precision >= llm_report.precision


def test_human_and_llm_both_prevent_failures() -> None:
    trajs = [
        _traj("F1", "git push fails", False, error="err"),
        _traj("F2", "git push fails again", False, error="err"),
        _traj("S1", "lint check", True),
    ]
    manual = deterministic_replay(_manual_rule(), trajs)
    llm = deterministic_replay(_llm_extracted_rule(), trajs)
    assert len(manual.failures_prevented) > 0
    assert len(llm.failures_prevented) > 0


def test_human_rule_higher_confidence() -> None:
    assert _manual_rule().confidence > _llm_extracted_rule().confidence


def test_varying_rule_specificity() -> None:
    specific = _manual_rule()
    generic = _llm_extracted_rule()
    trajs = [
        _traj("F1", "git push fails on main", False, error="err"),
        _traj("F2", "git push fails on feature", False, error="err"),
        _traj("S1", "npm test", True),
    ]
    specific_report = deterministic_replay(specific, trajs)
    generic_report = deterministic_replay(generic, trajs)
    assert specific_report.precision == generic_report.precision
    assert specific_report.recall == generic_report.recall
