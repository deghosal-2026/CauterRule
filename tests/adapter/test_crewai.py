"""Tests for the CrewAI adapter (#536)."""

from __future__ import annotations

from pathlib import Path

import pytest

from cauterule.adapter.crewai import CrewaiTracer, inject_crew_rules
from cauterule.models.rule import Provenance, RuleDo, RuleWhen, StandingRule


def test_import_without_crewai() -> None:
    import cauterule.adapter.crewai as m

    assert isinstance(m.HAS_CREWAI, bool)
    assert callable(m.inject_crew_rules)


def _rule() -> StandingRule:
    return StandingRule(
        id="R-CR",
        when=RuleWhen(trigger="reconcile invoices"),
        do=RuleDo(directive="flag mismatch"),
        confidence=0.9,
        provenance=Provenance(
            source_trajectory="T", extracted_by="t", extract_timestamp="x", extraction_pass=1
        ),
        status="active",
        promoted_at="2026-01-01",
    )


def test_inject_crew_rules_block() -> None:
    block = inject_crew_rules("reconcile invoices failed", rules=[_rule()])
    assert "R-CR" in block
    assert block.startswith("Standing rules")


def test_inject_crew_rules_no_match() -> None:
    assert inject_crew_rules("unrelated task", rules=[_rule()]) == ""


def test_tracer_task_success(tmp_path: Path) -> None:
    tracer = CrewaiTracer(task_desc="reconcile", base_dir=str(tmp_path / "trajectories"))
    with tracer.task("reconcile invoices", agent_role="accountant"):
        tracer.record_tool("ledger_query", input_="SELECT", output="2 rows")
    files = list((tmp_path / "trajectories").rglob("*.jsonl"))
    assert len(files) == 1
    assert "success" in files[0].name


def test_tracer_task_failure_captures(tmp_path: Path) -> None:
    tracer = CrewaiTracer(task_desc="reconcile", base_dir=str(tmp_path / "trajectories"))
    with pytest.raises(RuntimeError, match="boom"), tracer.task("reconcile invoices"):
        raise RuntimeError("boom")
    files = list((tmp_path / "trajectories").rglob("*.jsonl"))
    assert len(files) == 1
    assert "failure" in files[0].name
    assert "boom" in files[0].read_text()
