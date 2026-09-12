from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.models.trajectory import Step, Trajectory
from cauterule.replay.determinism import deterministic_replay


def _cand(trigger: str) -> CandidateRule:
    return CandidateRule(when=RuleWhen(trigger=trigger), do=RuleDo(directive="d"), confidence=0.9)


def test_deterministic_same_result() -> None:
    cand = _cand("git push")
    trajs = [
        Trajectory(
            id="T-1",
            timestamp="t",
            task="git push fails",
            steps=(Step(1, "bash", error="err"),),
            success=False,
        ),
        Trajectory(
            id="T-2",
            timestamp="t",
            task="docker fails",
            steps=(Step(1, "bash", error="err"),),
            success=False,
        ),
    ]
    r1 = deterministic_replay(cand, trajs)
    r2 = deterministic_replay(cand, trajs)
    assert r1 == r2


def test_deterministic_ordering() -> None:
    cand = _cand("git push")
    trajs = [
        Trajectory(
            id="T-2",
            timestamp="t",
            task="git push",
            steps=(Step(1, "bash", error="err"),),
            success=False,
        ),
        Trajectory(
            id="T-1",
            timestamp="t",
            task="git push",
            steps=(Step(1, "bash", error="err"),),
            success=False,
        ),
    ]
    # Sorted by id internally, so should be deterministic
    r = deterministic_replay(cand, trajs)
    assert len(r.failures_prevented) == 2


def test_corpus_change_invalidates_cached_verdict() -> None:
    # #520: a content edit (same id) changes corpus_hash.
    cand = _cand("git push")
    trajs = [
        Trajectory(
            id="T-1",
            timestamp="t",
            task="git push",
            steps=(Step(1, "bash", error="err"),),
            success=False,
        ),
    ]
    edited = [
        Trajectory(
            id="T-1",
            timestamp="t",
            task="git push",
            steps=(Step(1, "bash", error="changed error text"),),
            success=False,
        ),
    ]
    r1 = deterministic_replay(cand, trajs)
    r2 = deterministic_replay(cand, edited)
    assert r1.corpus_hash is not None
    assert r1.corpus_hash != r2.corpus_hash


def test_same_corpus_same_hash() -> None:
    cand = _cand("git push")
    trajs = [
        Trajectory(
            id="T-1",
            timestamp="t",
            task="git push",
            steps=(Step(1, "bash", error="err"),),
            success=False,
        ),
        Trajectory(
            id="T-2",
            timestamp="t",
            task="docker",
            steps=(Step(1, "bash", error="err"),),
            success=False,
        ),
    ]
    r1 = deterministic_replay(cand, trajs)
    r2 = deterministic_replay(cand, trajs)
    assert r1.corpus_hash == r2.corpus_hash
    assert r1 == r2
