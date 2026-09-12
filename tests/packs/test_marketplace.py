"""Tests for pack docs + marketplace stub (#560)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from cauterule.cli.app import main
from cauterule.packs.format import PackManifest
from cauterule.packs.publish import _reject_service_owned_fields, lint_readme


class TestMarketplace:
    def test_round_trip(self) -> None:
        manifest = PackManifest.from_dict(
            {
                "name": "p",
                "version": "1.0.0",
                "description": "d",
                "author": "a",
                "rules": ["R-1"],
                "marketplace": {"categories": ["docker"], "keywords": ["compose"]},
            }
        )
        assert manifest.to_dict()["marketplace"]["categories"] == ["docker"]

    def test_rejects_hand_set_rating(self) -> None:
        manifest = PackManifest.from_dict(
            {
                "name": "p",
                "version": "1.0.0",
                "description": "d",
                "author": "a",
                "rules": ["R-1"],
                "marketplace": {"rating": 5, "downloads": 100},
            }
        )
        with pytest.raises(ValueError, match="service-owned"):
            _reject_service_owned_fields(manifest)

    def test_allows_preview_fields(self, tmp_path: Path) -> None:
        from cauterule.packs.publish import publish_pack
        from tests.packs.test_publish import FakeApi

        d = tmp_path / "p"
        d.mkdir()
        (d / "pack.yaml").write_text(
            yaml.safe_dump(
                {
                    "name": "p",
                    "version": "1.0.0",
                    "description": "d",
                    "author": "a",
                    "rules": ["R-1"],
                    "marketplace": {"categories": ["docker"]},
                }
            ),
            encoding="utf-8",
        )
        (d / "R-1.yaml").write_text("id: R-1\n", encoding="utf-8")
        (d / "README.md").write_text(
            "# p\n\n## Symptoms\n\n## Rules\n\n## Install\n\n## Certification\n",
            encoding="utf-8",
        )
        result = publish_pack(str(d), repo="acme/packs", dry_run=True, api=FakeApi())
        assert result["dry_run"] is True

    def test_readme_lint_warns(self, tmp_path: Path) -> None:
        assert lint_readme(tmp_path) == ["README.md missing"]
        (tmp_path / "README.md").write_text("# p\n", encoding="utf-8")
        warnings = lint_readme(tmp_path)
        assert any("Symptoms" in w for w in warnings)

    def test_official_pack_readmes_pass_lint(self) -> None:
        for pack in ("pack-docker", "pack-deploy", "pack-testing", "pack-python"):
            assert lint_readme(Path(f"rules/packs/{pack}")) == [], pack

    def test_info_json(self) -> None:
        import json

        runner = CliRunner()
        result = runner.invoke(main, ["pack", "info", "pack-docker", "--json"])
        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)
        assert payload["name"] == "pack-docker"
        assert payload["rule_count"] == 10
