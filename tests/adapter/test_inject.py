from cauterule.adapter.inject import inject
from cauterule.models.rule import Provenance, RuleDo, RuleWhen, StandingRule


def _rule(trigger: str) -> StandingRule:
    return StandingRule(
        id="R-001",
        when=RuleWhen(trigger=trigger),
        do=RuleDo(directive="do something"),
        confidence=0.9,
        provenance=Provenance(
            source_trajectory="a.jsonl", extracted_by="m", extract_timestamp="t", extraction_pass=1
        ),
        status="active",
        promoted_at="2026-09-03T18:35:00Z",
    )


def test_inject_no_rules() -> None:
    with inject("git push") as matched:
        assert matched == []


def test_inject_none_rules() -> None:
    with inject("task", rules=None) as matched:
        assert matched == []


def test_inject_matching() -> None:
    r1 = _rule("git push fails")
    r2 = _rule("docker network")
    r3 = _rule("python import")
    rules = [r1, r2, r3]
    with inject("git push fails with non-fast-forward", rules=rules) as matched:
        assert r1 in matched
        assert r2 not in matched
        assert r3 not in matched


def test_inject_case_insensitive() -> None:
    r = _rule("GIT PUSH")
    with inject("git push fails", rules=[r]) as matched:
        assert len(matched) == 1


def test_inject_empty_trigger() -> None:
    r2 = _rule("unrelated trigger")
    with inject("git push", rules=[r2]) as matched:
        assert matched == []


def test_inject_with_kwargs() -> None:
    r = _rule("git push")
    with inject("git push", rules=[r], tool="bash", error="boom") as matched:
        assert len(matched) == 1
