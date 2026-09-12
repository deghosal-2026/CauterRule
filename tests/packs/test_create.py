"""Tests for ``cauterule pack create`` (#555)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from cauterule.cli.app import main
from cauterule.models.rule import Provenance, RuleDo, RuleWhen, StandingRule
from cauterule.packs.create import create_pack
from cauterule.serialization.rule_yaml import dump_rule_to_file


def _seed_store(store: Path) -> list[str]:
    store.mkdir(parents=True, exist_ok=True)
    ids = []
    for i, (tags, taxonomy) in enumerate(
        [(("docker/build",), "docker/build"), (("python/import",), "python/import")]
    ):
        rid = f"R-9{i}1"
        rule = StandingRule(
            id=rid,
            when=RuleWhen(trigger=f"trigger {rid}"),
            do=RuleDo(directive=f"fix {rid}"),
            confidence=0.9,
            provenance=Provenance(
                source_trajectory="t",
                extracted_by="m",
                extract_timestamp="t",
                extraction_pass=1,
            ),
            status="active",
            promoted_at="2026-09-01T00:00:00Z",
            tags=tags,
            taxonomy=taxonomy,
        )
        dump_rule_to_file(rule, store / f"{rid}.yaml")
        ids.append(rid)
    return ids


class TestCreatePack:
    def test_create_from_tag(self, tmp_path: Path) -> None:
        store = tmp_path / "store"
        _seed_store(store)
        out = tmp_path / "pack-docker"
        summary = create_pack(
            "pack-docker", store=str(store), from_tag=("docker/build",), out=str(out)
        )
        assert summary["rules"] == ["R-901"]
        assert (out / "pack.yaml").is_file()
        assert (out / "manifest.yaml").is_file()
        assert (out / "R-901.yaml").is_file()
        assert (out / "tests" / "replay_pack-docker.jsonl").is_file()
        assert (out / "README.md").is_file()
        assert (out / "LICENSE").is_file()

    def test_verbatim_copy(self, tmp_path: Path) -> None:
        store = tmp_path / "store"
        _seed_store(store)
        out = tmp_path / "p"
        create_pack("p", store=str(store), all_promoted=True, out=str(out))
        for rid in ("R-901", "R-911"):
            original = (store / f"{rid}.yaml").read_bytes()
            copied = (out / f"{rid}.yaml").read_bytes()
            assert original == copied

    def test_empty_selection_errors(self, tmp_path: Path) -> None:
        store = tmp_path / "store"
        _seed_store(store)
        with pytest.raises(ValueError, match="empty selection"):
            create_pack("p", store=str(store), out=str(tmp_path / "p"))

    def test_unknown_tag_did_you_mean(self, tmp_path: Path) -> None:
        store = tmp_path / "store"
        _seed_store(store)
        with pytest.raises(ValueError, match="did-you-mean|did you mean"):
            create_pack(
                "p",
                store=str(store),
                from_tag=("docker/buil",),
                out=str(tmp_path / "p"),
            )

    def test_invalid_name(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="invalid pack name"):
            create_pack("Bad_Name!", store=str(tmp_path), out=str(tmp_path / "x"))

    def test_nonempty_out_refused(self, tmp_path: Path) -> None:
        store = tmp_path / "store"
        _seed_store(store)
        out = tmp_path / "p"
        out.mkdir()
        (out / "junk.txt").write_text("x")
        with pytest.raises(ValueError, match="--force"):
            create_pack("p", store=str(store), all_promoted=True, out=str(out))

    def test_min_rules(self, tmp_path: Path) -> None:
        store = tmp_path / "store"
        _seed_store(store)
        with pytest.raises(ValueError, match="--min-rules"):
            create_pack(
                "p",
                store=str(store),
                rule=("R-901",),
                min_rules=5,
                out=str(tmp_path / "p"),
            )

    def test_cli_create(self, tmp_path: Path) -> None:
        store = tmp_path / "store"
        _seed_store(store)
        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "pack",
                "create",
                "pack-demo",
                "--store",
                str(store),
                "--rule",
                "R-901",
                "--out",
                str(tmp_path / "pack-demo"),
            ],
        )
        assert result.exit_code == 0, result.output
        assert "Created pack pack-demo" in result.output

    def test_manifest_round_trip(self, tmp_path: Path) -> None:
        store = tmp_path / "store"
        _seed_store(store)
        out = tmp_path / "p"
        create_pack("p", store=str(store), all_promoted=True, out=str(out))
        manifest = yaml.safe_load((out / "pack.yaml").read_text())
        assert manifest["name"] == "p"
        assert manifest["version"] == "0.1.0"
        assert sorted(manifest["rules"]) == ["R-901", "R-911"]
