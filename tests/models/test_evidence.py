import pytest

from cauterule.models.evidence import EvidenceReport


def test_evidence_valid() -> None:
    e = EvidenceReport(
        failures_prevented=("F-001",),
        successes_broken=(),
        near_misses=("N-1",),
        precision=0.9,
        recall=0.5,
        verdict="pass",
        replay_trace=({"step": 1},),
    )
    assert e.precision == 0.9
    d = e.to_dict()
    assert d["verdict"] == "pass"
    assert EvidenceReport.from_dict(d) == e
    # default verdict
    e2 = EvidenceReport()
    assert e2.verdict == "inconclusive"


def test_evidence_validation() -> None:
    with pytest.raises(ValueError, match="precision"):
        EvidenceReport(precision=1.5)
    with pytest.raises(ValueError, match="recall"):
        EvidenceReport(recall=-0.1)
    with pytest.raises(ValueError, match="verdict"):
        EvidenceReport(verdict="bad")  # type: ignore[arg-type]
