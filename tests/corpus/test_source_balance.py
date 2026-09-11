"""Tests for corpus source-balance checks (#707)."""

from __future__ import annotations

import json
from pathlib import Path

from cauterule.corpus.balance import (
    SourceBalance,
    balance_violations,
    iter_jsonl_records,
    load_public_balance,
    source_balance,
)


def _write(path: Path, records: list[dict[str, object]]) -> None:
    path.write_text("\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8")


def test_source_balance_groups_by_source() -> None:
    records = [
        {"source_repo": "alpha", "success": True},
        {"source_repo": "alpha", "success": False},
        {"source": "beta", "success": False},
    ]
    balances = {b.source: b for b in source_balance(records)}
    assert balances["alpha"] == SourceBalance("alpha", successes=1, failures=1)
    assert balances["beta"] == SourceBalance("beta", successes=0, failures=1)


def test_balance_violations_flags_failure_only_source() -> None:
    balances = [
        SourceBalance("alpha", successes=1, failures=1),
        SourceBalance("beta", successes=0, failures=3),
        SourceBalance("gamma", successes=2, failures=0),
    ]
    violations = balance_violations(balances)
    assert len(violations) == 2
    assert any("beta" in v for v in violations)
    assert any("gamma" in v for v in violations)
    assert not any("alpha" in v for v in violations)


def test_iter_jsonl_records_skips_blank_and_invalid(tmp_path: Path) -> None:
    path = tmp_path / "c.jsonl"
    path.write_text(
        '{"source_repo": "a", "success": true}\n\nnot json\n{"source_repo": "a", "success": false}\n',
        encoding="utf-8",
    )
    records = list(iter_jsonl_records([path]))
    assert len(records) == 2


def test_load_public_balance_reports_known_reference_gap() -> None:
    # The 288 reference-expansion failures currently have no matching successes
    # from the same source — this is the actionable #698/#707 follow-up. When
    # successes are paired, update this expectation.
    violations = balance_violations(load_public_balance())
    assert any("CauterRule" in v for v in violations)
