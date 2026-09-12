import pytest

from cauterule.models.rule import (
    Provenance,
    ReplayEvidence,
    RuleDo,
    RuleWhen,
    StandingRule,
)


def _valid_provenance() -> Provenance:
    return Provenance(
        source_trajectory="trajectories/2026-09-03/failure-003.jsonl",
        extracted_by="gpt-4o",
        extract_timestamp="2026-09-03T18:30:00Z",
        extraction_pass=2,
        draft_tournament_rank=1,
        replay_evidence=ReplayEvidence(
            failures_prevented=("F-001",), successes_broken=(), precision=1.0, recall=0.28
        ),
        promotion_commit="abc123",
        promotion_mode="auto",
    )


def test_rule_when_valid() -> None:
    w = RuleWhen(trigger="git push fails", context=("shared branch",))
    assert w.trigger == "git push fails"
    assert w.to_dict() == {"trigger": "git push fails", "context": ["shared branch"]}
    assert RuleWhen.from_dict(w.to_dict()) == w
    # no context omits key
    w2 = RuleWhen(trigger="tool fails")
    assert w2.to_dict() == {"trigger": "tool fails"}


def test_rule_when_validation() -> None:
    with pytest.raises(ValueError, match="when.trigger"):
        RuleWhen(trigger="  ", context=())
    with pytest.raises(ValueError, match="when.context"):
        RuleWhen(trigger="ok", context=(" ",))


def test_rule_do_valid() -> None:
    d = RuleDo(directive="run pull --rebase", because="remote has commits")
    assert d.to_dict() == {"directive": "run pull --rebase", "because": "remote has commits"}
    assert RuleDo.from_dict(d.to_dict()) == d
    d2 = RuleDo(directive="do X")
    assert d2.to_dict() == {"directive": "do X"}


def test_rule_do_validation() -> None:
    with pytest.raises(ValueError, match="do.directive"):
        RuleDo(directive="  ")
    with pytest.raises(ValueError, match="do.because"):
        RuleDo(directive="ok", because="   ")


def test_replay_evidence_valid() -> None:
    ev = ReplayEvidence(
        failures_prevented=("F-001",), successes_broken=(), precision=0.9, recall=0.5
    )
    assert ev.to_dict()["precision"] == 0.9
    assert ReplayEvidence.from_dict(ev.to_dict()) == ev


def test_replay_evidence_validation() -> None:
    with pytest.raises(ValueError, match="precision"):
        ReplayEvidence(precision=1.5, recall=0.5)
    with pytest.raises(ValueError, match="recall"):
        ReplayEvidence(precision=0.5, recall=-0.1)


def test_provenance_valid() -> None:
    p = _valid_provenance()
    assert p.to_dict()["source_trajectory"] == "trajectories/2026-09-03/failure-003.jsonl"
    assert Provenance.from_dict(p.to_dict()) == p
    # minimal
    p2 = Provenance(
        source_trajectory="a.jsonl", extracted_by="m", extract_timestamp="t", extraction_pass=1
    )
    assert p2.replay_evidence is None


def test_provenance_validation() -> None:
    with pytest.raises(ValueError, match="source_trajectory"):
        Provenance(
            source_trajectory=" ", extracted_by="m", extract_timestamp="t", extraction_pass=1
        )
    with pytest.raises(ValueError, match="extracted_by"):
        Provenance(
            source_trajectory="a", extracted_by=" ", extract_timestamp="t", extraction_pass=1
        )
    with pytest.raises(ValueError, match="extraction_pass"):
        Provenance(
            source_trajectory="a", extracted_by="m", extract_timestamp="t", extraction_pass=0
        )


def test_standing_rule_valid() -> None:
    rule = StandingRule(
        id="R-018",
        when=RuleWhen(trigger="tool call to git push fails"),
        do=RuleDo(directive="Run git pull --rebase before push", because="reason"),
        confidence=0.85,
        provenance=_valid_provenance(),
        status="active",
        promoted_at="2026-09-03T18:35:00Z",
        hit_count=3,
        last_match="2026-09-10T14:00:00Z",
        tags=("git", "push"),
        taxonomy="git/push/non-fast-forward",
        template="verify-then-act",
        pack=None,
    )
    assert rule.id == "R-018"
    d = rule.to_dict()
    assert d["id"] == "R-018"
    assert d["tags"] == ["git", "push"]
    assert StandingRule.from_dict(d) == rule
    # minimal tags omits key
    rule2 = StandingRule(
        id="R-002",
        when=RuleWhen(trigger="t"),
        do=RuleDo(directive="d"),
        confidence=0.5,
        provenance=_valid_provenance(),
        status="active",
        promoted_at="2026-09-03T18:35:00Z",
    )
    assert "tags" not in rule2.to_dict()
    assert "taxonomy" not in rule2.to_dict()


def test_standing_rule_validation() -> None:
    with pytest.raises(ValueError, match="id"):
        StandingRule(
            id=" ",
            when=RuleWhen(trigger="t"),
            do=RuleDo(directive="d"),
            confidence=0.5,
            provenance=_valid_provenance(),
            status="active",
            promoted_at="2026-09-03T18:35:00Z",
        )
    with pytest.raises(ValueError, match="confidence"):
        StandingRule(
            id="R-1",
            when=RuleWhen(trigger="t"),
            do=RuleDo(directive="d"),
            confidence=1.5,
            provenance=_valid_provenance(),
            status="active",
            promoted_at="2026-09-03T18:35:00Z",
        )
    with pytest.raises(ValueError, match="promoted_at"):
        StandingRule(
            id="R-1",
            when=RuleWhen(trigger="t"),
            do=RuleDo(directive="d"),
            confidence=0.5,
            provenance=_valid_provenance(),
            status="active",
            promoted_at=" ",
        )
    with pytest.raises(ValueError, match="status"):
        StandingRule(
            id="R-1",
            when=RuleWhen(trigger="t"),
            do=RuleDo(directive="d"),
            confidence=0.5,
            provenance=_valid_provenance(),
            status="invalid",  # type: ignore[arg-type]
            promoted_at="2026-09-03T18:35:00Z",
        )
    with pytest.raises(ValueError, match="hit_count"):
        StandingRule(
            id="R-1",
            when=RuleWhen(trigger="t"),
            do=RuleDo(directive="d"),
            confidence=0.5,
            provenance=_valid_provenance(),
            status="active",
            promoted_at="2026-09-03T18:35:00Z",
            hit_count=-1,
        )
    with pytest.raises(ValueError, match="tags"):
        StandingRule(
            id="R-1",
            when=RuleWhen(trigger="t"),
            do=RuleDo(directive="d"),
            confidence=0.5,
            provenance=_valid_provenance(),
            status="active",
            promoted_at="2026-09-03T18:35:00Z",
            tags=(" ",),
        )
