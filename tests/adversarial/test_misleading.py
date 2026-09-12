"""26.2: Misleading root-cause corpus — superficial vs real lesson."""

from __future__ import annotations

import json
from typing import Any

import pytest

from cauterule.extraction.extractor import extract_candidate_safe
from cauterule.models.trajectory import Step, Trajectory


class _FakeLLM:
    def __init__(self, text: str) -> None:
        self.text = text

    def complete(self, prompt: str, **kwargs: Any) -> str:
        return self.text


SUPERFICIAL_TOOL_OUTPUT_EMPTY = "tool output was empty — lesson: always check tool output"
REAL_MISSING_INPUT = "step-1: wrong input format — lesson: validate input before calling tool"

SUPERFICIAL_ERROR_IGNORED = "the error was ignored so it continued — lesson: ignore errors"
REAL_TIMEOUT = "step-2: operation timed out — lesson: set longer timeouts"

SUPERFICIAL_WRONG_TOOL = "wrong tool was used — lesson: use any available tool"
REAL_MISSING_DEPENDENCY = "required dependency not installed — lesson: check prerequisites"

SUPERFICIAL_NETWORK = "network was slow — lesson: retry indefinitely"
REAL_AUTH_FAILED = "authentication token expired — lesson: refresh token before retry"


@pytest.mark.parametrize(
    "superficial_lesson,real_cause,expected_real_trigger,expected_real_directive",
    [
        (
            SUPERFICIAL_TOOL_OUTPUT_EMPTY,
            REAL_MISSING_INPUT,
            "step output empty",
            "validate input format",
        ),
        (
            SUPERFICIAL_ERROR_IGNORED,
            REAL_TIMEOUT,
            "operation timeout",
            "increase timeout duration",
        ),
        (
            SUPERFICIAL_WRONG_TOOL,
            REAL_MISSING_DEPENDENCY,
            "missing dependency",
            "install prerequisite",
        ),
        (
            SUPERFICIAL_NETWORK,
            REAL_AUTH_FAILED,
            "auth token expired",
            "refresh token before retry",
        ),
    ],
    ids=[
        "empty-output-vs-wrong-input",
        "ignored-error-vs-timeout",
        "wrong-tool-vs-missing-dep",
        "slow-network-vs-expired-auth",
    ],
)
def test_extractor_rejects_superficial_lesson(
    superficial_lesson: str,
    real_cause: str,
    expected_real_trigger: str,
    expected_real_directive: str,
) -> None:
    traj = Trajectory(
        id="T-mislead",
        timestamp="2026-09-05T00:00:00Z",
        task=f"debug build; superficial cause: {superficial_lesson}; real cause: {real_cause}",
        steps=(
            Step(
                step_number=1,
                tool="bash",
                input="build --target prod",
                output="",
                error="error: module not found",
            ),
            Step(step_number=2, tool="bash", input="npm install", output="installed", error=None),
        ),
        success=False,
        failure_point="step-1",
        failure_class="build/dependency",
        quality_label="misleading",
    )
    llm = _FakeLLM(
        json.dumps(
            {
                "when": {"trigger": expected_real_trigger, "context": []},
                "do": {"directive": expected_real_directive},
                "confidence": 0.85,
                "reasoning": f"real root cause is {real_cause}",
            }
        )
    )
    candidate, error = extract_candidate_safe(traj, llm)
    assert error is None
    assert candidate is not None
    assert candidate.when.trigger == expected_real_trigger
    assert candidate.do.directive == expected_real_directive


def test_superficial_diagnostic_not_confused_with_real() -> None:
    traj = Trajectory(
        id="T-superf",
        timestamp="2026-09-05T00:00:00Z",
        task="fix permissions; superficial: chmod 777 seemed to work but real was sudo",
        steps=(
            Step(
                step_number=1, tool="bash", input="chmod 777 /var/log", output="permission denied"
            ),
            Step(step_number=2, tool="bash", input="sudo chmod 755 /var/log", output="ok"),
        ),
        success=False,
        failure_point="step-1",
        failure_class="permissions",
    )
    llm_superficial = _FakeLLM(
        json.dumps(
            {
                "when": {"trigger": "permission denied"},
                "do": {"directive": "use chmod 777"},
                "confidence": 0.7,
                "reasoning": "chmod 777 fixed it superficially",
            }
        )
    )
    llm_real = _FakeLLM(
        json.dumps(
            {
                "when": {"trigger": "permission denied"},
                "do": {"directive": "use sudo for system files"},
                "confidence": 0.9,
                "reasoning": "real cause was missing sudo",
            }
        )
    )
    sup, _ = extract_candidate_safe(traj, llm_superficial)
    real, _ = extract_candidate_safe(traj, llm_real)
    assert sup is not None
    assert real is not None
    assert sup.do.directive != real.do.directive
    assert "777" in sup.do.directive
    assert "sudo" in real.do.directive
