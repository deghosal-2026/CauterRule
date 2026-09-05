from cauterule.corpus.staleness import build_staleness_corpus


def test_staleness_corpus_not_empty() -> None:
    corpus = build_staleness_corpus()
    assert len(corpus) >= 3


def test_staleness_corpus_has_outdated_models() -> None:
    corpus = build_staleness_corpus()
    models = {t.agent_config.model for t in corpus if t.agent_config and t.agent_config.model}
    assert "gpt-3.5-turbo" in models or "claude-2" in models


def test_staleness_corpus_tagged() -> None:
    corpus = build_staleness_corpus()
    for t in corpus:
        assert "staleness" in t.tags


def test_staleness_corpus_ids_unique() -> None:
    corpus = build_staleness_corpus()
    ids = [t.id for t in corpus]
    assert len(ids) == len(set(ids))


def test_staleness_corpus_deprecated_tool() -> None:
    corpus = build_staleness_corpus()
    tools_used: set[str] = set()
    for t in corpus:
        if t.agent_config:
            tools_used.update(t.agent_config.tools)
    assert "docker_compose" in tools_used


def test_staleness_corpus_mixed_success() -> None:
    corpus = build_staleness_corpus()
    successes = [t for t in corpus if t.success]
    failures = [t for t in corpus if not t.success]
    assert len(successes) >= 1
    assert len(failures) >= 1


def test_staleness_corpus_has_deprecated_os() -> None:
    corpus = build_staleness_corpus()
    oss = {t.environment.os for t in corpus if t.environment and t.environment.os}
    assert "ubuntu-18.04" in oss or "centos-7" in oss or "windows-server-2016" in oss
