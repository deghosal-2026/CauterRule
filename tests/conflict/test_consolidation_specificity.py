"""Tests for consolidation using score_specificity (#608)."""

from __future__ import annotations

from cauterule.conflict.consolidation import consolidate
from cauterule.conflict.specificity import score_specificity
from cauterule.lifecycle.supersede import orphan_middles
from cauterule.models.rule import Provenance, ReplayEvidence, RuleDo, RuleWhen, StandingRule


def _rule(
    rid: str,
    trigger: str = "git push fails",
    directive: str = "pull --rebase",
    context: tuple[str, ...] = (),
    hit_count: int = 0,
    precision: float = 0.0,
) -> StandingRule:
    replay = ReplayEvidence(precision=precision, recall=0.5)
    provenance = Provenance(
        source_trajectory="t.json",
        extracted_by="test",
        extract_timestamp="2025-01-01T00:00:00",
        extraction_pass=1,
        replay_evidence=replay,
    )
    return StandingRule(
        id=rid,
        when=RuleWhen(trigger=trigger, context=context),
        do=RuleDo(directive=directive),
        confidence=0.9,
        provenance=provenance,
        status="active",
        promoted_at="2025-01-01T00:00:00",
        hit_count=hit_count,
    )


def test_winner_matches_score_specificity_divergence_example() -> None:
    # Same trigger (consolidate only considers same-trigger pairs).
    # Rule A: one context item, but zero hits and no replay evidence.
    a = _rule("R-A", trigger="git push fails", context=("ci",))
    # Rule B: no context but hit-tested with replay evidence.
    b = _rule("R-B", trigger="git push fails", directive="force push", hit_count=3, precision=0.9)
    # Old ad-hoc count (context + trigger words) ranked A >= B; the canonical
    # scorer ranks B (evidence) above A (one context item).
    assert score_specificity(b) > score_specificity(a)
    merged, _ = consolidate([a, b])
    loser = next(r for r in merged if r.status == "superseded")
    assert loser.id == "R-A"  # scored loser, not ad-hoc loser


def test_equal_score_overlap_merge() -> None:
    # Identical rules (equal specificity) with overlapping directives merge,
    # keeping the higher-hit rule.
    a = _rule("R-001", directive="pull --rebase && fetch", hit_count=1)
    b = _rule("R-002", directive="pull --rebase", hit_count=9)
    merged, reports = consolidate([a, b])
    assert reports and reports[0].type == "overlap"
    loser = next(r for r in merged if r.status == "superseded")
    assert loser.id == "R-001"
    winner = next(r for r in merged if r.status == "active")
    assert winner.id == "R-002"


def test_tie_break_hit_count() -> None:
    a = _rule("R-A", "git push fails", "pull --rebase")
    b = _rule("R-B", "git push fails", "force push")
    # Equal specificity triggers contradict; winner should be same as before.
    assert score_specificity(a) == score_specificity(b)
    merged, reports = consolidate([a, b])
    assert reports and reports[0].type == "contradiction"
    assert len([r for r in merged if r.status == "superseded"]) == 1


def test_superseded_loser_points_at_winner() -> None:
    # #785: the loser must record its successor; otherwise orphan_middles
    # (and validate_store) reject the consolidated store as corrupt.
    a = _rule("R-A", "git push fails", "pull --rebase")
    b = _rule("R-B", "git push fails", "force push")
    merged, _ = consolidate([a, b])
    loser = next(r for r in merged if r.status == "superseded")
    winner = next(r for r in merged if r.status == "active")
    assert loser.superseded_by == winner.id
    assert orphan_middles(merged) == []


def test_superseded_loser_points_at_winner_on_overlap_merge() -> None:
    # #785: the overlap-merge branch must set the pointer too.
    a = _rule("R-001", directive="pull --rebase && fetch", hit_count=1)
    b = _rule("R-002", directive="pull --rebase", hit_count=9)
    merged, reports = consolidate([a, b])
    assert reports and reports[0].type == "overlap"
    loser = next(r for r in merged if r.status == "superseded")
    winner = next(r for r in merged if r.status == "active")
    assert loser.superseded_by == winner.id
    assert orphan_middles(merged) == []
