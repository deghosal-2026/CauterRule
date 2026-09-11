"""Tests for optional semantic/embedding matching (#689)."""

from __future__ import annotations

from collections.abc import Iterator

import pytest

from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.models.trajectory import Step, Trajectory
from cauterule.replay import embeddings
from cauterule.replay.matcher import match_score


class KeywordEmbedder:
    """Deterministic 3-axis embedder for tests (no model download)."""

    def __init__(self) -> None:
        self.calls = 0

    def encode(self, texts: list[str]) -> list[list[float]]:
        self.calls += len(texts)
        return [self._vec(t) for t in texts]

    @staticmethod
    def _vec(text: str) -> list[float]:
        lowered = text.lower()
        if any(k in lowered for k in ("database", "postgres", "lost connection", "db connection")):
            return [1.0, 0.0, 0.0]
        if any(k in lowered for k in ("kubernetes", "crd", "k8s", "customresourcedefinition")):
            return [0.0, 1.0, 0.0]
        if any(k in lowered for k in ("permission", "passwd", "privilege")):
            return [0.0, 0.0, 1.0]
        return [0.0, 0.0, 0.0]


def _cand(trigger: str, context: tuple[str, ...] = ()) -> CandidateRule:
    return CandidateRule(
        when=RuleWhen(trigger=trigger, context=context),
        do=RuleDo(directive="d"),
        confidence=0.9,
    )


def _traj(task: str, error: str, *, success: bool = False, failure_class: str | None = None) -> Trajectory:
    return Trajectory(
        id="T-sem",
        timestamp="t",
        task=task,
        steps=(Step(1, "bash", error=error),),
        success=success,
        failure_class=failure_class,
    )


@pytest.fixture(autouse=True)
def _reset_embeddings() -> Iterator[None]:
    embeddings.reset_embedder()
    yield
    embeddings.reset_embedder()


def test_semantic_disabled_by_default() -> None:
    assert embeddings.is_enabled() is False
    assert embeddings.embedding_similarity("database connection dropped", "lost postgres connection") == 0.0


def test_embedding_similarity_bridges_paraphrase() -> None:
    embeddings.set_embedder_for_testing(KeywordEmbedder())
    cand = _cand("database connection dropped")
    traj = _traj("run migration", "lost connection to postgres server")
    assert match_score(cand, traj) >= 0.70


def test_embedding_similarity_unrelated_text_stays_low() -> None:
    embeddings.set_embedder_for_testing(KeywordEmbedder())
    cand = _cand("permission denied on /etc/passwd")
    traj = _traj("kubernetes apply", "no matches for kind CustomResourceDefinition")
    assert match_score(cand, traj) < 0.60


def test_embedding_similarity_is_cached_per_text() -> None:
    embedder = KeywordEmbedder()
    embeddings.set_embedder_for_testing(embedder)
    cand = _cand("database connection dropped")
    match_score(cand, _traj("run migration", "lost connection to postgres server"))
    match_score(cand, _traj("startup", "db connection lost during boot"))
    # trigger embedded once (cache hit on the second call) + 2 distinct haystacks
    assert embedder.calls == 3


@pytest.mark.parametrize("trigger", ["command fails", "pipeline fails", "not found error"])
def test_semantic_similarity_does_not_reintroduce_492_regression(trigger: str) -> None:
    embeddings.set_embedder_for_testing(KeywordEmbedder())
    cand = _cand(trigger)
    traj = _traj("unit tests pass", "all tests passed successfully", success=True)
    assert match_score(cand, traj) < 0.60


def test_cosine_helpers() -> None:
    assert embeddings._cosine((1.0, 0.0), (1.0, 0.0)) == 1.0
    assert embeddings._cosine((1.0, 0.0), (0.0, 1.0)) == 0.0
    assert embeddings._cosine((0.0, 0.0), (1.0, 0.0)) == 0.0
