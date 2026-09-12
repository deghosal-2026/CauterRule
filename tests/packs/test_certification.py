"""Tests for the pack certification module."""

from __future__ import annotations

from cauterule.packs.certification import certify_pack
from cauterule.packs.format import PackManifest


class TestCertifyPack:
    def test_passes_valid_pack(self) -> None:
        pack = {
            "manifest": {
                "name": "pack-git",
                "version": "1.0.0",
                "description": "Git rules",
                "author": "Cauterule",
                "rules": ["R-101"],
            },
            "rules": [{"id": "R-101", "title": "Use git commit"}],
        }
        result = certify_pack(pack)
        assert result["passed"] is True
        assert all(c["status"] == "pass" for c in result["checks"])

    def test_fails_on_empty_rules(self) -> None:
        pack = {
            "manifest": {
                "name": "empty",
                "version": "1.0.0",
                "description": "Empty pack",
                "author": "Test",
                "rules": [],
            },
            "rules": [],
        }
        result = certify_pack(pack)
        assert result["passed"] is False
        assert any(c["name"] == "replay" and c["status"] == "fail" for c in result["checks"])

    def test_fails_on_missing_rule_ids(self) -> None:
        pack = {
            "manifest": {
                "name": "bad",
                "version": "1.0.0",
                "description": "Bad pack",
                "author": "Test",
                "rules": ["R-001", "R-002"],
            },
            "rules": [{"id": "R-001"}, {"title": "no id here"}],
        }
        result = certify_pack(pack)
        assert result["passed"] is False
        assert any(c["name"] == "provenance" and c["status"] == "fail" for c in result["checks"])

    def test_fails_on_invalid_manifest(self) -> None:
        pack = {
            "manifest": {
                "name": "",
                "version": "",
                "description": "",
                "author": "",
            },
            "rules": [{"id": "R-001"}],
        }
        result = certify_pack(pack)
        assert result["passed"] is False
        assert any(c["name"] == "safety" and c["status"] == "fail" for c in result["checks"])

    def test_accepts_packmanifest_object(self) -> None:
        manifest = PackManifest(
            name="obj", version="1", description="d", author="a", rules=("R-1",)
        )
        pack = {"manifest": manifest, "rules": [{"id": "R-1"}]}
        result = certify_pack(pack)
        assert result["passed"] is True

    def test_all_checks_present(self) -> None:
        pack = {
            "manifest": {
                "name": "n",
                "version": "1",
                "description": "d",
                "author": "a",
                "rules": ["R-1"],
            },
            "rules": [{"id": "R-1"}],
        }
        result = certify_pack(pack)
        names = {c["name"] for c in result["checks"]}
        assert names == {"safety", "replay", "provenance"}

    def test_replay_failure_message(self) -> None:
        pack = {
            "manifest": {
                "name": "n",
                "version": "1",
                "description": "d",
                "author": "a",
            },
            "rules": [],
        }
        result = certify_pack(pack)
        replay_check = next(c for c in result["checks"] if c["name"] == "replay")
        assert replay_check["status"] == "fail"
        assert "no rules" in replay_check["message"].lower()
