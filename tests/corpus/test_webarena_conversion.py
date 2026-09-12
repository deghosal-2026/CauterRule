"""Tests for the WebArena browser-tool failure converter (#705)."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

from cauterule.models.trajectory import Trajectory

_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "convert_webarena_to_corpus.py"

_ISSUES = [
    {
        "number": 101,
        "title": "stale element on add-to-cart",
        "body": "Step failed: StaleElementReferenceException: stale element reference: element is not attached to the page document",
    },
    {
        "number": 102,
        "title": "unexpected alert blocks click",
        "body": "UnexpectedAlertOpenException: unexpected alert open: {Alert text : Are you sure?} browser alert not handled",
    },
    {
        "number": 103,
        "title": "frame switch fails",
        "body": "NoSuchFrameException: no such frame: unable to switch to frame checkout-iframe",
    },
    {
        "number": 104,
        "title": "element not found in checkout",
        "body": "NoSuchElementException: no such element: Unable to locate element: {\"method\":\"css selector\",\"selector\":\"#checkout-btn\"} element not found",
    },
    {
        "number": 105,
        "title": "page load timeout on search",
        "body": "TimeoutException: timeout: page load timeout waiting for https://shop.example.com/search timed out after 30s",
    },
    {
        "number": 106,
        "title": "switch to frame fails on payment",
        "body": "WebDriverException: switch to frame failed: frame not found payment-frame",
    },
]


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("convert_webarena", _SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_classify_and_extract() -> None:
    module = _load()
    assert module.classify("StaleElementReferenceException: stale element reference") == "browser/stale_element"
    assert module.classify("UnexpectedAlertOpenException: unexpected alert open") == "browser/unexpected_alert"
    assert module.classify("NoSuchFrameException: no such frame") == "browser/no_such_frame"
    assert module.classify("switch to frame failed") == "browser/no_such_frame"
    assert module.classify("NoSuchElementException: no such element") == "browser/element_not_found"
    assert module.classify("element not found: Unable to locate element") == "browser/element_not_found"
    assert module.classify("TimeoutException: page load timeout timed out") == "browser/timeout"
    assert module.classify("nothing relevant") == "browser/issue"
    error = module.extract_error("```\nStaleElementReferenceException: stale element\n```")
    assert "stale element" in error.lower()


def test_convert_produces_schema_valid_and_balanced_records() -> None:
    module = _load()
    records = module.convert_webarena_issues(_ISSUES)
    for record in records:
        Trajectory.from_dict(record)
    failures = [r for r in records if not r["success"]]
    successes = [r for r in records if r["success"]]
    assert len(failures) == 6
    assert successes
    assert failures[0]["source_repo"] == "web-arena-x/webarena"
    assert failures[0]["expected_outcome"] == "should_extract"
    assert failures[0]["failure_class"].startswith("browser/")
    assert failures[0]["steps"][0]["tool"] == "browser"
    assert failures[0]["steps"][0]["error"]
    # check expected mapping for known samples
    by_id = {r["trajectory_id"]: r for r in failures}
    assert by_id["browser-issue-101"]["failure_class"] == "browser/stale_element"
    assert by_id["browser-issue-103"]["failure_class"] == "browser/no_such_frame"


def test_convert_respects_limit() -> None:
    module = _load()
    assert len([r for r in module.convert_webarena_issues(_ISSUES * 5, limit=2) if not r["success"]]) == 2


def test_cli_writes_failure_and_success_files(tmp_path: Path) -> None:
    module = _load()
    src = tmp_path / "issues.json"
    src.write_text(json.dumps(_ISSUES), encoding="utf-8")
    out = tmp_path / "browser"
    succ = tmp_path / "successes"
    module.main(
        ["--issues", str(src), "--output", str(out), "--success-output", str(succ), "--limit", "2"]
    )
    failure_rows = [
        json.loads(line) for line in (out / "browser-issues.jsonl").read_text(encoding="utf-8").splitlines() if line
    ]
    success_rows = [
        json.loads(line)
        for line in (succ / "browser-successes.jsonl").read_text(encoding="utf-8").splitlines()
        if line
    ]
    assert len(failure_rows) == 2 and success_rows
    for record in failure_rows + success_rows:
        Trajectory.from_dict(record)
    # also verify CLI without --issues synthesizes
    out2 = tmp_path / "browser2"
    succ2 = tmp_path / "successes2"
    module.main(["--output", str(out2), "--success-output", str(succ2), "--limit", "5"])
    synth_rows = [
        json.loads(line) for line in (out2 / "browser-issues.jsonl").read_text(encoding="utf-8").splitlines() if line
    ]
    assert len(synth_rows) == 5


def test_browser_alias_coverage_via_converter() -> None:
    """Every browser alias family must have at least one classifiable exemplar."""
    module = _load()
    aliases = [
        "stale element reference: element is not attached",
        "StaleElementReferenceException",
        "unexpected alert open: browser alert not handled",
        "browser alert unexpected",
        "no such frame: switch to frame failed",
        "frame not found checkout-iframe",
        "switch to frame payment-frame",
        "NoSuchElementException: no such element",
        "element not found Unable to locate element",
        "TimeoutException page load timeout timed out",
    ]
    for text in aliases:
        fc = module.classify(text)
        assert fc.startswith("browser/"), f"alias text not classified: {text!r} -> {fc}"
        assert fc != "browser/issue", f"alias text fell to generic: {text!r}"
