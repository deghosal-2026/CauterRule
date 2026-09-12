"""Extractor stability test — repeat extraction on same trajectory, bounded variance."""

from __future__ import annotations

import json
import statistics
from typing import Any

from cauterule.extraction.extractor import extract_candidate
from cauterule.llm.provider import LLMResponse
from cauterule.models.trajectory import Step, Trajectory


class DeterministicLLM:
    def __init__(self, text: str) -> None:
        self.text = text

    def complete(self, prompt: str, **kwargs: Any) -> LLMResponse:
        _ = prompt
        return LLMResponse(text=self.text, model="fake", provider="fake")


def _traj() -> Trajectory:
    return Trajectory(
        id="T-001",
        timestamp="t",
        task="git push fails with non-fast-forward",
        steps=(Step(1, "bash", error="non-fast-forward"),),
        success=False,
        failure_class="git/push",
    )


def test_stability_identical_results() -> None:
    payload = json.dumps(
        {
            "when": {"trigger": "git push fails", "context": ["shared branch"]},
            "do": {"directive": "pull --rebase first", "because": "remote ahead"},
            "confidence": 0.9,
            "reasoning": "remote has commits we don't",
            "template": "retry",
        }
    )
    llm = DeterministicLLM(payload)
    results = [extract_candidate(_traj(), llm, template="retry", extraction_pass=1) for _ in range(5)]
    triggers = [r.when.trigger for r in results]
    directives = [r.do.directive for r in results]
    confidences = [r.confidence for r in results]
    # With a deterministic LLM, all results should be identical
    assert len(set(triggers)) == 1, f"trigger variance: {triggers}"
    assert len(set(directives)) == 1, f"directive variance: {directives}"
    assert len(set(confidences)) == 1, f"confidence variance: {confidences}"
    for r in results:
        assert r.when.trigger == "git push fails"
        assert r.do.directive == "pull --rebase first"


def test_stability_with_varying_confidence() -> None:
    """Verify that confidence values from mock extraction stay within bounds."""
    payloads = [
        json.dumps(
            {"when": {"trigger": "git push fails"}, "do": {"directive": f"fix with method {i}"}, "confidence": 0.8 + i * 0.05}
        )
        for i in range(3)
    ]

    class CyclingLLM:
        def __init__(self, texts: list[str]) -> None:
            self.texts = texts
            self.idx = 0

        def complete(self, prompt: str, **kwargs: Any) -> LLMResponse:
            text = self.texts[self.idx % len(self.texts)]
            self.idx += 1
            _ = prompt
            return LLMResponse(text=text, model="fake", provider="fake")

    llm = CyclingLLM(payloads)
    confidences = [c.confidence for c in (extract_candidate(_traj(), llm) for _ in range(3))]
    assert all(0.0 <= c <= 1.0 for c in confidences)


def test_stability_variance_low() -> None:
    """Run extraction multiple times and verify confidence variance is bounded."""
    payload = json.dumps(
        {
            "when": {"trigger": "git push fails"},
            "do": {"directive": "pull --rebase"},
            "confidence": 0.85,
        }
    )
    llm = DeterministicLLM(payload)
    confidences = [extract_candidate(_traj(), llm).confidence for _ in range(10)]
    var = statistics.variance(confidences) if len(confidences) > 1 else 0.0
    assert var == 0.0, f"expected zero variance with deterministic LLM, got {var}"
