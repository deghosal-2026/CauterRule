"""Tests for the PydanticAI adapter (#537)."""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from cauterule.adapter.pydanticai import inject_system_rules, watch_run
from cauterule.models.rule import Provenance, RuleDo, RuleWhen, StandingRule


def test_import_without_pydantic_ai() -> None:
    import cauterule.adapter.pydanticai as m

    assert isinstance(m.HAS_PYDANTIC_AI, bool)
    assert callable(m.inject_system_rules)


def _rule() -> StandingRule:
    return StandingRule(
        id="R-PD",
        when=RuleWhen(trigger="answer billing question"),
        do=RuleDo(directive="clarify line items"),
        confidence=0.9,
        provenance=Provenance(
            source_trajectory="T", extracted_by="t", extract_timestamp="x", extraction_pass=1
        ),
        status="active",
        promoted_at="2026-01-01",
    )


def test_inject_system_rules_block() -> None:
    block = inject_system_rules("answer billing question", rules=[_rule()])
    assert "R-PD" in block
    assert block.startswith("Standing rules")


def test_inject_system_rules_empty_on_no_match() -> None:
    assert inject_system_rules("unrelated", rules=[_rule()]) == ""


def test_watch_run_async_success(tmp_path: Path) -> None:
    @watch_run(task="billing", base_dir=str(tmp_path / "trajectories"))
    async def run(prompt: str) -> str:
        return "answered"

    assert asyncio.run(run("hi")) == "answered"
    files = list((tmp_path / "trajectories").rglob("*.jsonl"))
    assert len(files) == 1
    assert "success" in files[0].name


def test_watch_run_async_failure_re_raises_and_captures(tmp_path: Path) -> None:
    @watch_run(task="billing", base_dir=str(tmp_path / "trajectories"))
    async def run(prompt: str) -> str:
        raise RuntimeError("model error")

    with pytest.raises(RuntimeError, match="model error"):
        asyncio.run(run("hi"))
    files = list((tmp_path / "trajectories").rglob("*.jsonl"))
    assert len(files) == 1
    assert "failure" in files[0].name
    assert "model error" in files[0].read_text()


def test_watch_run_sync_fallback(tmp_path: Path) -> None:
    @watch_run(task="billing", base_dir=str(tmp_path / "trajectories"))
    def run_sync(prompt: str) -> str:
        return "ok"

    assert run_sync("hi") == "ok"
    files = list((tmp_path / "trajectories").rglob("*.jsonl"))
    assert len(files) == 1


def test_watch_run_capture_success_false(tmp_path: Path) -> None:
    @watch_run(task="billing", base_dir=str(tmp_path / "trajectories"), capture_success=False)
    async def run(prompt: str) -> str:
        return "ok"

    assert asyncio.run(run("hi")) == "ok"
    assert list((tmp_path / "trajectories").rglob("*.jsonl")) == []
