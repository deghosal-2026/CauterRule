"""Tests for the loop package."""
from __future__ import annotations

from cauterule.loop.errors import (
    handle_extraction_error,
    handle_git_error,
    handle_linter_block,
    handle_replay_error,
)
from cauterule.loop.orchestrator import LoopConfig, run_loop
from cauterule.models.trajectory import Step, Trajectory


def _trajectory() -> Trajectory:
    return Trajectory(
        id="T-001",
        timestamp="2026-09-03T18:35:00Z",
        task="git push fails on shared branch",
        steps=(Step(step_number=1, tool="bash", error="non-fast-forward rejected"),),
        success=False,
        failure_class="git/push",
    )


# ── orchestrator ─────────────────────────────────────────────────────


def test_run_loop_default() -> None:
    result = run_loop(_trajectory(), LoopConfig())
    assert result is None


def test_run_loop_with_config() -> None:
    config = LoopConfig(max_iterations=3, replay_enabled=False, promotion_mode="manual")
    result = run_loop(_trajectory(), config)
    assert result is None


def test_loop_config_defaults() -> None:
    config = LoopConfig()
    assert config.max_iterations == 5
    assert config.replay_enabled is True
    assert config.promotion_mode == "auto"
    assert config.extract_template is None
    assert config.extra == {}


# ── errors ───────────────────────────────────────────────────────────


def test_handle_extraction_error() -> None:
    msg = handle_extraction_error(ValueError("bad JSON"))
    assert "bad JSON" in msg
    assert "extraction" in msg.lower()


def test_handle_replay_error() -> None:
    msg = handle_replay_error(RuntimeError("cache miss"))
    assert "cache miss" in msg
    assert "replay" in msg.lower()


def test_handle_linter_block() -> None:
    msg = handle_linter_block(["vague trigger", "low confidence"])
    assert "vague trigger" in msg
    assert "low confidence" in msg
    assert "blocked" in msg.lower()


def test_handle_linter_block_empty() -> None:
    msg = handle_linter_block([])
    assert "0 warning" in msg


def test_handle_git_error() -> None:
    msg = handle_git_error(PermissionError("permission denied"))
    assert "permission denied" in msg
    assert "git" in msg.lower()
