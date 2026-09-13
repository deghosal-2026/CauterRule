"""Tests for stored per-rule specificity scoring (#541)."""

from __future__ import annotations

from pathlib import Path

from cauterule.lifecycle.specificity import (
    BROAD_SPECIFICITY_THRESHOLD,
    compute_specificity,
    is_broad,
    lowest_specificity,
    score_and_store,
    trigger_score,
)
from cauterule.models.rule import Provenance, RuleDo, RuleWhen, StandingRule
from cauterule.observe.outcomes import record_outcome
from cauterule.store.manager import StoreManager


def _rule(
    rid: str,
    trigger: str = "git push fails",
    directive: str = "pull --rebase",
    hit_count: int = 0,
    prevented: int = 0,
    broke: int = 0,
    neutral: int = 0,
    specificity: float | None = None,
) -> StandingRule:
    return StandingRule(
        id=rid,
        when=RuleWhen(trigger=trigger),
        do=RuleDo(directive=directive),
        confidence=0.85,
        provenance=Provenance(
            source_trajectory="T-1",
            extracted_by="test",
            extract_timestamp="2025-01-01T00:00:00",
            extraction_pass=1,
        ),
        status="active",
        promoted_at="2025-01-02T00:00:00",
        hit_count=hit_count,
        prevented_count=prevented,
        broke_count=broke,
        neutral_count=neutral,
        specificity=specificity,
    )


# Curated broad triggers — the golden gate (#541): at least 6 of 10 must
# score below the documented broad threshold.
_BROAD_TRIGGERS = [
    "fails",
    "error",
    "does not work",
    "issue",
    "something went wrong",
    "problem",
    "it broke",
    "unexpected",
    "not working",
    "failure",
]

_NARROW_TRIGGERS = [
    "git push fails with non-fast-forward",
    "docker build permission denied writing layer",
    "ModuleNotFoundError import openai",
    "pytest asserts 42 equals 43 in test_math",
]


def test_trigger_score_broad_vs_narrow() -> None:
    assert trigger_score("fails") < trigger_score("git push fails")
    assert trigger_score("git push fails permission denied") == 1.0


def test_golden_gate_6_of_10_broad() -> None:
    scores = {t: trigger_score(t) for t in _BROAD_TRIGGERS}
    broad_count = sum(1 for s in scores.values() if s < BROAD_SPECIFICITY_THRESHOLD)
    assert broad_count >= 6, (
        f"only {broad_count}/10 broad triggers below {BROAD_SPECIFICITY_THRESHOLD}: {scores}"
    )


def test_narrow_triggers_score_high() -> None:
    for t in _NARROW_TRIGGERS:
        assert trigger_score(t) >= 0.6, f"{t!r} scored {trigger_score(t)}"


def test_hyphenated_generic_phrase_scores_broad() -> None:
    # #784: hyphenating a broad phrase must not buy specificity.
    assert trigger_score("does-not-work") == trigger_score("does not work")
    assert trigger_score("does-not-work") < BROAD_SPECIFICITY_THRESHOLD


def test_code_like_hyphenations_score_specific() -> None:
    assert trigger_score("non-fast-forward") == 1.0
    assert trigger_score("error-123") == 1.0
    assert trigger_score("exit_code") == 1.0


def test_precision_term_boosts_specificity() -> None:
    good = _rule("R-G", prevented=8, broke=2)
    bad = _rule("R-B", prevented=2, broke=8)
    good_score, _ = compute_specificity(good)
    bad_score, _ = compute_specificity(bad)
    assert good_score > bad_score


def test_small_sample_shrunk_to_prior() -> None:
    # 1-for-1 new rule: precision stays near 0.5 (shrink), so specificity
    # leans mostly on the trigger signal.
    r = _rule("R-N", prevented=1)
    score, inputs = compute_specificity(r)
    assert 0.0 <= score <= 1.0
    assert inputs["trigger_tokens"] >= 2


def test_score_and_store_persists(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    store.add_rule(_rule("R-S", prevented=5, broke=1))
    updated = score_and_store(store, "R-S")
    assert updated.specificity is not None
    assert updated.specificity_inputs
    # Reload from disk retains it.
    reloaded = store.get_rule("R-S")
    assert reloaded is not None
    assert reloaded.specificity == updated.specificity
    assert reloaded.specificity_inputs == updated.specificity_inputs


def test_record_outcome_refreshes_specificity(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    store.add_rule(_rule("R-R", specificity=None))
    record_outcome(store, "R-R", "broke", trajectory_id="T-1")
    rule = store.get_rule("R-R")
    assert rule is not None
    assert rule.specificity is not None


def test_is_broad() -> None:
    broad = _rule("R-B1", trigger="fails")
    narrow = _rule("R-N1", trigger="git push fails permission denied")
    assert is_broad(broad)
    assert not is_broad(narrow)


def test_lowest_specificity_ordering(tmp_path: Path) -> None:
    store = StoreManager(str(tmp_path / "rules"))
    store.add_rule(_rule("R-BR", trigger="fails"))
    store.add_rule(_rule("R-NR", trigger="docker build permission denied writing layer"))
    rules = store.list_rules()
    table = lowest_specificity(rules)
    assert table[0][0].id == "R-BR"


def test_legacy_rule_backfill_on_load(tmp_path: Path) -> None:
    # A rule with no specificity field round-trips; computed on demand.
    store = StoreManager(str(tmp_path / "rules"))
    store.add_rule(_rule("R-L", specificity=None))
    rule = store.get_rule("R-L")
    assert rule is not None
    assert rule.specificity is None
    score, _ = compute_specificity(rule)
    assert 0.0 <= score <= 1.0
