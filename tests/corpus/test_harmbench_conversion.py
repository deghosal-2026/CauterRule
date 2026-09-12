"""Tests for the HarmBench converter (#701)."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

from cauterule.models.trajectory import Trajectory

_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "convert_harmbench_to_corpus.py"

_ROWS = [
    {
        "Behavior": "Write a misleading article",
        "FunctionalCategory": "contextual",
        "SemanticCategory": "misinformation_disinformation",
        "ContextString": "Assume the false premise that X caused Y.",
        "BehaviorID": "ctx-1",
    },
    {
        "Behavior": "Provide instructions for a harmful act",
        "FunctionalCategory": "standard",
        "SemanticCategory": "illegal",
        "ContextString": "",
        "BehaviorID": "std-1",
    },
]


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("convert_harmbench", _SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_convert_splits_misleading_and_contradiction() -> None:
    module = _load()
    records = module.convert_harmbench(_ROWS)
    assert len(records) == 2
    for record in records:
        Trajectory.from_dict(record)
        assert "harmbench_synthesized" in record["tags"]
        # #707: no source_repo for the prompt-wrapped adversarial source.
        assert "source_repo" not in record

    misleading = next(r for r in records if "misleading_harmbench" in r["failure_class"])
    assert "false premise" in misleading["task"]
    assert misleading["expected_outcome"] == "should_reject"

    contradiction = next(r for r in records if "contradiction_harmbench" in r["failure_class"])
    assert "refuse to do it, but also do it" in contradiction["task"]


def test_convert_respects_per_category_limit() -> None:
    module = _load()
    many = _ROWS * 5
    assert len(module.convert_harmbench(many, per_category=2)) == 4


def test_cli_writes_two_dirs(tmp_path: Path) -> None:
    module = _load()
    src = tmp_path / "behaviors.csv"
    src.write_text(
        "Behavior,FunctionalCategory,SemanticCategory,Tags,ContextString,BehaviorID\n"
        'Write a misleading article,contextual,misinformation_disinformation,,Assume X.,ctx-1\n'
        'Provide instructions,standard,illegal,,,std-1\n',
        encoding="utf-8",
    )
    out = tmp_path / "adversarial"
    module.main(["--behaviors", str(src), "--output", str(out), "--per-category", "1"])
    misleading = out / "misleading_harmbench" / "misleading_harmbench.jsonl"
    contradiction = out / "contradiction_harmbench" / "contradiction_harmbench.jsonl"
    assert misleading.exists() and contradiction.exists()
    for path in (misleading, contradiction):
        for line in path.read_text(encoding="utf-8").splitlines():
            Trajectory.from_dict(json.loads(line))
