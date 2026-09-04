# v0.1.0 — Work Breakdown Structure

**Goal:** Complete extract → test → promote loop on a toy agent with seeded failure history.

## Parts

| Part | Title | Milestones | Issues |
|------|-------|------------|--------|
| [1](wbs-v0.1.0-part1-foundation.md) | Foundation | M1-M2 | 8 |
| [2](wbs-v0.1.0-part2-core-engine.md) | Core Engine | M3-M5 | 12 |
| [3](wbs-v0.1.0-part3-storage-guardrails.md) | Storage & Guardrails | M6-M7 | 8 |
| [4](wbs-v0.1.0-part4-intelligence.md) | Intelligence | M8-M9 | 8 |
| [5](wbs-v0.1.0-part5-cli.md) | CLI | M10 | 6 |
| [6](wbs-v0.1.0-part6-field-test.md) | Field Test | M11 | 4 |
| [7](wbs-v0.1.0-part7-release.md) | Release | M12 | 2 |

## Milestone Map

```
M1  M2  M3  M4  M5  M6  M7  M8  M9  M10  M11  M12
│   │   │   │   │   │   │   │   │    │    │    │
└───┴───┴───┴───┴───┴───┴───┴───┴────┴────┴────┘
Part 1  Part 2      Part 3  Part 4  P5   P6   P7
```

## Dependencies

- All parts depend on Part 1 (Foundation)
- Part 3 depends on Part 2
- Parts 4-7 can work partially in parallel