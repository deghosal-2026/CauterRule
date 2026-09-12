"""Tests for catalog loader."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from cauterule.corpus.catalog import load_catalog


def test_load_catalog_yaml(tmp_path: Path) -> None:
    p = tmp_path / "catalog.yaml"
    data = {
        "golden": {"id": "golden", "tier": "small", "trajectory_count": 10},
        "successes": {"id": "successes", "tier": "medium", "trajectory_count": 50},
    }
    p.write_text(yaml.safe_dump(data), encoding="utf-8")
    catalog = load_catalog(str(p))
    assert "golden" in catalog
    assert catalog["golden"].trajectory_count == 10


def test_load_catalog_not_found(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_catalog(str(tmp_path / "nope.yaml"))


def test_load_catalog_invalid_type(tmp_path: Path) -> None:
    p = tmp_path / "catalog.yaml"
    p.write_text("42", encoding="utf-8")
    with pytest.raises(ValueError, match="must be a mapping"):
        load_catalog(str(p))


def test_load_catalog_entry_not_mapping(tmp_path: Path) -> None:
    p = tmp_path / "catalog.yaml"
    p.write_text("golden: 42", encoding="utf-8")
    with pytest.raises(TypeError):
        load_catalog(str(p))
