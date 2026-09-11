"""Official packs gate: loader + cert + replay + dedupe for all M5 packs."""

from __future__ import annotations

import re
from pathlib import Path

from click.testing import CliRunner

from cauterule.cli.app import main
from cauterule.packs.certification import certify_pack
from cauterule.packs.deps import read_lockfile
from cauterule.packs.install import _rule_signal, install_pack
from cauterule.packs.loader import load_pack
from cauterule.packs.manager import list_packs
from cauterule.packs.safety import score_pack_safety

PACKS = ["pack-git", "pack-docker", "pack-deploy", "pack-testing", "pack-python"]


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z]{3,}", text.lower()))


class TestOfficialPacks:
    def test_all_packs_discoverable(self) -> None:
        names = list_packs(base_dir="rules")
        for pack in PACKS:
            assert pack in names

    def test_load_cert_safety(self) -> None:
        for pack in PACKS:
            manifest, rules = load_pack(pack, base_dir="rules")
            assert len(rules) >= 10, pack
            cert = certify_pack({"manifest": manifest, "rules": [{"id": r.id} for r in rules]})
            assert cert["passed"], (pack, cert)
            signals = [_rule_signal(p) for p in sorted(Path(f"rules/packs/{pack}").glob("R-*.yaml"))]
            safety = score_pack_safety(signals)
            assert safety["score"] >= 70, (pack, safety)

    def test_replay_green(self) -> None:
        runner = CliRunner()
        for pack in PACKS[1:]:  # pack-git ships no replay fixtures
            result = runner.invoke(main, ["test", "--pack", pack])
            assert result.exit_code == 0, f"{pack}: {result.output}"
            assert "10/10 rules green" in result.output

    def test_cross_pack_dedupe(self) -> None:
        triggers: dict[str, list[tuple[str, set[str]]]] = {}
        for pack in PACKS:
            _, rules = load_pack(pack, base_dir="rules")
            triggers[pack] = [(r.id, _tokens(r.when.trigger)) for r in rules]
        names = list(triggers)
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                for a_id, a in triggers[names[i]]:
                    for b_id, b in triggers[names[j]]:
                        similarity = len(a & b) / max(len(a | b), 1)
                        assert similarity < 0.6, (names[i], a_id, names[j], b_id)

    def test_deploy_dep_and_lockfile(self, tmp_path: Path) -> None:
        store = tmp_path / "store"
        docker = install_pack("rules/packs/pack-docker", store=str(store))
        assert docker["name"] == "pack-docker"
        deploy = install_pack("rules/packs/pack-deploy", store=str(store))
        assert deploy["dep_notes"] == []
        assert read_lockfile(str(store))["pack-deploy"] == "0.1.0"

    def test_deploy_missing_dep_warns(self, tmp_path: Path) -> None:
        store = tmp_path / "store"
        summary = install_pack("rules/packs/pack-deploy", store=str(store))
        assert any("pack-docker" in note for note in summary["dep_notes"])

    def test_match_e2e_python_pack(self, tmp_path: Path) -> None:
        from cauterule.models.candidate import CandidateRule
        from cauterule.replay.matcher import match_score
        from cauterule.serialization.trajectory_jsonl import load_trajectories

        store = tmp_path / "store"
        install_pack("rules/packs/pack-python", store=str(store))
        _, rules = load_pack("pack-python", base_dir=str(store))
        target = next(r for r in rules if r.id == "R-PY-001")
        cand = CandidateRule(when=target.when, do=target.do, confidence=target.confidence)
        trajs = list(
            load_trajectories(store / "packs" / "pack-python" / "tests" / "replay_pack-python.jsonl")
        )
        held_out = [t for t in trajs if "wrong interpreter" in (t.task + (t.steps[0].error or ""))]
        assert held_out, "held-out ModuleNotFoundError trajectory missing"
        assert max(match_score(cand, t) for t in held_out) == 1.0
