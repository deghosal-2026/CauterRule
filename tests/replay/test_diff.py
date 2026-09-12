from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.models.trajectory import Step, Trajectory
from cauterule.replay.diff import diff


def test_diff_prevented() -> None:
    cand = CandidateRule(
        when=RuleWhen(trigger="git push"), do=RuleDo(directive="d"), confidence=0.9
    )
    traj = Trajectory(
        id="T-1",
        timestamp="t",
        task="git push fails",
        steps=(Step(1, "bash", error="err"),),
        success=False,
    )
    d = diff(cand, traj)
    assert d["before"] == "failure"
    assert d["after"] in ("prevented", "no_effect")
    assert d["changed"] is True


def test_diff_no_change() -> None:
    cand = CandidateRule(when=RuleWhen(trigger="docker"), do=RuleDo(directive="d"), confidence=0.9)
    traj = Trajectory(
        id="T-1",
        timestamp="t",
        task="git push",
        steps=(Step(1, "bash", error="err"),),
        success=False,
    )
    d = diff(cand, traj)
    assert d["changed"] is False
