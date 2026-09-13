"""Negative control: replay verdicts ignore ``do.directive`` (#762, Phase 0).

The *text* replay gate has zero discriminating power over the directive — the
verdict is a pure function of ``when.trigger`` (+ context/signature) and the
trajectory text. These two tests pin that property so a matcher refactor cannot
quietly change it.

Phase 1 of #762 adds directive-aware grounding to the **behavioral-outcome**
signal (see ``test_outcome_path_is_directive_discriminating`` and
``test_outcome_directive_grounding.py``). Promoting on that signal is a
separate, measurement-affecting decision; the text path is intentionally
unchanged for now. See #762 and #720.
"""

from __future__ import annotations

from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.models.trajectory import Step, Trajectory
from cauterule.replay.outcome import simulate_outcome
from cauterule.replay.report import build_evidence_report
from cauterule.replay.simulator import simulate

_TRIGGER = "when git push fails with non-fast-forward"

_DIRECTIVES = (
    "pull latest changes before pushing",  # correct
    "force push with --force to overwrite the remote branch",  # destructive
    "delete the remote branch and recreate it from scratch",  # destructive
    "water the office plants",  # nonsense
)

_TRAJECTORIES = (
    Trajectory(
        id="F1",
        timestamp="t",
        task="git push origin main",
        steps=(Step(1, "bash", error="rejected: non-fast-forward"),),
        success=False,
        failure_class="git/push/non-fast-forward",
    ),
    Trajectory(
        id="S1",
        timestamp="t",
        task="git push origin main",
        steps=(),
        success=True,
        failure_class="git/push",
    ),
    Trajectory(
        id="S2",
        timestamp="t",
        task="npm install completed",
        steps=(),
        success=True,
    ),
)


def _candidate(directive: str) -> CandidateRule:
    return CandidateRule(
        when=RuleWhen(trigger=_TRIGGER),
        do=RuleDo(directive=directive),
        confidence=0.9,
    )


def test_simulate_outcomes_are_directive_invariant() -> None:
    vectors = {
        d: tuple(simulate(_candidate(d), t) for t in _TRAJECTORIES) for d in _DIRECTIVES
    }
    expected = vectors[_DIRECTIVES[0]]
    for directive, vector in vectors.items():
        assert vector == expected, directive


def test_evidence_is_directive_invariant() -> None:
    reports = {d: build_evidence_report(_candidate(d), list(_TRAJECTORIES)) for d in _DIRECTIVES}
    first = reports[_DIRECTIVES[0]]
    for directive, report in reports.items():
        assert report.precision == first.precision, directive
        assert report.verdict == first.verdict, directive
        assert report.failures_prevented == first.failures_prevented, directive


def test_outcome_path_is_directive_discriminating() -> None:
    # Phase 1 of #762: the *grounded-outcome* signal, unlike the text verdict,
    # must separate the correct directive from unanchored ones.
    correct, _force, destructive, nonsense = _DIRECTIVES
    vectors = {
        d: tuple(simulate_outcome(_candidate(d), t) for t in _TRAJECTORIES)
        for d in _DIRECTIVES
    }
    assert vectors[correct][0] == "prevented"
    assert vectors[destructive][0] == "unverified"
    assert vectors[nonsense][0] == "unverified"
    assert vectors[correct] != vectors[destructive]
    assert vectors[correct] != vectors[nonsense]
