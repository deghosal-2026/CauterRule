# PRD 09: Roadmap

## v0.1.0 — Core Loop (Current)

The extract → test → promote loop. The "wow" release.

**Target:** A complete loop on a toy agent with a seeded failure history showing 10+ rules extracted, tested, and promoted in <60 seconds via `cauterule demo`.
**Timeline:** 4-6 weeks from first commit

## v0.1.1 — Framework Adapters

Plug into the frameworks people already use. The "plug in" release.

**Target:** Adapters for LangGraph, CrewAI, PydanticAI, and a decorator for custom loops. `cauterule init --adapter langgraph` scaffolds a new project.
**Timeline:** 2-3 weeks after v0.1.0

## v0.2.0 — Intelligence & Rule Lifecycle

Rules live, conflict, retire, and consolidate. The "grows up" release.

**Target:** Conflict detection, specificity ordering, retirement workflow, TUI rule browser (`cauterule review`), batch review mode.
**Timeline:** 4-6 weeks after v0.1.1

## v0.3.0 — Rule Packs & Sharing

Pre-built, shareable rule collections. The "community" release.

**Target:** Official packs (`pack-git`, `pack-docker`, `pack-deploy`, `pack-testing`), `cauterule pack install/publish`, export to `.cursorrules` / `CLAUDE.md`, import from existing convention files.
**Timeline:** 4-6 weeks after v0.2.0

## v0.4.0 — MCP Server & Integrations

Rules as first-class artifacts accessible to any agent. The "plumbing" release.

**Target:** CauterRule MCP server (rules as MCP tools), GitHub Action for PR-based promotion, webhooks (Slack/Discord), AgentObservatory + AgentEvalForge + DecisionJournal integrations.
**Timeline:** 4-6 weeks after v0.3.0

## v0.5.0 — Observability & Analytics

See your agent's knowledge compound. The "dashboard" release.

**Target:** Web dashboard (FastAPI + React), replay visualization, "what if?" simulation, metrics CLI, weekly digest, failure recurrence tracking.
**Timeline:** 6-8 weeks after v0.4.0

## v0.6.0 — Advanced Extraction & Retrieval

Better extraction, better matching. The "smarter" release.

**Target:** Semantic rule matching (embeddings), hybrid matching, multi-pass extraction, cross-failure pattern detection, confidence calibration.
**Timeline:** 6-8 weeks after v0.5.0

## v0.7.0 — Multi-Agent & Cross-Agent Transfer

Rules learned by one agent benefit the fleet. The "fleet" release.

**Target:** Cross-agent rule transfer, shared rule registry, rule governance workflows, agent profiles, rule federation, `cauterule fleet` command.
**Timeline:** 8-12 weeks after v0.6.0

## Dependencies

| Version | Requires |
|---------|----------|
| v0.1.0 | Python 3.11+, LLM API access (OpenAI / Anthropic / local) |
| v0.1.1 | v0.1.0 + target framework installed |
| v0.2.0 | v0.1.0 |
| v0.3.0 | v0.2.0 |
| v0.4.0 | v0.3.0 + MCP SDK (for server), GitHub Actions (for action) |
| v0.5.0 | v0.4.0 + React (for dashboard) |
| v0.6.0 | v0.5.0 + embedding model (local or API) |
| v0.7.0 | v0.6.0 |