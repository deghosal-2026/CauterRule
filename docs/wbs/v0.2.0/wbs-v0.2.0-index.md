# v0.2.0 — Work Breakdown Structure

**Goal:** Distribution & Polish — ship safety improvements, new features, comprehensive field test, and full distribution channels. Build on v0.1.0's foundation with stronger safety guarantees, TUI review, observability, corpus infrastructure, benchmarks, adversarial testing, and release-ready packaging.

**Timeline:** 6-10 weeks

## Release Tagline

**From plausible to promotable.** v0.1.0 showed the product could extract rules. v0.2.0 proves they're safe to trust — with safety-adjusted ranking, pre-extraction gates, human review, enforced thresholds, and a field test that asserts on itself.

---

## Parts

| Part | Title | Milestones | Tasks | Issues |
|------|-------|------------|-------|--------|
| [1](wbs-v0.2.0-part1-fixes.md) | Phase 1 — Fixes on Existing Code | M1-M4 | 14 tasks | #417-#430 |
| [2](wbs-v0.2.0-part2-features.md) | Phase 2 — New Features | M5-M9 | 55 tasks | #171-#219, #411-#416 |
| [3](wbs-v0.2.0-part3-field-test.md) | Phase 3 — Comprehensive Field Test | M10 | 24 tasks | #431-#451, #466-#468 |
| [4](wbs-v0.2.0-part4-release.md) | Phase 4 — Release Readiness & Distribution | M11 | 23 tasks | #34-#42, #452-#465 |
| **Total** | | **M1-M11** | **116 tasks** | **81 issues** |

---

## Milestone Map

```
M1      M2      M3      M4      M5      M6      M7      M8      M9      M10     M11
│       │       │       │       │       │       │       │       │       │       │
└──┬────┴───┬───┴───┬───┘       │       │       │       │       │       │       │
   │       │       │           └──┬────┴───┬───┴───┬───┴───┬───┘       │       │
   │ Phase 1: Fixes              │ Phase 2: New Features              │       │
   │ M1-M4                      │ M5-M9                              │       │
   │                            │                                     │       │
   └────────────────────────────┴─────────────────────────────────────┘       │
                                    Phase 3 + 4: M10 (Field Test) → M11 (Release)
```

---

## Dependencies

```
Phase 1 (M1-M4 — Fixes) ──> Phase 2 (M5-M9 — New Features)
Phase 2 (M5-M9) ──> Phase 3 (M10 — Field Test)
Phase 1 (M1-M4) ──> Phase 3 (M10)          # Safety fixes needed before field test
Phase 3 (M10) ──> Phase 4 (M11 — Release)  # Field test results feed release notes
```

**Internal dependencies within Phase 2:**
- M5 (TUI) depends on M1-M4 (candidates to review)
- M6 (Observability) depends on M1-M4 (extraction pipeline)
- M7 (Corpus) depends on M3 (larger safety corpora)
- M8 (Benchmarks) depends on M1-M4 (safety-adjusted metrics)
- M9 (Scale + Adversarial) depends on M1-M4 (stable foundation)

**Internal dependencies within Phase 1:**
- M1 (Pre-extraction gate + matcher) → M2 (Safety scoring) — matcher feeds scoring
- M2 → M3 (Corpus validation) — scoring drives corpus thresholds
- M3 → M4 (Human review + release criteria) — validated corpus enables human review

---

## Standard Milestone Exit Gate

Every milestone (M1-M11) must pass its exit gate before the next milestone begins:

- [ ] Run all tests: `pytest` — all pass
- [ ] Lint strict clean: `ruff check .` + `mypy src/ tests/` — zero errors
- [ ] Test coverage total > 95%: `pytest --cov=src/cauterule --cov-report=term-missing`
- [ ] Update all docs affected by this milestone
- [ ] Verify all issues in this milestone are done
- [ ] Close all completed issues
- [ ] Commit with message: `milestone: M{N} complete`
- [ ] Push to main

---

## Final Release Gate (v0.2.0)

Before tagging v0.2.0, ALL of the following must be true:

- [ ] All 11 milestones complete and exit gates passed
- [ ] M10 field test complete and report published with safety-adjusted ranking
- [ ] M11 release readiness complete (distribution, packaging, documentation)
- [ ] Release gate thresholds met:
  - `successes` pass rate: 0%
  - `failures/negative` pass rate: 0%
  - `nearmiss` precision: >= 90%
  - `golden` pass rate: >= 70%
  - `failures/positive` pass rate: >= 50%
- [ ] Pre-extraction gate drops 100% of success trajectories
- [ ] Human review agreement rate documented
- [ ] Harness health assertions: all pass
- [ ] Docker, Homebrew, standalone binary all verified
- [ ] Security scan clean (truffleHog, pip-audit, OpenSSF)
- [ ] Lint strict clean, mypy strict, zero errors
- [ ] Test coverage total > 95%
- [ ] Documentation includes field test report, release notes, CHANGELOG
- [ ] All distribution channels verified (PyPI, Homebrew, Docker, GitHub Action)
- [ ] Article ideas documented and at least 1 announcement published