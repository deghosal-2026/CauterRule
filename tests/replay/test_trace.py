from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.models.trajectory import Step, Trajectory
from cauterule.replay.trace import build_trace


def _cand(trigger: str) -> CandidateRule:
    return CandidateRule(when=RuleWhen(trigger=trigger), do=RuleDo(directive="d"), confidence=0.9)


def test_trace_prevented() -> None:
    cand = _cand("git push")
    traj = Trajectory(id="T-1", timestamp="t", task="git push fails", steps=(Step(1, "bash", error="err"),), success=False)
    t = build_trace(cand, traj)
    assert t["outcome"] == "prevented"
    assert t["trajectory_id"] == "T-1"


def test_trace_no_effect() -> None:
    cand = _cand("docker")
    traj = Trajectory(id="T-1", timestamp="t", task="git push", steps=(Step(1, "bash", error="err"),), success=False)
    t = build_trace(cand, traj)
    assert t["outcome"] == "no_effect"