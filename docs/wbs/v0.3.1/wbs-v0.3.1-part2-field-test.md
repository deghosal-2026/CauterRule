# v0.3.1 — WBS Part 2: Phase 2 — Evaluation & Field Test

**Milestone:** M2 ([v0.3.1-M2: Field Test](https://github.com/deghosal-2026/CauterRule/milestone/67))

**Theme:** Measure the fixes directly (extraction accuracy, reference signatures, reproducible report) and re-verify with a full cloud field test; run the measurements that stayed pending in v0.3.0.

---

## M2: Evaluation & Field Test (17 issues)

**Goal:** A fix-and-re-verify release. Add the missing evaluation instrumentation, freeze the corpus, run the full sweep on the corrected pipeline, measure cost / cross-session / human agreement, and publish a report whose every number is reproducible from committed artifacts.

**Execution order:** evaluation implementation (#726, #730) → plan (#733) → runner (#734) → corpus (#735) → calibration (#736) → cloud sweep (#737) → Docker (#738) → multi-env (#739) → cost (#740) → cross-session (#741) → human agreement (#742) → report (#743) → known issues (#744) → exit gate (#745). (#728, #729 frame the measurement/reproducibility goals.)

**Dependencies:** M1 complete (fixes under test). Cost/cross-session/human-agreement depend on the sweep; the report depends on all measurements.

### Evaluation & measurement (kept from the original M2)

| # | Task | Issue |
|---|------|-------|
| 2.1 | Reference corpus: add adapter/CI failure signatures | [#726](https://github.com/deghosal-2026/CauterRule/issues/726) |
| 2.2 | Make field-test report numbers reproducible from artifacts | [#728](https://github.com/deghosal-2026/CauterRule/issues/728) |
| 2.3 | Run release-gate measurements (human agreement, cross-session, cost) | [#729](https://github.com/deghosal-2026/CauterRule/issues/729) |
| 2.4 | Add extraction-accuracy metric vs `expected_rule` | [#730](https://github.com/deghosal-2026/CauterRule/issues/730) |

> These overlap the field-test tickets below (#726↔#735, #730↔#734, #729↔#740-#742, #728↔#743). They were kept per request; close each as its counterpart lands.

### Field test

| # | Task | Issue |
|---|------|-------|
| 2.5 | Create the v0.3.1 field test plan — methodology, corpora, models, thresholds, exit criteria | [#733](https://github.com/deghosal-2026/CauterRule/issues/733) |
| 2.6 | Wire M1/M2 fixes into the runner + add extraction-accuracy measurement | [#734](https://github.com/deghosal-2026/CauterRule/issues/734) |
| 2.7 | Corpus: backfill `expected_rule` and add adapter/CI reference signatures | [#735](https://github.com/deghosal-2026/CauterRule/issues/735) |
| 2.8 | Re-calibrate matcher thresholds after semantic and scorer changes | [#736](https://github.com/deghosal-2026/CauterRule/issues/736) |
| 2.9 | Re-run the full cloud field-test sweep — 2 models × 40 corpora | [#737](https://github.com/deghosal-2026/CauterRule/issues/737) |
| 2.10 | Re-run the Docker field test on the v0.3.1 image | [#738](https://github.com/deghosal-2026/CauterRule/issues/738) |
| 2.11 | Multi-environment validation — macOS, Linux, Docker | [#739](https://github.com/deghosal-2026/CauterRule/issues/739) |
| 2.12 | Cost measurement — token-enabled re-run + `$`/1k table | [#740](https://github.com/deghosal-2026/CauterRule/issues/740) |
| 2.13 | Cross-session repeat-failure reduction protocol (5 sessions) | [#741](https://github.com/deghosal-2026/CauterRule/issues/741) |
| 2.14 | Human-vs-replay agreement sampling and scoring | [#742](https://github.com/deghosal-2026/CauterRule/issues/742) |
| 2.15 | Regenerate and publish the v0.3.1 field test report (reproducible from artifacts) | [#743](https://github.com/deghosal-2026/CauterRule/issues/743) |
| 2.16 | Document known issues from the v0.3.1 field test | [#744](https://github.com/deghosal-2026/CauterRule/issues/744) |
| 2.17 | M2 exit gate — thresholds, tests, docs, committed results | [#745](https://github.com/deghosal-2026/CauterRule/issues/745) |

### Scope notes

- **Models:** cloud only — `gpt-4o-mini`, `llama-3.1-8b-instruct` (local OMLX dropped, #713).
- **Sweep command:** `.venv312` (Python 3.12) + `CAUTERULE_SEMANTIC_MATCHING=1`, OpenRouter `--max-workers 6`.
- **Artifacts:** `field-test/results/0.3.1/` (`meta.json`, `results.jsonl`, `summary.json`, `harness_health.json` per run).
- **Thresholds:** golden ≥70%, failures/positive ≥50%, nearmiss precision ≥90%, adversarial 0, generic <10%, inconclusive <15%.
- **Statistical rigor:** Wilson CIs on every rate; paired per-trajectory model deltas; golden expanded to n≥60 (#735).

### M2 Exit Gate

- [ ] **All tests pass:** `pytest` — all pass
- [ ] **Lint strict clean:** `ruff check .` — zero errors
- [ ] **Types strict clean:** `mypy src/ tests/` (strict) — zero errors
- [ ] **Test coverage > 92%** (deterministic subset)
- [ ] **All necessary and affected docs updated** (field test plan, report, per-model sheets, known issues, WBS)
- [ ] **Code committed and pushed** to `feat-v0.3.1`
- [ ] **WBS updated** (`docs/wbs/v0.3.1/`)
- [ ] **All 17 M2 issues closed**
- [ ] Full sweep complete with results committed under `field-test/results/0.3.1/`
- [ ] Release thresholds evaluated and reported (met / not-met with CIs)
- [ ] Cost, cross-session, and human-agreement measured (not `_pending_`)
- [ ] Report regenerated from artifacts; artifact-vs-report drift check passes

### See also

- [Part 1 — Critical Code Fixes](wbs-v0.3.1-part1-fixes.md)
- [Part 3 — Release Readiness & Launch](wbs-v0.3.1-part3-release.md)
- [v0.3.0 WBS Part 3](../v0.3.0/wbs-v0.3.0-part3-field-test.md) (the template)
