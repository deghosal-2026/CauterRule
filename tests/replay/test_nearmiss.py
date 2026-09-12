from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.models.trajectory import Step, Trajectory
from cauterule.replay.nearmiss import log_near_misses


def _cand(trigger: str, context: tuple[str, ...] = ()) -> CandidateRule:
    return CandidateRule(when=RuleWhen(trigger=trigger, context=context), do=RuleDo(directive="d"), confidence=0.9)


def test_near_miss_logged() -> None:
    cand = _cand("git push", context=("shared branch", "multiple contributors"))
    trajs = [
        Trajectory(id="T-1", timestamp="t", task="git push on shared branch", steps=(Step(1, "bash", error="err"),), success=False),
        Trajectory(id="T-2", timestamp="t", task="git push only", steps=(Step(1, "bash", error="err"),), success=False),
    ]
    results = log_near_misses(cand, trajs)
    assert len(results) == 1
    assert results[0]["trajectory_id"] == "T-1"


def test_near_miss_empty() -> None:
    cand = _cand("git push")
    assert log_near_misses(cand, []) == []


def test_near_miss_no_context() -> None:
    cand = _cand("git push")
    trajs = [Trajectory(id="T-1", timestamp="t", task="git push fails", steps=(Step(1, "bash", error="err"),), success=False)]
    assert log_near_misses(cand, trajs) == []
