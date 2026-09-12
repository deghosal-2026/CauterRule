from pathlib import Path

import pytest

from cauterule.corpus.gold import GoldRuleFamily, load_gold_families


def test_gold_rule_family_valid() -> None:
    family = GoldRuleFamily(scenario_id="git-push-rejected")
    assert family.scenario_id == "git-push-rejected"
    assert family.trajectories == []
    assert family.acceptable_rules == []


def test_gold_rule_family_invalid_id() -> None:
    with pytest.raises(ValueError, match="scenario_id"):
        GoldRuleFamily(scenario_id="")
    with pytest.raises(ValueError, match="scenario_id"):
        GoldRuleFamily(scenario_id="   ")


def test_load_gold_families_missing_dir(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Path must be a directory"):
        load_gold_families(str(tmp_path / "nonexistent"))


def test_load_gold_families_empty_dir(tmp_path: Path) -> None:
    d = tmp_path / "gold_families"
    d.mkdir()
    families = load_gold_families(str(d))
    assert families == []


def test_load_gold_families_with_files(tmp_path: Path) -> None:
    import json

    from cauterule.models.trajectory import Step, Trajectory

    d = tmp_path / "families"
    d.mkdir()
    t1 = Trajectory(
        id="T-001",
        timestamp="t",
        task="Push to main",
        steps=(Step(step_number=1, tool="bash", input="git push"),),
        success=False,
    )
    t2 = Trajectory(
        id="T-002",
        timestamp="t",
        task="Deploy k8s",
        steps=(Step(step_number=1, tool="bash", input="kubectl apply"),),
        success=True,
    )
    fam1 = d / "git-push.jsonl"
    with fam1.open("w") as f:
        f.write(json.dumps(t1.to_dict()) + "\n")
    fam2 = d / "k8s-deploy.jsonl"
    with fam2.open("w") as f:
        f.write(json.dumps(t2.to_dict()) + "\n")

    families = load_gold_families(str(d))
    assert len(families) == 2
    ids = {f.scenario_id for f in families}
    assert ids == {"git-push", "k8s-deploy"}
    git_family = next(f for f in families if f.scenario_id == "git-push")
    assert len(git_family.trajectories) == 1
    assert git_family.trajectories[0].id == "T-001"
