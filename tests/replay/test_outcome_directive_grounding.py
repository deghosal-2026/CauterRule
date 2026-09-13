"""Directive-aware grounding — Phase 1 of #762.

A trigger match only counts as ``verified_prevented`` / ``verified_broken``
when the directive is anchored to the failure. Directives that say nothing
about the failure (nonsense) or that would erase the state (delete/recreate)
must not be credited.
"""

from __future__ import annotations

from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.models.trajectory import Step, Trajectory
from cauterule.replay.outcome import build_outcome_report, simulate_outcome

_TRIGGER = "when git push fails with non-fast-forward"
_CORRECT = "pull latest changes before pushing"
_DESTRUCTIVE = "delete the remote branch and recreate it from scratch"
_NONSENSE = "water the office plants"


def _cand(directive: str) -> CandidateRule:
    return CandidateRule(
        when=RuleWhen(trigger=_TRIGGER),
        do=RuleDo(directive=directive),
        confidence=0.9,
    )


def _failure() -> Trajectory:
    return Trajectory(
        id="F1",
        timestamp="t",
        task="git push origin main",
        steps=(Step(1, "bash", error="rejected: non-fast-forward"),),
        success=False,
        failure_class="git/push/non-fast-forward",
    )


def test_correct_directive_is_verified_prevented() -> None:
    assert simulate_outcome(_cand(_CORRECT), _failure()) == "prevented"


def test_nonsense_directive_is_unverified() -> None:
    assert simulate_outcome(_cand(_NONSENSE), _failure()) == "unverified"


def test_destructive_directive_is_unverified() -> None:
    assert simulate_outcome(_cand(_DESTRUCTIVE), _failure()) == "unverified"


def test_outcome_report_excludes_unanchored_directives() -> None:
    trajs = [_failure() for _ in range(3)]

    good = build_outcome_report(_cand(_CORRECT), trajs)
    assert len(good.verified_prevented) == 3
    assert good.verdict == "pass"

    for directive in (_DESTRUCTIVE, _NONSENSE):
        report = build_outcome_report(_cand(directive), trajs)
        assert report.verified_prevented == (), directive
        assert len(report.unverified) == 3, directive
