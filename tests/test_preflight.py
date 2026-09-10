"""Tests for operational preflight checks."""

import json
import tempfile
from pathlib import Path

from cauterule.config import Config, LLMConfig
from cauterule.preflight import check_corpus, check_provider, run_preflight


def test_provider_missing_api_key() -> None:
    cfg = Config(llm=LLMConfig(provider="openai", api_key="", model="gpt-4o"))
    results = check_provider(cfg)
    assert any(not r.passed and "api key" in r.message.lower() for r in results)


def test_provider_probe_failure() -> None:
    cfg = Config(llm=LLMConfig(provider="openai", api_key="sk-test", model="gpt-4o"))

    def failing_probe(_cfg: Config) -> float:
        raise RuntimeError("404 No endpoints found")

    results = check_provider(cfg, probe=failing_probe)
    assert any(not r.passed and "probe failed" in r.message.lower() for r in results)


def test_provider_slow_model() -> None:
    cfg = Config(llm=LLMConfig(provider="openai", api_key="sk-test", model="slow-model"))

    def slow_probe(_cfg: Config) -> float:
        return 45.0

    results = check_provider(cfg, probe=slow_probe)
    assert any(not r.passed and "slow" in r.message.lower() for r in results)


def test_corpus_missing_fields() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "test.jsonl"
        p.write_text(json.dumps({"id": "T-001", "task": "do thing"}) + "\n", encoding="utf-8")
        results = check_corpus(p)
        assert any(not r.passed and "missing fields" in r.message.lower() for r in results)


def test_corpus_missing_success_flagged() -> None:
    # Review: success is REQUIRED_FIELDS — flagged before strict load.
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "test.jsonl"
        p.write_text(
            json.dumps(
                {
                    "trajectory_id": "T-001",
                    "timestamp": "t",
                    "task": "do thing",
                    "steps": [],
                }
            )
            + "\n",
            encoding="utf-8",
        )
        results = check_corpus(p)
        assert any(
            not r.passed and "success" in r.message.lower() for r in results
        )


def test_corpus_empty_file() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "empty.jsonl"
        p.write_text("", encoding="utf-8")
        results = check_corpus(p)
        assert any(not r.passed and "empty" in r.message.lower() for r in results)


def test_corpus_duplicate_ids() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "dup.jsonl"
        traj = {"trajectory_id": "T-001", "timestamp": "t", "task": "do thing", "steps": [], "success": True}
        p.write_text(json.dumps(traj) + "\n" + json.dumps(traj) + "\n", encoding="utf-8")
        results = check_corpus(p)
        assert any(not r.passed and "duplicate" in r.message.lower() for r in results)


def test_run_preflight_cost_estimate() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "test.jsonl"
        traj = {"trajectory_id": "T-001", "timestamp": "t", "task": "do thing", "steps": [], "success": True}
        p.write_text(json.dumps(traj) + "\n", encoding="utf-8")
        cfg = Config(llm=LLMConfig(provider="openai", api_key="sk-test", model="gpt-4o"))
        result = run_preflight(cfg, corpus_path=p, cost_per_request_usd=0.02)
        assert result.cost_estimate_usd == 0.02


def test_run_preflight_aggregates() -> None:
    cfg = Config(llm=LLMConfig(provider="openai", api_key="", model="gpt-4o"))
    result = run_preflight(cfg, corpus_path="/nonexistent/path.jsonl")
    assert result.passed is False
    assert len(result.warnings) > 0
