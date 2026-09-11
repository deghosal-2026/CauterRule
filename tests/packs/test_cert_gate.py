"""Tests for pack certification + safety-score gating (#481)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from cauterule.cli.app import main
from cauterule.config import load_config
from cauterule.packs.install import install_pack
from cauterule.packs.manager import pack_info
from cauterule.packs.safety import score_pack_safety, score_rule_safety


def _pack_with_rules(tmp_path: Path, rules: list[dict[str, str]]) -> Path:
    src = tmp_path / "src-pack"
    src.mkdir(parents=True)
    (src / "pack.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "pack-risky",
                "version": "1.0.0",
                "description": "d",
                "author": "t",
                "rules": [r["id"] for r in rules],
            }
        ),
        encoding="utf-8",
    )
    for rule in rules:
        (src / f"{rule['id']}.yaml").write_text(
            yaml.safe_dump(
                {
                    "id": rule["id"],
                    "when": {"trigger": rule["trigger"]},
                    "do": {"directive": rule["directive"]},
                }
            ),
            encoding="utf-8",
        )
    return src


SAFE_RULE = {"id": "R-001", "trigger": "git push rejected non-fast-forward", "directive": "run git pull --rebase"}
RISKY_RULE = {"id": "R-666", "trigger": "error", "directive": "run rm -rf /tmp/cache to clean"}


class TestSafetyScoring:
    def test_safe_rule_scores_100(self) -> None:
        assert score_rule_safety("R-1", SAFE_RULE["trigger"], SAFE_RULE["directive"])["score"] == 100

    def test_unsafe_and_broad_penalties(self) -> None:
        result = score_rule_safety("R-x", RISKY_RULE["trigger"], RISKY_RULE["directive"])
        assert result["score"] < 70
        assert any("unsafe" in reason for reason in result["reasons"])
        assert any("broad" in reason for reason in result["reasons"])

    def test_pack_score_averages(self) -> None:
        report = score_pack_safety(
            [
                {"id": "R-1", "trigger": SAFE_RULE["trigger"], "directive": SAFE_RULE["directive"]},
                {"id": "R-2", "trigger": RISKY_RULE["trigger"], "directive": RISKY_RULE["directive"]},
            ]
        )
        assert 0 < report["score"] < 100
        assert len(report["drags"]) == 1


class TestThresholdConfig:
    def test_default_threshold(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        assert load_config().packs.min_safety_score == 70

    def test_toml_threshold(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        (tmp_path / "cauterule.toml").write_text("[packs]\nmin_safety_score = 85\n")
        monkeypatch.chdir(tmp_path)
        assert load_config().packs.min_safety_score == 85

    def test_toml_rejects_out_of_range(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        (tmp_path / "cauterule.toml").write_text("[packs]\nmin_safety_score = 101\n")
        monkeypatch.chdir(tmp_path)
        with pytest.raises(ValueError, match="0-100"):
            load_config()

    def test_env_override(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("CAUTERULE_PACKS_MIN_SAFETY_SCORE", "90")
        assert load_config().packs.min_safety_score == 90


class TestInstallGate:
    def test_safe_pack_installs(self, tmp_path: Path) -> None:
        src = _pack_with_rules(tmp_path, [SAFE_RULE])
        summary = install_pack(str(src), store=str(tmp_path / "store"))
        assert summary["safety"]["score"] == 100

    def test_risky_pack_blocked(self, tmp_path: Path) -> None:
        src = _pack_with_rules(tmp_path, [RISKY_RULE])
        with pytest.raises(ValueError, match="safety score"):
            install_pack(str(src), store=str(tmp_path / "store"))

    def test_cli_override_allows(self, tmp_path: Path) -> None:
        src = _pack_with_rules(tmp_path, [RISKY_RULE])
        summary = install_pack(str(src), store=str(tmp_path / "store"), min_safety_score=0)
        assert summary["safety"]["score"] < 70

    def test_skip_cert_skips_safety_gate(self, tmp_path: Path) -> None:
        src = _pack_with_rules(tmp_path, [RISKY_RULE])
        summary = install_pack(str(src), store=str(tmp_path / "store"), skip_cert=True)
        assert summary["cert"]["skipped"] is True

    def test_pack_info_shows_cert_and_safety(self, tmp_path: Path) -> None:
        src = _pack_with_rules(tmp_path, [SAFE_RULE])
        install_pack(str(src), store=str(tmp_path / "store"))
        info = pack_info("pack-risky", base_dir=str(tmp_path / "store"))
        assert info["cert"]["passed"] is True
        assert info["safety"]["score"] == 100

    def test_cli_info_output(self, tmp_path: Path) -> None:
        src = _pack_with_rules(tmp_path, [SAFE_RULE])
        store = tmp_path / "store"
        install_pack(str(src), store=str(store))
        runner = CliRunner()
        result = runner.invoke(main, ["pack", "info", "pack-risky", "--store", str(store)])
        assert result.exit_code == 0, result.output
        assert "Cert: passed" in result.output
        assert "Safety score: 100" in result.output


class TestPublishGate:
    def test_publish_blocks_risky(self, tmp_path: Path) -> None:
        from tests.packs.test_publish import FakeApi

        src = _pack_with_rules(tmp_path, [RISKY_RULE])
        (src / "pack.yaml").write_text(
            yaml.safe_dump(
                {
                    "name": "pack-risky",
                    "version": "1.0.0",
                    "description": "d",
                    "author": "t",
                    "rules": ["R-666"],
                }
            ),
            encoding="utf-8",
        )
        from cauterule.packs.publish import publish_pack

        with pytest.raises(ValueError, match="safety score"):
            publish_pack(str(src), repo="acme/packs", api=FakeApi())
