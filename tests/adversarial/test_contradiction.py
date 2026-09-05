"""26.3: Contradiction stress test — seeded contradictions between StandingRules."""

from __future__ import annotations

import pytest

from cauterule.conflict.contradiction import detect_contradictions
from cauterule.models.rule import Provenance, RuleDo, RuleWhen, StandingRule


def _rule(rid: str, trigger: str, directive: str) -> StandingRule:
    return StandingRule(
        id=rid,
        when=RuleWhen(trigger=trigger),
        do=RuleDo(directive=directive),
        confidence=0.9,
        provenance=Provenance(
            source_trajectory="t.json",
            extracted_by="test",
            extract_timestamp="2026-09-05T00:00:00Z",
            extraction_pass=1,
        ),
        status="active",
        promoted_at="2026-09-05T00:00:00Z",
    )


COMMIT_BEFORE_PULL = "always commit before pulling"
PULL_BEFORE_COMMIT = "always pull before committing"
FORCE_PUSH = "use force push to resolve conflicts"
REBASE_INSTEAD = "rebase instead of merging"
DELETE_REMOTE = "delete the remote branch"
KEEP_REMOTE = "keep the remote branch"
DISABLE_CI = "disable CI checks"
RUN_CI_FIRST = "run CI checks first"


@pytest.mark.parametrize(
    "rules,expected_contradictions",
    [
        (
            [
                _rule("R-001", "when using git", "always commit before pulling"),
                _rule("R-002", "when using git", "always pull before committing"),
            ],
            1,
        ),
        (
            [
                _rule("R-003", "merge conflict", "use force push to resolve conflicts"),
                _rule("R-004", "merge conflict", "rebase instead of merging"),
            ],
            1,
        ),
        (
            [
                _rule("R-005", "branch cleanup", "delete the remote branch"),
                _rule("R-006", "branch cleanup", "keep the remote branch"),
            ],
            1,
        ),
        (
            [
                _rule("R-007", "ci pipeline fails", "disable CI checks"),
                _rule("R-008", "ci pipeline fails", "run CI checks first"),
            ],
            1,
        ),
        (
            [
                _rule("R-009", "server error", "restart the server"),
                _rule("R-010", "server error", "restart the server"),
            ],
            0,
        ),
    ],
    ids=[
        "commit-order-contradiction",
        "merge-conflict-resolution",
        "branch-cleanup-strategy",
        "ci-pipeline-handling",
        "same-directive-no-contradiction",
    ],
)
def test_seeded_contradictions_detected(
    rules: list[StandingRule],
    expected_contradictions: int,
) -> None:
    reports = detect_contradictions(rules)
    assert len(reports) == expected_contradictions
    for r in reports:
        assert r.type == "contradiction"
        assert len(r.rules) >= 2


def test_contradiction_across_three_rules() -> None:
    rules = [
        _rule("R-011", "deploy to prod", "deploy on friday"),
        _rule("R-012", "deploy to prod", "never deploy on friday"),
        _rule("R-013", "deploy to prod", "deploy only on monday"),
    ]
    reports = detect_contradictions(rules)
    # Three active rules with same trigger → 3 choose 2 = 3 pairs
    assert len(reports) == 3
    involved_ids = {rid for r in reports for rid in r.rules}
    assert "R-011" in involved_ids
    assert "R-012" in involved_ids
    assert "R-013" in involved_ids


def test_contradiction_retired_ignored() -> None:
    active = _rule("R-014", "hotfix", "apply directly to prod")
    retired = StandingRule(
        id="R-015",
        when=RuleWhen(trigger="hotfix"),
        do=RuleDo(directive="always test in staging first"),
        confidence=0.9,
        provenance=Provenance(
            source_trajectory="t.json",
            extracted_by="test",
            extract_timestamp="2026-09-05T00:00:00Z",
            extraction_pass=1,
        ),
        status="retired",
        promoted_at="2026-09-05T00:00:00Z",
    )
    reports = detect_contradictions([active, retired])
    assert len(reports) == 0
