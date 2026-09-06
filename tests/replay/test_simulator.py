from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.models.trajectory import Step, Trajectory
from cauterule.replay.simulator import simulate


def _cand(trigger: str, context: tuple[str, ...] = ()) -> CandidateRule:
    return CandidateRule(when=RuleWhen(trigger=trigger, context=context), do=RuleDo(directive="d"), confidence=0.9)


def _traj(task: str, success: bool, error: str = "") -> Trajectory:
    steps = (Step(1, "bash", error=error),) if error else ()
    return Trajectory(id="T-001", timestamp="t", task=task, steps=steps, success=success)


def test_prevented() -> None:
    cand = _cand("git push")
    traj = _traj("git push fails", success=False, error="non-fast-forward")
    assert simulate(cand, traj) == "prevented"


def test_no_effect() -> None:
    cand = _cand("docker")
    traj = _traj("git push", success=False, error="non-fast-forward")
    assert simulate(cand, traj) == "no_effect"


def test_broken() -> None:
    cand = _cand("git push")
    traj = _traj("git push succeeds", success=True)
    assert simulate(cand, traj) == "broken"


def test_near_miss() -> None:
    cand = _cand("git push", context=("shared branch", "multiple contributors"))
    traj = _traj("git push on shared branch", success=False, error="non-fast-forward")
    assert simulate(cand, traj) == "near_miss"
