from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.models.trajectory import Step, Trajectory
from cauterule.replay.cache import ReplayCache


def _cand(trigger: str) -> CandidateRule:
    return CandidateRule(when=RuleWhen(trigger=trigger), do=RuleDo(directive="d"), confidence=0.9)


def test_cache_hit() -> None:
    cand = _cand("git push")
    trajs = [Trajectory(id="T-1", timestamp="t", task="git push", steps=(Step(1, "bash", error="err"),), success=False)]
    cache = ReplayCache()
    r1 = cache.get(cand, trajs)
    r2 = cache.get(cand, trajs)
    assert r1 == r2
    assert len(cache) == 1


def test_cache_miss() -> None:
    cand1 = _cand("git push")
    cand2 = _cand("docker")
    trajs = [Trajectory(id="T-1", timestamp="t", task="git push", steps=(Step(1, "bash", error="err"),), success=False)]
    cache = ReplayCache()
    cache.get(cand1, trajs)
    cache.get(cand2, trajs)
    assert len(cache) == 2


def test_cache_clear() -> None:
    cand = _cand("git push")
    trajs = [Trajectory(id="T-1", timestamp="t", task="task", steps=(Step(1, "bash", error="err"),), success=False)]
    cache = ReplayCache()
    cache.get(cand, trajs)
    assert len(cache) == 1
    cache.clear()
    assert len(cache) == 0