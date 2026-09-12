"""Tests for trajectory redaction — API key, token, password, export, and @watch.

All tests use the Python API directly (not Docker CLI).
"""

# SECURITY-FIXTURE: token-like strings below are intentional fake credentials
# used to verify redaction. None are real secrets.

from __future__ import annotations

from pathlib import Path

import pytest

from cauterule.adapter.decorator import watch
from cauterule.export.generic import export_markdown
from cauterule.models.rule import Provenance, RuleDo, RuleWhen, StandingRule
from cauterule.models.trajectory import Step, Trajectory
from cauterule.redaction.engine import redact_trajectory


@pytest.mark.docker
def test_api_key_redacted() -> None:
    step = Step(step_number=1, tool="bash", input="api_key=sk-1234567890")
    traj = Trajectory(
        id="T-001",
        timestamp="2026-09-05T00:00:00Z",
        task="deploy",
        steps=(step,),
        success=True,
    )
    redacted = redact_trajectory(traj)
    assert redacted.steps[0].input is not None
    assert "sk-1234567890" not in redacted.steps[0].input


@pytest.mark.docker
def test_token_redacted() -> None:
    step = Step(
        step_number=1,
        tool="bash",
        input="token=ghp_abc123def4567890123456789012345678901234567890",
    )
    traj = Trajectory(
        id="T-002",
        timestamp="2026-09-05T00:00:00Z",
        task="deploy",
        steps=(step,),
        success=True,
    )
    redacted = redact_trajectory(traj)
    assert redacted.steps[0].input is not None
    assert "ghp_" not in redacted.steps[0].input


@pytest.mark.docker
def test_password_redacted() -> None:
    step = Step(step_number=1, tool="bash", input="password=supersecret")
    traj = Trajectory(
        id="T-003",
        timestamp="2026-09-05T00:00:00Z",
        task="deploy",
        steps=(step,),
        success=True,
    )
    redacted = redact_trajectory(traj)
    assert redacted.steps[0].input is not None
    assert "supersecret" not in redacted.steps[0].input


@pytest.mark.docker
def test_redacted_flag_set() -> None:
    step = Step(step_number=1, tool="bash", input="password=supersecret")
    traj = Trajectory(
        id="T-004",
        timestamp="2026-09-05T00:00:00Z",
        task="deploy",
        steps=(step,),
        success=True,
    )
    redacted = redact_trajectory(traj)
    assert redacted.redacted is True
    assert traj.redacted is False


@pytest.mark.docker
def test_export_no_secrets() -> None:
    rule = StandingRule(
        id="R-001",
        when=RuleWhen(trigger="api_key=sk-1234567890"),
        do=RuleDo(directive="Rotate the key"),
        confidence=0.85,
        provenance=Provenance(
            source_trajectory="t.jsonl",
            extracted_by="gpt-4o",
            extract_timestamp="2026-09-05T00:00:00Z",
            extraction_pass=1,
        ),
        status="active",
        promoted_at="2026-09-05T00:00:00Z",
    )
    output = export_markdown([rule])
    assert "sk-1234567890" not in output
    assert "apikey" not in output.lower() or "[REDACTED]" in output


@pytest.mark.docker
def test_watch_decorator_redacts(tmp_path: Path) -> None:
    @watch(base_dir=str(tmp_path))
    def my_agent(greeting: str, api_key: str = "sk-1234567890") -> str:
        return f"{greeting} done"

    result = my_agent("hello")
    assert result == "hello done"
    files = list(tmp_path.rglob("*.jsonl"))
    assert len(files) == 1
    content = files[0].read_text()
    assert "sk-1234567890" not in content
    assert "ghp_" not in content
