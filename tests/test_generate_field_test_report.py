"""Tests for the field-test report generator (#686)."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest

_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "generate_field_test_report.py"


def _write_run(root: Path, corpus: str, model: str, verdicts: list[str]) -> None:
    d = root / corpus / model / "2026-09-13"
    d.mkdir(parents=True, exist_ok=True)
    (d / "results.jsonl").write_text(
        "\n".join(json.dumps({"status": "done", "best": {"verdict": v}}) for v in verdicts) + "\n",
        encoding="utf-8",
    )


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("generate_field_test_report", _SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _strip_timestamp(text: str) -> str:
    return "\n".join(line for line in text.splitlines() if not line.startswith("Generated:"))


def test_summarize_records_counts_statuses_and_verdicts() -> None:
    module = _load()
    records = [
        {"status": "done", "best": {"verdict": "pass"}},
        {"status": "done", "best": {"verdict": "fail"}},
        {"status": "done", "best": {"verdict": "inconclusive"}},
        {"status": "gate_dropped"},
        {"status": "no_candidates"},
    ]
    summary = module.summarize_records(records, corpus="golden", model="m", model_label="M")
    assert summary.total == 5
    assert summary.done == 3
    assert summary.gate_dropped == 1
    assert (summary.passed, summary.failed, summary.inconclusive) == (1, 1, 1)
    assert summary.pass_rate["rate"] == 0.5


def test_model_totals_sum_per_model() -> None:
    module = _load()
    runs = [
        module.summarize_records(
            [{"status": "done", "best": {"verdict": "pass"}}],
            corpus="golden",
            model="m1",
            model_label="M1",
        ),
        module.summarize_records(
            [{"status": "done"}, {"status": "done"}], corpus="otel", model="m1", model_label="M1"
        ),
        module.summarize_records(
            [{"status": "done"}], corpus="golden", model="m2", model_label="M2"
        ),
    ]
    assert module.model_totals(runs) == {"M1": 3, "M2": 1}


def test_render_markdown_includes_sentinel_and_tables() -> None:
    module = _load()
    runs = [
        module.summarize_records(
            [{"status": "done", "best": {"verdict": "pass"}}],
            corpus="golden",
            model="m1",
            model_label="M1",
        )
    ]
    rendered = module.render_markdown(runs)
    assert module._SENTINEL in rendered
    assert "## M1" in rendered
    assert "| golden | 1 | 1 | 0 | 0 |" in rendered


def test_committed_generated_results_doc_is_current() -> None:
    module = _load()
    assert module.DEFAULT_OUTPUT.exists(), (
        "run scripts/generate_field_test_report.py to create the committed report"
    )
    runs = module.load_runs()
    if not runs:
        pytest.skip("no raw field-test results present (sweep/re-run pending)")
    generated = module.render_markdown(runs)
    current = module.DEFAULT_OUTPUT.read_text(encoding="utf-8")
    assert _strip_timestamp(generated) == _strip_timestamp(current)


def test_default_paths_are_version_scoped() -> None:
    # #728: v0.3.1 tables land under results/0.3.1 and the v0.3.1 docs dir.
    module = _load()
    root, output = module.default_paths("0.3.1")
    assert root.parts[-2:] == ("results", "0.3.1")
    assert output.parts[-3:-1] == ("field-test", "v0.3.1")


def test_generate_and_drift_check_detects_change(tmp_path: Path) -> None:
    # #728: the committed report must be reproducible and drift must fail loud.
    root = tmp_path / "results"
    _write_run(root, "golden", "openai-openai_gpt-4o-mini", ["pass", "fail"])
    output = tmp_path / "generated-results.md"

    gen = subprocess.run(
        [sys.executable, str(_SCRIPT), "--results-root", str(root), "--output", str(output)],
        capture_output=True,
        text=True,
    )
    assert gen.returncode == 0, gen.stderr
    assert output.is_file()

    ok = subprocess.run(
        [
            sys.executable,
            str(_SCRIPT),
            "--results-root",
            str(root),
            "--output",
            str(output),
            "--check",
        ],
        capture_output=True,
        text=True,
    )
    assert ok.returncode == 0, ok.stdout + ok.stderr

    # Mutate the artifacts without regenerating -> drift must be detected.
    _write_run(root, "golden", "openai-openai_gpt-4o-mini", ["pass"])
    drift = subprocess.run(
        [
            sys.executable,
            str(_SCRIPT),
            "--results-root",
            str(root),
            "--output",
            str(output),
            "--check",
        ],
        capture_output=True,
        text=True,
    )
    assert drift.returncode == 1, drift.stdout + drift.stderr
