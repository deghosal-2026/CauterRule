"""Tests for field-test harness gate-reason persistence (#697).

The harness is a standalone hyphenated script, so it is loaded by path here.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

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


def test_all_corpus_types_resolve_to_existing_dirs(harness: ModuleType) -> None:
    """Every CORPUS_TYPES entry must point at a real corpus directory."""
    missing = [name for name, path in harness.CORPUS_TYPES.items() if not path.is_dir()]
    assert not missing, f"corpus dirs missing: {missing}"


def test_promoted_reference_corpora_are_targets(harness: ModuleType) -> None:
    """#704/#705/#706 corpora are promoted from reference-only to target sweeps."""
    for name in ("public/browser", "public/real-world/bugsinpy", "public/lifecycle_infra"):
        assert name in harness.CORPUS_TYPES, name
        assert harness.CORPUS_TYPES[name].is_dir(), name
        assert name in harness.CORPUS_THRESHOLDS, name


def test_replay_test_candidate_domain_scopes_reference_pool(harness: ModuleType) -> None:
    """#708: the reference pool is scoped to the source trajectory's domain."""

    def traj(tid: str, domain: str, fc: str) -> dict[str, Any]:
        return {
            "trajectory_id": tid,
            "timestamp": "t",
            "task": "git push fails with non-fast-forward error",
            "steps": [
                {
                    "step_number": 1,
                    "tool": "bash",
                    "input": "git push",
                    "output": "",
                    "error": "non-fast-forward",
                }
            ],
            "success": False,
            "failure_class": fc,
            "domain": domain,
            "quality_label": "clear",
            "severity": "medium",
            "tags": [],
        }

    refs = [traj(f"g{i}", "git", "git/push") for i in range(5)]
    refs += [traj(f"p{i}", "python", "python/import") for i in range(20)]
    cand = {
        "when": "git push fails with non-fast-forward",
        "do": "pull before push",
        "confidence": 0.8,
    }

    full = harness.replay_test_candidate(cand, refs, "golden")
    assert full["domain_scoped"] is False
    assert full["reference_pool_size"] == 25

    scoped = harness.replay_test_candidate(cand, refs, "golden", source_domain="git")
    assert scoped["domain_scoped"] is True
    assert scoped["reference_pool_size"] == 5


def test_quarantine_ids_from_env(harness: ModuleType, monkeypatch: pytest.MonkeyPatch) -> None:
    """#713: CAUTERULE_QUARANTINE_IDS is parsed into a skip set."""
    monkeypatch.setenv("CAUTERULE_QUARANTINE_IDS", "ci-fail-016, ci-fail-017,, ci-fail-018")
    ids = harness.quarantined_ids()
    assert ids == frozenset({"ci-fail-016", "ci-fail-017", "ci-fail-018"})
    assert harness.is_quarantined("ci-fail-017", ids) is True
    assert harness.is_quarantined("ci-fail-001", ids) is False


def test_quarantine_empty_by_default(harness: ModuleType, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CAUTERULE_QUARANTINE_IDS", raising=False)
    assert harness.quarantined_ids() == frozenset()


# ---------------------------------------------------------------------------
# v0.3.1 (#734): summary carries extraction accuracy + verdict-reason breakdown
# ---------------------------------------------------------------------------
def _done_record(
    *,
    verdict: str = "pass",
    verdict_reason: str | None = None,
    trigger: str = "when git push fails with non-fast-forward",
    directive: str = "pull latest changes before pushing",
    expected_rule: str = "when git push fails with non-fast-forward, pull latest changes before pushing",
) -> dict[str, object]:
    return {
        "trajectory_id": "T-1",
        "status": "done",
        "candidate_count": 1,
        "candidates": [
            {
                "verdict": verdict,
                "verdict_reason": verdict_reason,
                "trigger_specificity": "specific",
                "precision": 1.0,
                "recall": 1.0,
                "match_detail": {"score": 1.0},
            }
        ],
        "best": {
            "verdict": verdict,
            "verdict_reason": verdict_reason,
            "precision": 1.0,
            "recall": 1.0,
            "candidate": {"when": trigger, "do": directive},
        },
        "trajectory": {"expected_rule": expected_rule},
        "precision": 1.0,
        "recall": 1.0,
        "gate": {"reason": None, "is_silence": False},
        "task_specificity": "specific",
        "llm_calls_avoided": 0,
    }


def test_summary_includes_extraction_accuracy(harness: ModuleType, tmp_path: Path) -> None:
    results: list[dict[str, object]] = [_done_record()]
    summary_file = tmp_path / "summary.json"
    harness._write_summary(
        results, summary_file, {"corpus_type": "golden"}, harness.time.time(), "golden"
    )
    summary = json.loads(summary_file.read_text(encoding="utf-8"))
    assert "extraction_f1" in summary
    assert "extraction_agreement" in summary
    assert summary["extraction"]["n"] == 1
    assert summary["extraction_agreement"] == 1.0
    assert 0.0 <= summary["extraction_f1"] <= 1.0


def test_summary_extraction_metrics_null_when_no_ground_truth(
    harness: ModuleType, tmp_path: Path
) -> None:
    """J10: a corpus with no `expected_rule` must report null, not a hard 0.0."""
    rec = _done_record()
    rec["trajectory"] = {}  # no expected_rule
    summary_file = tmp_path / "summary.json"
    harness._write_summary(
        [rec], summary_file, {"corpus_type": "raw/ci"}, harness.time.time(), "raw/ci"
    )
    summary = json.loads(summary_file.read_text(encoding="utf-8"))
    assert summary["extraction"]["n"] == 0
    assert summary["extraction_f1"] is None
    assert summary["extraction_agreement"] is None
    assert summary["extraction"]["semantic_f1"] is None
    assert summary["extraction"]["agreement"] is None


def test_summary_safety_uses_acceptance_rate_for_extraction_corpus(
    harness: ModuleType, tmp_path: Path
) -> None:
    """J13: an extraction corpus must not be labelled with a safety false-accept rate."""
    summary_file = tmp_path / "summary.json"
    harness._write_summary(
        [_done_record()], summary_file, {"corpus_type": "raw/ci"}, harness.time.time(), "raw/ci"
    )
    summary = json.loads(summary_file.read_text(encoding="utf-8"))
    assert "false_accept_rate" not in summary["safety"]
    assert summary["safety"]["acceptance_rate"] == 1.0


def test_summary_includes_verdict_reason_breakdown(harness: ModuleType, tmp_path: Path) -> None:
    results: list[dict[str, object]] = [
        _done_record(verdict="inconclusive", verdict_reason="blocked_by_broken"),
        _done_record(verdict="fail", verdict_reason="blocked_by_precision"),
    ]
    summary_file = tmp_path / "summary.json"
    harness._write_summary(
        results, summary_file, {"corpus_type": "golden"}, harness.time.time(), "golden"
    )
    summary = json.loads(summary_file.read_text(encoding="utf-8"))
    assert summary["verdict_reason_breakdown"] == {
        "blocked_by_broken": 1,
        "blocked_by_precision": 1,
    }


def test_replay_candidate_reports_verdict_reason(harness: ModuleType) -> None:
    ref = {
        "trajectory_id": "R-1",
        "timestamp": "t",
        "task": "git push fails with non-fast-forward error",
        "steps": [
            {
                "step_number": 1,
                "tool": "bash",
                "input": "git push",
                "error": "non-fast-forward",
            }
        ],
        "success": False,
        "failure_class": "git/push",
        "domain": "git",
        "quality_label": "clear",
        "severity": "medium",
        "tags": [],
    }
    cand = {
        "when": "git push fails with non-fast-forward",
        "do": "pull before push",
        "confidence": 0.8,
    }
    out = harness.replay_test_candidate(cand, [ref], "golden")
    assert "verdict_reason" in out


def test_v031_validation_suites_are_wired(harness: ModuleType) -> None:
    for name in (
        "v031_extraction_accuracy",
        "v031_corpus_coverage",
        "v031_report_reproducibility",
        "v031_harness_metrics",
    ):
        assert name in harness.VALIDATION_SUITES, name
        assert harness.VALIDATION_SUITES[name]["targets"], name
