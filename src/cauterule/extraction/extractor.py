"""LLM extraction call."""

from __future__ import annotations

import json
from typing import Any

from cauterule.extraction.prompt import build_extraction_prompt
from cauterule.extraction.quality import check_quality
from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.models.trajectory import Trajectory


def _parse_candidate_json(text: str, extraction_pass: int = 1, template: str | None = None) -> CandidateRule:
    """Parse LLM output JSON into a :class:`CandidateRule`."""
    # Extract JSON object from text (find first { ... }).
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON object found in LLM output")
    json_str = text[start : end + 1]
    data = json.loads(json_str)
    if not isinstance(data, dict):
        raise ValueError("LLM output must be a JSON object")

    when_data = data.get("when", {})
    do_data = data.get("do", {})
    if not isinstance(when_data, dict) or not isinstance(do_data, dict):
        raise ValueError("when/do must be objects")

    when = RuleWhen(
        trigger=str(when_data.get("trigger", "")),
        context=tuple(when_data.get("context", [])),
    )
    do = RuleDo(
        directive=str(do_data.get("directive", "")),
        because=do_data.get("because"),
    )
    confidence = float(data.get("confidence", 0.5))
    reasoning = data.get("reasoning")
    tmpl = data.get("template", template)

    return CandidateRule(
        when=when,
        do=do,
        confidence=confidence,
        reasoning=str(reasoning) if reasoning is not None else None,
        extraction_pass=extraction_pass,
        template=str(tmpl) if tmpl is not None else None,
    )


def extract_candidate(
    trajectory: Trajectory,
    llm: Any,
    template: str | None = None,
    extraction_pass: int = 1,
    temperature: float = 0.5,
) -> CandidateRule:
    """Call LLM to extract a candidate rule from *trajectory*.

    Args:
        trajectory: Trajectory to extract from.
        llm: LLM provider with ``complete(prompt)`` method.
        template: Optional template hint.
        extraction_pass: Pass number (1-indexed).
        temperature: LLM temperature for this pass.

    Raises:
        ValueError: If LLM output cannot be parsed or fails quality checks with hard fail
            (caller may decide to fallback to human review).
    """
    prompt = build_extraction_prompt(trajectory, template=template)
    result = llm.complete(prompt, temperature=temperature)
    text = result.text if hasattr(result, "text") else str(result)
    candidate = _parse_candidate_json(text, extraction_pass=extraction_pass, template=template)

    _ = check_quality(candidate, trajectory)
    return candidate


def extract_candidate_safe(
    trajectory: Trajectory,
    llm: Any,
    template: str | None = None,
    extraction_pass: int = 1,
    temperature: float = 0.5,
) -> tuple[CandidateRule | None, str | None]:
    """Safe wrapper that returns (candidate, error) instead of raising."""
    try:
        candidate = extract_candidate(trajectory, llm, template=template, extraction_pass=extraction_pass, temperature=temperature)
        return candidate, None
    except Exception as exc:
        return None, str(exc)
