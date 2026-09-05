import pytest

from cauterule.extraction.clustering.config import ClusteringConfig


def test_defaults() -> None:
    cfg = ClusteringConfig()
    assert cfg.enabled is True
    assert cfg.threshold == 0.85


def test_custom() -> None:
    cfg = ClusteringConfig(enabled=False, threshold=0.5)
    assert cfg.enabled is False
    assert cfg.threshold == 0.5


def test_invalid_threshold() -> None:
    with pytest.raises(ValueError, match="threshold"):
        ClusteringConfig(threshold=1.5)
    with pytest.raises(ValueError, match="threshold"):
        ClusteringConfig(threshold=-0.1)
