"""Redaction corpus — 100% success validation."""

# SECURITY-FIXTURE: token-like strings below are intentional fake credentials
# used to verify redaction. None are real secrets.

from cauterule.models.trajectory import Step, Trajectory
from cauterule.redaction.engine import contains_secret, redact_trajectory

# Corpus of trajectories containing secrets — each must be fully redacted (no secret remains, redacted flag true).
CORPUS: list[Trajectory] = [
    Trajectory(
        id="T-aws-1",
        timestamp="2026-09-03T18:25:00Z",
        task="deploy",
        steps=(Step(step_number=1, tool="bash", input="AKIAIOSFODNN7EXAMPLE"),),
        success=False,
    ),
    Trajectory(
        id="T-ghp-1",
        timestamp="2026-09-03T18:25:00Z",
        task="git push",
        steps=(
            Step(step_number=1, tool="bash", output="ghp_123456789012345678901234567890123456"),
        ),
        success=False,
    ),
    Trajectory(
        id="T-jwt-1",
        timestamp="2026-09-03T18:25:00Z",
        task="api call",
        steps=(
            Step(
                step_number=1,
                tool="bash",
                error="eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.sig",
            ),
        ),
        success=False,
    ),
    Trajectory(
        id="T-openai-1",
        timestamp="2026-09-03T18:25:00Z",
        task="llm",
        steps=(Step(step_number=1, tool="bash", input="sk-12345678901234567890abc"),),
        success=False,
    ),
    Trajectory(
        id="T-password-1",
        timestamp="2026-09-03T18:25:00Z",
        task="password: s3cr3t",
        steps=(Step(step_number=1, tool="bash", error="password: hunter2"),),
        success=False,
    ),
    Trajectory(
        id="T-bearer-1",
        timestamp="2026-09-03T18:25:00Z",
        task="auth",
        steps=(Step(step_number=1, tool="bash", input="Bearer abc.def.ghi123"),),
        success=False,
    ),
    Trajectory(
        id="T-private-1",
        timestamp="2026-09-03T18:25:00Z",
        task="key",
        steps=(Step(step_number=1, tool="bash", output="-----BEGIN PRIVATE KEY-----"),),
        success=False,
    ),
    Trajectory(
        id="T-api-key-1",
        timestamp="2026-09-03T18:25:00Z",
        task="api_key: 12345678901234567890",
        steps=(Step(step_number=1, tool="bash", input="api_key: mykey12345678"),),
        success=False,
    ),
    Trajectory(
        id="T-secret-1",
        timestamp="2026-09-03T18:25:00Z",
        task="secret: mysecretvalue",
        steps=(
            Step(
                step_number=1, tool="bash", state={"secret": "mysecret", "data": "secret: hidden"}
            ),
        ),
        success=False,
    ),
    Trajectory(
        id="T-multi-1",
        timestamp="2026-09-03T18:25:00Z",
        task="AKIAIOSFODNN7EXAMPLE and ghp_123456789012345678901234567890123456",
        steps=(
            Step(
                step_number=1,
                tool="bash",
                input="password: foo",
                output="sk-12345678901234567890abc",
            ),
            Step(
                step_number=2,
                tool="bash",
                error="Bearer token123",
                state={"jwt": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZXN0In0.sig"},
            ),
        ),
        success=False,
    ),
]


def test_corpus_100_percent() -> None:
    failures: list[str] = []
    for traj in CORPUS:
        redacted = redact_trajectory(traj)
        # Must be flagged
        if not redacted.redacted:
            failures.append(f"{traj.id}: not flagged redacted")
            continue
        # No secret should remain in any field
        fields_to_check: list[str] = [redacted.task]
        if redacted.failure_class:
            fields_to_check.append(redacted.failure_class)
        for step in redacted.steps:
            if step.input:
                fields_to_check.append(step.input)
            if step.output:
                fields_to_check.append(step.output)
            if step.error:
                fields_to_check.append(step.error)
            if step.state:
                fields_to_check.append(str(step.state))
        for field in fields_to_check:
            if contains_secret(field):
                failures.append(f"{traj.id}: secret still present in {field[:50]}")
    assert not failures, f"Redaction failures: {failures}"
    # Also test extra pattern corpus: custom pattern should also be 100%
    custom = Trajectory(
        id="T-custom-1",
        timestamp="t",
        task="CUSTOM_SECRET_123",
        steps=(Step(step_number=1, tool="bash", input="CUSTOM_SECRET_999"),),
        success=False,
    )
    redacted_custom = redact_trajectory(custom, extra_patterns=["CUSTOM_SECRET_\\d+"])
    assert not contains_secret(redacted_custom.task, extra_patterns=["CUSTOM_SECRET_\\d+"])
    assert not contains_secret(
        redacted_custom.steps[0].input or "", extra_patterns=["CUSTOM_SECRET_\\d+"]
    )
    assert redacted_custom.redacted
