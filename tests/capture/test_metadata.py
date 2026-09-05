from cauterule.capture.metadata import enrich_from_dict, enrich_trajectory
from cauterule.models.trajectory import AgentConfig, Environment, Step, Trajectory


def test_enrich_trajectory_domain() -> None:
    t = Trajectory(
        id="T-001",
        timestamp="2026-09-03T18:25:00Z",
        task="git push",
        steps=(Step(step_number=1, tool="bash", error="non-fast-forward"),),
        success=False,
        failure_class="git/push/non-fast-forward",
    )
    enriched = enrich_trajectory(t)
    assert enriched.domain == "git"
    assert enriched.severity == "medium"
    assert enriched.tags == ("git", "push", "non-fast-forward")
    assert enriched.quality_label == "clear"
    assert enriched.environment is not None
    assert enriched.agent_config is not None


def test_enrich_preserves_existing() -> None:
    t = Trajectory(
        id="T-002",
        timestamp="2026-09-03T18:25:00Z",
        task="task",
        steps=(),
        success=True,
        domain="python",
        severity="low",
        tags=("custom",),
        quality_label="ambiguous",
        environment=Environment(os="linux", ci=True),
        agent_config=AgentConfig(model="gpt-4o"),
    )
    enriched = enrich_trajectory(t)
    assert enriched.domain == "python"
    assert enriched.tags == ("custom",)
    assert enriched.quality_label == "ambiguous"


def test_enrich_overrides() -> None:
    t = Trajectory(id="T-003", timestamp="t", task="task", steps=(), success=False)
    enriched = enrich_trajectory(t, domain="docker", severity="high", tags=("docker",), quality_label="misleading")
    assert enriched.domain == "docker"
    assert enriched.severity == "high"
    assert enriched.tags == ("docker",)
    assert enriched.quality_label == "misleading"


def test_enrich_environment() -> None:
    t = Trajectory(id="T-004", timestamp="t", task="task", steps=(), success=True, environment=Environment(ci=True))
    enriched = enrich_trajectory(t)
    assert enriched.environment is not None
    assert enriched.environment.ci is True
    assert enriched.environment.os is not None

    t2 = Trajectory(id="T-005", timestamp="t", task="task", steps=(), success=True)
    enriched2 = enrich_trajectory(t2)
    assert enriched2.environment is not None
    assert enriched2.environment.os is not None


def test_enrich_success_no_quality() -> None:
    t = Trajectory(id="T-006", timestamp="t", task="task", steps=(), success=True)
    enriched = enrich_trajectory(t)
    assert enriched.quality_label is None
    assert enriched.severity == "low"


def test_enrich_from_dict() -> None:
    data = {
        "trajectory_id": "T-007",
        "timestamp": "2026-09-03T18:25:00Z",
        "task": "task",
        "steps": [{"step_number": 1, "tool": "bash", "error": "boom"}],
        "success": False,
        "failure_class": "git/push",
    }
    enriched = enrich_from_dict(data)
    assert enriched.id == "T-007"
    assert enriched.domain == "git"


def test_enrich_no_steps() -> None:
    t = Trajectory(id="T-008", timestamp="t", task="task", steps=(), success=False)
    enriched = enrich_trajectory(t)
    assert enriched.domain is None or isinstance(enriched.domain, str)
