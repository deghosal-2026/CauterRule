from cauterule.extraction.tournament import run_tournament
from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.models.trajectory import Step, Trajectory


def _cand(trigger: str) -> CandidateRule:
    return CandidateRule(when=RuleWhen(trigger=trigger), do=RuleDo(directive="d"), confidence=0.9)


def _traj(id: str, task: str, success: bool) -> Trajectory:
    return Trajectory(id=id, timestamp="t", task=task, steps=(Step(1, "bash", error="err"),) if not success else (), success=success)


def test_tournament_basic() -> None:
    c1 = _cand("git push")
    c2 = _cand("docker")
    trajs = [_traj("T-1", "git push fails", False), _traj("T-2", "docker fails", False), _traj("T-3", "git push ok", True)]
    ranked = run_tournament([c1, c2], trajs)
    assert len(ranked) == 2
    # c1 should prevent T-1, c2 prevents T-2, both precision 1.0, tie broken by recall/confidence
    assert ranked[0].rank == 1


def test_tournament_empty() -> None:
    assert run_tournament([], []) == []


def test_tournament_no_trajectories() -> None:
    c = _cand("trigger")
    ranked = run_tournament([c], [])
    assert len(ranked) == 1
    assert ranked[0].evidence.precision == 0.0
