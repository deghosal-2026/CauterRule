# v0.1.0 — Work Breakdown Structure

**Goal:** Ship a complete, usable, impressive system on day one. The extract → test → promote loop plus the full DX, corpus, benchmarks, MCP server, rule packs, export/import, field tests, scale tests, and adversarial testing — all in one release.

**Timeline:** 8-12 weeks

## Parts

| Part | Title | Milestones | Tasks |
|------|-------|------------|-------|
| [1](wbs-v0.1.0-part1-foundation.md) | Foundation & Data Models | M1-M3 | 16 |
| [2](wbs-v0.1.0-part2-trajectory-capture.md) | Trajectory Capture & Redaction | M4-M5 | 12 |
| [3](wbs-v0.1.0-part3-extraction.md) | Rule Extraction & Clustering | M6-M8 | 15 |
| [4](wbs-v0.1.0-part4-replay.md) | Replay Engine & Visualization | M9-M11 | 16 |
| [5](wbs-v0.1.0-part5-promotion.md) | Promotion Gate, Linter & Conflicts | M12-M14 | 17 |
| [6](wbs-v0.1.0-part6-store.md) | Rule Store, Packs, Injection & Loop | M15-M17 | 20 |
| [7](wbs-v0.1.0-part7-export-import.md) | Export, Import & MCP Server | M18-M19 | 16 |
| [8](wbs-v0.1.0-part8-cli-tui.md) | CLI, TUI & Observability | M20-M22 | 30 |
| [9](wbs-v0.1.0-part9-corpus.md) | Corpus, Benchmarks & Scale | M23-M25 | 27 |
| [10](wbs-v0.1.0-part10-safety.md) | Safety & Adversarial | M26 | 6 |
| [11](wbs-v0.1.0-part11-distribution.md) | Distribution, Demo & Examples | M28-M29 | 20 |
| [12](wbs-v0.1.0-part12-field-test.md) | Comprehensive Field Test | M30 | 42 |
| [13](wbs-v0.1.0-part13-release-readiness.md) | Release Readiness | M31 | 6 |
| [14](wbs-v0.1.0-part14-release.md) | Release | M32 | 6 |
| **Total** | | **M1-M32** | **241** |

## Milestone Map

```
M1  M2  M3  M4  M5  M6  M7  M8  M9  M10 M11 M12 M13 M14 M15
 │   │   │   │   │   │   │   │   │   │   │   │   │   │   │
 └───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘
 Part 1      Part 2    Part 3       Part 4       Part 5

M16 M17 M18 M19 M20 M21 M22 M23 M24 M25 M26 M28 M29 M30 M31 M32
 │   │   │   │   │   │   │   │   │   │   │   │   │   │   │   │
 └───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘
 Part 6    Part 7     Part 8        Part 9      P10 P11 Part 12  P13 P14
```

## Dependencies

```
Part 1 (Foundation) ──> Part 2 (Trajectory) ──> Part 3 (Extraction)
                                              ──> Part 4 (Replay)
                                              ──> Part 5 (Promotion)
Part 5 ──> Part 6 (Store & Injection) ──> Part 7 (Export & MCP)
Part 6 ──> Part 8 (CLI & TUI)
Part 4 ──> Part 9 (Corpus & Scale)
Part 9 ──> Part 10 (Safety & Adversarial)
All ──> Part 11 (Distribution & Demo)
All ──> Part 12 (Comprehensive Field Test)
```

## Exit Gate (per milestone)

Every milestone (M1-M31) must pass its exit gate before the next milestone begins:

- [ ] Run all tests: `pytest` — all pass
- [ ] Lint strict clean: `ruff check` + `mypy src/` — zero errors
- [ ] Test coverage total > 95%: `pytest --cov=src/cauterule --cov-report=term-missing`
- [ ] Update all docs affected by this milestone
- [ ] Verify all issues in this milestone are done
- [ ] Close all completed issues
- [ ] Commit with message: `milestone: M{n} complete`
- [ ] Push to main

## Final Release Gate (v0.1.0)

Before tagging v0.1.0, ALL of the following must be true:

- [ ] All 32 milestones complete and exit gates passed
- [ ] M30 field test complete and report published
- [ ] `cauterule demo` runs successfully end-to-end on macOS, Linux, and CI
- [ ] Replay precision >= 90% on public benchmark corpus
- [ ] Counterexample rejection rate >= 90%
- [ ] Secret redaction passes on redaction corpus (100%)
- [ ] Conflict detection catches seeded contradictions (>=90% recall)
- [ ] `cauterule validate` passes on shipped example rule store
- [ ] Install + demo flow works in under 5 minutes for a new user
- [ ] Lint strict clean, mypy strict, zero errors
- [ ] Test coverage total > 95%
- [ ] Documentation includes benchmark, corpus, and field-test methodology
- [ ] CONTRIBUTING.md, CHANGELOG.md, SECURITY.md published
- [ ] PyPI, Homebrew, Docker distribution verified