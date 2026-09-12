# v0.4.0 — Work Breakdown Structure

**Goal:** Intelligence & Scale — deep integrations with the agent ecosystem, semantic/hybrid matching, a web dashboard with analytics, multi-agent fleet support, then field test and release.

**Milestones:** M1-M6 (GitHub milestones 58-61, 64-65) — 66 open issues, 0 closed.

## Release Tagline

**From robust to intelligent.** v0.3.0 hardened the core. v0.4.0 makes it perceptive — embedding-based matching that understands paraphrase, a dashboard that shows learning over time, and fleets of agents sharing one rule registry.

---

## Parts

| Part | Title | Milestones | Tasks | Issues |
|------|-------|------------|-------|--------|
| [1](wbs-v0.4.0-part1-integrations.md) | Phase 1 — Deep Integrations & Observability | M1-M2 | 18 tasks | #482-#485, #528-#530, #533, #535, #539, #561-#562, #566-#569, #589-#590 |
| [2](wbs-v0.4.0-part2-matching.md) | Phase 2 — Advanced Matching, Extraction & Fleet | M3-M4 | 19 tasks | #509-#511, #513-#515, #570-#580, #591-#592 |
| [3](wbs-v0.4.0-part3-field-test.md) | Phase 3 — Field Test | M5 | 12 tasks | #619, #624, #628, #631, #636, #638, #643, #647, #652, #656, #659, #664 |
| [4](wbs-v0.4.0-part4-release.md) | Phase 4 — Release Readiness & Distribution | M6 | 17 tasks | #617-#618, #621, #623, #627, #632, #634, #639, #644, #646, #651, #655, #660, #662, #666, #669, #672 |
| **Total** | | **M1-M6** | **66 tasks** | **66 issues** |

---

## Milestone Map

```
M1      M2      M3      M4      M5      M6
│       │       │       │       │       │
└──┬────┴───┬───┴───┬───┘       │       │
   │       │       │           │       │
   │ Phase 1       │ Phase 2   │       │
   │ M1-M2         │ M3-M4     │       │
   │               │           │       │
   └───────────────┴───────────┘       │
          Phase 3: M5 (Field Test) → M6 (Release)
```

---

## Dependencies

```
Phase 1 (M1-M2 — Integrations + Observability) ──> Phase 2 (M3-M4 — Matching + Fleet)
Phase 2 (M3-M4) ──> Phase 3 (M5 — Field Test)
Phase 1 (M1-M2) ──> Phase 3 (M5)          # Integration trajectories feed field test
Phase 3 (M5) ──> Phase 4 (M6 — Release)  # Field test results feed release notes
```

**Internal dependencies within Phase 2:**
- M3 (semantic/hybrid matcher #509 epic, #570-#571) before fleet transfer (adaptation needs good matching)
- Outcome tracking prerequisite (#561) gates derived metrics (#589) and trend lines (#562)
- M4 fleet registry (#576) before governance (#577), profiles (#578), federation (#579)

---

## Standard Milestone Exit Gate

Every milestone (M1-M6) must pass its exit gate before the next milestone begins:

- [ ] All tests run clear: `pytest` — all pass
- [ ] Total code coverage > 92%: `pytest --cov=src/cauterule --cov-report=term-missing`
- [ ] Lint strict clean: `ruff check .` + `mypy src/ tests/` — zero errors
- [ ] All necessary and affected docs are updated
- [ ] Verify all issues in this milestone are done
- [ ] Close all completed issues
- [ ] Code committed and pushed to branch (v0.4.0 branch — TBD, confirm before Phase 1)

---

## Final Release Gate (v0.4.0)

Before tagging v0.4.0, ALL of the following must be true:

- [ ] All 6 milestones complete and exit gates passed
- [ ] M5 field test complete and report published (semantic + fleet results)
- [ ] M6 release readiness complete (PyPI, Docker multi-arch, Homebrew, docs)
- [ ] Release gate thresholds met (golden ≥ 70%, nearmiss precision ≥ 90%)
- [ ] Semantic/hybrid ablation shows hybrid ≥ heuristic on golden + failures-positive
- [ ] Security scan clean (truffleHog, pip-audit, OpenSSF) with new integration footprint
- [ ] Lint strict clean, mypy strict, zero errors
- [ ] Total code coverage > 92%
- [ ] Documentation includes field test report, release notes, CHANGELOG
- [ ] All distribution channels verified (PyPI incl. TestPyPI, Docker, Homebrew)
- [ ] Article ideas documented and at least 1 announcement published
