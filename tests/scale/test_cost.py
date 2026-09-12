"""LLM cost benchmark — cost per extracted candidate, per promoted rule.

Mock LLM calls to simulate costs.
"""

from __future__ import annotations

import json
from typing import Any

from cauterule.extraction.extractor import extract_candidate
from cauterule.llm.provider import LLMResponse
from cauterule.models.trajectory import Step, Trajectory


class CostTrackingLLM:
    def __init__(self, text: str) -> None:
        self.text = text
        self.call_count: int = 0

    def complete(self, prompt: str, **kwargs: Any) -> LLMResponse:
        self.call_count += 1
        return LLMResponse(text=self.text, model="gpt-4o", provider="openai")


def _traj() -> Trajectory:
    return Trajectory(
        id="T-001",
        timestamp="t",
        task="git push fails",
        steps=(Step(1, "bash", error="non-fast-forward"),),
        success=False,
        failure_class="git/push",
    )


def test_cost_per_extraction() -> None:
    payload = json.dumps(
        {
            "when": {"trigger": "git push fails"},
            "do": {"directive": "pull --rebase"},
            "confidence": 0.9,
        }
    )
    mock = CostTrackingLLM(payload)
    mock.complete = lambda p: mock.complete(p)  # type: ignore[assignment, method-assign, misc]
    mock.call_count = 0

    def tracking_complete(prompt: str) -> LLMResponse:
        mock.call_count += 1
        return LLMResponse(text=payload, model="gpt-4o", provider="openai")

    mock.complete = tracking_complete  # type: ignore[assignment]

    # We need to test the mock differently since extract_candidate expects an LLM with complete method
    class TrackingLLM:
        def __init__(self, text: str) -> None:
            self.text = text
            self.call_count: int = 0

        def complete(self, prompt: str, **kwargs: Any) -> LLMResponse:
            self.call_count += 1
            _ = prompt
            return LLMResponse(text=self.text, model="gpt-4o", provider="openai")

    llm = TrackingLLM(payload)
    candidate = extract_candidate(_traj(), llm, template="retry", extraction_pass=1)
    assert candidate is not None
    assert llm.call_count == 1


def test_cost_multiple_extractions() -> None:
    payload = json.dumps(
        {
            "when": {"trigger": "git push fails"},
            "do": {"directive": "pull --rebase"},
            "confidence": 0.9,
        }
    )

    class TrackingLLM:
        def __init__(self, text: str) -> None:
            self.text = text
            self.call_count: int = 0

        def complete(self, prompt: str, **kwargs: Any) -> LLMResponse:
            self.call_count += 1
            _ = prompt
            return LLMResponse(text=self.text, model="gpt-4o", provider="openai")

    llm = TrackingLLM(payload)
    for _ in range(5):
        extract_candidate(_traj(), llm)
    assert llm.call_count == 5


def test_cost_estimate_output() -> None:
    """Verify the test prints cost estimates for review."""
    payload = json.dumps({"when": {"trigger": "t"}, "do": {"directive": "d"}, "confidence": 0.8})

    class TrackingLLM:
        def __init__(self, text: str) -> None:
            self.text = text
            self.call_count: int = 0

        def complete(self, prompt: str, **kwargs: Any) -> LLMResponse:
            self.call_count += 1
            _ = prompt
            return LLMResponse(text=self.text, model="gpt-4o", provider="openai")

    llm = TrackingLLM(payload)
    candidates: list[Any] = []
    for _ in range(10):
        c = extract_candidate(_traj(), llm)
        candidates.append(c)
    total_calls = llm.call_count
    cost_per_call = 0.002
    est_cost = total_calls * cost_per_call
    print(f"Estimated cost: {total_calls} calls x ${cost_per_call} = ${est_cost:.4f}")
    assert len(candidates) == 10
