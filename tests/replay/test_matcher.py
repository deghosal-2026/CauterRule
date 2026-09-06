from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.models.trajectory import Step, Trajectory
from cauterule.replay.matcher import is_near_miss, rule_matches


def _cand(trigger: str, context: tuple[str, ...] = ()) -> CandidateRule:
    return CandidateRule(when=RuleWhen(trigger=trigger, context=context), do=RuleDo(directive="d"), confidence=0.9)


def _traj(task: str = "git push", error: str = "non-fast-forward", success: bool = False) -> Trajectory:
    return Trajectory(id="T-001", timestamp="t", task=task, steps=(Step(1, "bash", error=error),), success=success)


def test_matches_trigger() -> None:
    cand = _cand("git push")
    traj = _traj()
    assert rule_matches(cand, traj)


def test_no_match() -> None:
    cand = _cand("docker")
    assert not rule_matches(cand, _traj())


def test_empty_trigger() -> None:
    # Handled via rule_matches returning False, but CandidateRule validation
    # prevents empty trigger at construction. So we test via a non-matching trigger.
    cand = _cand("zzzzz_nonexistent")
    assert not rule_matches(cand, _traj())


def test_matches_context() -> None:
    cand = _cand("git push", context=("shared branch",))
    traj = _traj(task="git push on shared branch fails")
    assert rule_matches(cand, traj)
    traj2 = _traj(task="git push solo")
    assert not rule_matches(cand, traj2)


def test_case_insensitive() -> None:
    cand = _cand("Git Push")
    assert rule_matches(cand, _traj())


def test_near_miss() -> None:
    cand = _cand("git push", context=("shared branch", "multiple contributors"))
    traj = _traj(task="git push on shared branch")
    assert is_near_miss(cand, traj)
    assert not is_near_miss(_cand("git push"), _traj())
    assert not is_near_miss(_cand("docker"), _traj())
    # full context match is not near miss
    traj2 = _traj(task="git push on shared branch with multiple contributors")
    assert not is_near_miss(cand, traj2)
