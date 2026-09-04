# Design Documents

Design docs for CauterRule — organized by subsystem and PRD.

## PRD

| # | Document | Description |
|---|----------|-------------|
| 01 | [Why](prd/01-why.md) | Problem statement and motivation |
| 02 | [Architecture](prd/02-architecture.md) | System architecture overview |
| 03 | [Landscape](prd/03-landscape.md) | Competitive and adjacent landscape |
| 04 | [Users and CUJs](prd/04-users-and-cujs.md) | Users, critical user journeys |
| 05 | [Features](prd/05-features.md) | Feature breakdown by version |
| 06 | [Security Baseline](prd/06-security-baseline.md) | Security considerations |
| 07 | [Success Metrics](prd/07-success-metrics.md) | How we measure success |
| 08 | [Risks](prd/08-risks.md) | Risks, hard parts, mitigations |
| 09 | [Roadmap](prd/09-roadmap.md) | Version roadmap and timeline |

## Subsystem Designs

| D# | Document | Topic |
|----|----------|-------|
| D1 | [standing-rule-format-design.md](standing-rule-format-design.md) | Standing rule format (*when X, do Y*) |
| D2 | [trajectory-schema-design.md](trajectory-schema-design.md) | Trajectory capture schema |
| D3 | [rule-extractor-design.md](rule-extractor-design.md) | LLM extraction of candidate rules |
| D4 | [historical-replay-design.md](historical-replay-design.md) | Historical replay engine |
| D5 | [promotion-gate-design.md](promotion-gate-design.md) | Evidence-based promotion gate |
| D6 | [rule-store-design.md](rule-store-design.md) | Versioned YAML rule store |
| D7 | [rule-injection-design.md](rule-injection-design.md) | Context injection on matching tasks |
| D8 | [conflict-detection-design.md](conflict-detection-design.md) | Precedence and specificity ordering |
| D9 | [loop-orchestration-design.md](loop-orchestration-design.md) | Overall extract-test-promote loop |

## Cross-Cutting

- [Design Decisions](design-decisions.md) — all DD-01 through DD-NN