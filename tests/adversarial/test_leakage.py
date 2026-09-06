"""26.6: Instruction leakage test — secrets do not survive export."""

from __future__ import annotations

import pytest

from cauterule.export.redaction import contains_secret, redact_export
from cauterule.models.rule import Provenance, RuleDo, RuleWhen, StandingRule
from cauterule.redaction.engine import redact_text


def _rule_with_secret(directive: str) -> StandingRule:
    return StandingRule(
        id="R-LEAK",
        when=RuleWhen(trigger="deploy"),
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


RULES_WITH_SECRETS = [
    (
        _rule_with_secret("use API key AKIAIOSFODNN7EXAMPLE for auth"),
        "AKIAIOSFODNN7EXAMPLE",
    ),
    (
        _rule_with_secret("token is ghp_123456789012345678901234567890123456"),
        "ghp_123456789012345678901234567890123456",
    ),
    (
        _rule_with_secret("Bearer token eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIn0.dummy for auth"),
        "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIn0.dummy",
    ),
    (
        _rule_with_secret("password: s3cr3t, do not share"),
        "s3cr3t",
    ),
    (
        _rule_with_secret("private key: -----BEGIN PRIVATE KEY----- abcdef"),
        "-----BEGIN PRIVATE KEY-----",
    ),
]


@pytest.mark.parametrize(
    "rule,secret_fragment",
    [
        (r, s) for r, s in RULES_WITH_SECRETS
    ],
    ids=[
        "aws-key",
        "github-token",
        "jwt-token",
        "password",
        "private-key",
    ],
)
def test_secret_in_directive_redacted_by_engine(
    rule: StandingRule,
    secret_fragment: str,
) -> None:
    redacted = redact_text(rule.do.directive)
    assert "[REDACTED]" in redacted
    assert secret_fragment not in redacted


def test_secret_in_trigger_redacted_by_engine() -> None:
    rule_with_secret_trigger = StandingRule(
        id="R-TRIG",
        when=RuleWhen(trigger="deploy with token sk-12345678901234567890abc"),
        do=RuleDo(directive="verify"),
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
    redacted = redact_text(rule_with_secret_trigger.when.trigger)
    assert "[REDACTED]" in redacted


def test_secret_in_because_redacted_by_engine() -> None:
    rule = StandingRule(
        id="R-BEC",
        when=RuleWhen(trigger="login"),
        do=RuleDo(directive="refresh", because="token ghp_123456789012345678901234567890123456 expired"),
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
    assert rule.do.because is not None
    redacted = redact_text(rule.do.because)
    assert "[REDACTED]" in redacted


def test_export_redact_wrapper_strips_secrets() -> None:
    leaky_text = "API key AKIAIOSFODNN7EXAMPLE and token ghp_123456789012345678901234567890123456"
    redacted = redact_export(leaky_text)
    assert "[REDACTED]" in redacted
    assert "AKIAIOSFODNN7EXAMPLE" not in redacted
    assert "ghp_" not in redacted


def test_contains_secret_detects_leakage() -> None:
    assert contains_secret("sk-12345678901234567890abc")
    assert contains_secret("-----BEGIN RSA PRIVATE KEY-----")
    assert not contains_secret("safe deployment instruction")
    assert not contains_secret("")


def test_clean_rule_no_leakage() -> None:
    clean_directive = "run git pull --rebase before push"
    assert "[REDACTED]" not in redact_text(clean_directive)
    assert not contains_secret(clean_directive)
