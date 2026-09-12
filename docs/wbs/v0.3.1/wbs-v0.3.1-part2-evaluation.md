# v0.3.1 — WBS Part 2: Phase 2 — Evaluation & Measurement

**Milestone:** M2 ([v0.3.1-M2: Evaluation & Measurement](https://github.com/deghosal-2026/CauterRule/milestone/67))

**Theme:** Measure extraction directly, close the reference-corpus gap, run the release-gate measurements that were tooled but never executed, and make the field-test report reproducible from committed artifacts.

---

## M2: Evaluation & Measurement (4 issues)

**Goal:** Turn the v0.3.0 "unknowns" into measured numbers. The v0.3.0 report carried three `_pending_` placeholders (cost table, cross-session, human agreement), no extraction-accuracy metric, no adapter/CI references, and headline numbers that could not be reproduced from `field-test/results/0.3.0/`.

**Execution order:** #730 (extraction metric) → #726 (corpus) → #729 (measurements) → #728 (report reproducibility).

**Dependencies:** M1 (measurement must run on corrected code).

| # | Task | Severity | Issue |
|---|------|----------|-------|
| 2.1 | Add extraction-accuracy metric vs `expected_rule` (parse + score + report) | High | [#730](https://github.com/deghosal-2026/CauterRule/issues/730) |
| 2.2 | Reference corpus: add adapter/CI failure signatures (langgraph/crewai/pydanticai + CI) | High | [#726](https://github.com/deghosal-2026/CauterRule/issues/726) |
| 2.3 | Run release-gate measurements — human agreement, cross-session, cost | High | [#729](https://github.com/deghosal-2026/CauterRule/issues/729) |
| 2.4 | Make field-test report numbers reproducible from committed artifacts | Medium | [#728](https://github.com/deghosal-2026/CauterRule/issues/728) |

### Context (from the v0.3.0 field test)

- `expected_rule` is populated on 23/50 `failures_positive` and 288 `reference-expansion` trajectories, and is **null in `golden`** — the ground truth exists but is dropped at parse (`Trajectory` has no such field) (#730).
- A naive token-F1 of the best extracted rule vs `expected_rule` reaches only ~0.58 (llama) / ~0.50 (gpt-4o-mini) on `failures_positive` — the model rewords, and a token comparator can't see through it (#730).
- `adapters` (0/60) and `raw_ci` (0/110) both fail because their domain slices carry no matching signatures (#726).
- Committed golden `verdict`s are pre-tolerance-band (30% both models) while the report headlines 40-50%; the band-applied run was never committed (#728).
- `docs/field-test/v0.3.0/human-agreement.md`, `cost-measurement.md`, `cross-session-results.md` are `_pending_` (#729).

### M2 Exit Gate

- [ ] **All tests pass:** `pytest` — all pass
- [ ] **Lint strict clean:** `ruff check .` — zero errors
- [ ] **Types strict clean:** `mypy src/ tests/` (strict) — zero errors
- [ ] **Test coverage > 92%** (deterministic subset)
- [ ] **All necessary and affected docs updated** (extraction metric, corpus diagnostics, report reproducibility note)
- [ ] **Code committed and pushed** to `feat-v0.3.1`
- [ ] **WBS updated** (`docs/wbs/v0.3.1/`)
- [ ] **All 4 M2 issues closed**
- [ ] `expected_rule` parsed and scored; `extraction_f1` emitted in `summary.json`
- [ ] `adapters` / `raw_ci` produce non-zero `prevented` on a smoke run

### See also

- [Part 1 — Critical Code Fixes](wbs-v0.3.1-part1-fixes.md)
- [Part 3 — Field Test](wbs-v0.3.1-part3-field-test.md)
- [corpus-diagnostics.md](../../field-test/v0.3.0/corpus-diagnostics.md) · [human-agreement.md](../../field-test/v0.3.0/human-agreement.md) · [cost-measurement.md](../../field-test/v0.3.0/cost-measurement.md)
