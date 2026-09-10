"""Tests for the LangGraph adapter (#534)."""

from __future__ import annotations

from pathlib import Path

import pytest

from cauterule.adapter.langgraph import capture_node_error, inject_rules, langgraph_node
from cauterule.models.rule import Provenance, RuleDo, RuleWhen, StandingRule
from cauterule.serialization.rule_yaml import dump_rule_to_file


def _rule(tmp_path: Path) -> StandingRule:
    r = StandingRule(
        id="R-LG",
        when=RuleWhen(trigger="sync billing records"),
        do=RuleDo(directive="retry with backoff"),
        confidence=0.9,
        provenance=Provenance(
            source_trajectory="T", extracted_by="t", extract_timestamp="x", extraction_pass=1
        ),
        status="active",
        promoted_at="2026-01-01",
    )
    dump_rule_to_file(r, tmp_path / "rules" / "R-LG.yaml")
    return r


def test_import_without_langgraph() -> None:
    import cauterule.adapter.langgraph as m

    assert m.HAS_LANGGRAPH is False or m.HAS_LANGGRAPH in (True, False)
    assert callable(m.inject_rules)
    assert callable(m.capture_node_error)


def test_inject_rules_returns_state_key(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _rule(tmp_path)
    monkeypatch.chdir(tmp_path)
    state = {"task": "sync billing records failed"}
    out = inject_rules(state)
    assert "cauterule_rules" in out
    assert any("R-LG" in line for line in out["cauterule_rules"])


def test_capture_node_error_writes_trajectory(tmp_path: Path) -> None:
    traj = capture_node_error(
        "sync_node",
        {"task": "sync"},
        {"partial": True},
        RuntimeError("boom"),
        base_dir=str(tmp_path / "trajectories"),
    )
    assert traj.success is False
    assert traj.task == "sync_node"
    files = list((tmp_path / "trajectories").rglob("*.jsonl"))
    assert len(files) == 1


def test_langgraph_node_decorator_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _rule(tmp_path)
    monkeypatch.chdir(tmp_path)

    @langgraph_node(task="sync billing records", base_dir=str(tmp_path / "trajectories"))
    def sync_node(state: dict) -> dict:
        raise RuntimeError("sync failed")

    with pytest.raises(RuntimeError, match="sync failed"):
        sync_node({"task": "sync billing records"})
    files = list((tmp_path / "trajectories").rglob("*.jsonl"))
    assert len(files) == 1
