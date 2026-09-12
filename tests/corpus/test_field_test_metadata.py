"""Test that all corpus JSONL files contain required metadata fields.

Every trajectory in field-test/corpus/ and corpus/public/ must have fields
defined by the corpus format spec (M7 #188) and raw annotation requirement
(M3 #423):
  - identity: trajectory_id (or id)
  - core: timestamp, task, steps, success
  - metadata: domain, quality_label, tags
  - failure tracking: failure_point, failure_class, severity
  - annotation: expected_outcome, expected_outcome_rationale
"""

from __future__ import annotations

import json
from pathlib import Path

CORPUS_ROOTS = [Path("field-test/corpus"), Path("corpus/public")]

REQUIRED_FIELDS = frozenset({
    "trajectory_id",
    "timestamp",
    "task",
    "steps",
    "success",
    "domain",
    "quality_label",
    "tags",
    "failure_point",
    "failure_class",
    "severity",
    "expected_outcome",
    "expected_outcome_rationale",
})

OPTIONAL_FIELDS = frozenset({
    "expected_rule",
    "human_correction",
    "notes",
    "redacted",
    "source",
    "source_repo",
    "id",
})

# Fields that can be absent when the record is a success
_OPTIONAL_ON_SUCCESS = frozenset({"failure_point", "failure_class", "severity"})


def _collect_missing(path: Path) -> list[dict]:
    """Return list of {trajectory_id, missing_fields} for each missing-field record."""
    results: list[dict] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped:
                continue
            rec = json.loads(stripped)
            tid = rec.get("trajectory_id") or rec.get("id") or path.stem
            required = REQUIRED_FIELDS - (
                _OPTIONAL_ON_SUCCESS if rec.get("success") is True else frozenset()
            )
            missing = sorted(f for f in required if f not in rec)
            if missing:
                results.append({"trajectory_id": tid, "missing_fields": missing})
    return results


def _assert_corpus(root: Path) -> None:
    """Assert all JSONL files under *root* have complete metadata."""
    jsonl_files = sorted(root.rglob("*.jsonl"))
    assert jsonl_files, f"No JSONL files found under {root}"

    all_issues: list[str] = []
    total_checked = 0

    for fpath in jsonl_files:
        issues = _collect_missing(fpath)
        if issues:
            for entry in issues:
                all_issues.append(
                    f"{fpath.relative_to(root.parent)}: "
                    f"{entry['trajectory_id']}: missing {entry['missing_fields']}"
                )
        total_checked += sum(
            1 for _ in fpath.open()
        )

    assert not all_issues, (
        f"\n{len(all_issues)} trajectory(s) with missing fields "
        f"(checked {total_checked} records under {root}):\n"
        + "\n".join(all_issues)
    )


def test_field_test_corpus_all_required_fields() -> None:
    """Every JSONL in field-test/corpus/ must have all REQUIRED_FIELDS."""
    _assert_corpus(Path("field-test/corpus"))


def test_public_corpus_all_required_fields() -> None:
    """Every JSONL in corpus/public/ must have all REQUIRED_FIELDS."""
    _assert_corpus(Path("corpus/public"))
