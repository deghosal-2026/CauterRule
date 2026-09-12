"""CI guard for v0.3.0 corpus / reference-corpus coverage (#690).

A silent "empty reference set" regression previously only surfaced as an
inexplicable 0-pass corpus in a full field sweep.  These checks fail fast if a
new v0.3.0 target corpus or a shared reference bucket becomes empty or
implausibly small.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from cauterule.replay.diagnostics import (
    MIN_REFERENCE_TRAJECTORIES,
    load_jsonl_trajectories,
)

_REPO = Path(__file__).resolve().parents[2]
_CORPUS = _REPO / "field-test" / "corpus"

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
