# v0.1.0 — WBS Part 12: Comprehensive Field Test

**Milestone:** M30

**Structure:** Three buckets — Pre-Field Validation, Field Tests, Reporting. Only the "Field Tests" bucket contains true field tests. Pre-Field Validation is quality/benchmark/infra work that must pass before field testing begins.

```
Pre-Field Validation (30.1, 30.2, 30.6, 30.7) ──> Field Tests (30.3, 30.4, 30.8) ──> Reporting (30.5)
```

---

## Bucket 1: Pre-Field Validation

These are NOT field tests. They are regression, benchmark, infra, and validation work that must pass before field testing begins. They verify the system is correct enough to field test.

### 30.1 — System Validation (regression + integration checks)

| # | Task | Files | Behavior | Status | Issue |
|---|------|-------|----------|--------|-------|
| 30.1.1 | Establish baseline metrics | `field-test/v0.1.0/baseline.md` | Capture pre-field-test metrics: test count, source files, rules in store, coverage | ⬜ | #231 |
| 30.1.2 | Hermetic non-LLM CI suite | `tests/` | All unit + integration tests pass without LLM calls | ✅ | #232 |
| 30.1.3 | Sentinel regression benchmark | `tests/benchmark/` | Determinism, counterexample, near-miss, regression, gold-family benchmarks pass | ✅ | #233 |
| 30.1.4 | Adversarial validation | `tests/adversarial/` | All 6 adversarial corpora pass (injection, misleading, contradiction, unsafe, poisoning, leakage) | ✅ | #234 |
| 30.1.5 | Rollback verification | `tests/store/` | Promote → rollback via git → re-promote works correctly | ✅ | #235 |
| 30.1.6 | MCP integration validation | `tests/mcp/` | MCP server starts, all 4 tools return correct responses | ✅ | #236 |
| 30.1.7 | Export/import validation | `tests/export/ tests/import_/` | All 7 formats valid, round-trip fidelity, active-only filter | ✅ | #237 |
| 30.1.8 | @cauterule.watch adapter validation | `tests/adapter/` | Trajectory capture + redaction on failure works correctly | ✅ | #238 |

### 30.2 — Corpus & Benchmark Validation

| # | Task | Files | Behavior | Status | Issue |
|---|------|-------|----------|--------|-------|
| 30.2.1 | Tiered corpus validation | `tests/corpus/` | tiny/small/medium/large — balanced success/failure, valid metadata | ✅ | #239 |
| 30.2.2 | Gold rule families validation | `tests/corpus/` | Each scenario has ≥2 acceptable rule abstractions | ⬜ | #240 |
| 30.2.3 | Model bake-off | `tests/benchmark/` | Compare OMLX (local), gpt-4o-mini (cheap), gpt-4o (better) on extraction quality | ⬜ | #241 |
| 30.2.4 | Prompt bake-off | `tests/benchmark/` | Compare 3 prompt variants by replay pass rate | ⬜ | #242 |
| 30.2.5 | Coverage measurement | `src/cauterule/observe/` | Rule coverage ≥80%, domain ≥60%, failure-class ≥60% | ⬜ | #243 |
| 30.2.6 | Scale benchmarks | `tests/scale/` | Latency, memory, conflict detection within targets | ✅ | #244 |
| 30.2.7 | Cost-per-iteration documentation | `field-test/v0.1.0/cost.md` | Document LLM cost per candidate, per promoted rule | ⬜ | #245 |

### 30.6 — Docker Validation (✅ DONE)

| # | Task | Status | Issue |
|---|------|--------|-------|
| 30.6.1-30.6.14 | Docker build, CLI, TUI, MCP, pipeline, redaction, export, git, loop, multi-env, compose, script, fixtures, compose.yaml | ✅ | #370-#384 |

### 30.7 — Advanced Validation

| # | Task | Files | Behavior | Status | Issue |
|---|------|-------|----------|--------|-------|
| 30.7.1 | Performance baselines | `field-test/v0.1.0/performance-baselines.json` | Capture 12 baseline metrics for regression tracking | ⬜ | #385 |
| 30.7.2 | Failure mode catalog | `field-test/v0.1.0/trajectories/` | 20 hand-crafted trajectories covering all failure modes | ⬜ | #386 |
| 30.7.3 | Data drift & staleness | `field-test/v0.1.0/staleness.md` | Old rules flagged stale, retired correctly | ⬜ | #387 |
| 30.7.4 | Rule conflict resolution | `field-test/v0.1.0/conflicts.md` | 5 conflict scenarios: contradictions blocked, overlaps resolved/merged | ⬜ | #388 |
| 30.7.5 | Token budget limits | `field-test/v0.1.0/budget.md` | 100/500/1000 rules with compression tiers | ⬜ | #389 |
| 30.7.6 | Upgrade path | `field-test/v0.1.0/upgrade.md` | Install over pre-existing store, backward compat | ⬜ | #390 |
| 30.7.7 | Concurrent agents | `field-test/v0.1.0/concurrent.md` | 5 simultaneous trajectories, no dupes, no data loss | ⬜ | #391 |
| 30.7.8 | LLM provider fallback | `field-test/v0.1.0/fallback.md` | Primary LLM down → fallback → recovery | ⬜ | #392 |
| 30.7.9 | Negative tests | `field-test/v0.1.0/negative.md` | 10 inputs that should NOT produce rules | ⬜ | #393 |
| 30.7.10 | Golden trajectory set | `field-test/v0.1.0/golden-trajectories.json` | 10 trajectories with known expected rules | ⬜ | #394 |
| 30.7.11 | Rule quality scoring | `field-test/v0.1.0/rule-quality-scores.md` | Score 20 rules on readability, specificity, actionability | ⬜ | #395 |
| 30.7.12 | Time-to-value | `field-test/v0.1.0/time-to-value.md` | Install → first prevented failure <15 min | ⬜ | #396 |
| 30.7.13 | CI integration | `field-test/v0.1.0/ci.md` | `cauterule test --ci` produces valid JUnit XML | ⬜ | #397 |
| 30.7.14 | Export validation | `field-test/v0.1.0/export-validation.md` | AGENTS.md works with OpenCode, other formats valid | ⬜ | #398 |

---

## Bucket 2: Field Tests

These are the ACTUAL field tests. They validate that CauterRule learns from real agent work and measurably reduces repeat failures. They require real corpus (per `corpus-plan.md`) and/or a running LLM.

### 30.3 — Single-Agent Field Tests

| # | Task | Files | Behavior | Status | Issue |
|---|------|-------|----------|--------|-------|
| 30.3.1 | Create coding agent harness | `field-test/v0.1.0/harness.py` | Toy agent with git/python/shell tasks and known failure modes | ⬜ | #246 |
| 30.3.2 | Cold-start field test | `field-test/v0.1.0/cold-start.md` | Zero rules → time to first useful rule + first prevented failure | ⬜ | #247 |
| 30.3.3 | Bundled-pack field test | `field-test/v0.1.0/bundled-pack.md` | Pack-git rules prevent known git failures with zero learning | ⬜ | #248 |
| 30.3.4 | Learning field test | `field-test/v0.1.0/learning.md` | 10 tasks: extract → test → promote → inject → prevent | ⬜ | #249 |
| 30.3.5 | Cross-session field test | `field-test/v0.1.0/cross-session.md` | Session 1 fails → session 2 prevents same failure | ⬜ | #250 |
| 30.3.6 | Long-horizon field test | `field-test/v0.1.0/long-horizon.md` | 20-50 step tasks, late failures, rules still help | ⬜ | #251 |
| 30.3.7 | Noisy trajectory field test | `field-test/v0.1.0/noisy.md` | Retries + irrelevant calls, extractor still finds lesson | ⬜ | #252 |
| 30.3.8 | Human-correction field test | `field-test/v0.1.0/human-correction.md` | "Next time do X" → candidate → test → promote | ⬜ | #253 |
| 30.3.9 | Demo field test | `field-test/v0.1.0/demo.md` | `cauterule demo` end-to-end <60s with narrated walkthrough | ⬜ | #254 |
| 30.3.10 | Repeat-failure reduction | `field-test/v0.1.0/reduction.md` | Before/after: repeat-failure rate drops ≥50% | ⬜ | #255 |
| 30.3.11 | Regression field test | `field-test/v0.1.0/regression.md` | Rules survive model/prompt changes | ⬜ | #31 |

### 30.4 — Multi-Environment Field Tests

| # | Task | Files | Behavior | Status | Issue |
|---|------|-------|----------|--------|-------|
| 30.4.1 | macOS field test | `field-test/v0.1.0/macos.md` | Full test suite + demo + agent harness on macOS | ⬜ | #256 |
| 30.4.2 | Linux field test | `field-test/v0.1.0/linux.md` | Full test suite + demo in Linux container | ⬜ | #257 |
| 30.4.3 | Docker field test | `field-test/v0.1.0/docker.md` | `docker run cauterule demo` + full test suite passes | ⬜ | #258 |
| 30.4.4 | Homebrew install field test | `field-test/v0.1.0/homebrew.md` | `brew install cauterule` + `cauterule demo` works | ⬜ | #259 |
| 30.4.5 | Standalone binary field test | `field-test/v0.1.0/binary.md` | Binary runs demo without Python | ⬜ | #260 |

### 30.8 — Real Corpus Field Tests

See: `corpus-test-plan.md` for full details.

| # | Task | Corpus | LLM | Status | Issue |
|---|------|--------|-----|--------|-------|
| 30.8.1 | Real corpus validation | 70 trajectories | None | ⬜ | #399 |
| 30.8.2 | Real corpus extraction | 30 failures | OMLX | ⬜ | #400 |
| 30.8.3 | Real corpus replay testing | 50 trajectories | None | ⬜ | #401 |
| 30.8.4 | Real corpus promotion & injection | Passing candidates | None | ⬜ | #402 |
| 30.8.5 | Real corpus repeat-failure reduction | 30F + 20S | OMLX | ⬜ | #403 |
| 30.8.6 | Real corpus cross-session memory | 10 failures | OMLX | ⬜ | #404 |
| 30.8.7 | Real corpus golden set regression | 10 golden | OMLX + gpt-4o-mini | ⬜ | #405 |
| 30.8.8 | Real corpus coverage measurement | 30 failures | None | ⬜ | #406 |
| 30.8.9 | Real corpus near-miss precision | 10 near-miss | None | ⬜ | #407 |
| 30.8.10 | Real corpus correction flow | 5 corrections | OMLX | ⬜ | #408 |
| 30.8.11 | Real corpus export to AGENTS.md | Promoted rules | None | ⬜ | #409 |
| 30.8.12 | Real corpus cost measurement | 30 failures | OMLX + gpt-4o-mini | ⬜ | #410 |

---

## Bucket 3: Reporting

### 30.5 — Field Test Reporting

| # | Task | Files | Behavior | Status | Issue |
|---|------|-------|----------|--------|-------|
| 30.5.1 | Document field test methodology | `field-test/v0.1.0/methodology.md` | Test harness, corpus, environment, success criteria, limitations | ⬜ | #261 |
| 30.5.2 | Generate field test report | `field-test/v0.1.0/FIELD_TEST_REPORT.md` | Comprehensive report: baseline vs results, metrics, costs, findings | ⬜ | #262 |
| 30.5.3 | Document known issues | `field-test/v0.1.0/known-issues.md` | Issues found during field testing with severity and workaround | ⬜ | #263 |
| 30.5.4 | Update release notes | `docs/release/v0.1.0/release-notes.md` | Append field test results to release notes | ⬜ | #264 |

---

## Duplicate Issues Closed

These issues duplicated 30.3.* and 30.4.* tasks and have been closed:

| Closed Issue | Duplicated By | Reason |
|-------------|---------------|--------|
| #25 (27.1 Single-agent) | #246 (30.3.1) | Same intent — 30.3.1 is better scoped |
| #26 (27.2 Long-horizon) | #251 (30.3.6) | Same intent — 30.3.6 is better scoped |
| #27 (27.3 Noisy) | #252 (30.3.7) | Same intent — 30.3.7 is better scoped |
| #28 (27.4 Human-in-loop) | #253 (30.3.8) | Same intent — 30.3.8 is better scoped |
| #29 (27.5 Cold-start) | #247 (30.3.2) | Same intent — 30.3.2 is better scoped |
| #30 (27.6 Cross-session) | #250 (30.3.5) | Same intent — 30.3.5 is better scoped |
| #32 (27.8 Multi-env) | #256-#260 (30.4.*) | 30.4.* is more specific breakdown |

---

## M30 Exit Gate

Before M30 closes, ALL of the following must be true:

### Pre-Field Validation
- [ ] 30.1: System validation — all 8 tasks complete
- [ ] 30.2: Corpus & benchmark validation — all 7 tasks complete
- [ ] 30.6: Docker validation — all 14 tasks complete (✅)
- [ ] 30.7: Advanced validation — all 14 tasks complete

### Field Tests
- [ ] 30.3: Single-agent — all 11 tasks complete
- [ ] 30.4: Multi-environment — all 5 tasks complete
- [ ] 30.8: Real corpus — all 12 tasks complete

### Reporting
- [ ] 30.5: Reporting — all 4 tasks complete

### Quality Gates
- [ ] `pytest tests/` — all pass
- [ ] `ruff check .` + `mypy src/ tests/` — zero errors
- [ ] `pytest --cov=src/cauterule --cov-report=term-missing` — >95%
- [ ] Field test report is published
- [ ] Known issues are documented
- [ ] All GitHub issues in M30 milestone closed
- [ ] Commit: `milestone: M30 complete`
- [ ] Push to main