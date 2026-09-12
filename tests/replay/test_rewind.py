from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.models.trajectory import Step, Trajectory
from cauterule.replay.rewind import rewind


def test_rewind_matched() -> None:
    cand = CandidateRule(when=RuleWhen(trigger="git push"), do=RuleDo(directive="pull --rebase"), confidence=0.9)
    traj = Trajectory(id="T-1", timestamp="t", task="git push fails", steps=(Step(1, "bash", error="non-fast-forward"),), success=False)
    result = rewind(traj, cand)
    assert result["matched"] is True
    assert result["original_success"] is False
    assert result["simulated_success"] is True
    assert len(result["step_by_step"]) == 1
    assert result["step_by_step"][0]["rule_would_apply"] is True


def test_rewind_no_match() -> None:
    cand = CandidateRule(when=RuleWhen(trigger="docker"), do=RuleDo(directive="d"), confidence=0.9)
    traj = Trajectory(id="T-1", timestamp="t", task="git push", steps=(Step(1, "bash", error="err"),), success=False)
    result = rewind(traj, cand)
    assert result["matched"] is False
    assert result["simulated_success"] is False
