# PRD 09: Roadmap

## v0.1.0 — Core Loop + First-Class DX (Current)

The extract → test → promote loop plus everything that makes it usable, measurable, and shareable on day one.

**Target:** `pip install cauterule && cauterule demo` — full loop in 60 seconds. 25+ CLI commands. Bundled `pack-git`. MCP server. Export/import. `@cauterule.watch` adapter. Tiered corpus. Field tests. Scale tests. Adversarial tests.
**Timeline:** 8-12 weeks from first commit

## v0.1.1 — Framework Adapters

Plug into the frameworks people already use.

**Target:** Adapters for LangGraph, CrewAI, PydanticAI, and a decorator for custom loops. `cauterule init --adapter langgraph` scaffolds a new project.
**Timeline:** 2-3 weeks after v0.1.0

## v0.2.0 — Rule Lifecycle Management

Deepen rule lifecycle management with outcome tracking, specificity scoring, and automated retirement.

**Target:** Specificity scoring, per-rule outcome tracking, automated retirement, supersession chains, auto-promotion tuning.
**Timeline:** 4-6 weeks after v0.1.1

## v0.3.0 — Rule Pack Ecosystem

Full pack ecosystem — install, create, publish, share.

**Target:** Official packs (docker, deploy, testing, python), `cauterule pack install/publish`, pack versioning, `cauterule share <rule-id>`.
**Timeline:** 4-6 weeks after v0.2.0

## v0.4.0 — Deep Integrations

Rules as first-class artifacts accessible to any platform.

**Target:** AgentObservatory + AgentEvalForge + DecisionJournal integrations, LangSmith/Phoenix, rule testing in CI pipelines.
**Timeline:** 4-6 weeks after v0.3.0

## v0.5.0 — Observability & Analytics

See your agent's knowledge compound.

**Target:** Web dashboard (FastAPI + React), replay visualization, trend lines, weekly digest, failure recurrence tracking.
**Timeline:** 6-8 weeks after v0.4.0

## v0.6.0 — Advanced Extraction & Retrieval

Better extraction, better matching.

**Target:** Semantic rule matching (embeddings), hybrid matching, rule embedding index, cross-failure pattern detection, confidence calibration.
**Timeline:** 6-8 weeks after v0.5.0

## v0.7.0 — Multi-Agent & Cross-Agent Transfer

Rules learned by one agent benefit the fleet.

**Target:** Cross-agent rule transfer, shared rule registry, rule governance workflows, agent profiles, rule federation, `cauterule fleet`.
**Timeline:** 8-12 weeks after v0.6.0

## Dependencies

| Version | Requires |
|---------|----------|
| v0.1.0 | Python 3.11+, LLM API access (OpenAI / Anthropic / local via Ollama / LiteLLM) |
| v0.1.1 | v0.1.0 + target framework installed |
| v0.2.0 | v0.1.0 |
| v0.3.0 | v0.2.0 |
| v0.4.0 | v0.3.0 |
| v0.5.0 | v0.4.0 + React (for dashboard) |
| v0.6.0 | v0.5.0 + embedding model (local or API) |
| v0.7.0 | v0.6.0 |