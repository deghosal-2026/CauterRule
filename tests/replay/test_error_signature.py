"""Tests for the structured error_signature field (#725)."""

from __future__ import annotations

from cauterule.extraction.extractor import _parse_candidate_json
from cauterule.extraction.prompt import build_extraction_prompt
from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.models.trajectory import Step, Trajectory
from cauterule.replay.matcher import match_score, rule_matches


def _cand(trigger: str, signature: str | None = None) -> CandidateRule:
    return CandidateRule(
        when=RuleWhen(trigger=trigger, signature=signature),
        do=RuleDo(directive="d"),
        confidence=0.9,
    )


def _traj(*, error: str, failure_class: str | None, task: str = "run script") -> Trajectory:
    return Trajectory(
        id="T-sig",
        timestamp="t",
        task=task,
        steps=(Step(1, "bash", error=error),),
        success=False,
        failure_class=failure_class,
    )


def test_rule_when_round_trips_signature() -> None:
    when = RuleWhen(trigger="when import fails", signature="ModuleNotFoundError")
    data = when.to_dict()
    assert data["signature"] == "ModuleNotFoundError"
    assert RuleWhen.from_dict(data).signature == "ModuleNotFoundError"


def test_rule_when_signature_optional() -> None:
    when = RuleWhen(trigger="when import fails")
    assert when.signature is None
    assert "signature" not in when.to_dict()
    assert RuleWhen.from_dict({"trigger": "x"}).signature is None


def test_signature_hit_floors_match_regardless_of_wording() -> None:
    # Trigger wording is generic; the structured signature must carry the match.
    cand = _cand("when python import fails", signature="ModuleNotFoundError")
    traj = _traj(
        error="ImportError: no module named foo",
        failure_class="python/import/ModuleNotFoundError",
    )
    assert match_score(cand, traj) >= 0.70
    assert rule_matches(cand, traj, threshold=0.70)


def test_no_signature_falls_back_to_fuzzy_path() -> None:
    # Without a signature the matcher behaves exactly as before.
    cand = _cand("when python import fails")
    traj = _traj(
        error="ImportError: no module named foo",
        failure_class="python/import/ModuleNotFoundError",
    )
    assert match_score(cand, traj) < 0.70


def test_signature_does_not_match_unrelated_reference() -> None:
    cand = _cand("when python import fails", signature="ModuleNotFoundError")
    traj = _traj(error="non-fast-forward push rejected", failure_class="git/push/non-fast-forward")
    assert match_score(cand, traj) < 0.70


def test_generic_signature_does_not_floor() -> None:
    # A generic single-token signature must not floor a match (#725 review).
    cand = _cand("when python import fails", signature="error")
    traj = _traj(error="some error occurred", failure_class="python/import")
    assert match_score(cand, traj) < 0.70


def test_prompt_requests_error_signature() -> None:
    traj = Trajectory(
        id="T",
        timestamp="t",
        task="run script",
        steps=(Step(1, "bash", error="ImportError"),),
        success=False,
    )
    prompt = build_extraction_prompt(traj)
    assert "error_signature" in prompt


def test_parser_populates_error_signature() -> None:
    raw = (
        '{"when": {"trigger": "when import fails", "context": ["python"], '
        '"error_signature": "ModuleNotFoundError"}, '
        '"do": {"directive": "install the missing package"}, "confidence": 0.9}'
    )
    cand = _parse_candidate_json(raw)
    assert cand.when.signature == "ModuleNotFoundError"
    assert cand.when.trigger == "when import fails"


def test_parser_handles_missing_error_signature() -> None:
    raw = '{"when": {"trigger": "when import fails"}, "do": {"directive": "x"}, "confidence": 0.9}'
    cand = _parse_candidate_json(raw)
    assert cand.when.signature is None
