"""Tests for cost/latency story (#486)."""

from __future__ import annotations

from click.testing import CliRunner

from cauterule.cli.app import main
from cauterule.preflight import cost_per_1k_trajectories, cost_table, estimate_cost


class TestCostModel:
    def test_local_models_free(self) -> None:
        assert cost_per_1k_trajectories("llama-3.2-3b-instruct")["cost_per_1k"] == 0.0
        assert cost_per_1k_trajectories("qwen3-4b-instruct")["cost_per_1k"] == 0.0

    def test_cloud_models_priced(self) -> None:
        assert cost_per_1k_trajectories("gpt-4o-mini")["cost_per_1k"] > 0
        assert cost_per_1k_trajectories("gpt-4o")["cost_per_1k"] > cost_per_1k_trajectories("gpt-4o-mini")["cost_per_1k"]

    def test_tier_assigned(self) -> None:
        assert "local" in cost_per_1k_trajectories("llama-3.2-3b-instruct")["tier"]
        assert "cloud" in cost_per_1k_trajectories("gpt-4o-mini")["tier"]
        assert "flagship" in cost_per_1k_trajectories("gpt-4o")["tier"]

    def test_table_covers_all_models(self) -> None:
        table = cost_table()
        assert len(table) >= 7
        models = [row["model"] for row in table]
        assert "gpt-4o-mini" in models
        assert "llama-3.2-3b-instruct" in models

    def test_estimate_cost_scales(self) -> None:
        cost_1k = estimate_cost(1000, "gpt-4o-mini")
        cost_2k = estimate_cost(2000, "gpt-4o-mini")
        assert cost_2k == round(2 * cost_1k, 2)


class TestPreflightCli:
    def test_cost_table_flag(self) -> None:
        result = CliRunner().invoke(main, ["preflight", "--cost-table"])
        assert result.exit_code == 0, result.output
        assert "gpt-4o-mini" in result.output
        assert "tier=" in result.output
        assert "llama-3.2-3b" in result.output

    def test_max_cost_rejects(self, tmp_path) -> None:
        import json

        corpus = tmp_path / "traj.jsonl"
        for i in range(100):
            corpus.write_text(
                json.dumps({
                    "trajectory_id": f"T-{i}", "timestamp": "2026-01-01T00:00:00Z",
                    "task": "x", "steps": [{"step_number": 1, "tool": "t", "input": "x", "output": "", "error": "e"}],
                    "success": False, "domain": "git", "quality_label": "clear", "tags": [],
                }) + "\n",
                encoding="utf-8",
            )
        result = CliRunner().invoke(
            main,
            ["preflight", "--corpus", str(corpus), "--no-probe", "--max-cost", "0.01"],
        )
        assert result.exit_code != 0
        assert "exceeds" in result.output or "FAIL" in result.output
