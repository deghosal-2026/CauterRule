"""Tests for corpus replay diagnostics (#690)."""

from __future__ import annotations

import json
from pathlib import Path

from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.models.trajectory import Step, Trajectory
from cauterule.replay.diagnostics import (
    candidate_funnel,
    diagnose_corpus,
    load_jsonl_trajectories,
    reference_coverage,
)


def _cand(trigger: str, context: tuple[str, ...] = ()) -> CandidateRule:
    return CandidateRule(
        when=RuleWhen(trigger=trigger, context=context),
        do=RuleDo(directive="d"),
        confidence=0.9,
    )


def _traj(failure_class: str | None) -> Trajectory:
    return Trajectory(
        id=f"T-{failure_class}",
        timestamp="t",
        task="do work",
        steps=(Step(1, "bash", error="err"),),
        success=False,
        failure_class=failure_class,
    )


def test_candidate_funnel_partitions_before_scoring() -> None:
    candidates = [
        _cand("step_1"),
        _cand("error"),
        _cand("distinctive failure signature"),
        _cand("another distinctive signature"),
    ]
    funnel = candidate_funnel(candidates)
    assert funnel.total == 4
    assert funnel.degenerate == 1
    assert funnel.generic == 1
    assert funnel.scored == 2


def test_candidate_funnel_generic_allowed_with_context() -> None:
    funnel = candidate_funnel([_cand("error", context=("fatal",))])
    assert funnel.generic == 0
    assert funnel.scored == 1


def test_reference_coverage_groups_by_domain_segment() -> None:
    coverage = reference_coverage(
        [_traj("git/push"), _traj("git/push"), _traj("docker/build"), _traj(None)]
    )
    assert coverage["git"] == 2
    assert coverage["docker"] == 1
    assert coverage["unknown"] == 1


def test_diagnose_corpus_flags_uncovered_target_domains() -> None:
    targets = [_traj("otel/exporter"), _traj("otel/sampling")]
    references = [_traj("git/push") for _ in range(5)]
    diag = diagnose_corpus("otel", targets, references)
    assert diag.target_count == 2
    assert diag.uncovered_domains == ("otel",)
    assert diag.reference_sufficient is True


def test_diagnose_corpus_flags_insufficient_reference_set() -> None:
    diag = diagnose_corpus("otel", [_traj("otel/exporter")], [_traj("git/push")])
    assert diag.reference_sufficient is False


def test_load_jsonl_trajectories_round_trip(tmp_path: Path) -> None:
    payload = _traj("git/push").to_dict()
    file = tmp_path / "corpus.jsonl"
    file.write_text(json.dumps(payload) + "\n\n", encoding="utf-8")
    loaded = load_jsonl_trajectories(file)
    assert len(loaded) == 1
    assert loaded[0].failure_class == "git/push"
