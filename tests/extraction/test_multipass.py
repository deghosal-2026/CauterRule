from __future__ import annotations

import json

from cauterule.extraction.multipass import multipass_extract
from cauterule.llm.provider import LLMResponse
from cauterule.models.trajectory import Step, Trajectory


class FakeLLM:
    def __init__(self, texts: list[str]) -> None:
        self.texts = texts
        self.calls = 0
        self.temperatures: list[float] = []

    def complete(self, prompt: str, **kwargs: object) -> LLMResponse:
        text = self.texts[self.calls % len(self.texts)]
        self.temperatures.append(kwargs.get("temperature", 0.5))  # type: ignore[arg-type]
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
    payload = json.dumps({"when": {"trigger": "git push"}, "do": {"directive": "pull"}, "confidence": 0.8})
    llm = FakeLLM([payload, "bad json", payload])
    cands = multipass_extract(_traj(), llm)
    assert len(cands) == 2


def test_multipass_custom_temps() -> None:
    payload = json.dumps({"when": {"trigger": "git push"}, "do": {"directive": "pull"}, "confidence": 0.8})
    llm = FakeLLM([payload])
    cands = multipass_extract(_traj(), llm, temperatures=(0.1, 0.9))
    assert len(cands) == 2
    assert llm.temperatures == [0.1, 0.9], f"Expected [0.1, 0.9], got {llm.temperatures}"


def test_multipass_default_temps() -> None:
    payload = json.dumps({"when": {"trigger": "git push"}, "do": {"directive": "pull"}, "confidence": 0.8})
    llm = FakeLLM([payload, payload, payload])
    cands = multipass_extract(_traj(), llm)
    assert len(cands) == 3
    # Default temperatures are (0.2, 0.5, 0.8)
    assert llm.temperatures == [0.2, 0.5, 0.8], f"Expected [0.2, 0.5, 0.8], got {llm.temperatures}"


def test_multipass_confidence_threshold_passthrough() -> None:
    # Review: non-default confidence_threshold reaches extract_candidate_safe.
    payload_high = json.dumps({"when": {"trigger": "git push"}, "do": {"directive": "pull"}, "confidence": 0.95})
    payload_low = json.dumps({"when": {"trigger": "git push"}, "do": {"directive": "pull"}, "confidence": 0.65})
    good = FakeLLM([payload_high, payload_high, payload_high])
    bad = FakeLLM([payload_low, payload_low, payload_low])
    cands = multipass_extract(_traj(), good, confidence_threshold=0.7)
    assert len(cands) == 3
    cands2 = multipass_extract(_traj(), bad, confidence_threshold=0.9)
    assert len(cands2) == 0  # 0.65 < 0.9 gate


def _clean_success_traj() -> Trajectory:
    return Trajectory(
        id="T-clean",
        timestamp="t",
        task="run tests",
        steps=(Step(1, "bash", output="all green"),),
        success=True,
    )


def test_multipass_gate_drops_clean_success() -> None:
    payload = json.dumps({"when": {"trigger": "git push"}, "do": {"directive": "pull"}, "confidence": 0.8})
    llm = FakeLLM([payload, payload, payload])
    cands = multipass_extract(_clean_success_traj(), llm, gate_mode="strict")
    assert cands == []
    assert llm.calls == 0


def test_multipass_gate_relaxed_proceeds() -> None:
    # #709: relaxed mode silences *clean successes*, but still proceeds for
    # failures without signals (the raw-corpus case relaxed mode exists for).
    payload = json.dumps({"when": {"trigger": "run tests"}, "do": {"directive": "rerun tests"}, "confidence": 0.8})
    llm = FakeLLM([payload, payload, payload])
    traj = Trajectory(
        id="T-nosig-relaxed",
        timestamp="t",
        task="run tests",
        steps=(Step(1, "bash", output=""),),
        success=False,
    )
    cands = multipass_extract(traj, llm, gate_mode="relaxed")
    assert len(cands) == 3
    assert llm.calls == 3


def test_multipass_gate_relaxed_silences_clean_success() -> None:
    payload = json.dumps({"when": {"trigger": "run tests"}, "do": {"directive": "rerun tests"}, "confidence": 0.8})
    llm = FakeLLM([payload, payload, payload])
    cands = multipass_extract(_clean_success_traj(), llm, gate_mode="relaxed")
    assert cands == []
    assert llm.calls == 0
