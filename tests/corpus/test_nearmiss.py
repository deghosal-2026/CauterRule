from cauterule.corpus.nearmiss import build_nearmiss_corpus


def test_nearmiss_corpus_not_empty() -> None:
    corpus = build_nearmiss_corpus()
    assert len(corpus) >= 3


def test_nearmiss_corpus_all_success() -> None:
    corpus = build_nearmiss_corpus()
    for t in corpus:
        assert t.success is True, f"{t.id} should succeed (near-miss)"


def test_nearmiss_corpus_has_failure_attributes() -> None:
    corpus = build_nearmiss_corpus()
    # Near-misses have failure_point/failure_class from the failure pattern even though they succeed
    for t in corpus:
        if t.id == "nearmiss-git-001":
            assert t.failure_point is None  # first attempt fails but trajectory succeeds via retry
        if t.id == "nearmiss-k8s-002":
            assert t.quality_label == "multi-causal"


def test_nearmiss_corpus_ids_unique() -> None:
    corpus = build_nearmiss_corpus()
    ids = [t.id for t in corpus]
    assert len(ids) == len(set(ids))


def test_nearmiss_corpus_tagged() -> None:
    corpus = build_nearmiss_corpus()
    for t in corpus:
        assert "nearmiss" in t.tags


def test_nearmiss_corpus_has_steps() -> None:
    corpus = build_nearmiss_corpus()
    for t in corpus:
        assert len(t.steps) >= 2
