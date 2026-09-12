"""Shared fixtures for performance benchmarks (sizes mirror real stores)."""

from __future__ import annotations

import pytest

from cauterule.models.rule import Provenance, RuleDo, RuleWhen, StandingRule
from cauterule.models.trajectory import Step, Trajectory


def make_rule(i: int) -> StandingRule:
    """Build a synthetic standing rule."""
    return StandingRule(
        id=f"R-B{i:04d}",
        when=RuleWhen(trigger=f"synthetic failure signature number {i} in git push"),
        do=RuleDo(directive=f"apply synthetic fix {i}"),
        confidence=0.8,
        provenance=Provenance(
            source_trajectory="bench",
            extracted_by="bench",
            extract_timestamp="2026-09-01T00:00:00Z",
            extraction_pass=1,
        ),
        status="active",
        promoted_at="2026-09-01T00:00:00Z",
    )


def make_trajectory(i: int) -> Trajectory:
    """Build a synthetic failure trajectory."""
    return Trajectory(
        id=f"T-{i}",
        timestamp="2026-09-01T00:00:00Z",
        task=f"synthetic task {i}",
        steps=[
            Step(
                step_number=1,
                tool="git",
                input=f"git push attempt {i}",
                output="",
                error=f"synthetic failure signature number {i % 50} in git push",
            )
        ],
        success=False,
    )


@pytest.fixture(params=[10, 100, 300], ids=["n10", "n100", "n300"])
def rule_store(request: pytest.FixtureRequest) -> list[StandingRule]:
    """Rule lists at realistic store sizes."""
    return [make_rule(i) for i in range(request.param)]


@pytest.fixture
def trajectories() -> list[Trajectory]:
    """Fixed trajectory sample for matcher/consolidation benchmarks."""
    return [make_trajectory(i) for i in range(20)]
