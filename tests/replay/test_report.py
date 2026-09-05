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
    trajs = [_traj("T-1", "git push fails", False, error="non-fast-forward"), _traj("T-2", "docker", False, error="err")]
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
