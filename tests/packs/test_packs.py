"""Comprehensive tests for the rule packs module."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from cauterule.models.rule import Provenance, RuleDo, RuleWhen, StandingRule
from cauterule.packs.format import PackManifest, create_manifest, validate_manifest
from cauterule.packs.loader import load_pack
from cauterule.packs.manager import list_packs, pack_info
from cauterule.packs.readonly import check_readonly

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def valid_manifest() -> PackManifest:
    return PackManifest(
        name="pack-git",
        version="1.0.0",
        description="Git rules",
        author="Cauterule",
        rules=("R-101", "R-102"),
    )


@pytest.fixture
def pack_rules_dir(tmp_path: Path) -> Path:
    """Create a temporary ``rules/packs/pack-git/`` with manifest + 2 rules."""
    pack_dir = tmp_path / "rules" / "packs" / "pack-git"
    pack_dir.mkdir(parents=True)

    manifest = {
        "name": "pack-git",
        "version": "1.0.0",
        "description": "Pre-built Git rules",
        "author": "Cauterule",
        "rules": ["R-101", "R-102"],
    }
    (pack_dir / "manifest.yaml").write_text(
        yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8"
    )

    for rule_id in ("R-101", "R-102"):
        rule = StandingRule(
            id=rule_id,
            when=RuleWhen(trigger=f"trigger-{rule_id}"),
            do=RuleDo(directive=f"do-{rule_id}"),
            confidence=0.9,
            provenance=Provenance(
                source_trajectory="pack-builtin",
                extracted_by="pack-author",
                extract_timestamp="2026-09-01T00:00:00Z",
                extraction_pass=1,
            ),
            status="active",
            promoted_at="2026-09-01T00:00:00Z",
            pack="pack-git",
        )
        (pack_dir / f"{rule_id}.yaml").write_text(
            yaml.safe_dump(rule.to_dict(), sort_keys=False), encoding="utf-8"
        )

    return tmp_path


@pytest.fixture
def readonly_pack_rule() -> StandingRule:
    return StandingRule(
        id="R-999",
        when=RuleWhen(trigger="t"),
        do=RuleDo(directive="d"),
        confidence=0.5,
        provenance=Provenance(
            source_trajectory="a.jsonl",
            extracted_by="m",
            extract_timestamp="t",
            extraction_pass=1,
        ),
        status="active",
        promoted_at="2026-09-01T00:00:00Z",
        pack="pack-git",
    )


@pytest.fixture
def normal_rule() -> StandingRule:
    return StandingRule(
        id="R-001",
        when=RuleWhen(trigger="t"),
        do=RuleDo(directive="d"),
        confidence=0.5,
        provenance=Provenance(
            source_trajectory="a.jsonl",
            extracted_by="m",
            extract_timestamp="t",
            extraction_pass=1,
        ),
        status="active",
        promoted_at="2026-09-01T00:00:00Z",
    )


# ---------------------------------------------------------------------------
# format.py — PackManifest
# ---------------------------------------------------------------------------


class TestPackManifest:
    def test_create_via_dataclass(self) -> None:
        m = PackManifest(name="x", version="1", description="d", author="a", rules=("R1",))
        assert m.name == "x"
        assert m.rules == ("R1",)

    def test_create_via_create_manifest(self) -> None:
        m = create_manifest(name="x", version="1", description="d", author="a", rules=("R1",))
        assert isinstance(m, PackManifest)
        assert m.name == "x"

    def test_empty_rules_default(self) -> None:
        m = PackManifest(name="x", version="1", description="d", author="a")
        assert m.rules == ()

    def test_to_dict(self) -> None:
        m = PackManifest(name="n", version="v", description="d", author="a", rules=("R1", "R2"))
        d = m.to_dict()
        assert d["name"] == "n"
        assert d["rules"] == ["R1", "R2"]

    def test_from_dict(self) -> None:
        data = {
            "name": "n",
            "version": "v",
            "description": "d",
            "author": "a",
            "rules": ["R1"],
        }
        m = PackManifest.from_dict(data)
        assert m.name == "n"
        assert m.rules == ("R1",)

    def test_from_dict_missing_keys(self) -> None:
        m = PackManifest.from_dict({})
        assert m.name == ""


# ---------------------------------------------------------------------------
# format.py — validate_manifest
# ---------------------------------------------------------------------------


class TestValidateManifest:
    def test_valid_manifest(self, valid_manifest: PackManifest) -> None:
        errors = validate_manifest(valid_manifest)
        assert errors == []

    def test_blank_name(self) -> None:
        m = PackManifest(name="", version="1", description="d", author="a", rules=("R1",))
        errors = validate_manifest(m)
        assert "name" in errors[0]

    def test_blank_version(self) -> None:
        m = PackManifest(name="n", version="", description="d", author="a", rules=("R1",))
        errors = validate_manifest(m)
        assert "version" in errors[0]

    def test_blank_description(self) -> None:
        m = PackManifest(name="n", version="1", description="", author="a", rules=("R1",))
        errors = validate_manifest(m)
        assert "description" in errors[0]

    def test_blank_author(self) -> None:
        m = PackManifest(name="n", version="1", description="d", author="", rules=("R1",))
        errors = validate_manifest(m)
        assert "author" in errors[0]

    def test_empty_rules(self) -> None:
        m = PackManifest(name="n", version="1", description="d", author="a")
        errors = validate_manifest(m)
        assert "rules" in errors[0]

    def test_blank_rule_in_list(self) -> None:
        m = PackManifest(name="n", version="1", description="d", author="a", rules=("R1", ""))
        errors = validate_manifest(m)
        assert any("rules[1]" in e for e in errors)

    def test_multiple_errors(self) -> None:
        m = PackManifest(name="", version="", description="", author="")
        errors = validate_manifest(m)
        assert len(errors) >= 4


# ---------------------------------------------------------------------------
# loader.py — load_pack
# ---------------------------------------------------------------------------


class TestLoadPack:
    def test_loads_manifest_and_rules(self, pack_rules_dir: Path) -> None:
        manifest, rules = load_pack("pack-git", base_dir=str(pack_rules_dir / "rules"))
        assert manifest.name == "pack-git"
        assert len(rules) == 2
        assert rules[0].pack == "pack-git"

    def test_raises_if_pack_dir_missing(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError, match="Pack directory"):
            load_pack("nonexistent", base_dir=str(tmp_path / "rules"))

    def test_raises_if_manifest_missing(self, tmp_path: Path) -> None:
        (tmp_path / "rules" / "packs" / "empty").mkdir(parents=True)
        with pytest.raises(FileNotFoundError, match="Pack manifest"):
            load_pack("empty", base_dir=str(tmp_path / "rules"))

    def test_raises_if_manifest_not_mapping(self, pack_rules_dir: Path) -> None:
        bad = pack_rules_dir / "rules" / "packs" / "bad"
        bad.mkdir(parents=True)
        (bad / "manifest.yaml").write_text("42", encoding="utf-8")
        with pytest.raises(ValueError, match="must be a mapping"):
            load_pack("bad", base_dir=str(pack_rules_dir / "rules"))

    def test_raises_if_rule_file_missing(self, pack_rules_dir: Path) -> None:
        manifest_path = pack_rules_dir / "rules" / "packs" / "partial" / "manifest.yaml"
        manifest_path.parent.mkdir(parents=True)
        manifest = {
            "name": "p",
            "version": "1",
            "description": "d",
            "author": "a",
            "rules": ["MISSING"],
        }
        manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
        with pytest.raises(ValueError, match="missing rule"):
            load_pack("partial", base_dir=str(pack_rules_dir / "rules"))

    def test_rejects_traversal_pack_name(self, tmp_path: Path) -> None:
        # Review: pack name traversal raises before any I/O.
        with pytest.raises(ValueError, match="invalid rule_id"):
            load_pack("../../evil", base_dir=str(tmp_path / "rules"))
        with pytest.raises(ValueError, match="invalid rule_id"):
            pack_info("/etc/passwd", base_dir=str(tmp_path / "rules"))

    def test_rejects_traversal_rule_id_in_manifest(self, tmp_path: Path) -> None:
        # Review: manifest-listed rule ids are validated identically.
        pack_dir = tmp_path / "rules" / "packs" / "evil"
        pack_dir.mkdir(parents=True)
        manifest = {
            "name": "e",
            "version": "1",
            "description": "d",
            "author": "a",
            "rules": ["../escape"],
        }
        (pack_dir / "manifest.yaml").write_text(yaml.safe_dump(manifest), encoding="utf-8")
        with pytest.raises(ValueError, match="invalid rule_id"):
            load_pack("evil", base_dir=str(tmp_path / "rules"))


# ---------------------------------------------------------------------------
# manager.py — list_packs & pack_info
# ---------------------------------------------------------------------------


class TestManager:
    def test_list_packs_returns_names(self, pack_rules_dir: Path) -> None:
        names = list_packs(base_dir=str(pack_rules_dir / "rules"))
        assert "pack-git" in names

    def test_list_packs_empty_when_no_dir(self, tmp_path: Path) -> None:
        assert list_packs(base_dir=str(tmp_path / "nonexistent")) == []

    def test_pack_info_returns_dict(self, pack_rules_dir: Path) -> None:
        info = pack_info("pack-git", base_dir=str(pack_rules_dir / "rules"))
        assert info["name"] == "pack-git"
        assert info["rule_count"] == 2
        assert "version" in info
        assert "description" in info
        assert "author" in info

    def test_pack_info_raises_if_missing(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError, match="Pack manifest"):
            pack_info("nowhere", base_dir=str(tmp_path / "rules"))


# ---------------------------------------------------------------------------
# readonly.py — check_readonly
# ---------------------------------------------------------------------------


class TestReadonly:
    def test_pack_rule_is_readonly(
        self, pack_rules_dir: Path, readonly_pack_rule: StandingRule
    ) -> None:
        assert check_readonly(readonly_pack_rule, base_dir=str(pack_rules_dir / "rules")) is True

    def test_normal_rule_not_readonly(self, normal_rule: StandingRule) -> None:
        assert check_readonly(normal_rule) is False

    def test_pack_rule_without_pack_dir_is_not_readonly(
        self, tmp_path: Path, readonly_pack_rule: StandingRule
    ) -> None:
        assert check_readonly(readonly_pack_rule, base_dir=str(tmp_path / "rules")) is False

    def test_none_pack_field_not_readonly(self, normal_rule: StandingRule) -> None:
        normal_rule = StandingRule(
            id="R-001",
            when=RuleWhen(trigger="t"),
            do=RuleDo(directive="d"),
            confidence=0.5,
            provenance=Provenance(
                source_trajectory="a.jsonl",
                extracted_by="m",
                extract_timestamp="t",
                extraction_pass=1,
            ),
            status="active",
            promoted_at="2026-09-01T00:00:00Z",
            pack=None,
        )
        assert check_readonly(normal_rule) is False

    def test_hostile_pack_id_returns_false(self, tmp_path: Path, normal_rule: StandingRule) -> None:
        # Review: crafted rule.pack must not raise or escape.
        import dataclasses

        hostile = dataclasses.replace(normal_rule, pack="../../evil")
        assert check_readonly(hostile, base_dir=str(tmp_path / "rules")) is False


# ---------------------------------------------------------------------------
# Integration — round-trip with real pack-git
# ---------------------------------------------------------------------------


class TestIntegration:
    def test_load_real_pack_git(self) -> None:
        """Load the actual pack-git from the repository."""
        repo_root = Path(__file__).resolve().parent.parent.parent
        manifest, rules = load_pack("pack-git", base_dir=str(repo_root / "rules"))
        assert manifest.name == "pack-git"
        assert len(rules) == 10
        ids = {r.id for r in rules}
        assert ids == {f"R-{i}" for i in range(101, 111)}
        for r in rules:
            assert r.pack == "pack-git"

    def test_list_packs_finds_pack_git(self) -> None:
        repo_root = Path(__file__).resolve().parent.parent.parent
        names = list_packs(base_dir=str(repo_root / "rules"))
        assert "pack-git" in names

    def test_readonly_for_pack_git_rules(self) -> None:
        repo_root = Path(__file__).resolve().parent.parent.parent
        _, rules = load_pack("pack-git", base_dir=str(repo_root / "rules"))
        for r in rules:
            assert check_readonly(r, base_dir=str(repo_root / "rules")) is True
