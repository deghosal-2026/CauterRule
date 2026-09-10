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


def _traj(task: str) -> Trajectory:
    return Trajectory(
        id="T-1",
        timestamp="t",
        task=task,
        steps=(Step(1, "bash", error="err"),),
        success=False,
    )


def test_cache_content_edit_misses() -> None:
    # #506: same id, edited content → fresh verdict, not stale.
    cand = _cand("git push")
    cache = ReplayCache()
    r1 = cache.get(cand, [_traj("git push")])
    r2 = cache.get(cand, [_traj("git push --force")])
    assert r1 is not r2
    assert len(cache) == 2


def test_cache_threshold_change_misses() -> None:
    # #506: same corpus, different threshold → different key.
    cand = _cand("git push")
    trajs = [_traj("git push")]
    cache = ReplayCache()
    cache.get(cand, trajs, threshold=0.6)
    cache.get(cand, trajs, threshold=0.35)
    assert len(cache) == 2


def test_cache_confidence_change_misses() -> None:
    # #506: same trigger text, different confidence → different key.
    from cauterule.models.rule import RuleDo, RuleWhen

    trajs = [_traj("git push")]
    cache = ReplayCache()
    lo = CandidateRule(when=RuleWhen(trigger="git push"), do=RuleDo(directive="d"), confidence=0.5)
    hi = CandidateRule(when=RuleWhen(trigger="git push"), do=RuleDo(directive="d"), confidence=0.9)
    cache.get(lo, trajs)
    cache.get(hi, trajs)
    assert len(cache) == 2


def test_cache_threshold_reaches_replay() -> None:
    # Review: the cached threshold must actually drive the replay verdict.
    from unittest.mock import patch

    from cauterule.models.evidence import EvidenceReport

    cand = _cand("git push")
    trajs = [_traj("git push")]
    cache = ReplayCache()
    seen: list[float | None] = []
    real = EvidenceReport(failures_prevented=(), precision=0.0, recall=0.0, verdict="fail")

    def fake_build(c: object, t: object, threshold: float | None = None) -> EvidenceReport:
        seen.append(threshold)
        return real

    with patch("cauterule.replay.determinism.build_evidence_report", side_effect=fake_build):
        cache.get(cand, trajs, threshold=0.35)
    assert seen == [0.35]


def test_parallel_threshold_passthrough() -> None:
    # Review: run_parallel forwards threshold to the cache.
    from unittest.mock import patch

    from cauterule.replay.parallel import run_parallel

    cand = _cand("git push")
    trajs = [_traj("git push")]
    with patch("cauterule.replay.cache.ReplayCache.get") as mock_get:
        run_parallel([cand], trajs, threshold=0.35)
    mock_get.assert_called_once_with(cand, trajs, 0.35)