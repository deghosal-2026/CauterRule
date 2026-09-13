"""CI guard for v0.3.0 corpus / reference-corpus coverage (#690).

A silent "empty reference set" regression previously only surfaced as an
inexplicable 0-pass corpus in a full field sweep.  These checks fail fast if a
new v0.3.0 target corpus or a shared reference bucket becomes empty or
implausibly small.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from cauterule.replay.diagnostics import (
    MIN_REFERENCE_TRAJECTORIES,
    load_jsonl_trajectories,
)

_REPO = Path(__file__).resolve().parents[2]
_CORPUS = _REPO / "field-test" / "corpus"
_PUBLIC = _REPO / "corpus" / "public"


def _load_jsonl(paths: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for p in paths:
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
    return rows

_V030_TARGETS = ("adapters", "lifecycle", "packs", "mcp", "otel")
_REFERENCE_BUCKETS = (
    "curated/failures/positive",
    "curated/failures/negative",
    "curated/successes",
    "curated/nearmiss",
)


@pytest.mark.parametrize("name", _V030_TARGETS)
def test_v030_target_corpus_is_non_trivial(name: str) -> None:
    trajectories = load_jsonl_trajectories(_CORPUS / name / f"{name}.jsonl")
    assert len(trajectories) >= MIN_REFERENCE_TRAJECTORIES


@pytest.mark.parametrize("rel", _REFERENCE_BUCKETS)
def test_shared_reference_buckets_are_non_trivial(rel: str) -> None:
    files = sorted((_CORPUS / rel).glob("*.jsonl"))
    assert len(files) >= MIN_REFERENCE_TRAJECTORIES


# ---------------------------------------------------------------------------
# v0.3.1 #726/#735: adapter/CI signature coverage + expected_rule backfill
# ---------------------------------------------------------------------------
def test_adapter_reference_signatures_cover_frameworks() -> None:
    refs = _load_jsonl(
        [
            _PUBLIC / "adapters" / "reference.jsonl",
            _PUBLIC / "adapters" / "reference_frameworks.jsonl",
        ]
    )
    signed = [r for r in refs if r.get("error_signature")]
    assert len(signed) >= 20, f"expected >=20 signature-bearing adapter refs, got {len(signed)}"
    classes = {r.get("failure_class") for r in refs}
    assert {"agent/graph", "agent/crew", "agent/pydantic"} <= classes
    # domain must match the adapter target corpus (domain=python) or #708
    # domain-scoping falls back to the full pool.
    assert any(r.get("domain") == "python" for r in refs)


def test_ci_reference_slice_is_routed() -> None:
    refs = _load_jsonl(sorted((_PUBLIC / "ci_reference").glob("*.jsonl")))
    assert len(refs) >= MIN_REFERENCE_TRAJECTORIES
    assert all(r.get("domain") == "ci" for r in refs)


def test_golden_and_paraphrase_carry_expected_rule() -> None:
    for rel in ("golden", "reference-expansion/paraphrase-diversity"):
        rows = _load_jsonl(sorted((_PUBLIC / rel).glob("*.jsonl")))
        assert rows, rel
        missing = [r.get("id") for r in rows if not r.get("expected_rule")]
        assert not missing, f"{rel} missing expected_rule: {missing[:3]}"
