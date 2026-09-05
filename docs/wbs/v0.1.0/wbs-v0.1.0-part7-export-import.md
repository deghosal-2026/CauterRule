# v0.1.0 — WBS Part 7: Export, Import & MCP Server

**Milestones:** M18-M19

## M18: Export & Import

| # | Task | Files | Behavior | Status |
|---|------|-------|----------|--------|
| 18.1 | Export to `.cursorrules` | `src/cauterule/export/cursorrules.py` | Drop-in for Cursor | ✅ |
| 18.2 | Export to `CLAUDE.md` | `src/cauterule/export/claude_md.py` | Drop-in for Claude Code | ✅ |
| 18.3 | Export to `AGENTS.md` | `src/cauterule/export/agents_md.py` | Drop-in for any agent | ✅ |
| 18.4 | Export to `.windsurfrules` | `src/cauterule/export/windsurf.py` | Drop-in for Windsurf | ✅ |
| 18.5 | Export to `aider.conf.yml` | `src/cauterule/export/aider.py` | Drop-in for Aider | ✅ |
| 18.6 | Export to markdown/JSON | `src/cauterule/export/generic.py` | Human-readable / machine-readable | ✅ |
| 18.7 | Import from `.cursorrules`/`CLAUDE.md`/`AGENTS.md` | `src/cauterule/import_/conventions.py` | Parse existing convention files into candidate rules | ✅ |
| 18.8 | Import from chat history | `src/cauterule/import_/chat_history.py` | Parse past chat corrections, convert to candidates | ✅ |
| 18.9 | Export redaction | `src/cauterule/export/redaction.py` | Strip secrets from exported rules (same redaction as trajectory) | ✅ |
| 18.10 | Export/import CLI | `src/cauterule/export/cli.py` | `cauterule export --format <format>`, `cauterule import <file>` | ✅ |

### M18 Exit Gate

- [x] Run all tests: `pytest` — all pass (509 passed)
- [x] Lint strict clean: `ruff check` + `mypy src/` — zero errors
- [x] Test coverage total > 95%: `pytest --cov=src/cauterule --cov-report=term-missing` — 95.44%
- [x] Update all docs affected by this milestone
- [x] Verify all issues in this milestone are done
- [x] Close all completed issues
- [x] Commit with message: `milestone: M18 complete` (in 024cf08)
- [x] Push to main

## M19: MCP Server

| # | Task | Files | Behavior | Status |
|---|------|-------|----------|--------|
| 19.1 | MCP server scaffold | `src/cauterule/mcp/server.py` | stdio + HTTP transport, MCP SDK integration | ✅ |
| 19.2 | `get_matching_rules` tool | `src/cauterule/mcp/tools/matching.py` | Returns rules matching a task | ✅ |
| 19.3 | `get_rule` tool | `src/cauterule/mcp/tools/get_rule.py` | Returns single rule with full provenance | ✅ |
| 19.4 | `list_rules` tool | `src/cauterule/mcp/tools/list_rules.py` | Browse rule store with filters | ✅ |
| 19.5 | `report_failure` tool | `src/cauterule/mcp/tools/report_failure.py` | Trigger extraction from MCP client | ✅ |
| 19.6 | `cauterule mcp` launcher | `src/cauterule/mcp/launch.py` | Launch MCP server from CLI | ✅ |

### M19 Exit Gate

- [x] Run all tests: `pytest` — all pass (509 passed)
- [x] Lint strict clean: `ruff check` + `mypy src/` — zero errors
- [x] Test coverage total > 95%: `pytest --cov=src/cauterule --cov-report=term-missing` — 95.44%
- [x] Update all docs affected by this milestone
- [x] Verify all issues in this milestone are done
- [x] Close all completed issues
- [x] Commit with message: `milestone: M19 complete` (in 024cf08)
- [x] Push to main
