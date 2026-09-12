"""Tests for the import module."""

from __future__ import annotations

from pathlib import Path

from cauterule.import_.chat_history import import_chat_history
from cauterule.import_.conventions import import_conventions


def test_import_conventions_cursorrules(tmp_path: Path) -> None:
    content = """# Standing Rules

You MUST follow these standing rules:

1. **When** git push fails → **Do** Run git pull --rebase before push
   - Because: remote has commits
   - Tags: git, push
"""
    p = tmp_path / ".cursorrules"
    p.write_text(content)
    rules = import_conventions(str(p))
    assert len(rules) == 1
    assert rules[0].when.trigger == "git push fails"
    assert rules[0].do.directive == "Run git pull --rebase before push"


def test_import_conventions_empty(tmp_path: Path) -> None:
    p = tmp_path / "CLAUDE.md"
    p.write_text("")
    rules = import_conventions(str(p))
    assert rules == []


def test_import_conventions_nonexistent(tmp_path: Path) -> None:
    rules = import_conventions("/tmp/nope")
    assert rules == []


def test_import_conventions_claude_md(tmp_path: Path) -> None:
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
    rules = import_conventions(str(p))
    assert len(rules) >= 1
    assert rules[0].do.directive == "Run git pull --rebase before push"


def test_import_chat_history(tmp_path: Path) -> None:
    content = """User: when the build fails, always check the logs first.
Agent: Understood.
User: rule: when deployment fails then rollback immediately.
"""
    p = tmp_path / "chat.log"
    p.write_text(content)
    rules = import_chat_history(str(p))
    assert len(rules) >= 1
    assert "deployment fails" in rules[0].when.trigger or "build fails" in rules[0].when.trigger


def test_import_chat_history_empty(tmp_path: Path) -> None:
    p = tmp_path / "empty.log"
    p.write_text("hello world")
    rules = import_chat_history(str(p))
    assert rules == []


def test_import_chat_history_nonexistent(tmp_path: Path) -> None:
    rules = import_chat_history(str(tmp_path / "nope"))
    assert rules == []
