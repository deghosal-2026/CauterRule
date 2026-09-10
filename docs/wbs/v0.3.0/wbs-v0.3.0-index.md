# v0.3.0 — Work Breakdown Structure

**Goal:** Hardening & Ecosystem — fix critical bugs from the v0.2.0 field test, ship adapters, rule lifecycle, pack ecosystem, corpus/benchmark infra, then prove it with a full field test and release.

**Milestones:** M1-M8 (GitHub milestones 52-57, 62-63) — M1 ✓ (18/18 verified), M2 ✓ (7/13 verified, 4 deferred to M7), M3 ✓ (16/16 verified, #524→M7, #614/#615→M8), 64 open, 41 closed.

## Release Tagline

**From released to robust.** v0.2.0 shipped the product. v0.3.0 makes it trustworthy at the seams — no silent data corruption, no phantom gates, adapters for real frameworks, rules with measured specificity and tracked outcomes, and packs users can install.

---

## Parts

| Part | Title | Milestones | Tasks | Issues |
|------|-------|------------|-------|--------|
| [1](wbs-v0.3.0-part1-fixes.md) | Phase 1 — Critical Fixes & Reliability | M1-M3 (M1 ✓, M2 ✓, M3 ✓) | 50 tasks | #487-#508, #517-#527, #593-#600, #608-#616 |
| [2](wbs-v0.3.0-part2-features.md) | Phase 2 — Adapters, Lifecycle, Packs & Infra | M4-M6 | 40 tasks | #479-#481, #486, #512, #516, #534-#560, #581-#588, #601-#607 |
| [3](wbs-v0.3.0-part3-field-test.md) | Phase 3 — Field Test | M7 | 13 tasks | #625, #629, #635, #641-#642, #648, #650, #653, #658, #663, #667, #671, #673 |
| [4](wbs-v0.3.0-part4-release.md) | Phase 4 — Release Readiness & Distribution | M8 | 17 tasks | #622, #626, #630, #633, #637, #640, #645, #649, #654, #657, #661, #665, #668, #670, #674-#675 |
| **Total** | | **M1-M8** | **120 tasks** | **120 issues** |

---

## Milestone Map

```
M1 ✓    M2 ✓   M3 ✓    M4      M5      M6      M7      M8
│       │       │       │       │       │       │       │
└──┬────┴───┬───┴───┬───┘       │       │       │       │
   │       │       │           └──┬────┴───┬───┴───┬───┘
   │ Phase 1: Fixes             │ Phase 2: Features              │
   │ M1-M3 ✓                    │ M4-M6                          │
   │                            │                                 │
   └────────────────────────────┴─────────────────────────────────┘
                                    Phase 3 + 4: M7 (Field Test) → M8 (Release)
```

---

## Dependencies

```
Phase 1 (M1-M3 — Fixes) ──> Phase 2 (M4-M6 — Features)
Phase 2 (M4-M6) ──> Phase 3 (M7 — Field Test)
Phase 1 (M1-M3) ──> Phase 3 (M7)          # Safety fixes needed before field test
Phase 3 (M7) ──> Phase 4 (M8 — Release)  # Field test results feed release notes
```

**Internal dependencies within Phase 2:**
- M4 (Adapters) depends on M1-M3 (stable store/extraction to adapt)
- M4 (Lifecycle: #512 epic, #541-#545) depends on M1 replay/matcher fixes
- M5 (Packs) depends on M4 lifecycle (specificity/outcome data feeds pack certification)
- M6 (Benchmark/corpus CLI) depends on M1-M3 (deterministic replay to measure)

**Internal dependencies within Phase 1:**
- M1 (silent-corruption + security fixes) → M2 (gates can trust the data)
- M2 (corpus expansion #489, mismatch detection #487) → M3 (matcher hardening #517)
- M3 (durability) → Phase 2 (features build on durable store)

---

## Standard Milestone Exit Gate

Every milestone (M1-M8) must pass its exit gate before the next milestone begins:

- [ ] All tests run clear: `pytest` — all pass
- [ ] Total code coverage > 92%: `pytest --cov=src/cauterule --cov-report=term-missing`
- [ ] Lint strict clean: `ruff check .` + `mypy src/ tests/` — zero errors
- [ ] All necessary and affected docs are updated
- [ ] Verify all issues in this milestone are done
- [ ] Close all completed issues
- [ ] Code committed and pushed to branch (`feat-v0.3.0`)

---

## Final Release Gate (v0.3.0)

Before tagging v0.3.0, ALL of the following must be true:

- [ ] All 8 milestones complete and exit gates passed
- [ ] M7 field test complete and report published (packs/adapters/lifecycle safety)
- [ ] M8 release readiness complete (PyPI, Docker, Homebrew, docs)
- [ ] Release gate thresholds met (golden ≥ 70%, nearmiss precision ≥ 90%)
- [ ] Cross-session repeat-failure reduction measured (#496)
- [ ] Security scan clean (truffleHog, pip-audit, OpenSSF)
- [ ] Lint strict clean, mypy strict, zero errors
- [ ] Total code coverage > 92%
- [ ] Documentation includes field test report, release notes, CHANGELOG
- [ ] All distribution channels verified (PyPI, Homebrew, Docker)
- [ ] Article ideas documented and at least 1 announcement published
