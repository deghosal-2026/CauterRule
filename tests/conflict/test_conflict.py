"""Tests for the conflict detection package."""

from cauterule.conflict.consolidation import consolidate
from cauterule.conflict.contradiction import detect_contradictions
from cauterule.conflict.overlap import detect_overlaps
from cauterule.conflict.report import (
    build_contradiction_report,
    build_duplicate_report,
    build_overlap_report,
    build_specificity_report,
)
from cauterule.conflict.specificity import score_specificity
from cauterule.models.conflict import ConflictReport
from cauterule.models.rule import Provenance, ReplayEvidence, RuleDo, RuleWhen, StandingRule


def _rule(
    rid: str,
    trigger: str,
    directive: str,
    status: str = "active",
    context: tuple[str, ...] = (),
    taxonomy: str | None = None,
    hit_count: int = 0,
    precision: float = 0.0,
    recall: float = 0.0,
    tags: tuple[str, ...] = (),
) -> StandingRule:
    replay = ReplayEvidence(precision=precision, recall=recall)
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
        status=status,  # type: ignore[arg-type]
        promoted_at="2025-01-01T00:00:00",
        hit_count=hit_count,
        tags=tags,
        taxonomy=taxonomy,
    )


class TestDetectContradictions:
    def test_no_contradictions_empty(self) -> None:
        assert detect_contradictions([]) == []

    def test_no_contradictions_single(self) -> None:
        r = _rule("R-001", "git push fails", "run pull --rebase")
        assert detect_contradictions([r]) == []

    def test_no_contradictions_same_directive(self) -> None:
        a = _rule("R-001", "git push fails", "run pull --rebase")
        b = _rule("R-002", "git push fails", "run pull --rebase")
        assert detect_contradictions([a, b]) == []

    def test_contradiction_detected(self) -> None:
        a = _rule("R-001", "git push fails", "run pull --rebase")
        b = _rule("R-002", "git push fails", "run force push")
        reports = detect_contradictions([a, b])
        assert len(reports) == 1
        assert reports[0].type == "contradiction"
        assert "R-001" in reports[0].rules and "R-002" in reports[0].rules

    def test_contradiction_case_insensitive(self) -> None:
        a = _rule("R-001", "Git Push Fails", "pull --rebase")
        b = _rule("R-002", "git push fails", "force push")
        reports = detect_contradictions([a, b])
        assert len(reports) == 1

    def test_ignores_retired_rules(self) -> None:
        a = _rule("R-001", "git push fails", "pull --rebase")
        b = _rule("R-002", "git push fails", "force push", status="retired")
        assert detect_contradictions([a, b]) == []

    def test_multiple_contradictions(self) -> None:
        a = _rule("R-001", "git push fails", "pull --rebase")
        b = _rule("R-002", "git push fails", "force push")
        c = _rule("R-003", "build fails", "fix build")
        d = _rule("R-004", "build fails", "revert last commit")
        reports = detect_contradictions([a, b, c, d])
        assert len(reports) == 2


class TestScoreSpecificity:
    def test_minimal_rule(self) -> None:
        r = _rule("R-001", "fail", "fix it")
        score = score_specificity(r)
        assert 0.0 <= score <= 1.0

    def test_context_boosts_score(self) -> None:
        low = _rule("R-001", "fail", "fix it")
        high = _rule("R-002", "fail", "fix it", context=("a", "b", "c"))
        assert score_specificity(high) > score_specificity(low)

    def test_trigger_precision_boosts_score(self) -> None:
        short = _rule("R-001", "fail", "fix it")
        long = _rule("R-002", "when git push fails with merge conflict", "fix it")
        assert score_specificity(long) > score_specificity(short)

    def test_taxonomy_depth(self) -> None:
        no_tax = _rule("R-001", "fail", "fix it")
        has_tax = _rule("R-002", "fail", "fix it", taxonomy="git/workflow/push")
        assert score_specificity(has_tax) > score_specificity(no_tax)

    def test_hit_count_boosts(self) -> None:
        no_hits = _rule("R-001", "fail", "fix it")
        has_hits = _rule("R-002", "fail", "fix it", hit_count=5)
        assert score_specificity(has_hits) > score_specificity(no_hits)

    def test_replay_precision_boosts(self) -> None:
        low_prec = _rule("R-001", "fail", "fix it", precision=0.0)
        high_prec = _rule("R-002", "fail", "fix it", precision=0.9)
        assert score_specificity(high_prec) > score_specificity(low_prec)

    def test_score_bounds(self) -> None:
        max_spec = _rule(
            "R-001",
            "a " * 20 + "b",
            "fix it",
            context=tuple(f"c{n}" for n in range(10)),
            taxonomy="a/b/c/d/e/f",
            hit_count=99,
            precision=1.0,
        )
        s = score_specificity(max_spec)
        assert 0.0 <= s <= 1.0

    def test_all_factors_contribute(self) -> None:
        r = _rule(
            "R-001",
            "when git push fails on main",
            "run pull --rebase",
            context=("branch=main", "repo=foo"),
            taxonomy="git/workflow/push",
            hit_count=3,
            precision=0.75,
        )
        s = score_specificity(r)
        assert 0.2 < s < 1.0


class TestDetectOverlaps:
    def test_no_overlaps_empty(self) -> None:
        assert detect_overlaps([]) == []

    def test_no_overlaps_different_triggers(self) -> None:
        a = _rule("R-001", "git push fails", "pull --rebase")
        b = _rule("R-002", "docker image prune", "cleanup docker")
        assert detect_overlaps([a, b]) == []

    def test_overlap_detected(self) -> None:
        a = _rule("R-001", "git push fails", "pull --rebase")
        b = _rule("R-002", "git pull fails", "fetch --all")
        reports = detect_overlaps([a, b])
        assert len(reports) == 1
        assert reports[0].type == "overlap"

    def test_excludes_same_trigger(self) -> None:
        a = _rule("R-001", "git push fails", "pull --rebase")
        b = _rule("R-002", "git push fails", "force push")
        assert detect_overlaps([a, b]) == []

    def test_excludes_same_directive(self) -> None:
        a = _rule("R-001", "git push fails", "pull --rebase")
        b = _rule("R-002", "git pull fails", "pull --rebase")
        assert detect_overlaps([a, b]) == []

    def test_ignores_non_active(self) -> None:
        a = _rule("R-001", "git push fails", "pull --rebase")
        b = _rule("R-002", "git pull fails", "fetch --all", status="retired")
        assert detect_overlaps([a, b]) == []

    def test_overlap_with_context(self) -> None:
        a = _rule("R-001", "push fails on main", "pull --rebase")
        b = _rule("R-002", "push fails on staging", "force push")
        reports = detect_overlaps([a, b])
        assert len(reports) == 1


class TestConsolidate:
    def test_consolidate_no_conflicts(self) -> None:
        a = _rule("R-001", "git push fails", "pull --rebase")
        b = _rule("R-002", "docker build fails", "fix dockerfile")
        merged, reports = consolidate([a, b])
        assert len(merged) == 2
        assert reports == []

    def test_consolidate_supersedes_loser(self) -> None:
        a = _rule("R-001", "git push fails", "pull --rebase", context=("a", "b"))
        b = _rule("R-002", "git push fails", "force push")
        merged, reports = consolidate([a, b])
        assert len(reports) == 1
        losers = [r for r in merged if r.status == "superseded"]
        assert len(losers) == 1
        assert losers[0].id == "R-002"
        assert any(r.status == "active" for r in merged)

    def test_consolidate_same_winner_by_specificity(self) -> None:
        a = _rule("R-001", "git push fails", "pull --rebase", context=())
        b = _rule("R-002", "git push fails", "force push", context=("a", "b"))
        _merged, _ = consolidate([a, b])
        losers = [r for r in _merged if r.status == "superseded"]
        assert losers[0].id == "R-001"

    def test_consolidate_retired_rules_untouched(self) -> None:
        a = _rule("R-001", "git push fails", "pull --rebase")
        b = _rule("R-002", "git push fails", "force push", status="retired")
        _, _reports = consolidate([a, b])
        assert _reports == []

    def test_consolidate_empty(self) -> None:
        merged, reports = consolidate([])
        assert merged == []
        assert reports == []


class TestReportBuilder:
    def test_build_contradiction(self) -> None:
        r = build_contradiction_report(("R-001", "R-002"), "trigger", "resolve")
        assert r.type == "contradiction"
        assert r.rules == ("R-001", "R-002")
        assert r.trigger == "trigger"
        assert r.resolution == "resolve"

    def test_build_duplicate(self) -> None:
        r = build_duplicate_report(("R-001", "R-002"))
        assert r.type == "duplicate"

    def test_build_overlap(self) -> None:
        r = build_overlap_report(("R-001", "R-002"), trigger="t")
        assert r.type == "overlap"
        assert r.trigger == "t"

    def test_build_specificity(self) -> None:
        r = build_specificity_report(("R-001", "R-002"), scores={"R-001": 0.8, "R-002": 0.3})
        assert r.type == "specificity"
        assert r.specificity_scores["R-001"] == 0.8
        assert r.specificity_scores["R-002"] == 0.3

    def test_conflict_report_round_trip(self) -> None:
        original = ConflictReport(
            type="contradiction",
            rules=("R-001", "R-002"),
            trigger="test",
            resolution="fix it",
            specificity_scores={"R-001": 0.9},
        )
        d = original.to_dict()
        restored = ConflictReport.from_dict(d)
        assert restored == original


class TestImport:
    def test_module_imports(self) -> None:
        from cauterule.conflict import (
            consolidate,
            detect_contradictions,
            detect_overlaps,
            score_specificity,
        )

        assert consolidate is not None
        assert detect_contradictions is not None
        assert detect_overlaps is not None
        assert score_specificity is not None
