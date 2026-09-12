"""Test 24.7: Prompt bake-off harness compares prompt variants."""

from __future__ import annotations

from cauterule.benchmark.prompts import PromptBakeoffHarness
from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.models.trajectory import Step, Trajectory


def _traj(tid: str) -> Trajectory:
    return Trajectory(
        id=tid,
        timestamp="t",
        task="git push fails",
        steps=(Step(1, "bash", error="err"),),
        success=False,
    )


def _prompt_high_conf(traj: Trajectory) -> CandidateRule | None:
    return CandidateRule(
        when=RuleWhen(trigger="git push fails"), do=RuleDo(directive="fix"), confidence=0.95
    )


def _prompt_low_conf(traj: Trajectory) -> CandidateRule | None:
    return CandidateRule(
        when=RuleWhen(trigger="git push fails"), do=RuleDo(directive="fix"), confidence=0.60
    )


def _prompt_fails(traj: Trajectory) -> CandidateRule | None:
    return None


def test_prompt_bakeoff_run() -> None:
    prompts = {"high": _prompt_high_conf, "low": _prompt_low_conf, "fail": _prompt_fails}
    harness = PromptBakeoffHarness(prompts)
    trajs = [_traj("T-1"), _traj("T-2")]
    results = harness.run(trajs)
    assert "high" in results
    assert "low" in results
    assert "fail" in results
    assert len(results["high"]) == 2
    assert len(results["fail"]) == 2


def test_prompt_bakeoff_best_prompt() -> None:
    prompts = {"high": _prompt_high_conf, "low": _prompt_low_conf}
    harness = PromptBakeoffHarness(prompts)
    results = harness.run([_traj("T-1"), _traj("T-2")])
    best = harness.best_prompt(results)
    assert best == "high"


def test_prompt_bakeoff_best_prompt_handles_empty() -> None:
    prompts = {"fail": _prompt_fails}
    harness = PromptBakeoffHarness(prompts)
    results = harness.run([_traj("T-1")])
    best = harness.best_prompt(results)
    assert best == ""  # no successful extractions


def test_prompt_bakeoff_confidence_in_result() -> None:
    prompts = {"high": _prompt_high_conf}
    harness = PromptBakeoffHarness(prompts)
    results = harness.run([_traj("T-1")])
    assert results["high"][0].confidence == 0.95
