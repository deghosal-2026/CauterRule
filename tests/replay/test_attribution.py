"""Tests for inconclusive verdict attribution."""

from cauterule.models.candidate import CandidateRule
from cauterule.models.evidence import EvidenceReport
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.models.trajectory import Step, Trajectory
from cauterule.replay.attribution import (
    attribute_inconclusive,
    summarize_inconclusive,
)
from cauterule.replay.report import build_evidence_report


def _cand(trigger: str) -> CandidateRule:
    return CandidateRule(when=RuleWhen(trigger=trigger), do=RuleDo(directive="d"), confidence=0.9)


def _traj(
    tid: str = "T-001",
    task: str = "git push",
    error: str = "non-fast-forward",
    success: bool = False,
) -> Trajectory:
    return Trajectory(
        id=tid,
        timestamp="t",
        task=task,
        steps=(Step(1, "bash", error=error),),
        success=success,
    )


def _report(
    verdict: str = "inconclusive",
    reason: str | None = None,
    prevented: tuple[str, ...] = (),
    broken: tuple[str, ...] = (),
    near_misses: tuple[str, ...] = (),
) -> EvidenceReport:
    return EvidenceReport(
        failures_prevented=prevented,
        successes_broken=broken,
        near_misses=near_misses,
        verdict=verdict,  # type: ignore[arg-type]
        inconclusive_reason=reason,  # type: ignore[arg-type]
    )


def test_broad_trigger() -> None:
    cand = _cand("when a command fails")
    trajs = [_traj(f"T-{i}") for i in range(3)]
    evidence = _report()
    assert attribute_inconclusive(cand, trajs, evidence) == "broad_trigger"


def test_matcher_gap() -> None:
    cand = _cand("when git push fails with non-fast-forward on shared branch")
    trajs = [_traj(f"T-{i}", task="unrelated docker build", error="oom") for i in range(3)]
    evidence = _report()
    assert attribute_inconclusive(cand, trajs, evidence) == "matcher_gap"


def test_corpus_mismatch_small_history() -> None:
    cand = _cand("when git push fails with non-fast-forward on shared branch")
    trajs = [_traj()]
    evidence = _report()
    assert attribute_inconclusive(cand, trajs, evidence) == "corpus_mismatch"


def test_ambiguous_evidence_near_miss() -> None:
    cand = _cand("when git push fails on shared branch")
    trajs = [_traj(f"T-{i}") for i in range(3)]
    evidence = _report(near_misses=("T-001",))
    assert attribute_inconclusive(cand, trajs, evidence) == "ambiguous_evidence"


def test_report_sets_reason_on_inconclusive() -> None:
    cand = _cand("when a command fails")
    trajs = [_traj(f"T-{i}") for i in range(3)]
    report = build_evidence_report(cand, trajs)
    if report.verdict == "inconclusive":
        assert report.inconclusive_reason in (
            "broad_trigger",
            "matcher_gap",
            "corpus_mismatch",
            "ambiguous_evidence",
        )


def test_report_no_reason_on_decisive() -> None:
    cand = _cand("git push")
    trajs = [_traj(f"T-{i}") for i in range(3)]
    report = build_evidence_report(cand, trajs)
    if report.verdict != "inconclusive":
        assert report.inconclusive_reason is None


def test_summarize_inconclusive() -> None:
    reports = [
        _report(reason="broad_trigger"),
        _report(reason="broad_trigger"),
        _report(reason="matcher_gap"),
        _report(verdict="pass"),
        _report(verdict="fail"),
        _report(),  # inconclusive without reason — not counted
    ]
    summary = summarize_inconclusive(reports)
    assert summary == {
        "broad_trigger": 2,
        "matcher_gap": 1,
        "corpus_mismatch": 0,
        "ambiguous_evidence": 0,
    }


def test_evidence_roundtrip_with_reason() -> None:
    report = _report(reason="matcher_gap")
    restored = EvidenceReport.from_dict(report.to_dict())
    assert restored.inconclusive_reason == "matcher_gap"


def test_evidence_roundtrip_without_reason() -> None:
    report = _report()
    d = report.to_dict()
    assert "inconclusive_reason" not in d
    restored = EvidenceReport.from_dict(d)
    assert restored.inconclusive_reason is None
