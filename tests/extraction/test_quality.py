from cauterule.extraction.quality import check_quality, is_valid
from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.models.trajectory import Step, Trajectory


def _traj() -> Trajectory:
    return Trajectory(
        id="T-001",
        timestamp="t",
        task="git push fails on shared branch",
        steps=(Step(step_number=1, tool="bash", error="non-fast-forward rejected"),),
        success=False,
        failure_class="git/push",
    )


def _candidate(trigger: str = "git push fails", directive: str = "pull --rebase first", confidence: float = 0.9) -> CandidateRule:
    return CandidateRule(
        when=RuleWhen(trigger=trigger),
        do=RuleDo(directive=directive),
        confidence=confidence,
        extraction_pass=1,
    )


def test_quality_valid() -> None:
    c = _candidate()
    warnings = check_quality(c, _traj())
    assert warnings == []
    assert is_valid(c, _traj())


def test_quality_low_confidence() -> None:
    c = _candidate(confidence=0.5)
    warnings = check_quality(c, _traj())
    assert any("confidence" in w for w in warnings)
    assert not is_valid(c, _traj())


def test_quality_tautological() -> None:
    c = _candidate(trigger="same", directive="same")
    warnings = check_quality(c, _traj())
    assert any("tautological" in w for w in warnings)


def test_quality_no_reference() -> None:
    # trajectory has git push, candidate talks about unrelated
    c = CandidateRule(
        when=RuleWhen(trigger="unrelated trigger about unicorns"),
        do=RuleDo(directive="do unrelated unicorn thing"),
        confidence=0.9,
    )
    warnings = check_quality(c, _traj())
    assert any("does not reference" in w for w in warnings)


def test_quality_phrase_tautology() -> None:
    c = CandidateRule(
        when=RuleWhen(trigger="when failing happens"),
        do=RuleDo(directive="don't fail"),
        confidence=0.9,
    )
    warnings = check_quality(c, _traj())
    # This may trigger tautological phrase check
    # Our check is when fail in trigger and don't fail in directive
    # Here trigger contains "when fail" and directive contains "don't fail"
    assert any("tautological" in w for w in warnings)


def test_quality_threshold_param() -> None:
    # #497: threshold comes from the caller, not a hardcode.
    c = _candidate(confidence=0.65)
    assert check_quality(c, _traj()) == []
    assert check_quality(c, _traj(), threshold=0.7) != []
    assert is_valid(c, _traj(), threshold=0.7) is False
