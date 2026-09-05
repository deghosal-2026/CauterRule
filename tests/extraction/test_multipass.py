import json

from cauterule.extraction.multipass import multipass_extract
from cauterule.llm.provider import LLMResponse
from cauterule.models.trajectory import Step, Trajectory


class FakeLLM:
    def __init__(self, texts: list[str]) -> None:
        self.texts = texts
        self.calls = 0

    def complete(self, prompt: str) -> LLMResponse:
        _ = prompt
        text = self.texts[self.calls % len(self.texts)]
        self.calls += 1
        return LLMResponse(text=text, model="fake", provider="fake")


def _traj() -> Trajectory:
    return Trajectory(id="T-001", timestamp="t", task="git push", steps=(Step(1, "bash", error="fail"),), success=False, failure_class="git/push")


def test_multipass_three() -> None:
    payload = json.dumps({"when": {"trigger": "git push"}, "do": {"directive": "pull"}, "confidence": 0.8})
    llm = FakeLLM([payload, payload, payload])
    cands = multipass_extract(_traj(), llm)
    assert len(cands) == 3
    assert all(c.extraction_pass in (1, 2, 3) for c in cands)


def test_multipass_partial_failure() -> None:
    payload = json.dumps({"when": {"trigger": "t"}, "do": {"directive": "d"}, "confidence": 0.8})
    llm = FakeLLM([payload, "bad json", payload])
    cands = multipass_extract(_traj(), llm)
    assert len(cands) == 2


def test_multipass_custom_temps() -> None:
    payload = json.dumps({"when": {"trigger": "t"}, "do": {"directive": "d"}, "confidence": 0.8})
    llm = FakeLLM([payload])
    cands = multipass_extract(_traj(), llm, temperatures=(0.1, 0.9))
    assert len(cands) == 2
