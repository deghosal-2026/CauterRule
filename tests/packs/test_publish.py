"""Tests for pack publish + semver + dep resolution (#548). Hermetic fakes only."""

from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar

import pytest
import yaml

from cauterule.packs import semver
from cauterule.packs.deps import parse_dep, read_lockfile, resolve, write_lockfile
from cauterule.packs.publish import auto_notes, build_asset, publish_pack


class TestSemver:
    def test_parse(self) -> None:
        assert str(semver.parse("1.2.3")) == "1.2.3"
        assert str(semver.parse("v1.2.3")) == "1.2.3"

    def test_rejects_non_strict(self) -> None:
        for bad in ("1.2", "1", "latest", "1.2.3.4", ""):
            with pytest.raises(ValueError):
                semver.parse(bad)

    def test_bump(self) -> None:
        assert semver.bump("1.2.3", "major") == "2.0.0"
        assert semver.bump("1.2.3", "minor") == "1.3.0"
        assert semver.bump("1.2.3", "patch") == "1.2.4"

    def test_suggest_bump(self) -> None:
        assert semver.suggest_bump(["A"], ["A", "B"]) == "minor"
        assert semver.suggest_bump(["A", "B"], ["A"]) == "major"
        assert semver.suggest_bump(["A"], ["A"]) == "patch"

    def test_satisfies_ranges(self) -> None:
        assert semver.satisfies("1.4.2", ">=1.0.0,<2.0.0")
        assert not semver.satisfies("2.1.0", ">=1.0.0,<2.0.0")
        assert semver.satisfies("1.2.5", "^1.2.0")
        assert not semver.satisfies("2.0.0", "^1.2.0")
        assert semver.satisfies("1.2.9", "~1.2.0")
        assert not semver.satisfies("1.3.0", "~1.2.0")
        assert semver.satisfies("1.2.0", "1.2.0")
        assert not semver.satisfies("1.2.0-rc.1", ">=1.0.0")

    def test_prerelease_exact_pin(self) -> None:
        assert semver.satisfies("1.2.0-rc.1", "1.2.0-rc.1")


class TestDeps:
    AVAILABLE: ClassVar[dict[str, dict[str, object]]] = {
        "pack-deploy": {
            "versions": ["1.1.0"],
            "deps": {"1.1.0": ["pack-docker >=1.0.0,<2.0.0"]},
        },
        "pack-docker": {"versions": ["1.4.2", "2.0.0"], "deps": {}},
    }

    def test_parse_dep(self) -> None:
        assert parse_dep("pack-docker >=1.0.0,<2.0.0") == ("pack-docker", ">=1.0.0,<2.0.0")
        assert parse_dep("pack-foo") == ("pack-foo", "")

    def test_diamond_resolves(self) -> None:
        resolved = resolve({"pack-deploy": ""}, self.AVAILABLE)
        assert resolved == {"pack-deploy": "1.1.0", "pack-docker": "1.4.2"}

    def test_conflict_actionable(self) -> None:
        available = {
            "pack-a": {"versions": ["1.0.0"], "deps": {"1.0.0": ["pack-c <2.0.0"]}},
            "pack-b": {"versions": ["1.0.0"], "deps": {"1.0.0": ["pack-c >=2.0.0"]}},
            "pack-c": {"versions": ["1.0.0", "2.0.0"], "deps": {}},
        }
        with pytest.raises(ValueError, match="conflict"):
            resolve({"pack-a": "", "pack-b": ""}, available)

    def test_cycle_reported(self) -> None:
        available = {
            "pack-a": {"versions": ["1.0.0"], "deps": {"1.0.0": ["pack-b"]}},
            "pack-b": {"versions": ["1.0.0"], "deps": {"1.0.0": ["pack-a"]}},
        }
        with pytest.raises(ValueError, match="cycle"):
            resolve({"pack-a": ""}, available)

    def test_lockfile_round_trip(self, tmp_path: Path) -> None:
        write_lockfile(str(tmp_path), {"a": "1.0.0"}, {"a": "github:x/a@1.0.0"})
        assert read_lockfile(str(tmp_path)) == {"a": "1.0.0"}


class FakeApi:
    """Hermetic fake of the ReleasesApi protocol."""

    def __init__(self) -> None:
        self.versions: list[str] = []
        self.manifests: dict[str, dict[str, Any]] = {}
        self.releases: list[dict[str, Any]] = []

    def list_versions(self, repo: str) -> list[str]:
        return list(self.versions)

    def get_manifest(self, repo: str, version: str) -> dict[str, Any] | None:
        return self.manifests.get(version)

    def create_release(self, repo: str, tag: str, asset: Path, notes: str, prerelease: bool) -> str:
        self.releases.append({"tag": tag, "notes": notes, "prerelease": prerelease})
        return f"https://github.com/{repo}/releases/{tag}"


def _pack_dir(tmp_path: Path, version: str = "1.0.0", rules: tuple[str, ...] = ("R-201",)) -> Path:
    d = tmp_path / "pack-deploy"
    d.mkdir()
    (d / "pack.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "pack-deploy",
                "version": version,
                "description": "d",
                "author": "t",
                "rules": list(rules),
            }
        ),
        encoding="utf-8",
    )
    for rid in rules:
        (d / f"{rid}.yaml").write_text(f"id: {rid}\n", encoding="utf-8")
    return d


class TestPublish:
    def test_dry_run(self, tmp_path: Path) -> None:
        d = _pack_dir(tmp_path)
        result = publish_pack(str(d), repo="acme/packs", dry_run=True, api=FakeApi())
        assert result["dry_run"] is True
        assert result["tag"] == "pack-pack-deploy-v1.0.0"
        assert result["sha256"]

    def test_monotonic_enforced(self, tmp_path: Path) -> None:
        d = _pack_dir(tmp_path, version="1.0.0")
        api = FakeApi()
        api.versions = ["1.0.0"]
        with pytest.raises(ValueError, match="not newer"):
            publish_pack(str(d), repo="acme/packs", api=api)

    def test_publish_then_bump(self, tmp_path: Path) -> None:
        d = _pack_dir(tmp_path, version="1.0.0")
        api = FakeApi()
        first = publish_pack(str(d), repo="acme/packs", api=api)
        assert first["url"].endswith("pack-pack-deploy-v1.0.0")
        api.versions = ["1.0.0"]
        api.manifests = {"1.0.0": {"rules": ["R-201"]}}
        second = publish_pack(
            str(d), repo="acme/packs", bump_kind="minor", allow_dirty=True, api=api
        )
        assert second["version"] == "1.1.0"

    def test_cert_failure_blocks(self, tmp_path: Path) -> None:
        d = tmp_path / "bad"
        d.mkdir()
        (d / "pack.yaml").write_text(
            yaml.safe_dump({"name": "", "version": "x", "description": "", "author": ""}),
            encoding="utf-8",
        )
        with pytest.raises(ValueError, match="[Cc]ert|manifest|semver"):
            publish_pack(str(d), repo="acme/packs", dry_run=True, api=FakeApi())

    def test_auto_notes(self) -> None:
        notes = auto_notes("p", ["A"], ["A", "B"], "1.1.0")
        assert "Added" in notes and "B" in notes

    def test_build_asset(self, tmp_path: Path) -> None:
        d = _pack_dir(tmp_path)
        asset = build_asset(d, "pack-deploy", "1.0.0", tmp_path)
        assert asset.is_file()
