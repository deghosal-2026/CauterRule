import pytest

from cauterule.corpus.format import CORPUS_METADATA_FIELDS, CORPUS_SCHEMA_VERSION, CorpusMetadata


def test_schema_constants() -> None:
    assert CORPUS_SCHEMA_VERSION == "1.0"
    assert isinstance(CORPUS_METADATA_FIELDS, list)
    assert "id" in CORPUS_METADATA_FIELDS
    assert "tier" in CORPUS_METADATA_FIELDS
    assert "trajectory_count" in CORPUS_METADATA_FIELDS


def test_corpus_metadata_valid() -> None:
    meta = CorpusMetadata(
        id="test-corpus",
        tier="tiny",
        domain="coding",
        trajectory_count=25,
        gold_rule_ids=("GR-1", "GR-2"),
    )
    assert meta.id == "test-corpus"
    assert meta.tier == "tiny"
    assert meta.domain == "coding"
    assert meta.trajectory_count == 25
    assert meta.gold_rule_ids == ("GR-1", "GR-2")


def test_corpus_metadata_minimal() -> None:
    meta = CorpusMetadata(id="empty", tier="small")
    assert meta.domain is None
    assert meta.trajectory_count == 0
    assert meta.gold_rule_ids == ()


def test_corpus_metadata_invalid_id() -> None:
    with pytest.raises(ValueError, match="id"):
        CorpusMetadata(id=" ", tier="tiny")
    with pytest.raises(ValueError, match="id"):
        CorpusMetadata(id="", tier="tiny")


def test_corpus_metadata_invalid_tier() -> None:
    with pytest.raises(ValueError, match="tier"):
        CorpusMetadata(id="x", tier="huge")  # type: ignore[arg-type]


def test_corpus_metadata_negative_count() -> None:
    with pytest.raises(ValueError, match="trajectory_count"):
        CorpusMetadata(id="x", tier="tiny", trajectory_count=-1)


def test_corpus_metadata_all_tiers() -> None:
    for tier in ("tiny", "small", "medium", "large"):
        meta = CorpusMetadata(id=f"corpus-{tier}", tier=tier)
        assert meta.tier == tier


def test_corpus_metadata_roundtrip() -> None:
    meta = CorpusMetadata(
        id="rt", tier="medium", domain="devops", trajectory_count=100, gold_rule_ids=("GR-3",)
    )
    d = meta.to_dict()
    assert d["id"] == "rt"
    assert d["tier"] == "medium"
    assert d["domain"] == "devops"
    assert d["trajectory_count"] == 100
    assert d["gold_rule_ids"] == ["GR-3"]
    assert CorpusMetadata.from_dict(d) == meta


def test_corpus_metadata_roundtrip_minimal() -> None:
    meta = CorpusMetadata(id="min", tier="large")
    d = meta.to_dict()
    assert "domain" not in d
    assert "quality_label" not in d
    assert "gold_rule_ids" not in d
    restored = CorpusMetadata.from_dict(d)
    assert restored == meta
