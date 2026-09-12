"""Smoke tests for the v0.3.0 measurement CLI scripts."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[2]
_SCRIPTS = _REPO / "scripts"


def _load(name: str) -> Any:
    path = _SCRIPTS / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"ft_{name}", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_results(root: Path, model: str, corpus: str, records: list[dict[str, object]]) -> None:
    d = root / corpus / model / "2026-09-11"
    d.mkdir(parents=True, exist_ok=True)
    with (d / "results.jsonl").open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec) + "\n")


def test_measure_cost_script(tmp_path: Path) -> None:
    mod = _load("measure_cost")
    _write_results(
        tmp_path / "results",
        "gpt-4o-mini",
        "cost",
        [
            {"status": "gate_dropped"},
            {"status": "done", "candidate_count": 2, "best": {"verdict": "pass"}},
        ],
    )
    out = tmp_path / "cost.md"
    rc = mod.main(
        ["--results", str(tmp_path / "results"), "--cost-per-request", "0.01", "--output", str(out)]
    )
    assert rc == 0
    text = out.read_text(encoding="utf-8")
    assert "gpt-4o-mini" in text
    assert "Cost Measurement" in text


def test_pack_replay_script(tmp_path: Path) -> None:
    mod = _load("pack_replay")
    out = tmp_path / "pack.md"
    rc = mod.main(["--packs-dir", str(_REPO / "rules" / "packs"), "--output", str(out)])
    assert rc == 0
    text = out.read_text(encoding="utf-8")
    assert "pack-docker" in text
    assert "Pack Replay Score" in text


def test_cross_session_script(tmp_path: Path) -> None:
    mod = _load("cross_session")
    baseline = tmp_path / "b.jsonl"
    intervention = tmp_path / "i.jsonl"
    baseline.write_text(
        "\n".join(
            json.dumps({"session": s, "failure_class": "git/non-ff", "success": False})
            for s in (1, 2, 3, 4, 4, 5)
        )
        + "\n",
        encoding="utf-8",
    )
    intervention.write_text(
        "\n".join(
            json.dumps({"session": s, "failure_class": "git/non-ff", "success": False})
            for s in (1, 2)
        )
        + "\n",
        encoding="utf-8",
    )
    out = tmp_path / "cs.md"
    rc = mod.main(["--baseline", str(baseline), "--intervention", str(intervention), "--output", str(out)])
    assert rc == 0
    assert "Cross-Session" in out.read_text(encoding="utf-8")


def test_human_agreement_sample_and_score(tmp_path: Path) -> None:
    mod = _load("human_agreement")
    _write_results(
        tmp_path / "results",
        "m",
        "golden",
        [
            {"trajectory_id": "a", "best": {"verdict": "pass"}},
            {"trajectory_id": "b", "best": {"verdict": "fail"}},
        ],
    )
    sample_out = tmp_path / "reviews.jsonl"
    rc = mod.main(
        ["--results", str(tmp_path / "results"), "--sample-output", str(sample_out), "--per-bucket", "1"]
    )
    assert rc == 0
    rows = [json.loads(line) for line in sample_out.read_text().splitlines()]
    assert len(rows) == 2

    # Fill in matching verdicts and score.
    for row in rows:
        row["human_verdict"] = row["replay_verdict"]
    filled = tmp_path / "filled.jsonl"
    with filled.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")
    out = tmp_path / "agreement.md"
    rc = mod.main(["--reviews", str(filled), "--output", str(out)])
    assert rc == 0
    assert "Agreement" in out.read_text(encoding="utf-8")


def test_fix8_recovery_script(tmp_path: Path) -> None:
    mod = _load("fix8_recovery")
    corpus = tmp_path / "nearmiss"
    corpus.mkdir()
    (corpus / "n.jsonl").write_text(
        json.dumps(
            {
                "trajectory_id": "n1",
                "timestamp": "2026-09-11T00:00:00Z",
                "task": "retry succeeded",
                "steps": [{"step_number": 1, "tool": "bash", "input": "x", "output": "ok", "error": ""}],
                "success": True,
                "failure_class": None,
                "domain": "git",
                "quality_label": "clear",
                "severity": None,
                "tags": ["nearmiss"],
                "expected_outcome": "should_reject",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    out = tmp_path / "fix8.md"
    rc = mod.main(["--corpora", str(corpus), "--output", str(out)])
    assert rc == 0
    assert "Recovery-Exclusion" in out.read_text(encoding="utf-8")
