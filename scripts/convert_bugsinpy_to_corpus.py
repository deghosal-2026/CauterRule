#!/usr/bin/env python3
"""Convert BugsInPy bugs to CauterRule corpus (#706).

``soarsmu/BugsInPy`` (MIT) contains 493 real bugs from 17 Python projects.
Each bug ships with a failing test, buggy commit, and fix commit.  This
converter maps each bug to a CauterRule reference trajectory:

  trajectory_id     ``bugsinpy-<project>-<bug_id>``
  task              ``Run test suite after applying commit <buggy_commit>``
  steps[0].tool     ``pytest``
  steps[0].input    ``pytest tests/``
  steps[0].error    real captured pytest failure output
  success           false
  failure_class     ``python/test/<derived>``
  expected_outcome  should_extract
  source            bugsinpy
  source_repo       soarsmu/BugsInPy

A post-fix passing test run is emitted as a success counterpart for the
same bug (#707 balance).  Successful trajectories live under
``corpus/public/successes/bugsinpy-successes.jsonl``.

Defects4J (Java) is out of scope: ``src/cauterule/replay/matcher.py`` has
no ``java`` domain (``_KNOWN_DOMAINS`` / ``_DOMAIN_GROUPS``) so a Java
corpus cannot be matched.  See module docstring for the skip rationale.

Usage:
    # synthetic (no clone required, uses built-in fixtures):
    python scripts/convert_bugsinpy_to_corpus.py \\
        --output corpus/public/real-world/bugsinpy \\
        --success-output corpus/public/successes \\
        --limit 36

    # from a BugsInPy metadata JSON (array of {project, bug_id, ...}):
    python scripts/convert_bugsinpy_to_corpus.py \\
        --bugs /tmp/bugsinpy.json \\
        --output corpus/public/real-world/bugsinpy \\
        --success-output corpus/public/successes \\
        --limit 40

Fetch metadata sample with gh (optional):
    gh api repos/soarsmu/BugsInPy/contents --jq '.[].name' | head
    # Full clone is heavy (~493 bugs); synthesizing is preferred.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

_TS = "2026-09-11T00:00:00+00:00"
_SOURCE_REPO = "soarsmu/BugsInPy"
_LICENSE = "MIT"  # soarsmu/BugsInPy is MIT-licensed (checked via gh api repos/soarsmu/BugsInPy).

# Order most-specific -> generic.  Every python/test/* maps into the
# ``python`` group in matcher.py (_DOMAIN_GROUPS: pip/pytest/python -> python).
_CLASSIFIERS: tuple[tuple[str, str], ...] = (
    ("ModuleNotFoundError", "python/test/import_error"),
    ("ImportError", "python/test/import_error"),
    ("no module named", "python/test/import_error"),
    ("AssertionError", "python/test/assertion"),
    ("assert", "python/test/assertion"),
    ("FAILED", "python/test/assertion"),
    ("TypeError", "python/test/type_error"),
    ("ValueError", "python/test/value_error"),
    ("KeyError", "python/test/key_error"),
    ("IndexError", "python/test/index_error"),
    ("AttributeError", "python/test/attribute_error"),
    ("FileNotFoundError", "python/test/file_not_found"),
    ("SyntaxError", "python/test/syntax_error"),
    ("TimeoutError", "python/test/timeout"),
    ("ConnectionError", "python/test/connection_error"),
)


def classify(pytest_output: str) -> str:
    """Derive a ``python/test/*`` failure_class from pytest output."""
    lowered = pytest_output.lower()
    for needle, failure_class in _CLASSIFIERS:
        if needle.lower() in lowered:
            return failure_class
    return "python/test/failure"


def extract_error(pytest_output: str) -> str:
    """Return the most error-like slice of pytest output (capped at 1000 chars)."""
    # Prefer FAILED line + Assertion block, else first error-like line.
    for line in pytest_output.splitlines():
        if "FAILED" in line or "AssertionError" in line or "Error" in line:
            # Return a window around that line.
            idx = pytest_output.index(line)
            return pytest_output[max(0, idx - 200) : idx + 800].strip()[:1000]
    return pytest_output.strip()[:1000] or "pytest failure"


# ---------------------------------------------------------------------------
# Synthetic fixtures — 40 realistic bugs across popular projects.
# Each entry mirrors the BugsInPy metadata shape: project, bug_id,
# buggy_commit, fix_commit, failing_test, pytest failure snippet.
# ---------------------------------------------------------------------------
_SYNTHETIC_BUGS: list[dict[str, Any]] = [
    # pandas (6)
    {
        "project": "pandas",
        "bug_id": 1,
        "buggy_commit": "a1b2c3d",
        "fix_commit": "e4f5g6h",
        "failing_test": "tests/test_groupby.py::TestGroupBy::test_aggregate",
        "pytest_output": "FAILED tests/test_groupby.py::TestGroupBy::test_aggregate - AssertionError: DataFrame shape mismatch: (10, 3) != (10, 2)\nE       assert 0 == 1\nE        +  where 0 = len(result.columns)",
    },
    {
        "project": "pandas",
        "bug_id": 2,
        "buggy_commit": "b2c3d4e",
        "fix_commit": "f5g6h7i",
        "failing_test": "tests/test_frame.py::TestDataFrame::test_merge",
        "pytest_output": "FAILED tests/test_frame.py::TestDataFrame::test_merge - ValueError: cannot merge DataFrame with duplicate columns\nE       ValueError: cannot reindex from a duplicate axis",
    },
    {
        "project": "pandas",
        "bug_id": 3,
        "buggy_commit": "c3d4e5f",
        "fix_commit": "g6h7i8j",
        "failing_test": "tests/test_indexing.py::TestIndexing::test_loc",
        "pytest_output": "FAILED tests/test_indexing.py::TestIndexing::test_loc - KeyError: 'missing_idx'\nE       KeyError: 'missing_idx'",
    },
    {
        "project": "pandas",
        "bug_id": 4,
        "buggy_commit": "d4e5f6a",
        "fix_commit": "h7i8j9k",
        "failing_test": "tests/test_nanops.py::TestNanOps::test_mean",
        "pytest_output": "FAILED tests/test_nanops.py::TestNanOps::test_mean - TypeError: unsupported operand type(s) for +: 'NoneType' and 'float'",
    },
    {
        "project": "pandas",
        "bug_id": 5,
        "buggy_commit": "e5f6a7b",
        "fix_commit": "i8j9k0l",
        "failing_test": "tests/test_reshape.py::TestReshape::test_pivot",
        "pytest_output": "FAILED tests/test_reshape.py::TestReshape::test_pivot - AssertionError: assert 5 == 4\nE        +  where 5 = pivot.shape[0]",
    },
    {
        "project": "pandas",
        "bug_id": 6,
        "buggy_commit": "f6a7b8c",
        "fix_commit": "j9k0l1m",
        "failing_test": "tests/test_strings.py::TestStrings::test_split",
        "pytest_output": "FAILED tests/test_strings.py::TestStrings::test_split - AttributeError: 'Series' object has no attribute 'str_split'",
    },
    # keras (5)
    {
        "project": "keras",
        "bug_id": 1,
        "buggy_commit": "111aaab",
        "fix_commit": "222bbbc",
        "failing_test": "tests/test_layers.py::TestDense::test_call",
        "pytest_output": "FAILED tests/test_layers.py::TestDense::test_call - ValueError: Input 0 of layer dense is incompatible with the layer: expected axis -1 of input shape to have value 10 but received shape (None, 5)",
    },
    {
        "project": "keras",
        "bug_id": 2,
        "buggy_commit": "112aabb",
        "fix_commit": "223bbcc",
        "failing_test": "tests/test_optimizers.py::TestAdam::test_update",
        "pytest_output": "FAILED tests/test_optimizers.py::TestAdam::test_update - AssertionError: assert 0.001 == 0.0009 ± 1.0e-06\nE       assert 0.001 == 0.0009",
    },
    {
        "project": "keras",
        "bug_id": 3,
        "buggy_commit": "113abbb",
        "fix_commit": "224bccc",
        "failing_test": "tests/test_models.py::TestSequential::test_compile",
        "pytest_output": "FAILED tests/test_models.py::TestSequential::test_compile - TypeError: compile() missing 1 required positional argument: 'optimizer'",
    },
    {
        "project": "keras",
        "bug_id": 4,
        "buggy_commit": "114abcc",
        "fix_commit": "225ccdd",
        "failing_test": "tests/test_losses.py::TestLosses::test_categorical_crossentropy",
        "pytest_output": "FAILED tests/test_losses.py::TestLosses::test_categorical_crossentropy - AssertionError: loss mismatch: 0.693 != 0.5",
    },
    {
        "project": "keras",
        "bug_id": 5,
        "buggy_commit": "115accc",
        "fix_commit": "226cddd",
        "failing_test": "tests/test_callbacks.py::TestEarlyStopping::test_patience",
        "pytest_output": "FAILED tests/test_callbacks.py::TestEarlyStopping::test_patience - IndexError: list index out of range\nE       IndexError: list index out of range at callback index 3",
    },
    # youtube-dl (5)
    {
        "project": "youtube-dl",
        "bug_id": 1,
        "buggy_commit": "aaa1001",
        "fix_commit": "bbb2002",
        "failing_test": "tests/test_download.py::TestDownload::test_youtube",
        "pytest_output": "FAILED tests/test_download.py::TestDownload::test_youtube - AssertionError: 'https://www.youtube.com/watch?v=BaW_jenozKc' != 'https://youtube.com/watch?v=BaW_jenozKc'\nE       AssertionError: URL normalization failed",
    },
    {
        "project": "youtube-dl",
        "bug_id": 2,
        "buggy_commit": "aaa1002",
        "fix_commit": "bbb2003",
        "failing_test": "tests/test_extractors.py::TestExtractors::test_soundcloud",
        "pytest_output": "FAILED tests/test_extractors.py::TestExtractors::test_soundcloud - KeyError: 'title'\nE       KeyError: 'title' at extractor soundcloud:42",
    },
    {
        "project": "youtube-dl",
        "bug_id": 3,
        "buggy_commit": "aaa1003",
        "fix_commit": "bbb2004",
        "failing_test": "tests/test_utils.py::TestUtils::test_parse_duration",
        "pytest_output": "FAILED tests/test_utils.py::TestUtils::test_parse_duration - ValueError: invalid duration string: '1::05'",
    },
    {
        "project": "youtube-dl",
        "bug_id": 4,
        "buggy_commit": "aaa1004",
        "fix_commit": "bbb2005",
        "failing_test": "tests/test_networking.py::TestNetworking::test_head_request",
        "pytest_output": "FAILED tests/test_networking.py::TestNetworking::test_head_request - ConnectionError: HTTPSConnectionPool(host='www.youtube.com', port=443): Max retries exceeded",
    },
    {
        "project": "youtube-dl",
        "bug_id": 5,
        "buggy_commit": "aaa1005",
        "fix_commit": "bbb2006",
        "failing_test": "tests/test_aes.py::TestAES::test_decrypt",
        "pytest_output": "FAILED tests/test_aes.py::TestAES::test_decrypt - AssertionError: decrypted bytes mismatch\nE       assert b'hello' == b'hell0'",
    },
    # scrapy (4)
    {
        "project": "scrapy",
        "bug_id": 1,
        "buggy_commit": "ccc1001",
        "fix_commit": "ddd2001",
        "failing_test": "tests/test_spider.py::TestSpider::test_parse",
        "pytest_output": "FAILED tests/test_spider.py::TestSpider::test_parse - AttributeError: 'NoneType' object has no attribute 'css'\nE       AttributeError: 'NoneType' object has no attribute 'css'",
    },
    {
        "project": "scrapy",
        "bug_id": 2,
        "buggy_commit": "ccc1002",
        "fix_commit": "ddd2002",
        "failing_test": "tests/test_middleware.py::TestMiddleware::test_retry",
        "pytest_output": "FAILED tests/test_middleware.py::TestMiddleware::test_retry - AssertionError: expected retry count 3, got 2",
    },
    {
        "project": "scrapy",
        "bug_id": 3,
        "buggy_commit": "ccc1003",
        "fix_commit": "ddd2003",
        "failing_test": "tests/test_http.py::TestRequest::test_headers",
        "pytest_output": "FAILED tests/test_http.py::TestRequest::test_headers - TypeError: headers must be dict, got list",
    },
    {
        "project": "scrapy",
        "bug_id": 4,
        "buggy_commit": "ccc1004",
        "fix_commit": "ddd2004",
        "failing_test": "tests/test_selector.py::TestSelector::test_xpath",
        "pytest_output": "FAILED tests/test_selector.py::TestSelector::test_xpath - ValueError: XPath error: Invalid expression '//div[@'",
    },
    # black (4)
    {
        "project": "black",
        "bug_id": 1,
        "buggy_commit": "eee1001",
        "fix_commit": "fff2001",
        "failing_test": "tests/test_format.py::TestFormat::test_simple",
        "pytest_output": "FAILED tests/test_format.py::TestFormat::test_simple - AssertionError: formatted output differs\nE       assert 'x=1' == 'x = 1'",
    },
    {
        "project": "black",
        "bug_id": 2,
        "buggy_commit": "eee1002",
        "fix_commit": "fff2002",
        "failing_test": "tests/test_black.py::BlackTestCase::test_empty",
        "pytest_output": "FAILED tests/test_black.py::BlackTestCase::test_empty - FileNotFoundError: [Errno 2] No such file or directory: '/tmp/black_test_empty.py'",
    },
    {
        "project": "black",
        "bug_id": 3,
        "buggy_commit": "eee1003",
        "fix_commit": "fff2003",
        "failing_test": "tests/test_comments.py::TestComments::test_trailing",
        "pytest_output": "FAILED tests/test_comments.py::TestComments::test_trailing - SyntaxError: invalid syntax at line 5 col 10",
    },
    {
        "project": "black",
        "bug_id": 4,
        "buggy_commit": "eee1004",
        "fix_commit": "fff2004",
        "failing_test": "tests/test_imports.py::TestImports::test_sort",
        "pytest_output": "FAILED tests/test_imports.py::TestImports::test_sort - ImportError: cannot import name 'format_str' from 'black'",
    },
    # httpie (4)
    {
        "project": "httpie",
        "bug_id": 1,
        "buggy_commit": "ggg1001",
        "fix_commit": "hhh2001",
        "failing_test": "tests/test_client.py::TestClient::test_get",
        "pytest_output": "FAILED tests/test_client.py::TestClient::test_get - AssertionError: status_code 404 != 200\nE       assert 404 == 200",
    },
    {
        "project": "httpie",
        "bug_id": 2,
        "buggy_commit": "ggg1002",
        "fix_commit": "hhh2002",
        "failing_test": "tests/test_auth.py::TestAuth::test_basic",
        "pytest_output": "FAILED tests/test_auth.py::TestAuth::test_basic - ValueError: invalid header value: 'Bearer \\n'",
    },
    {
        "project": "httpie",
        "bug_id": 3,
        "buggy_commit": "ggg1003",
        "fix_commit": "hhh2003",
        "failing_test": "tests/test_cli.py::TestCLI::test_verbose",
        "pytest_output": "FAILED tests/test_cli.py::TestCLI::test_verbose - ModuleNotFoundError: No module named 'httpie.plugins'",
    },
    {
        "project": "httpie",
        "bug_id": 4,
        "buggy_commit": "ggg1004",
        "fix_commit": "hhh2004",
        "failing_test": "tests/test_downloads.py::TestDownloads::test_resume",
        "pytest_output": "FAILED tests/test_downloads.py::TestDownloads::test_resume - TimeoutError: request timed out after 30s",
    },
    # ansible (4)
    {
        "project": "ansible",
        "bug_id": 1,
        "buggy_commit": "iii1001",
        "fix_commit": "jjj2001",
        "failing_test": "tests/test_templating.py::TestTemplating::test_variable",
        "pytest_output": "FAILED tests/test_templating.py::TestTemplating::test_variable - AssertionError: template 'hello {{ name }}' did not render: 'hello '",
    },
    {
        "project": "ansible",
        "bug_id": 2,
        "buggy_commit": "iii1002",
        "fix_commit": "jjj2002",
        "failing_test": "tests/test_inventory.py::TestInventory::test_host",
        "pytest_output": "FAILED tests/test_inventory.py::TestInventory::test_host - KeyError: 'host_vars'\nE       KeyError: 'host_vars'",
    },
    {
        "project": "ansible",
        "bug_id": 3,
        "buggy_commit": "iii1003",
        "fix_commit": "jjj2003",
        "failing_test": "tests/test_module.py::TestModule::test_args",
        "pytest_output": "FAILED tests/test_module.py::TestModule::test_args - TypeError: argument of type 'NoneType' is not iterable",
    },
    {
        "project": "ansible",
        "bug_id": 4,
        "buggy_commit": "iii1004",
        "fix_commit": "jjj2004",
        "failing_test": "tests/test_playbook.py::TestPlaybook::test_include",
        "pytest_output": "FAILED tests/test_playbook.py::TestPlaybook::test_include - FileNotFoundError: [Errno 2] No such file or directory: 'playbooks/include.yml'",
    },
    # matplotlib (4)
    {
        "project": "matplotlib",
        "bug_id": 1,
        "buggy_commit": "kkk1001",
        "fix_commit": "lll2001",
        "failing_test": "tests/test_axes.py::TestAxes::test_plot",
        "pytest_output": "FAILED tests/test_axes.py::TestAxes::test_plot - AssertionError: image comparison failed: RMS 12.5 > tolerance 2.0",
    },
    {
        "project": "matplotlib",
        "bug_id": 2,
        "buggy_commit": "kkk1002",
        "fix_commit": "lll2002",
        "failing_test": "tests/test_colors.py::TestColors::test_to_rgba",
        "pytest_output": "FAILED tests/test_colors.py::TestColors::test_to_rgba - ValueError: Invalid RGBA argument: 'not-a-color'",
    },
    {
        "project": "matplotlib",
        "bug_id": 3,
        "buggy_commit": "kkk1003",
        "fix_commit": "lll2003",
        "failing_test": "tests/test_ticker.py::TestTicker::test_format",
        "pytest_output": "FAILED tests/test_ticker.py::TestTicker::test_format - IndexError: list index out of range in ticker.py:120",
    },
    {
        "project": "matplotlib",
        "bug_id": 4,
        "buggy_commit": "kkk1004",
        "fix_commit": "lll2004",
        "failing_test": "tests/test_patches.py::TestPatches::test_rectangle",
        "pytest_output": "FAILED tests/test_patches.py::TestPatches::test_rectangle - AttributeError: 'Rectangle' object has no attribute 'get_bbox'",
    },
    # fastapi (4)
    {
        "project": "fastapi",
        "bug_id": 1,
        "buggy_commit": "mmm1001",
        "fix_commit": "nnn2001",
        "failing_test": "tests/test_router.py::TestRouter::test_get",
        "pytest_output": "FAILED tests/test_router.py::TestRouter::test_get - AssertionError: response status 422 != 200\nE       assert 422 == 200\nE       detail: field required",
    },
    {
        "project": "fastapi",
        "bug_id": 2,
        "buggy_commit": "mmm1002",
        "fix_commit": "nnn2002",
        "failing_test": "tests/test_dependencies.py::TestDeps::test_inject",
        "pytest_output": "FAILED tests/test_dependencies.py::TestDeps::test_inject - TypeError: Depends() missing annotation",
    },
]


def _failure(bug: dict[str, Any], ts: str) -> dict[str, Any]:
    project = str(bug["project"])
    bug_id = bug["bug_id"]
    buggy_commit = str(bug["buggy_commit"])
    failing_test = str(bug.get("failing_test", "tests/"))
    pytest_output = str(bug.get("pytest_output", ""))
    tid = f"bugsinpy-{project}-{bug_id}"
    fc = classify(pytest_output)
    return {
        "trajectory_id": tid,
        "id": tid,
        "timestamp": ts,
        "task": f"Run test suite after applying commit {buggy_commit}",
        "steps": [
            {
                "step_number": 1,
                "tool": "pytest",
                "input": "pytest tests/",
                "output": None,
                "error": pytest_output[:1000],
            }
        ],
        "success": False,
        "redacted": False,
        "failure_point": "step_1",
        "failure_class": fc,
        "quality_label": "noisy",
        "domain": "code",
        "severity": "medium",
        "tags": ["reference", "bugsinpy", "real-world", project],
        "expected_outcome": "should_extract",
        "expected_outcome_rationale": f"Real pytest failure from BugsInPy {project} bug {bug_id} ({failing_test}).",
        "expected_outcome_confidence": "medium",
        "source": "bugsinpy",
        "source_repo": _SOURCE_REPO,
        # Extra metadata for traceability (preserved through to_dict via extra keys ignored by model).
        "bugsinpy_project": project,
        "bugsinpy_bug_id": bug_id,
        "buggy_commit": buggy_commit,
        "fix_commit": str(bug.get("fix_commit", "")),
        "failing_test": failing_test,
    }


def _success(bug: dict[str, Any], ts: str) -> dict[str, Any]:
    project = str(bug["project"])
    bug_id = bug["bug_id"]
    fix_commit = str(bug.get("fix_commit", bug.get("buggy_commit", "")))
    failing_test = str(bug.get("failing_test", "tests/"))
    tid = f"bugsinpy-{project}-{bug_id}-fix"
    return {
        "trajectory_id": tid,
        "id": tid,
        "timestamp": ts,
        "task": f"Run test suite after applying commit {fix_commit}",
        "steps": [
            {
                "step_number": 1,
                "tool": "pytest",
                "input": "pytest tests/",
                "output": f"{failing_test} PASSED [100%]\n1 passed in 0.42s",
                "error": None,
            }
        ],
        "success": True,
        "redacted": False,
        "failure_point": None,
        "failure_class": None,
        "quality_label": "clear",
        "domain": "code",
        "severity": "low",
        "tags": ["reference", "bugsinpy", "real-world", project, "success"],
        "expected_outcome": "should_silence",
        "expected_outcome_rationale": f"Post-fix passing run for BugsInPy {project} bug {bug_id} (#707 balance).",
        "expected_outcome_confidence": "high",
        "source": "bugsinpy",
        "source_repo": _SOURCE_REPO,
        "bugsinpy_project": project,
        "bugsinpy_bug_id": bug_id,
        "buggy_commit": str(bug.get("buggy_commit", "")),
        "fix_commit": fix_commit,
        "failing_test": failing_test,
    }


def convert_bugsinpy(
    bugs: list[dict[str, Any]],
    *,
    limit: int | None = None,
    timestamp: str = _TS,
) -> list[dict[str, Any]]:
    """Return failure + success records for *bugs*.

    When *bugs* is empty, the built-in synthetic fixtures are used.
    Each bug yields one failure and one success trajectory (paired).
    """
    source: list[dict[str, Any]] = bugs if bugs else list(_SYNTHETIC_BUGS)
    if limit is not None:
        source = source[:limit]
    records: list[dict[str, Any]] = []
    for bug in source:
        records.append(_failure(bug, timestamp))
        records.append(_success(bug, timestamp))
    return records


def _is_java_supported() -> bool:
    """Return whether the ``java`` domain is matcher-supported (Defects4J gate)."""
    # Defects4J is Java-only; skip if Java is not in matcher domains.
    # ``src/cauterule/replay/matcher.py`` defines _KNOWN_DOMAINS without java.
    try:
        from cauterule.replay.matcher import _KNOWN_DOMAINS
    except Exception:
        return False
    else:
        return "java" in _KNOWN_DOMAINS


def main(argv: list[str] | None = None) -> None:
    """Convert BugsInPy metadata JSON and write failure + success corpus files."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bugs", type=Path, required=False, default=None, help="BugsInPy metadata JSON array.")
    parser.add_argument("--output", type=Path, required=True, help="Failure corpus dir (e.g. corpus/public/real-world/bugsinpy).")
    parser.add_argument("--success-output", type=Path, default=None, help="Success counterpart dir (#707).")
    parser.add_argument("--limit", type=int, default=36, help="Max bugs (default 36).")
    args = parser.parse_args(argv)

    if not _is_java_supported():
        # Informational: Defects4J skip rationale (not an error).
        print("[bugsinpy] Defects4J skipped: java domain not in matcher (_KNOWN_DOMAINS).", flush=True)

    if args.bugs is not None:
        raw = json.loads(args.bugs.read_text(encoding="utf-8"))
        if isinstance(raw, dict) and "bugs" in raw:
            raw = raw["bugs"]
        bugs: list[dict[str, Any]] = raw if isinstance(raw, list) else []
    else:
        bugs = list(_SYNTHETIC_BUGS)

    if args.limit is not None:
        bugs = bugs[: args.limit]

    records = convert_bugsinpy(bugs, limit=None)  # already limited
    failures = [r for r in records if not r["success"]]
    successes = [r for r in records if r["success"]]

    args.output.mkdir(parents=True, exist_ok=True)
    out = args.output / "bugsinpy.jsonl"
    # Strip extra Traceability keys that Trajectory.from_dict would otherwise store?
    # Keep them — they are extra metadata, harmless. Write as-is.
    out.write_text("\n".join(json.dumps(r) for r in failures) + "\n", encoding="utf-8")
    print(f"[convert] {len(failures)} failures -> {out} (license: {_LICENSE}, source: {_SOURCE_REPO})")

    if args.success_output is not None:
        args.success_output.mkdir(parents=True, exist_ok=True)
        success_out = args.success_output / "bugsinpy-successes.jsonl"
        success_out.write_text("\n".join(json.dumps(r) for r in successes) + "\n", encoding="utf-8")
        print(f"[convert] {len(successes)} successes -> {success_out}")


if __name__ == "__main__":
    main()
