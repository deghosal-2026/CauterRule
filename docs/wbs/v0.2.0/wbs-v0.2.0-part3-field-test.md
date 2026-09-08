# v0.2.0 — WBS Part 3: Phase 3 — Comprehensive Field Test

**Milestone:** M10

**Theme:** Field test — model bake-off, corpus sweep, results report modeled on v0.1.0 M30. Every milestone includes code review, lint strict, coverage >95%, docs updated.

---

## M10: Comprehensive Field Test

**Goal:** Run a comprehensive field test across all v0.2.0 features, with safety-adjusted metrics, enforced release thresholds, and harness health assertions. Produce a report with release gate verdict.

**Input:** `docs/field-test/v0.2.0/field-test-plan.md` — executable field-test plan with methodology (§15) and corpus plan (§14). M10 consumes this to drive sweeps, runner scripts, and corpus.

**Dependencies:** M1-M9 (all features must be complete before field test)

**Structure:** Three buckets — Pre-Field Validation, Field Tests, Reporting.

```
Field Test Design (10.22-10.24) ──> Pre-Field Validation ──> Field Tests ──> Reporting
```

### Bucket 0: Field Test Design (from changes-needed.md)

These are the design tasks that consume `docs/field-test/v0.2.0/changes-needed.md` to create the executable field-test artifacts. They must complete before pre-field validation.

| # | Task | Issue | Files | Behavior | Status |
|---|------|-------|-------|----------|--------|
| 10.22 | Create 0.2.0 field test plan from changes-needed.md — methodology, corpus plan, thresholds, scoring | [#466](https://github.com/deghosal-2026/CauterRule/issues/466) | `docs/field-test/v0.2.0/field-test-plan.md` | Translate changes-needed.md into executable plan covering all M1-M9 changes: corpus (new public/adversarial), new tests (benchmarks, adversarial, scale, TUI, observability), new methodology (gate, matcher, specificity, safety scoring, human review, harness health), new thresholds (0% successes/negative, ≥90% nearmiss), new scoring (safety-adjusted ranking, decision economics, cost) | ✅ |
| 10.23 | Update field test runner scripts to handle v0.2.0 changes — preflight, harness, gate, thresholds, scoring | [#467](https://github.com/deghosal-2026/CauterRule/issues/467) | `scripts/run-field-test.py` | Update runner to call preflight, harness health, gate mode, thresholds, scoring | ✅ |
| 10.24 | Expand and annotate corpus for 0.2.0 field test — safety sizes, raw annotations, new corpora | [#468](https://github.com/deghosal-2026/CauterRule/issues/468) | `corpus/public/`, `field-test/corpus/` | Expand safety to ≥50, annotate raw, build tiered/domain/adversarial corpora | ✅ |

---

### Bucket 1: Pre-Field Validation

These are NOT field tests. They are regression, benchmark, infra, and validation work that must pass before field testing begins.

| # | Task | Issue | Files | Behavior | Status |
|---|------|-------|-------|----------|--------|
| 10.1 | Establish baseline metrics — capture pre-field-test metrics for v0.2.0 | [#431](https://github.com/deghosal-2026/CauterRule/issues/431) | `docs/field-test/v0.2.0/baseline.md` | Capture test count, source files, rules in store, coverage | ✅ |
| 10.2 | Hermetic non-LLM CI suite — all tests pass without LLM calls | [#432](https://github.com/deghosal-2026/CauterRule/issues/432) | `tests/` | All unit + integration tests pass without LLM | ✅ |
| 10.3 | Sentinel regression benchmark — verify new safety-adjusted metrics pass | [#433](https://github.com/deghosal-2026/CauterRule/issues/433) | `tests/benchmark/` | Determinism, acceptance, rejection, precision, regression, benchmarks pass with safety-adjusted scoring | ✅ |
| 10.4 | Adversarial validation — all 6 adversarial corpora from M9 pass | [#434](https://github.com/deghosal-2026/CauterRule/issues/434) | `tests/adversarial/` | All 6 adversarial corpora produce 0 promoted rules | ✅ |
| 10.5 | Corpus validation — verify expanded safety corpora from M3 and corpus infrastructure from M7 | [#435](https://github.com/deghosal-2026/CauterRule/issues/435) | `tests/corpus/` | Tiered, domain-specific, gold families, counterexample, near-miss, staleness, synthetic, private local, contribution guide all validated | ✅ |
| 10.6 | Docker validation — build, CLI, TUI, MCP, pipeline, redaction, export, compose, preflight, harness-health, success metrics | [#436](https://github.com/deghosal-2026/CauterRule/issues/436) | `docs/field-test/v0.2.0/docker-test-plan.md`, `docs/field-test/v0.2.0/docker-test-results.md`, `tests/field/test_docker_v020_cli.py`, `tests/field/test_docker_v020_metrics.py`, `docker-compose.yaml` | All 127 docker tests pass (23 new v0.2.0 tests + 104 inherited); demo <60s, CLI <500ms, preflight <30s, harness parse-rate ≥70%, coverage score ∈ [0,1]; loop gate verified; pure-JSON review fix | ✅ |
| 10.7 | Scale and performance benchmarks — validate M9 scale targets | [#437](https://github.com/deghosal-2026/CauterRule/issues/437) | `tests/scale/` | All 9 scale benchmarks meet targets | ✅ |

---

### Bucket 2: Field Test Plans

| # | Task | Issue | Files | Behavior | Status |
|---|------|-------|-------|----------|--------|
| 10.8 | Field test methodology document — test harness, corpus, environment, success criteria | [#438](https://github.com/deghosal-2026/CauterRule/issues/438) | `docs/field-test/v0.2.0/field-test-plan.md` §15 | Document methodology with enforced thresholds, safety-adjusted ranking, human review workflow | ✅ |
| 10.9 | Field test corpus plan — define which corpora, sizes, and expected outcomes | [#439](https://github.com/deghosal-2026/CauterRule/issues/439) | `docs/field-test/v0.2.0/field-test-plan.md` §14 | Corpus sizes, expected outcomes per corpus, tied to release thresholds | ✅ |

### Bucket 2b: Infrastructure & Tooling (Step 1-2, #469-#478)

These are the corpus, runner, and code enhancements completed before field test runs begin.

| # | Task | Issue | Files | Behavior | Status |
|---|------|-------|-------|----------|--------|
| 10.25 | Balance domain distribution on failures/negative — add shell, research, support | [#469](https://github.com/deghosal-2026/CauterRule/issues/469) | `scripts/generate-safety-corpus.py` | Add ≥5 negatives in shell, research, support domains | ✅ |
| 10.26 | Add expected_outcome_confidence tiering to raw corpus annotations | [#470](https://github.com/deghosal-2026/CauterRule/issues/470) | `scripts/normalize-corpus.py`, `src/cauterule/models/trajectory.py` | Backfill high/medium/low confidence on all raw trajectories | ✅ |
| 10.27 | Create private local corpus — 0 network calls validation | [#471](https://github.com/deghosal-2026/CauterRule/issues/471) | `corpus/public/private/` | 5 local-only trajectories | ✅ |
| 10.28 | Capture match_detail() diagnostics in field-test runner results | [#472](https://github.com/deghosal-2026/CauterRule/issues/472) | `scripts/run-field-test.py` | Wire match_detail() into replay_test_candidate() | ✅ |
| 10.29 | Add inconclusive rate tracking over time — compare-runs.py | [#473](https://github.com/deghosal-2026/CauterRule/issues/473) | `scripts/compare-runs.py` | Diff inconclusive rates, specificity, silence between runs | ✅ |
| 10.30 | Split benchmark and scale results into separate files | [#474](https://github.com/deghosal-2026/CauterRule/issues/474) | `docs/field-test/v0.2.0/benchmark-results.md`, `scale-benchmarks.md` | Extract from validation-results.md into standalone files | ✅ |
| 10.31 | Wire safety warnings into promotion provenance audit trail | [#475](https://github.com/deghosal-2026/CauterRule/issues/475) | `src/cauterule/models/decision.py`, `src/cauterule/promotion/auto.py` | Add safety_warnings field to PromotionDecision | ✅ |
| 10.32 | Add cauterule report --safety-adjusted CLI command | [#477](https://github.com/deghosal-2026/CauterRule/issues/477) | `src/cauterule/cli/report.py` | CLI produces ranking + decision economics from summary.json | ✅ |
| 10.33 | Generate combined benchmark JUnit XML for report consumption | [#478](https://github.com/deghosal-2026/CauterRule/issues/478) | `scripts/run-field-test.py` | Copy sentinel_benchmark.xml to field-test/results/0.2.0/benchmark-results.xml | ✅ |

---

### Bucket 3: Field Test Runs

| # | Task | Issue | Files | Behavior | Status |
|---|------|-------|-------|----------|--------|
| 10.10 | Local OMLX model field test runs — full corpus sweep on local models | [#440](https://github.com/deghosal-2026/CauterRule/issues/440) | `field-test/results/0.2.0/` | Full sweep on Llama-3.2-3B + Qwen3-4B with safety-adjusted scoring | ✅ Complete — see results in raw-results.md §8-9 |
| 10.11 | Cloud OpenRouter model field test runs — full corpus sweep on cloud models | [#441](https://github.com/deghosal-2026/CauterRule/issues/441) | `field-test/results/0.2.0/` | Full sweep on gpt-4o-mini + llama-3.1-8b with decision-economics | ✅ Complete — 22 corpora, both models. See raw-results.md §11 |
| 10.12 | Safety corpora field test — validate M1-M4 fixes on successes, failures/negative, nearmiss | [#442](https://github.com/deghosal-2026/CauterRule/issues/442) | `field-test/results/0.2.0/` | 100% pre-extraction drop on successes, 0% pass on failures/negative, ≥90% on nearmiss | ✅ Complete — all 4 models 100% silence; nearmiss 86-94% precision |
| 10.13 | TUI review workflow field test — validate M5 TUI with real candidates | [#443](https://github.com/deghosal-2026/CauterRule/issues/443) | `tests/tui/` | TUI launches, reviews, approves, rejects, annotates correctly | ✅ Complete — 43 hermetic tests pass |
| 10.14 | Observability metrics field test — validate M6 analytics with real data | [#444](https://github.com/deghosal-2026/CauterRule/issues/444) | `tests/observe/` | Hit counters, coverage scores, gap detector, leaderboard, journal, report all working | ✅ Complete — 52 hermetic tests pass |
| 10.15 | Cross-session repeat-failure reduction field test — measure before/after reduction | [#445](https://github.com/deghosal-2026/CauterRule/issues/445) | `field-test/v0.2.0/repeat-failure-reduction.md` | Repeat-failure rate drops ≥50% after CauterRule intervention | ⏳ Deferred to v0.2.1 — requires M11 product changes and before/after measurement protocol |
| 10.16 | Multi-environment field test — macOS, Linux, Docker end-to-end validation | [#446](https://github.com/deghosal-2026/CauterRule/issues/446) | `field-test/v0.2.0/multi-env-results.md` | Full suite + demo + TUI on macOS, Linux, Docker | ⏳ Deferred to v0.2.1 — requires CI setup for cross-platform testing |
| 10.17 | Cost measurement field test — document LLM cost per candidate, per promoted rule | [#447](https://github.com/deghosal-2026/CauterRule/issues/447) | `FIELD_TEST_REPORT.md §10` | Cost per candidate, per promoted rule, pre-extraction gate savings | ✅ Complete — $3.20 saved (Llama), $2.40 (Qwen), ~$5-10 for cloud sweep |

---

### Bucket 4: Reporting

| # | Task | Issue | Files | Behavior | Status |
|---|------|-------|-------|----------|--------|
| 10.18 | Generate field test report — comprehensive assessment with safety-adjusted metrics | [#448](https://github.com/deghosal-2026/CauterRule/issues/448) | `docs/field-test/v0.2.0/FIELD_TEST_REPORT.md` | BLUF, release gate verdict, safety-adjusted ranking, model comparisons, gaps, conclusions | ✅ Complete — all 13 required sections present |
| 10.19 | Document known issues — issues found during field testing with severity and workaround | [#449](https://github.com/deghosal-2026/CauterRule/issues/449) | `FIELD_TEST_REPORT.md §13` | All field test issues documented with severity, workaround, impact | ✅ Complete — 10 known issues documented |
| 10.20 | Update release notes with field test results — append to v0.2.0 release notes | [#450](https://github.com/deghosal-2026/CauterRule/issues/450) | `docs/release/v0.2.0/release-notes.md` | Field test results appended to release notes | ✅ Complete |
| 10.21 | M10 exit gate — code review, lint strict, coverage >95%, docs updated | [#451](https://github.com/deghosal-2026/CauterRule/issues/451) | — | Verify all M10 issues complete, tests pass, lint clean, coverage >95%, docs updated, milestones closed | ⚠️ Partially met — all issues closed, docs updated, lint clean. Coverage 86% (below 95%, accepted). Remaining: coverage restoration tracked in v0.2.1 |

---

### M10 Exit Gate

- [ ] Run all tests: `pytest` — all pass
- [ ] Lint strict clean: `ruff check .` + `mypy src/ tests/` — zero errors
- [ ] Test coverage total > 95%: `pytest --cov=src/cauterule --cov-report=term-missing`
- [ ] Update all docs affected by this milestone
- [ ] Update `docs/field-test/v0.2.0/changes-needed.md` to reflect final field-test design (ensure field test is in sync)
- [ ] Verify all issues in this milestone are done (close #431-#451 and new M10 issues for field test plan/scripts/corpus)
- [ ] Close all completed issues
- [ ] Commit with message: `milestone: M10 complete`
- [ ] Push to main

#### Pre-Release Gate (M10-specific)

- [ ] Field test report published with safety-adjusted ranking
- [ ] Release gate verdict: PASS (all enforced thresholds met)
- [ ] Known issues documented
- [ ] Harness health assertions: all pass
- [ ] Human review agreement rate documented