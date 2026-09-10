import json

import pytest

from cauterule.extraction.extractor import extract_candidate, extract_candidate_safe
from cauterule.llm.provider import LLMResponse
from cauterule.models.trajectory import Step, Trajectory


class FakeLLM:
    def __init__(self, text: str) -> None:
        self.text = text

    def complete(self, prompt: str, **kwargs: object) -> LLMResponse:
        _ = prompt
        _ = kwargs
        return LLMResponse(text=self.text, model="fake", provider="fake")


def _traj() -> Trajectory:
    return Trajectory(
        id="T-001",
        timestamp="t",
        task="git push fails",
        steps=(Step(step_number=1, tool="bash", error="non-fast-forward"),),
        success=False,
        failure_class="git/push",
    )


def test_extract_candidate_valid() -> None:
    llm_text = json.dumps(
        {
            "when": {"trigger": "git push fails", "context": ["shared branch"]},
            "do": {"directive": "pull --rebase first", "because": "remote ahead"},
            "confidence": 0.9,
            "reasoning": "remote has commits",
            "template": "retry",
        }
    )
    llm = FakeLLM(llm_text)
    candidate = extract_candidate(_traj(), llm, template="retry", extraction_pass=2)
    assert candidate.when.trigger == "git push fails"
    assert candidate.do.directive == "pull --rebase first"
    assert candidate.confidence == 0.9
    assert candidate.extraction_pass == 2
    assert candidate.template == "retry"


def test_extract_candidate_with_extra_text() -> None:
    payload = json.dumps({"when": {"trigger": "git push"}, "do": {"directive": "pull"}, "confidence": 0.8})
    llm = FakeLLM(f"Here is the JSON: {payload} thanks")
    candidate = extract_candidate(_traj(), llm)
    assert candidate.when.trigger == "git push"
    assert candidate.do.directive == "pull"


def test_extract_candidate_string_response() -> None:
    # LLM returns plain string, not LLMResponse
    class StringLLM:
        def complete(self, prompt: str, **kwargs: object) -> str:
            _ = prompt
            _ = kwargs
            return json.dumps({"when": {"trigger": "git push"}, "do": {"directive": "pull"}, "confidence": 0.7})

    candidate = extract_candidate(_traj(), StringLLM())
    assert candidate.confidence == 0.7


def test_extract_candidate_no_json() -> None:
    llm = FakeLLM("no json here")
    with pytest.raises(ValueError, match="No JSON"):
        extract_candidate(_traj(), llm)


def test_extract_candidate_invalid_json() -> None:
    llm = FakeLLM("{ not valid json }")
    with pytest.raises(ValueError):
        extract_candidate(_traj(), llm)


def test_extract_candidate_invalid_when_do() -> None:
    llm = FakeLLM(json.dumps({"when": "not dict", "do": {"directive": "pull"}, "confidence": 0.5}))
    with pytest.raises(ValueError, match="when/do must be objects"):
        extract_candidate(_traj(), llm)
    llm2 = FakeLLM(json.dumps({"when": {"trigger": "git push"}, "do": "not dict", "confidence": 0.5}))
    with pytest.raises(ValueError, match="when/do must be objects"):
        extract_candidate(_traj(), llm2)


def test_extract_candidate_low_confidence_fails_gate() -> None:
    # #497: confidence=0.1 is not promotable — hard fail with warnings.
    payload = json.dumps(
        {"when": {"trigger": "git push"}, "do": {"directive": "pull"}, "confidence": 0.1}
    )
    with pytest.raises(ValueError, match="quality gate"):
        extract_candidate(_traj(), FakeLLM(payload))
    candidate, error = extract_candidate_safe(_traj(), FakeLLM(payload))
    assert candidate is None
    assert error is not None and "quality gate" in error


def test_extract_candidate_grounded_high_confidence_passes() -> None:
    # #497: grounded confidence-0.9 output still succeeds.
    payload = json.dumps(
        {"when": {"trigger": "git push fails"}, "do": {"directive": "pull"}, "confidence": 0.9}
    )
    candidate = extract_candidate(_traj(), FakeLLM(payload))
    assert candidate.confidence == 0.9


def test_extract_candidate_not_dict() -> None:
    llm = FakeLLM("[1,2,3]")
    with pytest.raises(ValueError, match="No JSON object found"):
        extract_candidate(_traj(), llm)


def test_extract_candidate_safe_success() -> None:
    payload = json.dumps({"when": {"trigger": "git push"}, "do": {"directive": "pull"}, "confidence": 0.8})
    llm = FakeLLM(payload)
    candidate, error = extract_candidate_safe(_traj(), llm)
    assert candidate is not None
    assert error is None


def test_extract_candidate_safe_failure() -> None:
    llm = FakeLLM("bad")
    candidate, error = extract_candidate_safe(_traj(), llm)
    assert candidate is None
    assert error is not None
    assert "No JSON" in error
