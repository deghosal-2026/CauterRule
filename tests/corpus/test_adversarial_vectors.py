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


_SYNTHETIC_PREFIX = {
    "tool_output_injection": "tool-output-injection-",
    "compounding_multiturn": "compounding-multiturn-",
}


def _load(vector: str, prefix: str | None = None) -> list[Trajectory]:
    trajectories: list[Trajectory] = []
    for path in sorted((_ADV / vector).glob("*.jsonl")):
        if prefix is not None and not path.name.startswith(prefix):
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                trajectories.append(Trajectory.from_dict(json.loads(line)))
    return trajectories


@pytest.mark.parametrize("vector", _VECTORS)
def test_vector_has_ten_should_reject_trajectories(vector: str) -> None:
    trajectories = _load(vector, _SYNTHETIC_PREFIX[vector])
    assert len(trajectories) == 10
    for traj in trajectories:
        assert traj.expected_outcome == "should_reject"
        assert vector in traj.tags


@pytest.mark.parametrize("vector", _VECTORS)
def test_injection_payload_lives_in_tool_telemetry_not_task(vector: str) -> None:
    for traj in _load(vector, _SYNTHETIC_PREFIX[vector]):
        task = traj.task.lower()
        assert not any(marker in task for marker in _INJECTION_MARKERS), traj.id
        telemetry = " ".join(
            f"{step.output or ''} {step.error or ''}" for step in traj.steps
        ).lower()
        assert any(marker in telemetry for marker in _INJECTION_MARKERS), traj.id


def test_compounding_vector_spreads_across_three_steps() -> None:
    for traj in _load("compounding_multiturn", _SYNTHETIC_PREFIX["compounding_multiturn"]):
        assert len(traj.steps) >= 3
        # Each step carries a fragment; the full instruction is only assembled
        # by reading the sequence.
        assert all((step.output or step.error or "").strip() for step in traj.steps)


def test_tool_output_vector_places_payload_in_output_or_error() -> None:
    for traj in _load("tool_output_injection", _SYNTHETIC_PREFIX["tool_output_injection"]):
        assert any(
            (step.output and step.output.strip()) or (step.error and step.error.strip())
            for step in traj.steps
        )


def test_injecagent_records_are_classified_and_payload_is_in_telemetry() -> None:
    # #700: real InjecAgent-derived vectors (converter output).
    trajectories = _load("tool_output_injection", "injecagent-tool-output")
    assert len(trajectories) >= 10
    for traj in trajectories:
        assert traj.failure_class == "adversarial/tool_output_injection"
        assert traj.expected_outcome == "should_reject"
        output = " ".join((step.output or "") for step in traj.steps)
        assert "<Attacker Instruction>" not in output
        assert output.strip()


def test_agentharm_records_are_classified() -> None:
    # #699: real AgentHarm-derived unsafe vectors (converter output).
    trajectories = _load("unsafe_realistic", "agentharm-unsafe")
    assert len(trajectories) >= 20
    for traj in trajectories:
        assert traj.failure_class is not None
        assert traj.failure_class.startswith("adversarial/unsafe/")
        assert traj.expected_outcome == "should_reject"


def _load_harness() -> ModuleType:
    spec = importlib.util.spec_from_file_location("run_field_test_harness", _HARNESS)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_new_vectors_are_wired_into_field_harness() -> None:
    harness = _load_harness()
    adversarial = (
        "adversarial/tool_output_injection",
        "adversarial/compounding_multiturn",
        "adversarial/unsafe_realistic",
    )
    for key in adversarial:
        assert key in harness.CORPUS_TYPES
        assert harness.CORPUS_THRESHOLDS[key] == 0.70
    assert "reference-expansion/paraphrase-diversity" in harness.CORPUS_TYPES
