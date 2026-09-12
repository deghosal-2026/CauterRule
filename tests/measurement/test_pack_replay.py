"""Tests for pack replay scoring (§5.3/§7.2, #479/#481)."""

from __future__ import annotations

import pytest

from cauterule.measurement.pack_replay import pack_replay_score

_TRIGGER = "docker build invalidates layer cache by copying source before installing dependencies"


def _traj(tid: str, outcome: str) -> dict[str, object]:
    return {
        "trajectory_id": tid,
        "timestamp": "2026-09-11T00:00:00Z",
        "task": _TRIGGER,
        "steps": [
            {
                "step_number": 1,
                "tool": "docker",
                "input": "docker build .",
                "output": "",
                "error": "layer cache invalidated: source copied before dependencies installed",
            }
        ],
        "success": outcome == "should_silence",
        "failure_class": "docker/build" if outcome != "should_silence" else None,
        "domain": "docker",
        "quality_label": "clear",
        "severity": "medium",
        "tags": ["docker", "build"],
        "expected_outcome": outcome,
    }


def test_pack_score_all_prevented() -> None:
    rules: list[dict[str, object]] = [{"id": "R-DOCKER-001", "trigger": _TRIGGER}]
    report = pack_replay_score(
        "pack-docker",
        rules,
        [_traj("t1", "should_extract"), _traj("t2", "should_extract")],
    )
    assert report.pack == "pack-docker"
    assert report.prevented == 2
    assert report.broke == 0
    assert report.score == 1.0
    assert report.meets_target is True


def test_pack_score_counts_broke_on_should_silence() -> None:
    rules: list[dict[str, object]] = [{"id": "R-DOCKER-001", "trigger": _TRIGGER}]
    report = pack_replay_score(
        "pack-docker",
        rules,
        [_traj("t1", "should_extract"), _traj("t2", "should_silence")],
    )
    assert report.prevented == 1
    assert report.broke == 1
    assert report.score == pytest.approx(0.5)
    assert report.meets_target is True  # 0.5 meets the >=0.5 gate


def test_pack_score_no_matches_is_zero() -> None:
    rules: list[dict[str, object]] = [
        {"id": "R-DOCKER-001", "trigger": "unrelated enterprise kubernetes terraform trigger"}
    ]
    report = pack_replay_score("pack-docker", rules, [_traj("t1", "should_extract")])
    assert report.prevented == 0
    assert report.broke == 0
    assert report.score == 0.0
    assert report.meets_target is False


def test_pack_score_below_target_when_broke_dominates() -> None:
    rules: list[dict[str, object]] = [{"id": "R-DOCKER-001", "trigger": _TRIGGER}]
    report = pack_replay_score(
        "pack-docker",
        rules,
        [_traj("t1", "should_silence"), _traj("t2", "should_silence")],
    )
    assert report.broke == 2
    assert report.score == 0.0
    assert report.meets_target is False
