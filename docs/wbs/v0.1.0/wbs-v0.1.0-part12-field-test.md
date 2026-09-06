# v0.1.0 — WBS Part 12: Comprehensive Field Test

**Milestones:** M30 (70 tasks — 30.1-30.5 existing, 30.6 Docker done, 30.7 Advanced)

**Execution order:** Tasks must be executed in the order listed below. Each phase depends on the previous one completing.

```
Phase 1: Foundations (30.1) ──> Phase 2: Performance + Corpus (30.7.1, 30.7.2, 30.7.10, 30.2)
                              ──> Phase 3: Single-Agent (30.3)
                              ──> Phase 4: Advanced Tests (30.7.3-30.7.9, 30.7.11-30.7.14)
                              ──> Phase 5: Multi-Environment (30.4)
                              ──> Phase 6: Reporting (30.5)
```

**Note:** M30.6 (Docker infrastructure) is already complete (✅). All other tasks are ⬜.

---

## M30.6 — Docker Field Test Infrastructure (✅ DONE)

| # | Task | Status |
|---|------|--------|
| 30.6.1 | Docker image build & install verification | ✅ |
| 30.6.2 | Docker CLI integration test | ✅ |
| 30.6.3 | Docker TUI test (Textual Pilot) | ✅ |
| 30.6.4 | Docker MCP server test | ✅ |
| 30.6.5 | Docker pipeline E2E test | ✅ |
| 30.6.6 | Docker redaction verification test | ✅ |
| 30.6.7 | Docker export/import round-trip test | ✅ |
| 30.6.8 | Docker git integration test | ✅ |
| 30.6.9 | Docker loop orchestrator test | ✅ |
| 30.6.10 | Docker multi-environment test | ✅ |
| 30.6.11 | Docker compose orchestration | ✅ |
| 30.6.12 | Test orchestration script | ✅ |
| 30.6.13 | Test fixtures package | ✅ |
| 30.6.14 | Update docker-compose.yaml | ✅ |

---

## Phase 1: Field Test Foundations (30.1)

| # | Task | Files | Behavior | Status |
|---|------|-------|----------|--------|
| 30.1.1 | Establish baseline metrics | `field-test/v0.1.0/baseline.md` | Measure current repeat-failure rate, rule-store size, replay precision, coverage scores before running any field tests | ⬜ |
| 30.1.2 | Run hermetic non-LLM CI suite | `tests/field/hermetic.py` | All replay, store, linter, conflict, and injection tests pass without LLM calls (zero external dependencies) | ✅ |
| 30.1.3 | Validate sentinel regression benchmark | `tests/benchmark/sentinel.py` | Core replay determinism, counterexample rejection, and success-regression benchmarks all pass | ✅ |
| 30.1.4 | Run adversarial edit injection test | `tests/field/adversarial.py` | All 6 adversarial corpora pass (injection, misleading, contradiction, unsafe, poisoning, leakage) | ✅ |
| 30.1.5 | Test rollback with a real promoted rule | `tests/field/rollback.py` | Promote a rule, verify it appears in store, rollback via git, verify it is removed, re-promote | ✅ |
| 30.1.6 | Run MCP server field test | `tests/field/mcp.py` | Start MCP server, connect client, call all 4 tools, verify responses match expected rule store state | ✅ |
| 30.1.7 | Run export/import field test | `tests/field/export.py` | Export to all 7 formats, verify each file is valid, re-import from each format, verify round-trip fidelity | ✅ |
| 30.1.8 | Run `@cauterule.watch` adapter test | `tests/field/adapter.py` | Wrap a toy agent, run tasks that fail, verify trajectory capture, extraction, and promotion | ✅ |

---

## Phase 2: Performance Baselines + Corpus Preparation (30.7.1, 30.7.2, 30.7.10)

| # | Task | Files | Behavior | Status |
|---|------|-------|----------|--------|
| 30.7.1 | Performance baselines & regression tracking | `field-test/v0.1.0/performance-baselines.json` | Capture 12 baseline metrics (extraction time, replay latency, injection p50/p95, conflict detection, memory) before any field tests modify the system | ⬜ |
| 30.7.2 | Failure mode catalog | `field-test/v0.1.0/trajectories/` | Create 20 hand-crafted trajectories covering all failure modes (git, docker, python, deploy, test, API, browser, terraform) with known expected rules. Save as JSONL files with correct metadata | ⬜ |
| 30.7.10 | Golden trajectory set | `field-test/v0.1.0/golden-trajectories.json` | Create 10 fixed trajectories with known correct extractions for regression testing across versions. Save as machine-readable JSON for automated regression tests | ⬜ |

---

## Phase 3: Corpus & Benchmark Validation (30.2)

| # | Task | Files | Behavior | Status |
|---|------|-------|----------|--------|
| 30.2.1 | Validate tiered corpus completeness | `tests/corpus/validate.py` | tiny (25), small (100), medium (1k), large (10k+) — all trajectories have required metadata, balanced success/failure | ✅ |
| 30.2.2 | Validate gold rule families | `tests/corpus/gold.py` | Each benchmark scenario has >=2 acceptable rule abstractions documented | ⬜ |
| 30.2.3 | Run model bake-off | `tests/benchmark/bakeoff.py` | Compare Llama 3.1 (local), gpt-4o-mini (cheap), gpt-4o (better) on same corpus; document extraction quality and cost | ⬜ |
| 30.2.4 | Run prompt bake-off | `tests/benchmark/prompts.py` | Compare 3 extractor prompt variants; measure replay pass rate, not just readability | ⬜ |
| 30.2.5 | Measure coverage vs target | `tests/benchmark/coverage.py` | Rule coverage score >= 80%, domain coverage >= 60%, failure-class coverage >= 60% | ⬜ |
| 30.2.6 | Run scale benchmarks | `tests/benchmark/scale.py` | Replay latency, injection latency, conflict detection time, memory footprint all within targets | ✅ |
| 30.2.7 | Document cost-per-iteration | `field-test/v0.1.0/cost.md` | Measure and document LLM cost per extracted candidate, per promoted rule, per prevented failure | ⬜ |

---

## Phase 4: Single-Agent Field Tests (30.3)

| # | Task | Files | Behavior | Status |
|---|------|-------|----------|--------|
| 30.3.1 | Create coding agent harness | `field-test/v0.1.0/harness.py` | A toy coding agent that performs git, python, and shell tasks with known failure modes | ⬜ |
| 30.3.2 | Run cold-start field test | `field-test/v0.1.0/cold-start.md` | Start with zero rules, measure time to first useful rule and first prevented repeat failure | ⬜ |
| 30.3.3 | Run bundled-pack field test | `field-test/v0.1.0/bundled-pack.md` | Enable pack-git, verify rules prevent known git failures without any local learning | ⬜ |
| 30.3.4 | Run learning field test | `field-test/v0.1.0/learning.md` | Run 10 tasks with known failure modes, verify rules are extracted, tested, promoted, and injected | ⬜ |
| 30.3.5 | Run cross-session field test | `field-test/v0.1.0/cross-session.md` | Fail in session 1, verify promoted rule prevents the same failure in a fresh session 2 | ⬜ |
| 30.3.6 | Run long-horizon field test | `field-test/v0.1.0/long-horizon.md` | 20-50 step tasks with late-stage failures; verify rules still help when failures occur deep in the trajectory | ⬜ |
| 30.3.7 | Run noisy trajectory field test | `field-test/v0.1.0/noisy.md` | Inject retries, irrelevant tool calls, and distractions; verify extractor still finds the correct lesson | ⬜ |
| 30.3.8 | Run human-correction field test | `field-test/v0.1.0/human-correction.md` | User types "next time do X" after a failure; verify correction is converted, tested, and promoted | ⬜ |
| 30.3.9 | Run demo field test | `field-test/v0.1.0/demo.md` | `cauterule demo` runs end-to-end and produces expected output with narrated walkthrough | ⬜ |
| 30.3.10 | Measure repeat-failure reduction | `field-test/v0.1.0/reduction.md` | Before/after comparison: repeat-failure rate for covered failure classes should drop by >= 50% | ⬜ |
| 30.3.11 | Regression field test | `field-test/v0.1.0/regression.md` | Old promoted rules still pass after prompt/model changes | ⬜ |

---

## Phase 5: Advanced & Edge Case Tests (30.7.3-30.7.9, 30.7.11-30.7.14)

| # | Task | Files | Behavior | Status |
|---|------|-------|----------|--------|
| 30.7.3 | Data drift & staleness testing | `field-test/v0.1.0/staleness.md` | Old rules that no longer match new failure patterns are flagged as stale and retired | ⬜ |
| 30.7.4 | Rule conflict resolution in practice | `field-test/v0.1.0/conflicts.md` | 5 conflict scenarios tested: direct contradictions blocked, specificity overlaps resolved, equal overlaps merged, different-aspect overlaps coexist | ⬜ |
| 30.7.5 | Token budget & context window limits | `field-test/v0.1.0/budget.md` | 100/500/1000 rules injected with budget limits; compression tiers (full → compressed → one-liner → drop) | ⬜ |
| 30.7.6 | Upgrade path testing | `field-test/v0.1.0/upgrade.md` | Install v0.1.0 over pre-existing rule store; verify backward compat with old index.yaml format | ⬜ |
| 30.7.7 | Concurrent agent testing | `field-test/v0.1.0/concurrent.md` | 5 trajectories submitted simultaneously; verify no duplicates, no data loss, consistent store | ⬜ |
| 30.7.8 | LLM provider fallback | `field-test/v0.1.0/fallback.md` | Primary LLM (Ollama) stopped mid-test; verify fallback to gpt-4o-mini and recovery | ⬜ |
| 30.7.9 | Negative tests | `field-test/v0.1.0/negative.md` | 10 inputs that should NOT produce rules (successes, opinions, cosmetic issues, warnings, operator errors) | ⬜ |
| 30.7.11 | Rule quality scoring | `field-test/v0.1.0/rule-quality-scores.md` | Score 20 rules on readability, specificity, actionability, testability, coverage | ⬜ |
| 30.7.12 | Time-to-value measurement | `field-test/v0.1.0/time-to-value.md` | Time from install to first prevented failure: <15 minutes total | ⬜ |
| 30.7.13 | CI integration testing | `field-test/v0.1.0/ci.md` | `cauterule test --ci` produces valid JUnit XML for GitHub Actions | ⬜ |
| 30.7.14 | Export format validation against real tools | `field-test/v0.1.0/export-validation.md` | AGENTS.md verified with OpenCode, other formats verified for syntax | ⬜ |

---

## Phase 6: Multi-Environment Field Tests (30.4)

| # | Task | Files | Behavior | Status |
|---|------|-------|----------|--------|
| 30.4.1 | Run field test on macOS | `field-test/v0.1.0/macos.md` | Full test suite passes on macOS (local dev environment) | ⬜ |
| 30.4.2 | Run field test on Linux | `field-test/v0.1.0/linux.md` | Full test suite passes on Linux (CI environment) | ⬜ |
| 30.4.3 | Run field test in Docker | `field-test/v0.1.0/docker.md` | `docker run cauterule demo` + full test suite passes | ⬜ |
| 30.4.4 | Run field test with Homebrew install | `field-test/v0.1.0/homebrew.md` | `brew install cauterule` + `cauterule demo` works | ⬜ |
| 30.4.5 | Run field test with standalone binary | `field-test/v0.1.0/binary.md` | Standalone binary runs demo end-to-end | ⬜ |

---

## Phase 7: Field Test Reporting (30.5)

| # | Task | Files | Behavior | Status |
|---|------|-------|----------|--------|
| 30.5.1 | Document field test methodology | `field-test/v0.1.0/methodology.md` | Describe test harness, corpus, environment, success criteria, and limitations | ⬜ |
| 30.5.2 | Generate field test report | `field-test/v0.1.0/FIELD_TEST_REPORT.md` | Comprehensive report: baseline vs results, metrics, costs, findings, recommendations | ⬜ |
| 30.5.3 | Document known issues and limitations | `field-test/v0.1.0/known-issues.md` | List all known issues discovered during field testing with severity and workaround | ⬜ |
| 30.5.4 | Update release notes with field test results | `docs/release/v0.1.0/release-notes.md` | Append field test results to release notes | ⬜ |

---

## M30 Exit Gate

Before M30 closes, ALL of the following must be true:

- [ ] M30.6: Docker infrastructure — all 14 tasks complete (✅)
- [ ] Phase 1: Foundations — all 8 tasks complete (30.1.1-30.1.8)
- [ ] Phase 2: Performance + Corpus — all 3 tasks complete (30.7.1, 30.7.2, 30.7.10)
- [ ] Phase 3: Corpus & Benchmarks — all 7 tasks complete (30.2.1-30.2.7)
- [ ] Phase 4: Single-Agent — all 11 tasks complete (30.3.1-30.3.11)
- [ ] Phase 5: Advanced Tests — all 11 tasks complete (30.7.3-30.7.9, 30.7.11-30.7.14)
- [ ] Phase 6: Multi-Environment — all 5 tasks complete (30.4.1-30.4.5)
- [ ] Phase 7: Reporting — all 4 tasks complete (30.5.1-30.5.4)
- [ ] `pytest tests/` — all pass
- [ ] `ruff check .` + `mypy src/ tests/` — zero errors
- [ ] `pytest --cov=src/cauterule --cov-report=term-missing` — >95%
- [ ] Field test report is published
- [ ] Known issues are documented
- [ ] All GitHub issues in M30 milestone closed
- [ ] Commit with message: `milestone: M30 complete`
- [ ] Push to main