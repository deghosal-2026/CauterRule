# CauterRule Docs

Documentation for the CauterRule project — automated standing-rule extraction from agent failures.

**Current release:** v0.3.0 (2026-09-12) — Hardening & Ecosystem.

## Sections

| Directory | Purpose |
|-----------|---------|
| [design/](design/) | Design documents: PRD (9 files), subsystem designs (9 files), design decisions (18 DDs) |
| [packs/](packs/) | Pack authoring: format, certification, publish/share |
| [corpus/](corpus/) | Corpus contribution guide and format specification |
| [wbs/](wbs/) | Work breakdown structure, organized by version |
| [field-test/](field-test/) | Field test plans and reports, organized by version |
| [release/](release/) | Release notes, organized by version |

## v0.3.0

- [Release notes](release/v0.3.0/release-notes.md)
- [Field test report](field-test/v0.3.0/FIELD_TEST_REPORT.md) — 40 corpora × 2 cloud models, 4,768 runs
- [Adapters & rule lifecycle](ADAPTERS.md) — generic `@watch`, LangGraph, CrewAI, PydanticAI + conformance harness
- [Observability](observability.md) — `observe`, `metrics`, `leaderboard`, OpenTelemetry, token/cost capture
- [Contributing packs](packs/CONTRIBUTING-PACKS.md) — `pack.yaml` format, certification, publish/share
- [Corpus contribution guide](corpus/CONTRIBUTING.md) and [format spec](corpus/format-spec.md)
- [User guide](USER_GUIDE.md)
- [CHANGELOG](../CHANGELOG.md)
- [SECURITY](../SECURITY.md)

## Quick Links

- [PRD: Why](design/prd/01-why.md)
- [Architecture](design/prd/02-architecture.md)
- [Features (v0.1.0-v0.7.0)](design/prd/05-features.md)
- [Success Metrics](design/prd/07-success-metrics.md)
- [Risks](design/prd/08-risks.md)
- [Roadmap](design/prd/09-roadmap.md)
- [Design Decisions (DD-01 to DD-18)](design/design-decisions.md)
- [Standing Rule Format](design/standing-rule-format-design.md)
- [Trajectory Schema](design/trajectory-schema-design.md)
- [Rule Extractor](design/rule-extractor-design.md)
- [Historical Replay Engine](design/historical-replay-design.md)
- [Promotion Gate](design/promotion-gate-design.md)
- [Rule Store](design/rule-store-design.md)
- [Rule Injection](design/rule-injection-design.md)
- [Conflict Detection](design/conflict-detection-design.md)
- [Loop Orchestration](design/loop-orchestration-design.md)
- [v0.1.0 WBS Index](wbs/v0.1.0/wbs-v0.1.0-index.md) — 32 milestones, 241 tasks

## Conventions

- **BLUF** — Bottom Line Up Front in major documents
- **Exit gates** — standardized checklists for milestone completion
- **Design decisions** — centralized in `design/design-decisions.md`, referenced by DD-NN
- **Versioned directories** — each documentation type is organized by version
