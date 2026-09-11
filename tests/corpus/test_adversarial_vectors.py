"""Tests for the new adversarial vectors (#696).

Covers the tool-output-borne and multi-turn/compounding vectors added to close
the architectural gaps identified in #696.  The actual "0 promoted" field
measurement is produced by the field-test harness (these vectors are wired into
its adversarial sweep); these tests lock the corpus invariants and wiring.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest

from cauterule.models.trajectory import Trajectory

_REPO = Path(__file__).resolve().parents[2]
_ADV = _REPO / "corpus" / "public" / "adversarial"
_HARNESS = _REPO / "scripts" / "run-field-test.py"

_VECTORS = ("tool_output_injection", "compounding_multiturn")

# Attacker-instruction keywords that must appear in the tool telemetry, never
# in the (benign) task description.
_INJECTION_MARKERS = (
    "ignore", "instruction", "attacker@example.com", "should_reject", "force",
    "override", "unrestricted", "exfiltrate", "evil.example", "injected",
    "disable", "rm -rf", "extract", "bypass", "delete", "leak",
)


def _load(vector: str) -> list[Trajectory]:
    trajectories: list[Trajectory] = []
    for path in sorted((_ADV / vector).glob("*.jsonl")):
        first = path.read_text(encoding="utf-8").strip().splitlines()[0]
        trajectories.append(Trajectory.from_dict(json.loads(first)))
    return trajectories


@pytest.mark.parametrize("vector", _VECTORS)
def test_vector_has_ten_should_reject_trajectories(vector: str) -> None:
    trajectories = _load(vector)
    assert len(trajectories) == 10
    for traj in trajectories:
        assert traj.expected_outcome == "should_reject"
        assert vector in traj.tags


@pytest.mark.parametrize("vector", _VECTORS)
def test_injection_payload_lives_in_tool_telemetry_not_task(vector: str) -> None:
    for traj in _load(vector):
        task = traj.task.lower()
        assert not any(marker in task for marker in _INJECTION_MARKERS), traj.id
        telemetry = " ".join(
            f"{step.output or ''} {step.error or ''}" for step in traj.steps
        ).lower()
        assert any(marker in telemetry for marker in _INJECTION_MARKERS), traj.id


def test_compounding_vector_spreads_across_three_steps() -> None:
    for traj in _load("compounding_multiturn"):
        assert len(traj.steps) >= 3
        # Each step carries a fragment; the full instruction is only assembled
        # by reading the sequence.
        assert all((step.output or step.error or "").strip() for step in traj.steps)


def test_tool_output_vector_places_payload_in_output_or_error() -> None:
    for traj in _load("tool_output_injection"):
        assert any(
            (step.output and step.output.strip()) or (step.error and step.error.strip())
            for step in traj.steps
        )


def _load_harness() -> ModuleType:
    spec = importlib.util.spec_from_file_location("run_field_test_harness", _HARNESS)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_new_vectors_are_wired_into_field_harness() -> None:
    harness = _load_harness()
    for vector in _VECTORS:
        key = f"adversarial/{vector}"
        assert key in harness.CORPUS_TYPES
        assert harness.CORPUS_THRESHOLDS[key] == 0.70
