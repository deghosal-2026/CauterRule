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
        assert any(not r.passed and "success" in r.message.lower() for r in results)


def test_corpus_empty_file() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "empty.jsonl"
        p.write_text("", encoding="utf-8")
        results = check_corpus(p)
        assert any(not r.passed and "empty" in r.message.lower() for r in results)


def test_corpus_duplicate_ids() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "dup.jsonl"
        traj = {
            "trajectory_id": "T-001",
            "timestamp": "t",
            "task": "do thing",
            "steps": [],
            "success": True,
        }
        p.write_text(json.dumps(traj) + "\n" + json.dumps(traj) + "\n", encoding="utf-8")
        results = check_corpus(p)
        assert any(not r.passed and "duplicate" in r.message.lower() for r in results)


def test_run_preflight_cost_estimate() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "test.jsonl"
        traj = {
            "trajectory_id": "T-001",
            "timestamp": "t",
            "task": "do thing",
            "steps": [],
            "success": True,
            "domain": "devops",
            "quality_label": "clear",
            "tags": [],
        }
        p.write_text(json.dumps(traj) + "\n", encoding="utf-8")
        cfg = Config(llm=LLMConfig(provider="openai", api_key="sk-test", model="gpt-4o"))
        result = run_preflight(cfg, corpus_path=p)
        # gpt-4o rate 0.005 * 1 req * (4000/1000 = 4) = 0.02
        assert result.cost_estimate_usd == 0.02, f"got {result.cost_estimate_usd}"


def test_run_preflight_cost_per_request_override() -> None:
    # #678: the runner passes cost_per_request_usd; it must be accepted and
    # applied as a flat $/request override.
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "test.jsonl"
        traj = {
            "trajectory_id": "T-001",
            "timestamp": "t",
            "task": "do thing",
            "steps": [],
            "success": True,
            "domain": "devops",
            "quality_label": "clear",
            "tags": [],
        }
        p.write_text(
            "".join(json.dumps({**traj, "trajectory_id": f"T-{i:03d}"}) + "\n" for i in range(3)),
            encoding="utf-8",
        )
        cfg = Config(llm=LLMConfig(provider="openai", api_key="sk-test", model="gpt-4o"))
        result = run_preflight(cfg, corpus_path=p, cost_per_request_usd=0.25)
        assert result.cost_estimate_usd == 0.75, f"got {result.cost_estimate_usd}"


def test_run_preflight_aggregates() -> None:
    cfg = Config(llm=LLMConfig(provider="openai", api_key="", model="gpt-4o"))
    result = run_preflight(cfg, corpus_path="/nonexistent/path.jsonl")
    assert result.passed is False
    assert len(result.warnings) > 0


def test_estimate_cost_varies_by_model() -> None:
    from cauterule.preflight import estimate_cost

    assert estimate_cost(100, model="gpt-4o") < estimate_cost(100, model="claude-3-opus")


def test_check_output_dir(tmp_path: Path) -> None:
    from cauterule.preflight import check_output_dir

    r = check_output_dir(str(tmp_path / "out"))
    assert r.passed
    assert "ready" in r.message


def test_schema_version_unknown_rejected(tmp_path: Path) -> None:
    from cauterule.preflight import check_corpus

    p = tmp_path / "corpus.jsonl"
    p.write_text(
        json.dumps(
            {
                "trajectory_id": "T-1",
                "timestamp": "t",
                "task": "x",
                "steps": [],
                "success": True,
                "domain": "devops",
                "quality_label": "clear",
                "tags": [],
                "schema_version": "9.9",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    results = check_corpus(p)
    assert any(not r.passed and "9.9" in r.message for r in results)


def test_schema_version_absent_is_ok(tmp_path: Path) -> None:
    from cauterule.preflight import check_corpus

    p = tmp_path / "corpus.jsonl"
    p.write_text(
        json.dumps(
            {
                "trajectory_id": "T-1",
                "timestamp": "t",
                "task": "x",
                "steps": [],
                "success": True,
                "domain": "devops",
                "quality_label": "clear",
                "tags": [],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    results = check_corpus(p)
    # Must not fail on schema_version (absent is OK).
    assert all(r.passed for r in results if "schema" in r.name)
    assert any("absent" in r.message for r in results if "schema" in r.name)


def test_expanded_required_fields_flagged(tmp_path: Path) -> None:
    from cauterule.preflight import check_corpus

    p = tmp_path / "corpus.jsonl"
    p.write_text(
        json.dumps(
            {
                "trajectory_id": "T-1",
                "timestamp": "t",
                "task": "x",
                "steps": [],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    results = check_corpus(p)
    assert any("success" in r.message for r in results)
    assert any("domain" in r.message for r in results)
    assert any("quality_label" in r.message for r in results)
