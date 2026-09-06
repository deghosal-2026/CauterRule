import pytest

from cauterule.models.trajectory import AgentConfig, Environment, Step, Trajectory


def test_agent_config_roundtrip() -> None:
    ac = AgentConfig(model="gpt-4o", tools=("bash", "read"))
    assert ac.to_dict() == {"model": "gpt-4o", "tools": ["bash", "read"]}
    assert AgentConfig.from_dict(ac.to_dict()) == ac
    empty = AgentConfig()
    assert empty.to_dict() == {}


def test_environment_roundtrip() -> None:
    env = Environment(os="linux", ci=True)
    assert env.to_dict() == {"os": "linux", "ci": True}
    assert Environment.from_dict(env.to_dict()) == env
    empty = Environment()
    assert empty.to_dict() == {}


def test_step_valid() -> None:
    s = Step(step_number=1, tool="bash", input="git push", output="ok", error=None, state={"x": 1})
    assert s.to_dict()["tool"] == "bash"
    assert Step.from_dict(s.to_dict()) == s
    # minimal
    s2 = Step(step_number=2, tool="read")
    assert s2.input is None


def test_step_validation() -> None:
    with pytest.raises(ValueError, match="step_number"):
        Step(step_number=0, tool="bash")
    with pytest.raises(ValueError, match="step.tool"):
        Step(step_number=1, tool=" ")


def test_trajectory_valid() -> None:
    t = Trajectory(
        id="T-003",
        timestamp="2026-09-03T18:25:00Z",
        task="Deploy to staging",
        steps=(Step(step_number=1, tool="bash", input="git push"),),
        success=False,
        failure_point="step_1",
        failure_class="git/push/non-fast-forward",
        quality_label="clear",
        domain="git",
        severity="medium",
        tags=("git", "push"),
        agent_config=AgentConfig(model="gpt-4o", tools=("bash",)),
        environment=Environment(os="linux", ci=True),
        redacted=True,
    )
    d = t.to_dict()
    assert d["trajectory_id"] == "T-003"
    assert d["redacted"] is True
    assert Trajectory.from_dict(d) == t
    # from_dict accepts 'id' alias
    d2 = dict(d)
    d2["id"] = d2.pop("trajectory_id")
    # keep trajectory_id also? from_dict checks trajectory_id first, so need to remove it
    assert Trajectory.from_dict({"id": "T-999", "timestamp": "t", "task": "task", "steps": [], "success": True}).id == "T-999"


def test_trajectory_minimal() -> None:
    t = Trajectory(id="T-001", timestamp="2026-09-03T18:25:00Z", task="do thing", steps=(), success=True)
    d = t.to_dict()
    assert "failure_point" not in d
    assert Trajectory.from_dict(d) == t


def test_trajectory_validation() -> None:
    with pytest.raises(ValueError, match="trajectory.id"):
        Trajectory(id=" ", timestamp="t", task="task", steps=(), success=True)
    with pytest.raises(ValueError, match="trajectory.timestamp"):
        Trajectory(id="T-1", timestamp=" ", task="task", steps=(), success=True)
    with pytest.raises(ValueError, match="trajectory.task"):
        Trajectory(id="T-1", timestamp="t", task=" ", steps=(), success=True)
    with pytest.raises(ValueError, match="quality_label"):
        Trajectory(id="T-1", timestamp="t", task="task", steps=(), success=True, quality_label="bad")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="severity"):
        Trajectory(id="T-1", timestamp="t", task="task", steps=(), success=True, severity="bad")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="tags"):
        Trajectory(id="T-1", timestamp="t", task="task", steps=(), success=True, tags=(" ",))
