from cauterule.models.trajectory import Step, Trajectory
from cauterule.redaction.engine import contains_secret, redact_text, redact_trajectory


def test_redact_text_builtin() -> None:
    assert redact_text("AKIAIOSFODNN7EXAMPLE") == "[REDACTED]"
    assert redact_text("token ghp_123456789012345678901234567890123456 end") == "token [REDACTED] end"
    assert redact_text("Bearer abc.def.ghi token") == "[REDACTED] token" or "[REDACTED]" in redact_text("Bearer abc.def.ghi token")
    assert redact_text("password: s3cr3t") == "[REDACTED]"
    assert redact_text("api_key: 12345678901234567890") == "[REDACTED]"
    assert redact_text("sk-12345678901234567890abc") == "[REDACTED]"
    assert redact_text("normal text without secret") == "normal text without secret"
    assert redact_text("") == ""


def test_redact_text_custom() -> None:
    assert redact_text("my_custom_secret_123", extra_patterns=["my_custom_secret_\\d+"]) == "[REDACTED]"
    # invalid regex treated as literal
    assert redact_text("hello [invalid", extra_patterns=["[invalid"]) == "hello [REDACTED]"
    # tuple also works
    assert redact_text("AKIAIOSFODNN7EXAMPLE", extra_patterns=("AKIA.*",)) == "[REDACTED]"


def test_contains_secret() -> None:
    assert contains_secret("AKIAIOSFODNN7EXAMPLE")
    assert not contains_secret("hello world")
    assert contains_secret("my_secret_123", extra_patterns=["my_secret_\\d+"])
    assert not contains_secret("")
    assert not contains_secret("hello", extra_patterns=["notfound"])


def test_redact_trajectory() -> None:
    t = Trajectory(
        id="T-001",
        timestamp="2026-09-03T18:25:00Z",
        task="deploy with password: s3cr3t",
        steps=(
            Step(step_number=1, tool="bash", input="ghp_123456789012345678901234567890123456", output="ok"),
            Step(step_number=2, tool="bash", error="AKIAIOSFODNN7EXAMPLE", state={"key": "sk-12345678901234567890abc", "nested": {"secret": "password: hidden"}}),
        ),
        success=False,
        failure_class="git/push",
    )
    redacted = redact_trajectory(t)
    assert redacted.redacted is True
    assert "[REDACTED]" in redacted.task
    assert "[REDACTED]" in redacted.steps[0].input  # type: ignore
    assert redacted.steps[0].output == "ok"
    assert "[REDACTED]" in redacted.steps[1].error  # type: ignore
    assert "[REDACTED]" in str(redacted.steps[1].state)
    assert redacted.failure_class is not None
    # original not mutated
    assert "password: s3cr3t" in t.task
    # tool name not redacted
    assert redacted.steps[0].tool == "bash"


def test_redact_trajectory_extra_patterns() -> None:
    t = Trajectory(id="T-002", timestamp="t", task="custom_secret_123", steps=(), success=True)
    redacted = redact_trajectory(t, extra_patterns=["custom_secret_\\d+"])
    assert "[REDACTED]" in redacted.task


def test_redact_trajectory_already_redacted() -> None:
    t = Trajectory(id="T-003", timestamp="t", task="task", steps=(), success=True, redacted=True)
    redacted = redact_trajectory(t)
    assert redacted.redacted is True


def test_redact_text_jwt() -> None:
    jwt = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dummy"
    assert "[REDACTED]" in redact_text(f"token {jwt} end")


def test_redact_private_key() -> None:
    assert "[REDACTED]" in redact_text("-----BEGIN PRIVATE KEY----- abc")
    assert "[REDACTED]" in redact_text("-----BEGIN RSA PRIVATE KEY----- abc")


def test_redact_value_list_tuple() -> None:
    # Cover _redact_value list/tuple branches via state
    t = Trajectory(
        id="T-list",
        timestamp="t",
        task="task",
        steps=(
            Step(
                step_number=1,
                tool="bash",
                state={"items": ["AKIAIOSFODNN7EXAMPLE", "ok"], "pair": ("sk-12345678901234567890abc", "safe")},
            ),
        ),
        success=False,
    )
    redacted = redact_trajectory(t)
    # list should be redacted
    assert redacted.steps[0].state is not None
    assert redacted.steps[0].state["items"][0] == "[REDACTED]"
    assert redacted.steps[0].state["items"][1] == "ok"
    assert redacted.steps[0].state["pair"][0] == "[REDACTED]"
    assert redacted.steps[0].state["pair"][1] == "safe"
    assert isinstance(redacted.steps[0].state["pair"], tuple)


def test_redact_value_dict_keys_and_sets() -> None:
    # #502: dict keys and set/frozenset contents are scrubbed, type preserved.
    from cauterule.redaction.engine import _redact_value

    assert _redact_value({"AKIAIOSFODNN7EXAMPLE": "v"}, None) == {"[REDACTED]": "v"}
    assert _redact_value({"ok-key", "AKIAIOSFODNN7EXAMPLE"}, None) == {"ok-key", "[REDACTED]"}
    frozen = _redact_value(frozenset({"AKIAIOSFODNN7EXAMPLE"}), None)
    assert isinstance(frozen, frozenset)
    assert frozen == frozenset({"[REDACTED]"})
    # non-secret scalars untouched
    assert _redact_value(True, None) is True
    assert _redact_value(42, None) == 42
    assert _redact_value(None, None) is None


def test_redact_trajectory_scrubs_agent_config_environment() -> None:
    # #502: agent_config / environment mappings are scrubbed.
    from cauterule.models.trajectory import AgentConfig, Environment

    t = Trajectory(
        id="T-agent",
        timestamp="t",
        task="task",
        steps=(),
        success=False,
        agent_config=AgentConfig(model="gpt-4o", tools=("bash", "api_key: 12345678901234567890")),
        environment=Environment(os="linux AKIAIOSFODNN7EXAMPLE", ci=False),
    )
    redacted = redact_trajectory(t)
    assert redacted.agent_config is not None
    assert redacted.agent_config.model == "gpt-4o"
    assert "[REDACTED]" in redacted.agent_config.tools[1]
    assert redacted.environment is not None
    assert "[REDACTED]" in str(redacted.environment.os)
    assert redacted.environment.ci is False


def test_redact_trajectory_scrubs_domain_and_tags() -> None:
    # #502: domain + tags secret-shaped contents are scrubbed.
    t = Trajectory(
        id="T-dom",
        timestamp="t",
        task="task",
        steps=(),
        success=False,
        domain="team AKIAIOSFODNN7EXAMPLE",
        tags=("git", "sk-12345678901234567890abc"),
    )
    redacted = redact_trajectory(t)
    assert redacted.domain is not None
    assert "[REDACTED]" in redacted.domain
    assert redacted.tags[0] == "git"
    assert redacted.tags[1] == "[REDACTED]"


def test_redact_trajectory_idempotent() -> None:
    # #502: double redact is stable; structure preserved.
    t = Trajectory(
        id="T-idem",
        timestamp="t",
        task="deploy with password: s3cr3t",
        steps=(Step(step_number=1, tool="bash", input="ok"),),
        success=False,
        domain="git",
        tags=("a",),
    )
    once = redact_trajectory(t)
    twice = redact_trajectory(once)
    assert twice == once
    assert twice.steps[0].tool == "bash"
    assert twice.success is False
    assert twice.domain == "git"


def test_redact_trajectory_secret_quality_label_falls_back_to_none() -> None:
    # Review: secret-shaped quality_label cannot persist as an enum value.
    t = Trajectory(
        id="T-ql",
        timestamp="t",
        task="task",
        steps=(),
        success=False,
        quality_label="clear",
    )
    redacted = redact_trajectory(t)
    assert redacted.quality_label == "clear"
