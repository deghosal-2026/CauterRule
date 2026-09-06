"""Verify export/import round-trip via Python API in Docker context."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from cauterule.export.cli import export_rules, import_rules
from cauterule.models.rule import (
    Provenance,
    ReplayEvidence,
    RuleDo,
    RuleWhen,
    StandingRule,
    Status,
)


def _make_rule(
    trigger: str = "git push fails",
    directive: str = "Run git pull --rebase before push",
    because: str | None = "remote has commits",
    tags: tuple[str, ...] = ("git", "push"),
    confidence: float = 0.85,
    status: Status = "active",
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
        status=status,
        promoted_at="2026-09-03T18:35:00Z",
        hit_count=3,
        last_match="2026-09-10T14:00:00Z",
        tags=tags,
        taxonomy="git/push/non-fast-forward",
        template="verify-then-act",
        pack=None,
    )


def _make_retired_rule() -> StandingRule:
    return StandingRule(
        id="R-099",
        when=RuleWhen(trigger="old pattern"),
        do=RuleDo(directive="ignore it"),
        confidence=0.3,
        provenance=Provenance(
            source_trajectory="old.jsonl",
            extracted_by="gpt-4o",
            extract_timestamp="2026-06-01T12:00:00Z",
            extraction_pass=1,
        ),
        status="retired",
        promoted_at="2026-06-01T12:00:00Z",
        retired_at="2026-08-01T12:00:00Z",
        retirement_reason="superseded",
    )


@pytest.mark.docker
def test_export_cursorrules() -> None:
    result = export_rules([_make_rule()], "cursorrules")
    assert result.startswith("# Standing Rules")
    assert "**When**" in result
    assert "git push fails" in result
    assert "Run git pull --rebase before push" in result


@pytest.mark.docker
def test_export_claude_md() -> None:
    result = export_rules([_make_rule()], "claude")
    assert "## Rules" in result
    assert "**When:**" in result
    assert "**Do:**" in result
    assert "Confidence" in result


@pytest.mark.docker
def test_export_agents_md() -> None:
    result = export_rules([_make_rule()], "agents")
    assert "**When:**" in result
    assert "**Do:**" in result
    assert "**Taxonomy:**" in result


@pytest.mark.docker
def test_export_windsurf() -> None:
    result = export_rules([_make_rule()], "windsurf")
    assert "## Standing Rules" in result
    assert "When `git push fails`" in result
    assert "Rationale:" in result


@pytest.mark.docker
def test_export_aider() -> None:
    result = export_rules([_make_rule()], "aider")
    assert "rules:" in result
    parsed = yaml.safe_load(result)
    assert isinstance(parsed, dict)
    assert "rules" in parsed


@pytest.mark.docker
def test_export_markdown() -> None:
    result = export_rules([_make_rule()], "markdown")
    assert "## Rule 1" in result
    assert "**When:**" in result
    assert "**Do:**" in result


@pytest.mark.docker
def test_export_json() -> None:
    result = export_rules([_make_rule()], "json")
    data = json.loads(result)
    assert len(data) == 1
    assert data[0]["id"] == "R-001"
    assert data[0]["when"]["trigger"] == "git push fails"


@pytest.mark.docker
def test_export_active_only() -> None:
    rules = [_make_rule(), _make_retired_rule()]
    result = export_rules(rules, "json")
    data = json.loads(result)
    assert len(data) == 1
    assert data[0]["id"] == "R-001"


@pytest.mark.docker
def test_export_include_retired() -> None:
    rules = [_make_rule(), _make_retired_rule()]
    result = export_rules(rules, "json", include_retired=True)
    data = json.loads(result)
    assert len(data) == 2
    ids = {d["id"] for d in data}
    assert ids == {"R-001", "R-099"}


@pytest.mark.docker
def test_import_cursorrules(tmp_path: Path) -> None:
    content = """# Standing Rules

You MUST follow these standing rules:

1. **When** git push fails → **Do** Run git pull --rebase before push
   - Because: remote has commits
   - Tags: git, push
"""
    p = tmp_path / ".cursorrules"
    p.write_text(content)
    rules = import_rules(str(p))
    assert len(rules) == 1
    assert rules[0].when.trigger == "git push fails"
    assert rules[0].do.directive == "Run git pull --rebase before push"


@pytest.mark.docker
def test_import_claude_md(tmp_path: Path) -> None:
    content = """# Standing Rules

## Rules

### Rule 1
- **When:** git push fails
- **Do:** Run git pull --rebase before push
- **Because:** remote has commits
- **Tags:** git, push
- **Confidence:** 0.85
"""
    p = tmp_path / "CLAUDE.md"
    p.write_text(content)
    rules = import_rules(str(p))
    assert len(rules) >= 1
    assert rules[0].do.directive == "Run git pull --rebase before push"


@pytest.mark.docker
def test_import_agents_md(tmp_path: Path) -> None:
    content = """# Standing Rules

The following standing rules apply:

## Rule 1
- **When:** git push fails
- **Do:** Run git pull --rebase before push
- **Because:** remote has commits
"""
    p = tmp_path / "AGENTS.md"
    p.write_text(content)
    rules = import_rules(str(p))
    assert len(rules) >= 1
    assert rules[0].when.trigger == "git push fails"
    assert rules[0].do.directive == "Run git pull --rebase before push"


@pytest.mark.docker
def test_import_chat_history(tmp_path: Path) -> None:
    content = """User: rule: when deployment fails then rollback immediately.
Agent: Understood.
"""
    p = tmp_path / "chat.log"
    p.write_text(content)
    rules = import_rules(str(p))
    assert len(rules) >= 1
    assert "deployment fails" in rules[0].when.trigger
