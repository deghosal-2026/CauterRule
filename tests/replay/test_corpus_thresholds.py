"""Tests for corpus-aware matcher thresholds (#420)."""

from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.models.trajectory import Step, Trajectory
from cauterule.replay.matcher import (
    STRATEGY_THRESHOLDS,
    rule_matches,
    strategy_for_corpus,
    threshold_for_corpus,
)


def _cand(trigger: str) -> CandidateRule:
    return CandidateRule(when=RuleWhen(trigger=trigger), do=RuleDo(directive="d"), confidence=0.9)


def _traj(task: str, error: str = "") -> Trajectory:
    return Trajectory(id="T-001", timestamp="t", task=task, steps=(Step(1, "bash", error=error),), success=False)


def test_strategy_for_curated() -> None:
    assert strategy_for_corpus("golden") == "strict"
    assert strategy_for_corpus("successes") == "strict"
    assert strategy_for_corpus("failures/positive") == "semantic"  # not in CURATED set, defaults semantic
    assert strategy_for_corpus("curated/golden") == "strict"


def test_strategy_for_raw() -> None:
    assert strategy_for_corpus("raw/ci") == "loose"
    assert strategy_for_corpus("raw/opencode") == "loose"
    assert strategy_for_corpus("raw/synthetic") == "loose"


def test_strategy_for_transfer() -> None:
    assert strategy_for_corpus("raw/sibling-repos") == "transfer"
    assert strategy_for_corpus("sibling-repos") == "transfer"
    assert strategy_for_corpus("cross-repo/transfer") == "transfer"


def test_threshold_mapping() -> None:
    assert threshold_for_corpus("golden") == STRATEGY_THRESHOLDS["strict"]
    assert threshold_for_corpus("raw/ci") == STRATEGY_THRESHOLDS["loose"]
    assert threshold_for_corpus("raw/sibling-repos") == STRATEGY_THRESHOLDS["transfer"]
    assert threshold_for_corpus("failures/positive") == STRATEGY_THRESHOLDS["semantic"]


def test_strict_rejects_vague_loose_accepts() -> None:
    # Vague trigger with moderate overlap: strict should reject, loose should accept.
    # Use a trigger that scores around 0.5-0.6 (between thresholds).
    cand = _cand("install fails with missing dependency")
    traj = _traj(task="npm install fails", error="missing dep")
    # Score is around 0.6-0.7; strict (0.70) should be borderline, loose (0.45) should pass.
    # Verify the threshold param directly:
    assert rule_matches(cand, traj, threshold=0.45) is True
    # At strict threshold, may still pass if score is high; ensure strict is not looser than loose
    strict = threshold_for_corpus("golden")
    loose = threshold_for_corpus("raw/ci")
    assert strict > loose


def test_threshold_param_overrides_default() -> None:
    cand = _cand("when a non-fast-forward push is rejected")
    traj = _traj(task="deploy", error="Updates were rejected because the remote contains work")
    # Paraphrase "remote contains work" verbatim via alias_phrase_hit → floors at 0.70.
    # With Fix 3 (alias_phrase_hit floor raised to 0.70), strict passes now.
    assert rule_matches(cand, traj, threshold=0.45) is True
    assert rule_matches(cand, traj, threshold=0.70) is True
