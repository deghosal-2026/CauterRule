# v0.3.1 — WBS Part 3: Phase 3 — Field Test

**Milestone:** M3 ([v0.3.1-M3: Field Test](https://github.com/deghosal-2026/CauterRule/milestone/68))

**Theme:** Re-verify the M1/M2 fixes with a full cloud field test, run the measurements that stayed pending in v0.3.0, and publish a report whose every number is reproducible from committed artifacts.

---

## M3: Field Test (13 issues)

**Goal:** A fix-and-re-verify release. Freeze the corpus, run the full sweep on the corrected pipeline, measure cost / cross-session / human agreement, and compare against the committed v0.3.0 baseline.

**Execution order:** plan (#733) → runner (#734) → corpus (#735) → calibration (#736) → cloud sweep (#737) → Docker (#738) → multi-env (#739) → cost (#740) → cross-session (#741) → human agreement (#742) → report (#743) → known issues (#744) → exit gate (#745).

**Dependencies:** M1 + M2 complete (fixes + metrics under test). Cost/cross-session/human-agreement depend on the sweep; the report depends on all measurements.

| # | Task | Issue |
|---|------|-------|
| 3.1 | Create the v0.3.1 field test plan — methodology, corpora, models, thresholds, exit criteria | [#733](https://github.com/deghosal-2026/CauterRule/issues/733) |
| 3.2 | Wire M1/M2 fixes into the runner + add extraction-accuracy measurement | [#734](https://github.com/deghosal-2026/CauterRule/issues/734) |
| 3.3 | Corpus: backfill `expected_rule` and add adapter/CI reference signatures | [#735](https://github.com/deghosal-2026/CauterRule/issues/735) |
| 3.4 | Re-calibrate matcher thresholds after semantic and scorer changes | [#736](https://github.com/deghosal-2026/CauterRule/issues/736) |
| 3.5 | Re-run the full cloud field-test sweep — 2 models × 40 corpora | [#737](https://github.com/deghosal-2026/CauterRule/issues/737) |
| 3.6 | Re-run the Docker field test on the v0.3.1 image | [#738](https://github.com/deghosal-2026/CauterRule/issues/738) |
| 3.7 | Multi-environment validation — macOS, Linux, Docker | [#739](https://github.com/deghosal-2026/CauterRule/issues/739) |
| 3.8 | Cost measurement — token-enabled re-run + `$`/1k table | [#740](https://github.com/deghosal-2026/CauterRule/issues/740) |
| 3.9 | Cross-session repeat-failure reduction protocol (5 sessions) | [#741](https://github.com/deghosal-2026/CauterRule/issues/741) |
| 3.10 | Human-vs-replay agreement sampling and scoring | [#742](https://github.com/deghosal-2026/CauterRule/issues/742) |
| 3.11 | Regenerate and publish the v0.3.1 field test report (reproducible from artifacts) | [#743](https://github.com/deghosal-2026/CauterRule/issues/743) |
| 3.12 | Document known issues from the v0.3.1 field test | [#744](https://github.com/deghosal-2026/CauterRule/issues/744) |
| 3.13 | M3 exit gate — thresholds, tests, docs, committed results | [#745](https://github.com/deghosal-2026/CauterRule/issues/745) |

### Scope notes

- **Models:** cloud only — `gpt-4o-mini`, `llama-3.1-8b-instruct` (local OMLX dropped, #713).
- **Sweep command:** `.venv312` (Python 3.12) + `CAUTERULE_SEMANTIC_MATCHING=1`, OpenRouter `--max-workers 6`.
- **Artifacts:** `field-test/results/0.3.1/` (`meta.json`, `results.jsonl`, `summary.json`, `harness_health.json` per run).
- **Thresholds:** golden ≥70%, failures/positive ≥50%, nearmiss precision ≥90%, adversarial 0, generic <10%, inconclusive <15%.
- **Statistical rigor:** Wilson CIs on every rate; paired per-trajectory model deltas; golden expanded to n≥60 (#735).

### M3 Exit Gate

- [ ] **All tests pass:** `pytest` — all pass
- [ ] **Lint strict clean:** `ruff check .` — zero errors
- [ ] **Types strict clean:** `mypy src/ tests/` (strict) — zero errors
- [ ] **Test coverage > 92%** (deterministic subset)
- [ ] **All necessary and affected docs updated** (field test plan, report, per-model sheets, known issues, WBS)
- [ ] **Code committed and pushed** to `feat-v0.3.1`
- [ ] **WBS updated** (`docs/wbs/v0.3.1/`)
- [ ] **All 13 M3 issues closed**
- [ ] Full sweep complete with results committed under `field-test/results/0.3.1/`
- [ ] Release thresholds evaluated and reported (met / not-met with CIs)
- [ ] Cost, cross-session, and human-agreement measured (not `_pending_`)
- [ ] Report regenerated from artifacts; artifact-vs-report drift check passes

### See also

- [Part 2 — Evaluation & Measurement](wbs-v0.3.1-part2-evaluation.md)
- [Part 4 — Release Readiness & Launch](wbs-v0.3.1-part4-release.md)
- [v0.3.0 WBS Part 3](../v0.3.0/wbs-v0.3.0-part3-field-test.md) (the template)
