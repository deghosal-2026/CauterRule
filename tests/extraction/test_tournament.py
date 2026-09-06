"""Tests for the tournament module."""
from __future__ import annotations

from unittest.mock import ANY, MagicMock, patch

from cauterule.extraction.tournament import run_tournament
from cauterule.models.candidate import CandidateRule
from cauterule.models.evidence import EvidenceReport
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.models.trajectory import Step, Trajectory


def _cand(trigger: str) -> CandidateRule:
    return CandidateRule(when=RuleWhen(trigger=trigger), do=RuleDo(directive="d"), confidence=0.9)


def _traj(id: str, task: str, success: bool) -> Trajectory:
    return Trajectory(id=id, timestamp="t", task=task, steps=(Step(1, "bash", error="err"),) if not success else (), success=success)


def test_tournament_basic() -> None:
    c1 = _cand("git push")
    c2 = _cand("docker")
    trajs = [_traj("T-1", "git push fails", False), _traj("T-2", "docker fails", False), _traj("T-3", "git push ok", True)]
    with patch("cauterule.extraction.tournament.build_evidence_report") as mock_build:
        def fake_report(cand: CandidateRule, trajs: list[Trajectory]) -> EvidenceReport:
            if "git" in cand.when.trigger:
                return EvidenceReport(failures_prevented=("T-1",), precision=1.0, recall=0.5, verdict="inconclusive")
            return EvidenceReport(failures_prevented=("T-2",), precision=1.0, recall=0.5, verdict="inconclusive")
        mock_build.side_effect = fake_report
        ranked = run_tournament([c1, c2], trajs)
    assert len(ranked) == 2
    assert ranked[0].rank == 1
    # Both have precision == 1.0 and prevented >= 1, so both get verdict "pass"
    assert ranked[0].evidence.verdict == "pass"
    assert ranked[1].evidence.verdict == "pass"


def test_tournament_empty() -> None:
    assert run_tournament([], []) == []


def test_tournament_no_trajectories() -> None:
    c = _cand("trigger")
    with patch("cauterule.extraction.tournament.build_evidence_report") as mock_build:
        mock_build.return_value = EvidenceReport(precision=0.0, recall=0.0, verdict="inconclusive")
        ranked = run_tournament([c], [])
    assert len(ranked) == 1
    assert ranked[0].evidence.precision == 0.0
    # No failures prevented -> verdict should be "fail" after overrides
    assert ranked[0].evidence.verdict == "fail"


def test_tournament_verdict_threshold() -> None:
    """Verdict is pass only if precision == 1.0 and prevented >= 1."""
    c = _cand("test")
    trajs = [_traj("T-1", "test fails", False)]
    with patch("cauterule.extraction.tournament.build_evidence_report") as mock_build:
        mock_build.return_value = EvidenceReport(failures_prevented=("T-1",), precision=0.5, recall=1.0, verdict="inconclusive")
        ranked = run_tournament([c], trajs)
    # Precision < 1.0, so verdict should be "fail"
    assert ranked[0].evidence.verdict == "fail"

    with patch("cauterule.extraction.tournament.build_evidence_report") as mock_build:
        mock_build.return_value = EvidenceReport(failures_prevented=(), precision=1.0, recall=0.0, verdict="inconclusive")
        ranked = run_tournament([c], trajs)
    # prevented < 1, so verdict should be "fail"
    assert ranked[0].evidence.verdict == "fail"