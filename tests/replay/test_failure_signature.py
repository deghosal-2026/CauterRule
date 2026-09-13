"""Tests for failure-signature matching (#722).

The matcher should score a trigger against the trajectory's *failure
signature* (failure_point + failure_class + failing-step errors), not the
full haystack (which includes task text and every step's input/output).
Otherwise a short trigger phrase is compared to a long multi-step document
and the embedding cosine is diluted.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterator

import pytest

from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.models.trajectory import Step, Trajectory
from cauterule.replay import embeddings

_DIM = 64


def _bucket(word: str) -> int:
    return int(hashlib.md5(word.encode()).hexdigest(), 16) % _DIM


class BagEmbedder:
    """Length-sensitive bag-of-words embedder (cosine drops as text grows)."""

    def encode(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for text in texts:
            vec = [0.0] * _DIM
            for word in text.lower().split():
                vec[_bucket(word)] += 1.0
            vectors.append(vec)
        return vectors


def _cand(trigger: str) -> CandidateRule:
    return CandidateRule(
        when=RuleWhen(trigger=trigger), do=RuleDo(directive="d"), confidence=0.9
    )


def _traj(
    *,
    task: str = "run migration",
    error: str = "postgres connection lost",
    failure_point: str | None = None,
    failure_class: str | None = None,
    extra_input: str | None = None,
) -> Trajectory:
    steps = [Step(1, "bash", error=error)]
    if extra_input is not None:
        steps.append(Step(2, "bash", input=extra_input, output="noise"))
    return Trajectory(
        id="T-sig",
        timestamp="t",
        task=task,
        steps=tuple(steps),
        success=False,
        failure_point=failure_point,
        failure_class=failure_class,
    )


@pytest.fixture(autouse=True)
def _reset_embeddings() -> Iterator[None]:
    embeddings.reset_embedder()
    yield
    embeddings.reset_embedder()


def test_build_signature_excludes_input_and_output() -> None:
    from cauterule.replay.matcher import _build_signature

    traj = Trajectory(
        id="T-sig",
        timestamp="t",
        task="TASK_MARKER",
        steps=(
            Step(
                1,
                "bash",
                input="INPUT_MARKER",
                output="OUTPUT_MARKER",
                error="ModuleNotFoundError: no module named foo",
            ),
        ),
        success=False,
        failure_point="step_1",
        failure_class="python/import/ModuleNotFoundError",
    )
    sig = _build_signature(traj)
    assert "modulenotfounderror" in sig or "no module named foo" in sig
    assert "python import modulenotfounderror" in sig
    assert "step 1" in sig
    assert "input_marker" not in sig
    assert "output_marker" not in sig
    assert "task_marker" not in sig


def test_match_score_not_diluted_by_long_input() -> None:
    embeddings.set_embedder_for_testing(BagEmbedder())
    # Trigger is a paraphrase in different word order, so the exact-substring
    # fast path does not fire and the score must come from the signature view.
    cand = _cand("connection to postgres was lost")
    short = _traj(error="postgres connection lost")
    long_blob = " ".join(f"offtopic{i}" for i in range(200))
    long = _traj(error="postgres connection lost", extra_input=long_blob)

    from cauterule.replay.matcher import match_score

    assert match_score(cand, long) >= match_score(cand, short) - 1e-9
