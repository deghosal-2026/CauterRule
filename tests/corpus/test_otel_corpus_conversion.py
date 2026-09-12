"""Tests for the OpenTelemetry Demo issues converter (#702)."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

from cauterule.models.trajectory import Trajectory

_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "convert_otel_issues_to_corpus.py"

_ISSUES = [
    {
        "number": 1677,
        "title": "docker_stats errors",
        "body": "Symptom\n```\n2024-07-22 ERROR exporter export failed: dial tcp 127.0.0.1:4317: connect: connection refused\n```",
    },
    {
        "number": 3933,
        "title": "Add AI incident scenario",
        "body": "A feature request with no embedded error text at all.",
    },
]


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("convert_otel_issues", _SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_classify_and_extract() -> None:
    module = _load()
    assert module.classify("dial tcp: connection refused") == "otel/exporter/connection_refused"
    assert module.classify("nothing relevant") == "otel/issue"
    error = module.extract_error("```\nERROR: something failed\n```")
    assert "ERROR: something failed" in error


def test_convert_produces_schema_valid_and_balanced_records() -> None:
    module = _load()
    records = module.convert_otel_issues(_ISSUES)
    for record in records:
        Trajectory.from_dict(record)
    failures = [r for r in records if not r["success"]]
    successes = [r for r in records if r["success"]]
    assert len(failures) == 2
    assert successes
    assert failures[0]["source_repo"] == "open-telemetry/opentelemetry-demo"
    assert failures[0]["expected_outcome"] == "should_extract"
    assert "connection refused" in failures[0]["steps"][0]["error"]


def test_convert_respects_limit() -> None:
    module = _load()
    assert (
        len([r for r in module.convert_otel_issues(_ISSUES * 5, limit=2) if not r["success"]]) == 2
    )


def test_cli_writes_failure_and_success_files(tmp_path: Path) -> None:
    module = _load()
    src = tmp_path / "issues.json"
    src.write_text(json.dumps(_ISSUES), encoding="utf-8")
    out = tmp_path / "otel"
    succ = tmp_path / "successes"
    module.main(
        ["--issues", str(src), "--output", str(out), "--success-output", str(succ), "--limit", "2"]
    )
    failure_rows = [
        json.loads(line)
        for line in (out / "otel-issues.jsonl").read_text(encoding="utf-8").splitlines()
        if line
    ]
    success_rows = [
        json.loads(line)
        for line in (succ / "otel-successes.jsonl").read_text(encoding="utf-8").splitlines()
        if line
    ]
    assert len(failure_rows) == 2 and success_rows
    for record in failure_rows + success_rows:
        Trajectory.from_dict(record)
