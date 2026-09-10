"""Tests for supersession chains (#544)."""

from __future__ import annotations

from pathlib import Path

import pytest

from cauterule.lifecycle.supersede import (
    ChainCycleError,
    all_issues,
    chain,
    dangling,
    heads,
    orphan_middles,
    render_chain,
)
from cauterule.models.rule import Provenance, RuleDo, RuleWhen, StandingRule
from cauterule.store.manager import StoreManager
from cauterule.store.validator import validate_store


def _rule(
    rid: str,
    *,
    status: str = "active",
    superseded_by: str | None = None,
    trigger: str = "trigger",
) -> StandingRule:
    return StandingRule(
        id=rid,
        when=RuleWhen(trigger=trigger),
        do=RuleDo(directive="do x"),
        confidence=0.8,
        provenance=Provenance(
            source_trajectory="T",
            extracted_by="test",
            extract_timestamp="2025-01-01T00:00:00",
            extraction_pass=1,
        ),
        status=status,  # type: ignore[arg-type]
        promoted_at="2025-01-02T00:00:00",
        superseded_by=superseded_by,
    )


def test_linear_chain() -> None:
    v1 = _rule("R-1", status="superseded", superseded_by="R-2")
    v2 = _rule("R-2", status="superseded", superseded_by="R-3")
    v3 = _rule("R-3", status="superseded", superseded_by="R-4")
    v4 = _rule("R-4")
    chain_rules = chain("R-4", [v1, v2, v3, v4])
    assert [r.id for r in chain_rules] == ["R-1", "R-2", "R-3", "R-4"]
    assert render_chain(chain_rules) == "R-1 (superseded) → R-2 (superseded) → R-3 (superseded) → R-4 (active)"


def test_chain_from_middle() -> None:
    v1 = _rule("R-1", status="superseded", superseded_by="R-2")
    v2 = _rule("R-2", status="superseded", superseded_by="R-3")
    v3 = _rule("R-3")
    got = chain("R-2", [v1, v2, v3])
    assert [r.id for r in got] == ["R-1", "R-2", "R-3"]


def test_cycle_detected() -> None:
    a = _rule("R-A", status="superseded", superseded_by="R-B")
    b = _rule("R-B", status="superseded", superseded_by="R-A")
    with pytest.raises(ChainCycleError):
        chain("R-A", [a, b])


def test_dangling_detected() -> None:
    a = _rule("R-A", status="superseded", superseded_by="R-GONE")
    issues = dangling([a])
    assert len(issues) == 1
    assert issues[0].kind == "dangling"
    assert "R-GONE" in issues[0].detail


def test_orphan_middles_detected() -> None:
    a = _rule("R-ORPHAN", status="superseded", superseded_by=None)
    issues = orphan_middles([a])
    assert len(issues) == 1
    assert issues[0].kind == "orphan_middle"


def test_heads() -> None:
    v1 = _rule("R-1", status="superseded", superseded_by="R-2")
    v2 = _rule("R-2", status="superseded", superseded_by="R-3")
    v3 = _rule("R-3")
    heads_ = heads([v1, v2, v3])
    # Chain tip is R-3 (nobody supersedes it).
    assert {r.id for r in heads_} == {"R-3"}


def test_all_issues_aggregates() -> None:
    a = _rule("R-A", status="superseded", superseded_by="R-GONE")
    b = _rule("R-ORPHAN", status="superseded", superseded_by=None)
    issues = all_issues([a, b])
    kinds = {i.kind for i in issues}
    assert "dangling" in kinds
    assert "orphan_middle" in kinds


def test_validator_rejects_superseded_without_pointer(tmp_path: Path) -> None:
    import yaml

    base = tmp_path / "rules"
    base.mkdir(parents=True)
    data = _rule("R-BADSUP", status="superseded", superseded_by=None).to_dict()
    data["status"] = "superseded"
    data.pop("superseded_by", None)
    (base / "R-BADSUP.yaml").write_text(
        yaml.safe_dump(data, sort_keys=False), encoding="utf-8"
    )
    warnings = validate_store(str(base))
    assert any("superseded requires superseded_by" in w for w in warnings)


def test_validator_rejects_retired_with_pointer(tmp_path: Path) -> None:
    import yaml

    base = tmp_path / "rules"
    base.mkdir(parents=True)
    data = _rule("R-BADRET", status="retired", superseded_by="R-NEXT").to_dict()
    data["status"] = "retired"
    data["superseded_by"] = "R-NEXT"
    (base / "R-BADRET.yaml").write_text(
        yaml.safe_dump(data, sort_keys=False), encoding="utf-8"
    )
    warnings = validate_store(str(base))
    assert any("retired rules must not carry superseded_by" in w for w in warnings)


def test_health_reports_supersession_issues(tmp_path: Path) -> None:
    from cauterule.store.health import health_report

    store = StoreManager(str(tmp_path / "rules"))
    store.add_rule(_rule("R-A", status="superseded", superseded_by="R-GONE"))
    report = health_report(str(tmp_path / "rules"))
    assert any("dangling" in i for i in report["supersession_issues"])


def test_show_history_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from click.testing import CliRunner

    from cauterule.cli.show import show

    runner = CliRunner()
    store = StoreManager(str(tmp_path / "rules"))
    store.add_rule(
        _rule("R-X1", status="superseded", superseded_by="R-X2"),
    )
    store.add_rule(_rule("R-X2", status="superseded", superseded_by="R-X3"))
    store.add_rule(_rule("R-X3"))
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(show, ["--history", "R-X3"])
    assert result.exit_code == 0
    assert "Supersession chain for R-X3" in result.output
    assert "R-X1" in result.output and "R-X3" in result.output
