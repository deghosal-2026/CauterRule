
from cauterule.corpus.tiers import build_tiered_corpus


def test_build_tiered_corpus_tiny() -> None:
    result = build_tiered_corpus("/tmp/test-corpus", {"tiny": 25})
    assert "tiny" in result
    assert len(result["tiny"]) == 25


def test_build_tiered_corpus_multiple_tiers() -> None:
    result = build_tiered_corpus("/tmp/test-corpus", {"tiny": 10, "small": 20})
    assert len(result["tiny"]) == 10
    assert len(result["small"]) == 20


def test_build_tiered_corpus_balanced_success_failure() -> None:
    result = build_tiered_corpus("/tmp/test-corpus", {"tiny": 50})
    trajectories = result["tiny"]
    successes = sum(1 for t in trajectories if t.success)
    failures = sum(1 for t in trajectories if not t.success)
    # Should have roughly half success
    assert successes > 0
    assert failures > 0
    assert abs(successes - failures) <= 2  # roughly balanced


def test_build_tiered_corpus_all_have_required_fields() -> None:
    result = build_tiered_corpus("/tmp/test-corpus", {"tiny": 10})
    for t in result["tiny"]:
        assert t.id.startswith("tiny-")
        assert t.task
        assert len(t.steps) >= 2
        assert t.quality_label is not None


def test_build_tiered_corpus_empty() -> None:
    result = build_tiered_corpus("/tmp/test-corpus", {})
    assert result == {}


def test_build_tiered_corpus_deterministic_seed_independence() -> None:
    r1 = build_tiered_corpus("/tmp/x", {"tiny": 5})
    r2 = build_tiered_corpus("/tmp/x", {"tiny": 5})
    # Random is not seeded, so results differ
    ids1 = {t.id for t in r1["tiny"]}
    ids2 = {t.id for t in r2["tiny"]}
    # What we can assert: all IDs unique
    assert len(ids1) == 5
    assert len(ids2) == 5


def test_build_tiered_corpus_medium() -> None:
    result = build_tiered_corpus("/tmp/test-corpus", {"medium": 100})
    assert len(result["medium"]) == 100
    for t in result["medium"]:
        assert t.domain in ("coding", "devops", "research", "support", "browser_automation")
