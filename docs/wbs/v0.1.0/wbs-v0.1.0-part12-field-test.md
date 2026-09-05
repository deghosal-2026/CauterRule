# v0.1.0 — WBS Part 12: Comprehensive Field Test

**Milestones:** M30 (42 tasks — merged from former M27 Field Tests + M31 Comprehensive Field Test)

**Note:** M30 executes after M26 (safety), M28 (distribution), and M29 (demo) so that multi-env and demo field test tasks have their dependencies ready. Field test must be done as soon as all functionality is implemented.

## M30: Comprehensive Field Test

> **Goal:** Validate the full CauterRule system end-to-end across multiple environments, failure domains, and agent types. Confirm that the extract → test → promote → inject loop measurably reduces repeat failures, that replay is deterministic and safe, and that the system is ready for production use.

### M30.1 — Field Test Foundations

| # | Task | Files | Behavior | Status |
|---|------|-------|----------|--------|
| 30.1.1 | Establish baseline metrics | `field-test/v0.1.0/baseline.md` | Measure current repeat-failure rate, rule-store size, replay precision, coverage scores before running any field tests | ⬜ |
| 30.1.2 | Run hermetic non-LLM CI suite | `tests/field/hermetic.py` | All replay, store, linter, conflict, and injection tests pass without LLM calls (zero external dependencies) | ⬜ |
| 30.1.3 | Validate sentinel regression benchmark | `tests/benchmark/sentinel.py` | Core replay determinism, counterexample rejection, and success-regression benchmarks all pass | ⬜ |
| 30.1.4 | Run adversarial edit injection test | `tests/field/adversarial.py` | All 6 adversarial corpora pass (injection, misleading, contradiction, unsafe, poisoning, leakage) | ⬜ |
| 30.1.5 | Test rollback with a real promoted rule | `tests/field/rollback.py` | Promote a rule, verify it appears in store, rollback via git, verify it is removed, re-promote | ⬜ |
| 30.1.6 | Run MCP server field test | `tests/field/mcp.py` | Start MCP server, connect client, call all 4 tools, verify responses match expected rule store state | ⬜ |
| 30.1.7 | Run export/import field test | `tests/field/export.py` | Export to all 7 formats, verify each file is valid, re-import from each format, verify round-trip fidelity | ⬜ |
| 30.1.8 | Run `@cauterule.watch` adapter test | `tests/field/adapter.py` | Wrap a toy agent, run tasks that fail, verify trajectory capture, extraction, and promotion | ⬜ |

### M30.2 — Corpus & Benchmark Validation

| # | Task | Files | Behavior | Status |
|---|------|-------|----------|--------|
| 30.2.1 | Validate tiered corpus completeness | `tests/corpus/validate.py` | tiny (25), small (100), medium (1k), large (10k+) — all trajectories have required metadata, balanced success/failure | ⬜ |
| 30.2.2 | Validate gold rule families | `tests/corpus/gold.py` | Each benchmark scenario has >=2 acceptable rule abstractions documented | ⬜ |
| 30.2.3 | Run model bake-off | `tests/benchmark/bakeoff.py` | Compare GPT-4o, Claude Sonnet, and local Ollama model on same corpus; document extraction quality and cost | ⬜ |
| 30.2.4 | Run prompt bake-off | `tests/benchmark/prompts.py` | Compare 3 extractor prompt variants; measure replay pass rate, not just readability | ⬜ |
| 30.2.5 | Measure coverage vs target | `tests/benchmark/coverage.py` | Rule coverage score >= 80%, domain coverage >= 60%, failure-class coverage >= 60% | ⬜ |
| 30.2.6 | Run scale benchmarks | `tests/benchmark/scale.py` | Replay latency, injection latency, conflict detection time, memory footprint all within targets | ⬜ |
| 30.2.7 | Document cost-per-iteration | `field-test/v0.1.0/cost.md` | Measure and document LLM cost per extracted candidate, per promoted rule, per prevented failure | ⬜ |

### M30.3 — Single-Agent Field Test

| # | Task | Files | Behavior | Status |
|---|------|-------|----------|--------|
| 30.3.1 | Create coding agent harness | `field-test/v0.1.0/harness.py` | A toy coding agent that performs git, python, and shell tasks with known failure modes | ⬜ |
| 30.3.2 | Run cold-start field test | `field-test/v0.1.0/cold-start.md` | Start with zero rules (bundled pack-git disabled), measure time to first useful rule and first prevented repeat failure | ⬜ |
| 30.3.3 | Run bundled-pack field test | `field-test/v0.1.0/bundled-pack.md` | Enable pack-git, verify rules prevent known git failures without any local learning | ⬜ |
| 30.3.4 | Run learning field test | `field-test/v0.1.0/learning.md` | Run 10 tasks with known failure modes, verify rules are extracted, tested, promoted, and injected | ⬜ |
| 30.3.5 | Run cross-session field test | `field-test/v0.1.0/cross-session.md` | Fail in session 1, verify promoted rule prevents the same failure in a fresh session 2 | ⬜ |
| 30.3.6 | Run long-horizon field test | `field-test/v0.1.0/long-horizon.md` | 20-50 step tasks with late-stage failures; verify rules still help when failures occur deep in the trajectory | ⬜ |
| 30.3.7 | Run noisy trajectory field test | `field-test/v0.1.0/noisy.md` | Inject retries, irrelevant tool calls, and distractions; verify extractor still finds the correct lesson | ⬜ |
| 30.3.8 | Run human-correction field test | `field-test/v0.1.0/human-correction.md` | User types "next time do X" after a failure; verify correction is converted, tested, and promoted | ⬜ |
| 30.3.9 | Run demo field test | `field-test/v0.1.0/demo.md` | `cauterule demo` runs end-to-end and produces expected output with narrated walkthrough | ⬜ |
| 30.3.10 | Measure repeat-failure reduction | `field-test/v0.1.0/reduction.md` | Before/after comparison: repeat-failure rate for covered failure classes should drop by >= 50% | ⬜ |
| 30.3.11 | Regression field test | `field-test/v0.1.0/regression.md` | Old promoted rules still pass after prompt/model changes | ⬜ |

### M30.4 — Multi-Environment Field Test

| # | Task | Files | Behavior | Status |
|---|------|-------|----------|--------|
| 30.4.1 | Run field test on macOS | `field-test/v0.1.0/macos.md` | Full test suite passes on macOS (local dev environment) | ⬜ |
| 30.4.2 | Run field test on Linux | `field-test/v0.1.0/linux.md` | Full test suite passes on Linux (CI environment) | ⬜ |
| 30.4.3 | Run field test in Docker | `field-test/v0.1.0/docker.md` | `docker run cauterule demo` + full test suite passes | ⬜ |
| 30.4.4 | Run field test with Homebrew install | `field-test/v0.1.0/homebrew.md` | `brew install cauterule` + `cauterule demo` works | ⬜ |
| 30.4.5 | Run field test with standalone binary | `field-test/v0.1.0/binary.md` | Standalone binary runs demo end-to-end | ⬜ |

### M30.5 — Field Test Reporting

| # | Task | Files | Behavior | Status |
|---|------|-------|----------|--------|
| 30.5.1 | Document field test methodology | `field-test/v0.1.0/methodology.md` | Describe test harness, corpus, environment, success criteria, and limitations | ⬜ |
| 30.5.2 | Generate field test report | `field-test/v0.1.0/FIELD_TEST_REPORT.md` | Comprehensive report: baseline vs results, metrics, costs, findings, recommendations | ⬜ |
| 30.5.3 | Document known issues and limitations | `field-test/v0.1.0/known-issues.md` | List all known issues discovered during field testing with severity and workaround | ⬜ |
| 30.5.4 | Update release notes with field test results | `docs/release/v0.1.0/release-notes.md` | Append field test results to release notes | ⬜ |

### M30 Exit Gate

- [ ] Run all tests: `pytest` — all pass
- [ ] Lint strict clean: `ruff check` + `mypy src/` — zero errors
- [ ] Test coverage total > 95%: `pytest --cov=src/cauterule --cov-report=term-missing`
- [ ] All 30.x.x field test tasks are complete and documented
- [ ] Field test report is published
- [ ] Known issues are documented
- [ ] Update all docs affected by this milestone
- [ ] Verify all issues in this milestone are done
- [ ] Close all completed issues
- [ ] Commit with message: `milestone: M30 complete`
- [ ] Push to main