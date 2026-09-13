"""Tests for ``cauterule share`` + gist install round-trip (#547). Fakes only."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from cauterule.cli.app import main
from cauterule.models.rule import Provenance, RuleDo, RuleWhen, StandingRule
from cauterule.packs.install import install_pack
from cauterule.packs.share import import_gist, share_rule
from cauterule.serialization.rule_yaml import dump_rule_to_file


class FakeGist:
    def __init__(self) -> None:
        self.store: dict[str, dict[str, str]] = {}
        self.counter = 0

    def create_gist(self, description: str, public: bool, files: dict[str, str]) -> str:
        self.counter += 1
        gist_id = f"abc{self.counter:03d}"
        self.store[gist_id] = dict(files)
        return f"https://gist.github.com/test/{gist_id}"

    def fetch_gist(self, gist_id: str) -> dict[str, str]:
        return dict(self.store[gist_id])


def _seed(store: Path, secret: bool = False) -> str:
    store.mkdir(parents=True, exist_ok=True)
    trigger = "run the thing"
    if secret:
        trigger = "use password hunter2-hunter2-hunter2-hunter2-99"
    rule = StandingRule(
        id="R-001",
        when=RuleWhen(trigger=trigger),
        do=RuleDo(directive="fix it"),
        confidence=0.9,
        provenance=Provenance(
            source_trajectory="t", extracted_by="m", extract_timestamp="t", extraction_pass=1
        ),
        status="active",
        promoted_at="2026-09-01T00:00:00Z",
    )
    dump_rule_to_file(rule, store / "R-001.yaml")
    return "R-001"


class TestShare:
    def test_share_creates_secret_gist(self, tmp_path: Path) -> None:
        store = tmp_path / "store"
        _seed(store)
        api = FakeGist()
        result = share_rule("R-001", store=str(store), api=api)
        assert result["url"].startswith("https://gist.github.com/")
        assert "R-001.yaml" in result["files"]
        assert "PROVENANCE.json" in result["files"]

    def test_round_trip(self, tmp_path: Path) -> None:
        store = tmp_path / "store"
        _seed(store)
        api = FakeGist()
        shared = share_rule("R-001", store=str(store), api=api)
        gist_id = shared["url"].rsplit("/", 1)[-1]
        fresh = tmp_path / "fresh"
        fresh.mkdir()
        imported = import_gist(gist_id, store=str(fresh), api=api)
        assert imported["id"] == "R-001"
        assert "imported-from-gist" in imported["tags"]
        assert (fresh / "R-001.yaml").is_file()

    def test_install_gist_spec(self, tmp_path: Path) -> None:
        store = tmp_path / "store"
        _seed(store)
        api = FakeGist()
        shared = share_rule("R-001", store=str(store), api=api)
        fresh = tmp_path / "fresh"
        fresh.mkdir()
        summary = install_pack(shared["url"], store=str(fresh), gist_api=api)
        assert summary["rule_count"] == 1
        assert (fresh / "R-001.yaml").is_file()

    def test_install_gist_unsafe_rule_refused(self, tmp_path: Path) -> None:
        # #799: the gist install path must enforce safety, not report passed=True.
        other = tmp_path / "other"
        other.mkdir()
        rule = StandingRule(
            id="R-900",
            when=RuleWhen(trigger="stuff happens"),
            do=RuleDo(directive="run rm -rf /"),
            confidence=0.9,
            provenance=Provenance(
                source_trajectory="t", extracted_by="m", extract_timestamp="t", extraction_pass=1
            ),
            status="active",
            promoted_at="t",
        )
        dump_rule_to_file(rule, other / "R-900.yaml")
        api = FakeGist()
        shared = share_rule("R-900", store=str(other), api=api)
        fresh = tmp_path / "fresh"
        fresh.mkdir()
        with pytest.raises(ValueError, match="safety"):
            install_pack(shared["url"], store=str(fresh), gist_api=api)
        # atomic: the refused rule must not be in the store
        assert not (fresh / "R-900.yaml").exists()

    def test_missing_rule_did_you_mean(self, tmp_path: Path) -> None:
        store = tmp_path / "store"
        _seed(store)
        with pytest.raises(ValueError, match="did you mean"):
            share_rule("R-002", store=str(store), api=FakeGist())

    def test_collision_aborts_by_default(self, tmp_path: Path) -> None:
        store = tmp_path / "store"
        _seed(store)
        api = FakeGist()
        shared = share_rule("R-001", store=str(store), api=api)
        gist_id = shared["url"].rsplit("/", 1)[-1]
        with pytest.raises(ValueError, match="--force"):
            import_gist(gist_id, store=str(store), api=api)

    def test_as_id_collision_aborts_by_default(self, tmp_path: Path) -> None:
        # #803: importing under an existing rule id must not silently overwrite.
        store = tmp_path / "store"
        _seed(store)  # R-001 exists
        other = tmp_path / "other"
        other.mkdir()
        rule = StandingRule(
            id="R-900",
            when=RuleWhen(trigger="other trigger"),
            do=RuleDo(directive="other fix"),
            confidence=0.9,
            provenance=Provenance(
                source_trajectory="t", extracted_by="m", extract_timestamp="t", extraction_pass=1
            ),
            status="active",
            promoted_at="t",
        )
        dump_rule_to_file(rule, other / "R-900.yaml")
        api = FakeGist()
        shared = share_rule("R-900", store=str(other), api=api)
        gist_id = shared["url"].rsplit("/", 1)[-1]
        with pytest.raises(ValueError, match="--force"):
            import_gist(gist_id, store=str(store), as_id="R-001", api=api)

    def test_no_provenance_option(self, tmp_path: Path) -> None:
        store = tmp_path / "store"
        _seed(store)
        api = FakeGist()
        result = share_rule("R-001", store=str(store), include_provenance=False, api=api)
        assert "PROVENANCE.json" not in result["files"]

    def test_cli_share(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        store = tmp_path / "store"
        _seed(store)
        api = FakeGist()
        monkeypatch.setattr("cauterule.packs.share.GitHubGistApi", lambda: api)
        runner = CliRunner()
        result = runner.invoke(main, ["share", "R-001", "--store", str(store)])
        assert result.exit_code == 0, result.output
        assert "gist.github.com" in result.output

    def test_gist_url_forms_parsed(self) -> None:
        from cauterule.packs.spec import parse_spec

        assert parse_spec("https://gist.github.com/alice/abc123").kind == "gist"
        assert parse_spec("gist:abc123").gist_id == "abc123"

    def test_provenance_envelope_schema(self, tmp_path: Path) -> None:
        import json

        store = tmp_path / "store"
        _seed(store)
        api = FakeGist()
        share_rule("R-001", store=str(store), api=api)
        envelope = json.loads(api.store["abc001"]["PROVENANCE.json"])
        assert envelope["format"] == "cauterule-share/1"
        assert envelope["rule_id"] == "R-001"
