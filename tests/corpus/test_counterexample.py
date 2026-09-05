from cauterule.corpus.counterexample import build_counterexample_corpus


def test_counterexample_corpus_not_empty() -> None:
    corpus = build_counterexample_corpus()
    assert len(corpus) >= 3


def test_counterexample_corpus_all_success() -> None:
    corpus = build_counterexample_corpus()
    for t in corpus:
        assert t.success is True, f"{t.id} should be a success (counterexample)"


def test_counterexample_corpus_all_tagged() -> None:
    corpus = build_counterexample_corpus()
    for t in corpus:
        assert "counterexample" in t.tags


def test_counterexample_corpus_diverse_domains() -> None:
    corpus = build_counterexample_corpus()
    domains = {t.domain for t in corpus}
    assert len(domains) >= 2  # at least 2 different domains


def test_counterexample_corpus_ids_unique() -> None:
    corpus = build_counterexample_corpus()
    ids = [t.id for t in corpus]
    assert len(ids) == len(set(ids))


def test_counterexample_corpus_valid_trajectories() -> None:
    corpus = build_counterexample_corpus()
    for t in corpus:
        assert t.task
        assert len(t.steps) >= 1
        assert t.id.startswith("counterex-")


def test_counterexample_corpus_no_failure_points() -> None:
    corpus = build_counterexample_corpus()
    for t in corpus:
        assert t.failure_point is None
        assert t.failure_class is None
