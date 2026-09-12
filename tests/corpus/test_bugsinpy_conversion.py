"""Tests for the BugsInPy converter (#706)."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

from cauterule.models.trajectory import Trajectory

_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "convert_bugsinpy_to_corpus.py"

_BUGS = [
    {
        "project": "pandas",
        "bug_id": 99,
        "buggy_commit": "abc1234",
        "fix_commit": "def5678",
        "failing_test": "tests/test_groupby.py::TestGroupBy::test_aggregate",
        "pytest_output": "FAILED tests/test_groupby.py::TestGroupBy::test_aggregate - AssertionError: DataFrame shape mismatch",
    },
    {
        "project": "keras",
        "bug_id": 7,
        "buggy_commit": "aaa1111",
        "fix_commit": "bbb2222",
        "failing_test": "tests/test_layers.py::TestDense::test_call",
        "pytest_output": "FAILED tests/test_layers.py::TestDense::test_call - ValueError: Input 0 incompatible",
    },
    {
        "project": "youtube-dl",
        "bug_id": 3,
        "buggy_commit": "ccc3333",
        "fix_commit": "ddd4444",
        "failing_test": "tests/test_utils.py::TestUtils::test_parse_duration",
        "pytest_output": "FAILED tests/test_utils.py::TestUtils::test_parse_duration - ValueError: invalid duration",
    },
    {
        "project": "httpie",
        "bug_id": 1,
        "buggy_commit": "eee5555",
        "fix_commit": "fff6666",
        "failing_test": "tests/test_client.py::TestClient::test_get",
        "pytest_output": "FAILED tests/test_client.py::TestClient::test_get - ModuleNotFoundError: No module named 'httpie'",
    },
]


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("convert_bugsinpy", _SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_classify_and_extract() -> None:
    m = _load()
    assert m.classify("FAILED test - AssertionError: mismatch") == "python/test/assertion"
    assert m.classify("ModuleNotFoundError: No module named 'foo'") == "python/test/import_error"
    assert m.classify("ValueError: invalid") == "python/test/value_error"
    assert m.classify("AttributeError: 'Series' object has no attribute") == "python/test/attribute_error"
    assert m.classify("nothing relevant") == "python/test/failure"
    err = m.extract_error("FAILED tests/test_foo.py::test_bar - AssertionError: 1 != 2\nE       assert 1 == 2")
    assert "AssertionError" in err


def test_convert_produces_schema_valid_and_paired_records() -> None:
    m = _load()
    records = m.convert_bugsinpy(_BUGS)
    for r in records:
        Trajectory.from_dict(r)
    failures = [r for r in records if not r["success"]]
    successes = [r for r in records if r["success"]]
    assert len(failures) == 4
    assert len(successes) == 4
    # pairing: success id is failure id + "-fix"
    failure_ids = {r["trajectory_id"] for r in failures}
    for s in successes:
        base = s["trajectory_id"].removesuffix("-fix")
        assert base in failure_ids, f"orphan success {s['trajectory_id']}"
    # field contract per ticket
    f = next(r for r in failures if r["trajectory_id"] == "bugsinpy-pandas-99")
    assert f["task"] == "Run test suite after applying commit abc1234"
    assert f["steps"][0]["tool"] == "pytest"
    assert f["steps"][0]["input"] == "pytest tests/"
    assert f["steps"][0]["error"]
    assert f["failure_class"].startswith("python/test/")
    assert f["expected_outcome"] == "should_extract"
    assert f["source"] == "bugsinpy"
    assert f["source_repo"] == "soarsmu/BugsInPy"
    assert f["success"] is False
    # success counterpart
    s = next(r for r in successes if r["trajectory_id"] == "bugsinpy-pandas-99-fix")
    assert s["success"] is True
    assert s["failure_class"] is None
    assert s["expected_outcome"] == "should_silence"
    assert s["steps"][0]["output"] and "PASSED" in s["steps"][0]["output"]
    assert s["source_repo"] == "soarsmu/BugsInPy"


def test_convert_respects_limit() -> None:
    m = _load()
    records = m.convert_bugsinpy(_BUGS * 5, limit=2)
    assert len([r for r in records if not r["success"]]) == 2
    assert len([r for r in records if r["success"]]) == 2


def test_cli_writes_failure_and_success_files(tmp_path: Path) -> None:
    m = _load()
    src = tmp_path / "bugs.json"
    src.write_text(json.dumps(_BUGS), encoding="utf-8")
    out = tmp_path / "bugsinpy_out"
    succ = tmp_path / "successes"
    m.main(["--bugs", str(src), "--output", str(out), "--success-output", str(succ), "--limit", "2"])
    failure_rows = [json.loads(line) for line in (out / "bugsinpy.jsonl").read_text(encoding="utf-8").splitlines() if line]
    success_rows = [json.loads(line) for line in (succ / "bugsinpy-successes.jsonl").read_text(encoding="utf-8").splitlines() if line]
    assert len(failure_rows) == 2 and len(success_rows) == 2
    for r in failure_rows + success_rows:
        Trajectory.from_dict(r)
    # synth without --bugs
    out2 = tmp_path / "bugsinpy_out2"
    succ2 = tmp_path / "successes2"
    m.main(["--output", str(out2), "--success-output", str(succ2), "--limit", "3"])
    synth_rows = [json.loads(line) for line in (out2 / "bugsinpy.jsonl").read_text(encoding="utf-8").splitlines() if line]
    assert len(synth_rows) == 3
    assert all(r["trajectory_id"].startswith("bugsinpy-") for r in synth_rows)
    assert all(r["failure_class"].startswith("python/test/") for r in synth_rows)


def test_defects4j_skip_reason() -> None:
    m = _load()
    # Java domain not in matcher -> skip Defects4J
    assert m._is_java_supported() is False
