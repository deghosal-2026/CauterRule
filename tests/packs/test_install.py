"""Tests for pack SPEC parsing + installer (#554). Hermetic: no network."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from cauterule.cli.app import main
from cauterule.packs.install import INSTALL_JSON, compare_versions, install_pack
from cauterule.packs.spec import parse_spec


def _make_source_pack(tmp_path: Path, name: str = "pack-demo", version: str = "1.2.0") -> Path:
    src = tmp_path / "src-pack"
    rules_dir = src / "rules"
    rules_dir.mkdir(parents=True)
    manifest = {
        "name": name,
        "version": version,
        "description": "Demo pack",
        "author": "Tests",
        "rules": ["R-900"],
    }
    (src / "pack.yaml").write_text(yaml.safe_dump(manifest), encoding="utf-8")
    (rules_dir / "R-900.yaml").write_text(
        "id: R-900\nwhen:\n  trigger: demo trigger\n"
        "do:\n  directive: demo fix\nconfidence: 0.9\n"
        "provenance:\n  source_trajectory: t\n  extracted_by: m\n"
        "  extract_timestamp: t\n  extraction_pass: 1\n"
        "status: active\npromoted_at: t\npack: pack-demo\n",
        encoding="utf-8",
    )
    # Loader expects R-*.yaml at pack root; keep both layouts working.
    (src / "R-900.yaml").write_text((src / "rules" / "R-900.yaml").read_text(), encoding="utf-8")
    return src


class TestParseSpec:
    def test_github_pinned(self) -> None:
        s = parse_spec("acme/pack-docker@v1.2.0")
        assert (s.kind, s.owner, s.repo, s.version) == ("github", "acme", "pack-docker", "v1.2.0")

    def test_github_latest(self) -> None:
        s = parse_spec("acme/pack-docker")
        assert s.kind == "github" and s.version == ""

    def test_shorthand(self) -> None:
        s = parse_spec("pack-docker@1.2.0")
        assert (s.kind, s.name, s.version) == ("shorthand", "pack-docker", "1.2.0")

    def test_gist_url(self) -> None:
        s = parse_spec("https://gist.github.com/alice/abc123")
        assert (s.kind, s.gist_id) == ("gist", "abc123")

    def test_gist_prefix(self) -> None:
        assert parse_spec("gist:abc123").gist_id == "abc123"

    def test_local_dir(self, tmp_path: Path) -> None:
        src = _make_source_pack(tmp_path)
        s = parse_spec(str(src))
        assert s.kind == "local"

    def test_blank_rejected(self) -> None:
        with pytest.raises(ValueError):
            parse_spec("  ")


class TestCompareVersions:
    def test_ordering(self) -> None:
        assert compare_versions("1.0.0", "1.0.1") == -1
        assert compare_versions("v1.2.0", "1.2.0") == 0
        assert compare_versions("2.0.0", "1.9.9") == 1


class TestInstallPack:
    def test_install_local_dir(self, tmp_path: Path) -> None:
        src = _make_source_pack(tmp_path)
        store = tmp_path / "store"
        summary = install_pack(str(src), store=str(store))
        assert summary["name"] == "pack-demo"
        dest = Path(summary["path"])
        assert (dest / "pack.yaml").is_file()
        assert (dest / "INSTALL.json").is_file()
        record = json.loads((dest / INSTALL_JSON).read_text())
        assert record["source"] == str(src)
        assert record["cert"]["passed"] is True

    def test_reinstall_same_version_refused(self, tmp_path: Path) -> None:
        src = _make_source_pack(tmp_path)
        store = tmp_path / "store"
        install_pack(str(src), store=str(store))
        with pytest.raises(ValueError, match="--force"):
            install_pack(str(src), store=str(store))

    def test_force_overwrites(self, tmp_path: Path) -> None:
        src = _make_source_pack(tmp_path)
        store = tmp_path / "store"
        install_pack(str(src), store=str(store))
        summary = install_pack(str(src), store=str(store), force=True)
        assert summary["version"] == "1.2.0"

    def test_downgrade_refused(self, tmp_path: Path) -> None:
        src_new = _make_source_pack(tmp_path / "a", version="2.0.0")
        src_old = _make_source_pack(tmp_path / "b", version="1.0.0")
        store = tmp_path / "store"
        install_pack(str(src_new), store=str(store))
        with pytest.raises(ValueError, match="[Dd]owngrade"):
            install_pack(str(src_old), store=str(store))

    def test_uncertified_blocked_skip_cert_warns(self, tmp_path: Path) -> None:
        src = tmp_path / "bad"
        src.mkdir()
        (src / "pack.yaml").write_text(
            yaml.safe_dump({"name": "", "version": "", "description": "", "author": "", "rules": []}),
            encoding="utf-8",
        )
        with pytest.raises(ValueError, match="[Mm]anifest invalid"):
            install_pack(str(src), store=str(tmp_path / "store"))

    def test_checksum_mismatch_aborts(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        import tarfile

        src = _make_source_pack(tmp_path)
        asset = tmp_path / "pack.tar.gz"
        with tarfile.open(asset, "w:gz") as tar:
            tar.add(src, arcname="pack-demo")
        with pytest.raises(ValueError, match="checksum mismatch"):
            install_pack(
                str(asset),
                store=str(tmp_path / "store"),
                checksum="0" * 64,
            )

    def test_offline_no_cache_errors(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="[Oo]ffline|unknown pack shorthand"):
            install_pack(
                "pack-demo@1.0.0", store=str(tmp_path / "store"), offline=True
            )

    def test_cli_install_and_list(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        src = _make_source_pack(tmp_path)
        store = tmp_path / "store"
        runner = CliRunner()
        result = runner.invoke(main, ["pack", "install", str(src), "--store", str(store)])
        assert result.exit_code == 0, result.output
        assert "Installed pack-demo" in result.output
        result = runner.invoke(main, ["pack", "list", "--store", str(store)])
        assert result.exit_code == 0
        assert "pack-demo" in result.output
        result = runner.invoke(main, ["pack", "info", "pack-demo", "--store", str(store)])
        assert result.exit_code == 0
        assert "1.2.0" in result.output
