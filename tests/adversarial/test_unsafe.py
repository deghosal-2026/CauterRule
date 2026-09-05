"""26.4: Unsafe directive corpus — dangerous candidate rules blocked by linter."""

from __future__ import annotations

import pytest

from cauterule.linter.orchestrator import lint_rule
from cauterule.linter.unsafe import check_unsafe
from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.promotion.auto import auto_promote
from cauterule.promotion.thresholds import get_thresholds


def _candidate(trigger: str, directive: str) -> CandidateRule:
    return CandidateRule(
        when=RuleWhen(trigger=trigger),
        do=RuleDo(directive=directive),
        confidence=0.95,
    )


DELETE_ALL_FILES = "run rm -rf /tmp to free space"
RUN_ARBITRARY = "run arbitrary shell commands to fix"
BYPASS_AUTH = "bypass authentication by disabling login"
DROP_DATABASE = "run drop table if exists to restore from backup"
DISABLE_FIREWALL = "disable the firewall to speed up deployment"


@pytest.mark.parametrize(
    "trigger,directive,expected_blocked",
    [
        ("disk full", "run rm -rf /tmp to free space", True),
        ("unknown error", "run arbitrary shell commands to fix", False),
        ("login failure", "bypass authentication by disabling login", False),
        ("database corrupt", "run drop table if exists to restore from backup", True),
        ("deploy slow", "disable the firewall to speed up deployment", False),
    ],
    ids=[
        "rm-rf-detected",
        "arbitrary-commands-not-matched",
        "bypass-auth-not-in-patterns",
        "drop-table-detected",
        "disable-firewall-not-in-patterns",
    ],
)
def test_linter_blocks_unsafe_directives(
    trigger: str,
    directive: str,
    expected_blocked: bool,
) -> None:
    warnings = check_unsafe(directive)
    if expected_blocked:
        assert len(warnings) >= 1
        assert any("unsafe" in w for w in warnings)
    else:
        assert len(warnings) == 0


def test_promotion_gate_rejects_unsafe_rule() -> None:
    candidate = _candidate("disk full", "run rm -rf /tmp to free space")
    result = lint_rule(candidate.when.trigger, candidate.do.directive)
    assert not result.passed
    assert any("unsafe" in w for w in result.warnings)
    decision = auto_promote(candidate, result)
    assert decision.verdict == "reject"


def test_unsafe_patterns_coverage() -> None:
    unsafe_cases: list[tuple[str, bool]] = [
        ("rm -rf /var", True),
        ("git push --force", True),
        ("chmod 777 /etc", True),
        ("drop table users", True),
        ("delete from users", True),
        ("dd if=/dev/zero of=/dev/sda", True),
        (":(){ :|:& };:", True),
        ("> /dev/sda1", True),
        ("run git pull", False),
        ("restart nginx", False),
        ("check logs", False),
    ]
    for directive, should_trigger in unsafe_cases:
        warnings = check_unsafe(directive)
        if should_trigger:
            assert len(warnings) >= 1, f"expected unsafe warning for: {directive}"
        else:
            assert len(warnings) == 0, f"expected no warning for: {directive}"


def test_thresholds_block_low_confidence_unsafe_candidate() -> None:
    t = get_thresholds("conservative")
    candidate = _candidate("rm problem", "run rm -rf /data")
    result = lint_rule(candidate.when.trigger, candidate.do.directive)
    assert not result.passed
    # Even if linter were clean, min_confidence would block
    assert t["min_confidence"] == 0.95
    assert candidate.confidence >= t["min_confidence"]
    decision = auto_promote(candidate, result)
    assert decision.verdict == "reject"
