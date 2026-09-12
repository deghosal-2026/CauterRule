from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.models.trajectory import Step, Trajectory
from cauterule.replay.parallel import run_parallel


def _cand(trigger: str) -> CandidateRule:
    return CandidateRule(when=RuleWhen(trigger=trigger), do=RuleDo(directive="d"), confidence=0.9)


def test_parallel_basic() -> None:
    c1 = _cand("git push")
    c2 = _cand("docker")
    trajs = [
        Trajectory(
            id="T-1",
            timestamp="t",
            task="git push",
            steps=(Step(1, "bash", error="err"),),
            success=False,
        )
    ]
    reports = run_parallel([c1, c2], trajs, max_workers=2)
    assert len(reports) == 2
    assert reports[0] is not None
    assert reports[1] is not None


def test_parallel_empty() -> None:
    assert run_parallel([], []) == []


def test_parallel_cache_reuse() -> None:
    from cauterule.replay.cache import ReplayCache

    c1 = _cand("git push")
    trajs = [
        Trajectory(
            id="T-1",
            timestamp="t",
            task="git push",
            steps=(Step(1, "bash", error="err"),),
            success=False,
        )
    ]
    cache = ReplayCache()
    reports = run_parallel([c1, c1], trajs, cache=cache)
    assert len(reports) == 2
    assert len(cache) == 1
