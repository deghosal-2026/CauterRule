"""Conformance driver fixtures for each adapter (#540).

Each driver is a thin harness: a fake failing agent plus the trajectory /
redaction plumbing.  The kit (:mod:`kit`) is parametrized over these.
"""

# ruff: noqa: TRY300, TRY301 — test drivers intentionally raise in try to
# trigger the failure-capture path and return within try for the happy path.

# SECURITY-FIXTURE: token-like strings in this module are intentional fake
# credentials used to verify redaction. None are real secrets.

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

from cauterule.models.trajectory import Trajectory


@dataclass
class GenericDriver:
    """Driver for the generic ``@watch`` decorator."""

    name: str = "generic"
    base_dir: str = "trajectories"
    _last: Trajectory | None = None

    def trajectory_dir(self) -> Path:
        return Path(self.base_dir)

    def _reload_last(self) -> None:
        from cauterule.serialization.trajectory_jsonl import load_trajectories

        files = sorted(self.trajectory_dir().rglob("*.jsonl"))
        if not files:
            self._last = None
            return
        latest = list(load_trajectories(files[-1]))
        self._last = latest[-1] if latest else None

    def run_task(self, task: str, context: str = "") -> str:
        from cauterule.adapter.decorator import watch

        @watch(base_dir=self.base_dir)
        def _agent(task: str, api_key: str = "") -> str:
            if "connection timeout" in task or "sk-secret" in task or api_key:
                raise RuntimeError("agent failed")
            return "ok"

        redact_secret = "sk-secret-abcdef123456"
        # Pass the secret BOTH as a kwarg and (via context) as a positional
        # value so the adapter's own redaction path is exercised, not just the
        # builtin text patterns (code-review).
        kwarg_secret = redact_secret if "api_key=" in task else ""
        positional_secret = redact_secret if "positional" in task else ""
        try:
            _agent(task, kwarg_secret) if positional_secret else _agent(
                task=task, api_key=kwarg_secret
            )
            self._reload_last()
            return "ok"
        except RuntimeError:
            self._reload_last()
            return "failed"

    def last_trajectory(self) -> Trajectory | None:
        return self._last


@dataclass
class LangGraphDriver:
    name: str = "langgraph"
    base_dir: str = "trajectories"
    _last: Trajectory | None = None

    def trajectory_dir(self) -> Path:
        return Path(self.base_dir)

    def run_task(self, task: str, context: str = "") -> str:
        from cauterule.adapter.langgraph import capture_node_error

        if "connection timeout" in task:
            traj = capture_node_error(
                "node",
                {"task": task},
                {},
                RuntimeError("connection timeout"),
                base_dir=self.base_dir,
            )
            self._last = traj
            return "failed"
        return "ok"

    def last_trajectory(self) -> Trajectory | None:
        return self._last


@dataclass
class CrewAiDriver:
    name: str = "crewai"
    base_dir: str = "trajectories"
    _last: Trajectory | None = None

    def trajectory_dir(self) -> Path:
        return Path(self.base_dir)

    def run_task(self, task: str, context: str = "") -> str:
        from cauterule.adapter.crewai import CrewaiTracer

        tracer = CrewaiTracer(task_desc=task, base_dir=self.base_dir)
        try:
            with tracer.task(task):
                if "connection timeout" in task:
                    raise RuntimeError("connection timeout")
            self._last = tracer._last
        except RuntimeError:
            self._last = tracer._last
            return "failed"
        return "ok"

    def last_trajectory(self) -> Trajectory | None:
        return self._last


@dataclass
class PydanticAiDriver:
    name: str = "pydanticai"
    base_dir: str = "trajectories"
    _last: Trajectory | None = None

    def trajectory_dir(self) -> Path:
        return Path(self.base_dir)

    def run_task(self, task: str, context: str = "") -> str:
        import asyncio

        from cauterule.adapter.pydanticai import watch_run

        @watch_run(task=task, base_dir=self.base_dir)
        async def _agent(prompt: str = "") -> str:
            raise RuntimeError("connection timeout")

        try:
            asyncio.run(_agent())
            return "ok"
        except RuntimeError:
            files = sorted(self.trajectory_dir().rglob("*.jsonl"))
            from cauterule.serialization.trajectory_jsonl import load_trajectories

            latest = list(load_trajectories(files[-1])) if files else []
            self._last = latest[-1] if latest else None
            return "failed"

    def last_trajectory(self) -> Trajectory | None:
        return self._last


DRIVERS = {
    "generic": GenericDriver,
    "langgraph": LangGraphDriver,
    "crewai": CrewAiDriver,
    "pydanticai": PydanticAiDriver,
}


@pytest.fixture(params=list(DRIVERS), ids=list(DRIVERS))
def adapter_driver(request: pytest.FixtureRequest, tmp_path: Path) -> Iterator[Any]:
    """Parametrized fixture yielding each adapter's conformance driver."""
    cls = DRIVERS[request.param]
    driver = cls(base_dir=str(tmp_path / "trajectories"))
    yield driver
