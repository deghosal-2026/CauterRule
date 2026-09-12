"""Tests for the export module.

# SECURITY-FIXTURE: token-like strings in this module are intentional fake
# credentials used to verify redaction. None are real secrets.
"""

from __future__ import annotations

import json
from pathlib import Path

from cauterule.export.agents_md import export as export_agents_md
from cauterule.export.aider import export as export_aider
from cauterule.export.claude_md import export as export_claude_md
from cauterule.export.cli import export_rules, import_rules
from cauterule.export.cursorrules import export as export_cursorrules
from cauterule.export.generic import export_json, export_markdown
from cauterule.export.redaction import contains_secret, redact_export
from cauterule.export.windsurf import export as export_windsurf
from cauterule.models.rule import (
    Provenance,
    ReplayEvidence,
    RuleDo,
    RuleWhen,
    StandingRule,
)


def _make_rule(
    trigger: str = "git push fails",
    directive: str = "Run git pull --rebase before push",
    because: str | None = "remote has commits",
    tags: tuple[str, ...] = ("git", "push"),
    confidence: float = 0.85,
) -> StandingRule:
    return StandingRule(
        id="R-001",
        when=RuleWhen(trigger=trigger),
        do=RuleDo(directive=directive, because=because),
        confidence=confidence,
        provenance=Provenance(
            source_trajectory="t.jsonl",
            extracted_by="gpt-4o",
            extract_timestamp="2026-09-03T18:30:00Z",
            extraction_pass=2,
            replay_evidence=ReplayEvidence(
                failures_prevented=("F-001",), successes_broken=(), precision=1.0, recall=0.28
            ),
            promotion_commit="abc123",
            promotion_mode="auto",
        ),
        status="active",
        promoted_at="2026-09-03T18:35:00Z",
        hit_count=3,
        last_match="2026-09-10T14:00:00Z",
        tags=tags,
        taxonomy="git/push/non-fast-forward",
        template="verify-then-act",
        pack=None,
    )


def test_export_cursorrules() -> None:
    rule = _make_rule()
    result = export_cursorrules([rule])
    assert "**When**" in result
    assert "git push fails" in result
    assert "Run git pull --rebase before push" in result
    assert "Because:" in result
    assert "git, push" in result
    assert result.startswith("# Standing Rules")


def test_export_cursorrules_empty() -> None:
    result = export_cursorrules([])
    assert "# Standing Rules" in result


def test_export_claude_md() -> None:
    rule = _make_rule()
    result = export_claude_md([rule])
    assert "## Rules" in result
    assert "**When:**" in result
    assert "**Do:**" in result
    assert "git push fails" in result
    assert "Confidence" in result


def test_export_agents_md() -> None:
    rule = _make_rule()
    result = export_agents_md([rule])
    assert "**When:**" in result
    assert "**Do:**" in result
    assert "**Taxonomy:**" in result
    assert "git/push/non-fast-forward" in result


def test_export_windsurf() -> None:
    rule = _make_rule()
    result = export_windsurf([rule])
    assert "## Standing Rules" in result
    assert "When `git push fails`" in result
    assert "Rationale:" in result


def test_export_aider() -> None:
    rule = _make_rule()
    result = export_aider([rule])
    assert "rules:" in result
    assert 'when: "git push fails"' in result
    assert 'do: "Run git pull --rebase before push"' in result


def test_export_aider_empty() -> None:
    result = export_aider([])
    assert "rules: []" in result


def test_export_markdown() -> None:
    rule = _make_rule()
    result = export_markdown([rule])
    assert "## Rule 1" in result
    assert "**When:**" in result
    assert "**Do:**" in result


def test_export_json() -> None:
    rule = _make_rule()
    result = export_json([rule])
    data = json.loads(result)
    assert len(data) == 1
    assert data[0]["id"] == "R-001"
    assert data[0]["when"]["trigger"] == "git push fails"
    assert data[0]["do"]["directive"] == "Run git pull --rebase before push"
    assert data[0]["confidence"] == 0.85


def test_export_json_empty() -> None:
    result = export_json([])
    data = json.loads(result)
    assert data == []


def test_redact_export() -> None:
    assert "[REDACTED]" in redact_export("API key: sk-12345678901234567890abc")
    assert redact_export("normal text") == "normal text"


def test_contains_secret_in_export() -> None:
    assert contains_secret("AKIAIOSFODNN7EXAMPLE")
    assert not contains_secret("hello world")


def test_export_rules_dispatch() -> None:
    rules = [_make_rule()]
    result = export_rules(rules, "cursorrules")
    assert "**When**" in result
    result = export_rules(rules, "json")
    data = json.loads(result)
    assert len(data) == 1
    result = export_rules(rules, "markdown")
    assert "## Rule 1" in result


def test_export_rules_unknown_format() -> None:
    import pytest

    with pytest.raises(ValueError, match="Unknown export format"):
        export_rules([_make_rule()], "bogus")


def test_import_rules_empty_file(tmp_path: Path) -> None:
    p = tmp_path / "chat.log"
    p.write_text("hello world")
    result = import_rules(str(p))
    assert result == []


def test_import_rules_nonexistent(tmp_path: Path) -> None:
    p = tmp_path / "nope"
    result = import_rules(str(p))
    assert result == []
