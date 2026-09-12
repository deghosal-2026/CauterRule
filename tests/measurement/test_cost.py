"""Tests for cost measurement (§5.4/§7.4, #653/#486)."""

from __future__ import annotations

import pytest

from cauterule.measurement.cost import CostModel, measure_cost, records_from_results


def _rec(
    *,
    status: str = "done",
    llm_requests: int = 2,
    candidates_produced: int = 1,
    promoted: int = 0,
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
) -> dict[str, object]:
    return {
        "status": status,
        "llm_requests": llm_requests,
        "candidates_produced": candidates_produced,
        "promoted": promoted,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
    }


def test_measure_cost_request_based() -> None:
    records = [
        _rec(status="gate_dropped", llm_requests=0, candidates_produced=0),
        _rec(llm_requests=2, candidates_produced=2, promoted=1),
        _rec(llm_requests=2, candidates_produced=1, promoted=0),
        _rec(llm_requests=2, candidates_produced=0, promoted=0),
    ]
    report = measure_cost(records, cost_model=CostModel(cost_per_request_usd=0.01))

    assert report.trajectories == 4
    assert report.llm_requests == 6
    assert report.candidates_produced == 3
    assert report.rules_promoted == 1
    assert report.gate_dropped == 1
    assert report.total_cost_usd == pytest.approx(0.06)
    assert report.cost_per_candidate == pytest.approx(0.06 / 3)
    assert report.cost_per_promoted_rule == pytest.approx(0.06)
    assert report.cost_per_1k_trajectories == pytest.approx(0.06 / 4 * 1000)
    assert report.gate_savings_usd == pytest.approx(0.01)


def test_measure_cost_token_based_wins_over_request() -> None:
    records = [
        _rec(llm_requests=1, candidates_produced=1, prompt_tokens=1_000_000, completion_tokens=0),
    ]
    report = measure_cost(
        records,
        cost_model=CostModel(input_price_per_1k=0.001, output_price_per_1k=0.002),
    )
    # 1,000,000 prompt tokens at $0.001/1k = $1.00
    assert report.total_cost_usd == pytest.approx(1.0)
    assert report.prompt_tokens == 1_000_000


def test_measure_cost_zero_candidates_is_safe() -> None:
    report = measure_cost([_rec(status="gate_dropped", llm_requests=0, candidates_produced=0)])
    assert report.cost_per_candidate == 0.0
    assert report.cost_per_promoted_rule == 0.0
    assert report.total_cost_usd == 0.0


def test_records_from_results_maps_status_and_verdict() -> None:
    results: list[dict[str, object]] = [
        {"status": "gate_dropped"},
        {
            "status": "done",
            "llm_calls_avoided": 0,
            "candidate_count": 2,
            "candidates": [{"verdict": "pass"}, {"verdict": "fail"}],
            "best": {"verdict": "pass"},
        },
    ]
    records = records_from_results(results, extraction_passes=2)
    assert records[0]["llm_requests"] == 0
    assert records[0]["status"] == "gate_dropped"
    assert records[1]["llm_requests"] == 2
    assert records[1]["candidates_produced"] == 2
    assert records[1]["promoted"] == 1
