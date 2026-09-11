"""Tests for field-test harness gate-reason persistence (#697).

The harness is a standalone hyphenated script, so it is loaded by path here.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest

_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "run-field-test.py"


def _load_harness() -> ModuleType:
    spec = importlib.util.spec_from_file_location("run_field_test_harness", _SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def harness() -> ModuleType:
    return _load_harness()


def test_run_gate_persists_reason_for_gate_drop(harness: ModuleType) -> None:
    trajectory = {
        "trajectory_id": "T-gate",
        "timestamp": "t",
        "task": "healthy run",
        "steps": [{"step_number": 1, "tool": "bash", "output": "all good"}],
        "success": True,
        "redacted": False,
    }
    result = harness.run_gate(trajectory, "successes")
    assert result["is_silence"] is True
    assert result["reason"] == "no_failure_signal"


def test_summary_breaks_down_gate_dropped_by_reason(harness: ModuleType, tmp_path: Path) -> None:
    results = [
        {
            "trajectory_id": f"T-{i}",
            "status": "gate_dropped",
            "candidate_count": 0,
            "candidates": [],
            "gate": {"reason": reason, "is_silence": True},
            "task_specificity": "generic",
            "llm_calls_avoided": 1,
        }
        for i, reason in enumerate(
            [
                "no_failure_signal",
                "no_failure_signal",
                "nearmiss_recovery_succeeded",
                "failure_without_signal",
            ]
        )
    ]
    summary_file = tmp_path / "summary.json"
    harness._write_summary(
        results, summary_file, {"corpus_type": "golden"}, harness.time.time(), "golden"
    )
    summary = json.loads(summary_file.read_text(encoding="utf-8"))
    assert summary["gate_dropped"] == 4
    assert summary["gate_dropped_by_reason"] == {
        "no_failure_signal": 2,
        "nearmiss_recovery_succeeded": 1,
        "failure_without_signal": 1,
    }


def test_summary_includes_confidence_intervals(harness: ModuleType, tmp_path: Path) -> None:
    def done(verdict: str) -> dict[str, object]:
        return {
            "trajectory_id": f"T-{verdict}",
            "status": "done",
            "candidate_count": 1,
            "candidates": [],
            "best": {"verdict": verdict, "precision": 1.0, "recall": 1.0},
            "precision": 1.0,
            "recall": 1.0,
            "gate": {"reason": None, "is_silence": False},
            "task_specificity": "specific",
            "llm_calls_avoided": 0,
        }

    results: list[dict[str, object]] = [
        done("pass"),
        done("fail"),
        {
            "trajectory_id": "T-g",
            "status": "gate_dropped",
            "candidate_count": 0,
            "candidates": [],
            "gate": {"reason": "no_failure_signal", "is_silence": True},
            "task_specificity": "generic",
            "llm_calls_avoided": 1,
        },
    ]
    summary_file = tmp_path / "summary.json"
    harness._write_summary(
        results, summary_file, {"corpus_type": "golden"}, harness.time.time(), "golden"
    )
    summary = json.loads(summary_file.read_text(encoding="utf-8"))
    ci = summary["confidence_intervals"]
    assert ci["pass_rate"]["n"] == 2
    assert ci["pass_rate"]["rate"] == 0.5
    assert 0.0 <= ci["pass_rate"]["ci_low"] <= ci["pass_rate"]["ci_high"] <= 1.0
    assert ci["safety_silence_rate"]["n"] == 3
    assert ci["safety_silence_rate"]["rate"] == pytest.approx(1 / 3, abs=1e-3)
