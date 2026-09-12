"""Tests for the loop orchestrator (field/integration level).

These tests exercise the full loop pipeline end-to-end using the Python API
directly with a mock LLM provider.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest
import yaml

from cauterule.loop.orchestrator import LoopConfig, run_loop
from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.models.trajectory import Step, Trajectory
from cauterule.promotion.executor import execute_promotion


class MockLLM:
    """A realistic mock LLM that returns valid extraction JSON."""

    def __init__(self) -> None:
        self.calls = 0

    def complete(self, prompt: str, **kwargs: object) -> object:
        self.calls += 1
        from types import SimpleNamespace

        payload = json.dumps(
            {
                "when": {
                    "trigger": "git push fails",
                    "context": ["shared branch"],
                },
                "do": {
                    "directive": "pull --rebase first",
                    "because": "non-fast-forward rejected",
                },
                "confidence": 0.9,
                "reasoning": "prevents push rejection",
            }
        )
        return SimpleNamespace(text=payload, model="mock", provider="mock")


class EmptyLessonLLM:
    """A mock LLM that returns non-parseable output (no extractable lesson)."""

    def complete(self, prompt: str, **kwargs: object) -> object:
        from types import SimpleNamespace

        return SimpleNamespace(text="not json", model="mock", provider="mock")


def _simple_trajectory(
    tid: str = "T-001",
    task: str = "git push fails on shared branch",
    success: bool = False,
    failure_class: str = "git/push",
) -> Trajectory:
    return Trajectory(
        id=tid,
        timestamp="2026-09-03T18:35:00Z",
        task=task,
        steps=(Step(step_number=1, tool="bash", error="non-fast-forward rejected"),),
        success=success,
        failure_class=failure_class,
    )


def _init_git_repo(path: Path) -> None:
    """Initialise a temporary git repo with a dummy commit."""
    subprocess.run(["git", "init"], cwd=path, capture_output=True, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=test",
            "-c",
            "user.email=test@test.com",
            "commit",
            "--allow-empty",
            "-m",
            "initial",
        ],
        cwd=path,
        capture_output=True,
        check=True,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.docker
def test_loop_returns_rule_id() -> None:
    llm = MockLLM()
    traj = _simple_trajectory()
    config = LoopConfig(llm=llm)
    result = run_loop(traj, config)
    assert isinstance(result, str)
    assert result.startswith("R-T-001-")


@pytest.mark.docker
def test_loop_creates_rule_file(tmp_path: Path) -> None:
    _init_git_repo(tmp_path)
    llm = MockLLM()
    traj = _simple_trajectory()
    config = LoopConfig(llm=llm, historical_trajectories=())
    rule_id = run_loop(traj, config)
    assert rule_id is not None

    candidate = CandidateRule(
        when=RuleWhen(trigger="git push fails", context=("shared branch",)),
        do=RuleDo(directive="pull --rebase first", because="non-fast-forward rejected"),
        confidence=0.9,
        reasoning="prevents push rejection",
    )
    promoted_id = execute_promotion(
        candidate,
        {
            "rules_dir": str(tmp_path),
            "source_trajectory": "T-001",
            "extracted_by": "mock-llm",
            "extract_timestamp": "2026-09-03T18:35:00Z",
            "extraction_pass": 1,
            "promotion_mode": "auto",
        },
    )
    rule_path = tmp_path / f"{promoted_id}.yaml"
    assert rule_path.exists()
    loaded: dict[str, Any] = yaml.safe_load(rule_path.read_text(encoding="utf-8"))
    assert loaded["id"] == promoted_id


@pytest.mark.docker
def test_loop_creates_git_commit(tmp_path: Path) -> None:
    _init_git_repo(tmp_path)
    llm = MockLLM()
    traj = _simple_trajectory()
    config = LoopConfig(llm=llm, historical_trajectories=())
    rule_id = run_loop(traj, config)
    assert rule_id is not None

    candidate = CandidateRule(
        when=RuleWhen(trigger="git push fails", context=("shared branch",)),
        do=RuleDo(directive="pull --rebase first", because="non-fast-forward rejected"),
        confidence=0.9,
        reasoning="prevents push rejection",
    )
    execute_promotion(
        candidate,
        {
            "rules_dir": str(tmp_path),
            "source_trajectory": "T-001",
            "extracted_by": "mock-llm",
            "extract_timestamp": "2026-09-03T18:35:00Z",
            "extraction_pass": 1,
            "promotion_mode": "auto",
        },
    )
    result = subprocess.run(
        ["git", "log", "--oneline", "-5"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "promote:" in result.stdout


@pytest.mark.docker
def test_loop_all_stages_execute() -> None:
    llm = MockLLM()
    traj = _simple_trajectory()
    h1 = _simple_trajectory(tid="H-1", task="git push rejected", failure_class="git/push")
    h2 = _simple_trajectory(tid="H-2", task="docker build fails", failure_class="docker/build")
    config = LoopConfig(
        llm=llm,
        historical_trajectories=(h1, h2),
        existing_rules=(),
        replay_enabled=True,
    )
    result = run_loop(traj, config)
    assert isinstance(result, str)
    assert result.startswith("R-T-001-")


@pytest.mark.docker
def test_loop_empty_trajectory() -> None:
    llm = MockLLM()
    traj = Trajectory(
        id="T-EMPTY",
        timestamp="2026-09-03T18:35:00Z",
        task="no steps",
        steps=(),
        success=True,
    )
    config = LoopConfig(llm=llm)
    result = run_loop(traj, config)
    # M1 pre-extraction gate (#428): clean success trajectory with no failure
    # signal is dropped upstream → run_loop returns None (silence), no crash.
    assert result is None


@pytest.mark.docker
def test_loop_no_lesson() -> None:
    llm = EmptyLessonLLM()
    traj = _simple_trajectory()
    config = LoopConfig(llm=llm)
    result = run_loop(traj, config)
    assert result is None
