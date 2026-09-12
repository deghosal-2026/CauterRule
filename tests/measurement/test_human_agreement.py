"""Tests for human-vs-replay agreement (§5.5/§15.9, #493)."""

from __future__ import annotations

import pytest

from cauterule.measurement.human_agreement import (
    HUMAN_GATE_THRESHOLD,
    agreement_rate,
    human_agreement_report,
    sample_for_review,
)


def _r(tid: str, replay: str, human: str) -> dict[str, object]:
    return {"trajectory_id": tid, "replay_verdict": replay, "human_verdict": human}


def test_agreement_rate_all_match() -> None:
    reviews = [_r("a", "pass", "pass"), _r("b", "fail", "fail")]
    assert agreement_rate(reviews) == 1.0


def test_agreement_rate_partial() -> None:
    reviews = [_r("a", "pass", "pass"), _r("b", "fail", "pass")]
    assert agreement_rate(reviews) == pytest.approx(0.5)


def test_agreement_rate_empty_is_zero() -> None:
    assert agreement_rate([]) == 0.0


def test_report_flags_below_gate() -> None:
    report = human_agreement_report(
        [_r("a", "pass", "pass"), _r("b", "fail", "pass"), _r("c", "pass", "fail")]
    )
    assert report.reviewed == 3
    assert report.matches == 1
    assert report.agreement == pytest.approx(1 / 3)
    assert report.below_gate is True
    assert report.gate_threshold == HUMAN_GATE_THRESHOLD


def test_report_at_or_above_gate() -> None:
    report = human_agreement_report(
        [
            _r("a", "pass", "pass"),
            _r("b", "fail", "fail"),
            _r("c", "pass", "pass"),
            _r("d", "fail", "fail"),
            _r("e", "pass", "fail"),
        ]
    )
    assert report.agreement == pytest.approx(0.8)
    assert report.below_gate is False


def test_sample_for_review_takes_per_bucket() -> None:
    results: list[dict[str, object]] = [
        {"trajectory_id": "a", "best": {"verdict": "pass"}},
        {"trajectory_id": "b", "best": {"verdict": "pass"}},
        {"trajectory_id": "c", "best": {"verdict": "fail"}},
        {"trajectory_id": "d", "best": {"verdict": "inconclusive"}},
    ]
    sampled = sample_for_review(results, per_bucket=1)
    by_bucket: dict[str, int] = {}
    for item in sampled:
        bucket = str(item["bucket"])
        by_bucket[bucket] = by_bucket.get(bucket, 0) + 1
    assert by_bucket == {"pass": 1, "fail": 1, "inconclusive": 1}
