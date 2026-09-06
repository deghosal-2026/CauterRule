# Design Documents

Design docs for CauterRule — organized by subsystem and PRD.

## PRD

| # | Document | Description |
|---|----------|-------------|
| 01 | [Why](prd/01-why.md) | Problem statement and motivation |
| 02 | [Architecture](prd/02-architecture.md) | System architecture overview (13 components) |
| 03 | [Landscape](prd/03-landscape.md) | Competitive and adjacent landscape (researched) |
| 04 | [Users and CUJs](prd/04-users-and-cujs.md) | Users, 11 critical user journeys |
| 05 | [Features](prd/05-features.md) | Feature breakdown by version (v0.1.0-v0.7.0) |
| 06 | [Security Baseline](prd/06-security-baseline.md) | Security considerations, 7 threats, adversarial coverage |
| 07 | [Success Metrics](prd/07-success-metrics.md) | How we measure success (10 categories, release gates) |
| 08 | [Risks](prd/08-risks.md) | 11 risks, hard parts, mitigations |
| 09 | [Roadmap](prd/09-roadmap.md) | Version roadmap and timeline |

## Subsystem Designs

| D# | Document | Topic |
|----|----------|-------|
| D1 | [standing-rule-format-design.md](standing-rule-format-design.md) | Standing rule format (*when X, do Y*), tags, taxonomy, templates, linter |
| D2 | [trajectory-schema-design.md](trajectory-schema-design.md) | Trajectory capture schema, metadata, redaction, corpus tiers |
| D3 | [rule-extractor-design.md](rule-extractor-design.md) | Multi-pass extraction, clustering, draft tournament, dry-run, human correction |
| D4 | [historical-replay-design.md](historical-replay-design.md) | Replay engine, visualization, time machine, what-if, determinism |
| D5 | [promotion-gate-design.md](promotion-gate-design.md) | Three modes (auto/hybrid/human), linter + conflict integration, batch |
| D6 | [rule-store-design.md](rule-store-design.md) | Versioned YAML store, tags, packs, validation, health, consolidation |
| D7 | [rule-injection-design.md](rule-injection-design.md) | Structured matching, explanations, templates, context budget, preflight |
| D8 | [conflict-detection-design.md](conflict-detection-design.md) | Contradiction, specificity, supersession, consolidation, linter integration |
| D9 | [loop-orchestration-design.md](loop-orchestration-design.md) | Full loop with clustering, redaction, multi-pass, tournament, preflight |

## Cross-Cutting

- [Design Decisions](design-decisions.md) — DD-01 through DD-18