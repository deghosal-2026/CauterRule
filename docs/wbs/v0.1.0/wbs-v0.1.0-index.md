# v0.1.0 — Work Breakdown Structure

**Goal:** Ship a complete, usable, impressive system on day one. The extract → test → promote loop plus the full DX, corpus, benchmarks, MCP server, rule packs, export/import, field tests, scale tests, and adversarial testing — all in one release.

**Timeline:** 8-12 weeks

## Parts

| Part | Title | Milestones | Files |
|------|-------|------------|-------|
| [1](wbs-v0.1.0-part1-foundation.md) | Foundation & Data Models | M1-M3 | 12 |
| [2](wbs-v0.1.0-part2-trajectory-capture.md) | Trajectory Capture & Redaction | M4-M5 | 10 |
| [3](wbs-v0.1.0-part3-extraction.md) | Rule Extraction & Clustering | M6-M8 | 14 |
| [4](wbs-v0.1.0-part4-replay.md) | Replay Engine & Visualization | M9-M11 | 14 |
| [5](wbs-v0.1.0-part5-promotion.md) | Promotion Gate, Linter & Conflicts | M12-M14 | 12 |
| [6](wbs-v0.1.0-part6-store.md) | Rule Store, Packs & Injection | M15-M17 | 14 |
| [7](wbs-v0.1.0-part7-export-import.md) | Export, Import & MCP Server | M18-M19 | 10 |
| [8](wbs-v0.1.0-part8-cli-tui.md) | CLI, TUI & Observability | M20-M22 | 16 |
| [9](wbs-v0.1.0-part9-corpus.md) | Corpus, Benchmarks & Scale | M23-M25 | 12 |
| [10](wbs-v0.1.0-part10-safety.md) | Safety, Adversarial & Field Tests | M26-M27 | 10 |
| [11](wbs-v0.1.0-part11-distribution.md) | Distribution, Demo & Release | M28-M30 | 10 |

## Milestone Map

```
M1  M2  M3  M4  M5  M6  M7  M8  M9  M10 M11 M12 M13 M14 M15
 │   │   │   │   │   │   │   │   │   │   │   │   │   │   │
 └───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘
 Part 1      Part 2    Part 3       Part 4       Part 5

M16 M17 M18 M19 M20 M21 M22 M23 M24 M25 M26 M27 M28 M29 M30
 │   │   │   │   │   │   │   │   │   │   │   │   │   │   │
 └───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘
 Part 6    Part 7   Part 8       Part 9    P10  Part 11
```

## Dependencies

```
Part 1 (Foundation) ──> Part 2 (Trajectory) ──> Part 3 (Extraction)
                                              ──> Part 4 (Replay)
                                              ──> Part 5 (Promotion)
Part 5 ──> Part 6 (Store & Injection) ──> Part 7 (Export & MCP)
Part 6 ──> Part 8 (CLI & TUI)
Part 4 ──> Part 9 (Corpus & Scale)
Part 9 ──> Part 10 (Safety & Field Tests)
All ──> Part 11 (Distribution & Release)
```

## Exit Gate (per part)

Every part must pass before the next begins:
- [ ] ruff clean
- [ ] mypy strict, zero errors
- [ ] pytest passes, >=80% coverage on new modules
- [ ] docs updated
- [ ] PR merged to main