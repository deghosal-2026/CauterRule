"""Test 24.6: Model bake-off harness records results."""

from __future__ import annotations

from cauterule.benchmark.bakeoff import BakeoffHarness
from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.models.trajectory import Step, Trajectory


def _traj(tid: str, success: bool = False) -> Trajectory:
    steps = (Step(1, "bash", error="err"),) if not success else (Step(1, "bash", output="ok"),)
    return Trajectory(id=tid, timestamp="t", task="task", steps=steps, success=success)


def _extractor_success(traj: Trajectory) -> CandidateRule | None:
    return CandidateRule(
        when=RuleWhen(trigger=f"{traj.task} fails"),
        do=RuleDo(directive="fix it"),
        confidence=0.9,
    )


def _extractor_fail(traj: Trajectory) -> CandidateRule | None:
    return None


def test_bakeoff_run_records_results() -> None:
    models = {"good": _extractor_success, "bad": _extractor_fail}
    harness = BakeoffHarness(models)
    trajs = [_traj("T-1"), _traj("T-2")]
    results = harness.run(trajs)
    assert "good" in results
    assert "bad" in results
    assert len(results["good"]) == 2
    assert len(results["bad"]) == 2
    assert results["good"][0].candidate is not None
    assert results["bad"][0].candidate is None


def test_bakeoff_summary_counts() -> None:
    models = {"good": _extractor_success, "bad": _extractor_fail}
    harness = BakeoffHarness(models)
    trajs = [_traj("T-1"), _traj("T-2"), _traj("T-3")]
    results = harness.run(trajs)
    summaries = harness.summarize(results)
    assert isinstance(summaries, dict)
    assert "good" in summaries
    assert "bad" in summaries
    assert summaries["good"].succeeded == 3
    assert summaries["bad"].succeeded == 0
    assert summaries["good"].total == 3
    assert summaries["bad"].total == 3


def test_bakeoff_summary_extraction_rate() -> None:
    models = {"good": _extractor_success, "bad": _extractor_fail}
    harness = BakeoffHarness(models)
    results = harness.run([_traj("T-1"), _traj("T-2")])
    summaries = harness.summarize(results)
    assert summaries["good"].extraction_rate == 1.0
    assert summaries["bad"].extraction_rate == 0.0


def test_bakeoff_summary_avg_confidence() -> None:
    models = {"good": _extractor_success}
    harness = BakeoffHarness(models)
    results = harness.run([_traj("T-1")])
    summaries = harness.summarize(results)
    assert summaries["good"].avg_confidence == 0.9
