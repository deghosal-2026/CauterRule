"""Tests for the loop package."""
from __future__ import annotations

import json

from cauterule.loop.errors import (
    handle_extraction_error,
    handle_git_error,
    handle_linter_block,
    handle_replay_error,
)
from cauterule.loop.orchestrator import LoopConfig, run_loop
from cauterule.models.trajectory import Step, Trajectory


class FakeLLM:
    def __init__(self) -> None:
        self.calls = 0

    def complete(self, prompt: str, **kwargs: object) -> object:
        self.calls += 1
        payload = json.dumps({"when": {"trigger": "git push fails", "context": ["shared branch"]}, "do": {"directive": "pull --rebase first", "because": "non-fast-forward rejected"}, "confidence": 0.9, "reasoning": "prevents push rejection"})
        from types import SimpleNamespace
        return SimpleNamespace(text=payload, model="fake", provider="fake")


def _trajectory() -> Trajectory:
    return Trajectory(
        id="T-001",
        timestamp="2026-09-03T18:35:00Z",
        task="git push fails on shared branch",
        steps=(Step(step_number=1, tool="bash", error="non-fast-forward rejected"),),
        success=False,
        failure_class="git/push",
    )


def _traj_hist(id: str, task: str, success: bool) -> Trajectory:
    return Trajectory(
        id=id, timestamp="t", task=task,
        steps=(Step(1, "bash", error="err"),) if not success else (),
        success=success,
    )


# ── orchestrator ─────────────────────────────────────────────────────


def test_run_loop_promotes_rule() -> None:
    llm = FakeLLM()
    traj = _trajectory()
    historical = [
        _traj_hist("H-1", "git push rejected", False),
        _traj_hist("H-2", "docker build fails", False),
        _traj_hist("H-3", "git push ok", True),
    ]
    config = LoopConfig(llm=llm, historical_trajectories=tuple(historical))
    result = run_loop(traj, config)
    assert result is not None
    assert result.startswith("R-T-001-")


def test_run_loop_no_llm_returns_none() -> None:
    result = run_loop(_trajectory(), LoopConfig())
    assert result is None


def test_run_loop_no_candidates() -> None:
    class FailingLLM:
        def complete(self, prompt: str, **kwargs: object) -> object:
            from types import SimpleNamespace
            return SimpleNamespace(text="not json", model="fake", provider="fake")

    config = LoopConfig(llm=FailingLLM())
    result = run_loop(_trajectory(), config)
    assert result is None


def test_loop_config_defaults() -> None:
    config = LoopConfig()
    assert config.max_iterations == 5
    assert config.replay_enabled is True
    assert config.promotion_mode == "auto"
    assert config.extract_template is None
    assert config.llm is None
    assert config.historical_trajectories == ()
    assert config.existing_rules == ()
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