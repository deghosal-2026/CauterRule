from cauterule.extraction.dedup import deduplicate, is_duplicate
from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import RuleDo, RuleWhen


def _cand(trigger: str, directive: str, context: tuple[str, ...] = ()) -> CandidateRule:
    return CandidateRule(
        when=RuleWhen(trigger=trigger, context=context),
        do=RuleDo(directive=directive),
        confidence=0.9,
    )


def test_is_duplicate() -> None:
    a = _cand("git push", "pull --rebase")
    b = _cand("  Git Push  ", "  pull --rebase  ")
    assert is_duplicate(a, b)
    c = _cand("git push", "different")
    assert not is_duplicate(a, c)
    d = _cand("git push", "pull --rebase", context=("shared branch",))
    e = _cand("git push", "pull --rebase", context=("shared branch",))
    assert is_duplicate(d, e)
    f = _cand("git push", "pull --rebase", context=("other",))
    assert not is_duplicate(d, f)


def test_deduplicate() -> None:
    cands = [_cand("t", "d"), _cand("t", "d"), _cand("other", "d")]
    deduped = deduplicate(cands)
    assert len(deduped) == 2
    assert deduped[0].when.trigger == "t"
    assert deduped[1].when.trigger == "other"


def test_deduplicate_empty() -> None:
    assert deduplicate([]) == []


def test_deduplicate_keeps_higher_confidence() -> None:
    # #732: when duplicate passes differ in confidence, keep the stronger one.
    low = CandidateRule(when=RuleWhen(trigger="t"), do=RuleDo(directive="d"), confidence=0.6)
    high = CandidateRule(when=RuleWhen(trigger="t"), do=RuleDo(directive="d"), confidence=0.9)
    deduped = deduplicate([low, high])
    assert len(deduped) == 1
    assert deduped[0].confidence == 0.9


def test_signature_difference_not_duplicate() -> None:
    # #774: same trigger/directive but different error_signature are distinct.
    a = CandidateRule(
        when=RuleWhen(trigger="git push", signature="exit 128"),
        do=RuleDo(directive="pull --rebase"),
        confidence=0.9,
    )
    b = CandidateRule(
        when=RuleWhen(trigger="git push", signature="non-fast-forward"),
        do=RuleDo(directive="pull --rebase"),
        confidence=0.9,
    )
    assert not is_duplicate(a, b)
    assert len(deduplicate([a, b])) == 2


def test_same_signature_is_duplicate() -> None:
    a = CandidateRule(
        when=RuleWhen(trigger="git push", signature="non-fast-forward"),
        do=RuleDo(directive="pull --rebase"),
        confidence=0.9,
    )
    b = CandidateRule(
        when=RuleWhen(trigger="  Git Push ", signature="Non-Fast-Forward"),
        do=RuleDo(directive=" pull --rebase "),
        confidence=0.8,
    )
    assert is_duplicate(a, b)
