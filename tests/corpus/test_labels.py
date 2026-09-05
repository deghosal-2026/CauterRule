import pytest

from cauterule.corpus.labels import label_trajectory
from cauterule.models.trajectory import Step, Trajectory


def _make_trajectory() -> Trajectory:
    return Trajectory(
        id="T-001",
        timestamp="2026-09-03T18:25:00Z",
        task="Deploy to staging",
        steps=(Step(step_number=1, tool="bash", input="git push"),),
        success=False,
        failure_point="step_1",
        failure_class="git/push",
        quality_label="clear",
        domain="coding",
        severity="high",
        tags=("git",),
        redacted=False,
    )


def test_label_trajectory_changes_label() -> None:
    t = _make_trajectory()
    relabeled = label_trajectory(t, "ambiguous")
    assert relabeled.quality_label == "ambiguous"
    assert relabeled.id == t.id
    assert relabeled.task == t.task
    assert relabeled.timestamp == t.timestamp
    assert relabeled.success == t.success
    assert relabeled.domain == t.domain


def test_label_trajectory_does_not_mutate_original() -> None:
    t = _make_trajectory()
    original_label = t.quality_label
    label_trajectory(t, "multi-causal")
    assert t.quality_label == original_label


def test_label_trajectory_all_labels() -> None:
    t = _make_trajectory()
    for label in ("clear", "ambiguous", "multi-causal", "misleading", "operator-induced"):
        relabeled = label_trajectory(t, label)
        assert relabeled.quality_label == label


def test_label_trajectory_validation() -> None:
    t = _make_trajectory()
    with pytest.raises(ValueError, match="quality_label"):
        label_trajectory(t, "invalid")  # type: ignore[arg-type]


def test_label_trajectory_preserves_steps() -> None:
    t = _make_trajectory()
    relabeled = label_trajectory(t, "misleading")
    assert relabeled.steps == t.steps
    assert len(relabeled.steps) == 1


def test_label_trajectory_preserves_agent_config() -> None:
    from cauterule.models.trajectory import AgentConfig

    t = Trajectory(
        id="T-002",
        timestamp="t",
        task="task",
        steps=(),
        success=True,
        agent_config=AgentConfig(model="gpt-4o", tools=("bash",)),
    )
    relabeled = label_trajectory(t, "clear")
    assert relabeled.agent_config == t.agent_config
