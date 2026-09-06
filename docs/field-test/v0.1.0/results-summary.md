# Field Test Results Summary — CauterRule v0.1.0

**Date:** 2026-09-05
**Branch:** main
**Milestone:** M30 — Comprehensive Field Test

---

## 1. Overall Status

| Tests Total | Passed | Failed | Coverage | Status |
|-------------|--------|--------|----------|--------|
| 844+ | 844 | 0 | 87%* | ✅ In Progress |

*\*Coverage target is 95%. CLI subcommands and MCP/TUI paths are partially uncovered.*

---

## 2. Bucket 1: Pre-Field Validation

### 2.1 30.1 — System Validation

| # | Task | Status | Results | Artifact |
|---|------|--------|---------|----------|
| 30.1.1 | Baseline metrics | ✅ | 844 tests, 198 source files, 0 rules, 25/32 milestones | `field-test/v0.1.0/baseline.md` |
| 30.1.2 | Hermetic CI suite | ✅ | All tests pass | — |
| 30.1.3 | Sentinel benchmarks | ✅ | Determinism, counterexample, near-miss, regression, gold-family all pass | — |
| 30.1.4 | Adversarial | ✅ | 41/41 adversarial tests pass | — |
| 30.1.5 | Rollback | ✅ | Promote → revert → re-promote verified | — |
| 30.1.6 | MCP integration | ✅ | All 4 tools return correct responses | — |
| 30.1.7 | Export/import | ✅ | 16/16 tests pass (all 7 formats, round-trip) | — |
| 30.1.8 | @watch adapter | ✅ | Trajectory capture + redaction verified | — |

### 2.2 30.2 — Corpus & Benchmark Validation

| # | Task | Status | Results | Artifact |
|---|------|--------|---------|----------|
| 30.2.1 | Tiered corpus | ✅ | tiny/small/medium/large validated | — |
| 30.2.2 | Gold rule families | ✅ | 5/5 tests pass (0.03s) | `field-test/v0.1.0/gold-families-results.md` |
| 30.2.3 | Model bake-off | ⬜ | Not yet run | — |
| 30.2.4 | Prompt bake-off | ⬜ | Not yet run | — |
| 30.2.5 | Coverage measurement | ⬜ | Not yet run | — |
| 30.2.6 | Scale benchmarks | ✅ | Latency, memory, conflict all within targets | — |
| 30.2.7 | Cost-per-iteration | ⬜ | Not yet documented | — |

### 2.3 30.6 — Docker Validation

| # | Task | Status | Results | Artifact |
|---|------|--------|---------|----------|
| 30.6.1-30.6.14 | All Docker tests | ✅ | 104/104 tests pass (69.8s) | `field-test/v0.1.0/docker-test-results.md` |

### 2.4 30.7 — Advanced Validation

| # | Task | Status | Results | Artifact |
|---|------|--------|---------|----------|
| 30.7.1 | Performance baselines | ✅ | All 4 commands <70ms (threshold 500ms) | `field-test/v0.1.0/performance-baselines.json` |
| 30.7.2 | Failure mode catalog | ⬜ | Not yet created | — |
| 30.7.3 | Data drift & staleness | ⬜ | Not yet run | — |
| 30.7.4 | Rule conflict resolution | ⬜ | Not yet run | — |
| 30.7.5 | Token budget limits | ⬜ | Not yet run | — |
| 30.7.6 | Upgrade path | ⬜ | Not yet run | — |
| 30.7.7 | Concurrent agents | ⬜ | Not yet run | — |
| 30.7.8 | LLM provider fallback | ⬜ | Not yet run | — |
| 30.7.9 | Negative tests | ✅ | 10 negative trajectories created | `field-test/v0.1.0/corpus/curated/failures/negative/` |
| 30.7.10 | Golden trajectory set | ✅ | 10 golden trajectories + manifest created | `field-test/v0.1.0/corpus/golden/` |
| 30.7.11 | Rule quality scoring | ⬜ | Not yet run | — |
| 30.7.12 | Time-to-value | ✅ | Targets documented. Measurement script created. | `field-test/v0.1.0/time-to-value.md` |
| 30.7.13 | CI integration | ✅ | JUnit XML output function + tests created | `tests/field/test_ci_integration.py` |
| 30.7.14 | Export validation | ✅ | 16/16 export tests pass. All 7 formats + active-only filter verified. | `field-test/v0.1.0/export-validation.md` |

---

## 3. Bucket 2: Field Tests

### 3.1 30.3 — Single-Agent Field Tests

| # | Task | Status | Results | Artifact |
|---|------|--------|---------|----------|
| 30.3.1 | Coding agent harness | ⬜ | Not yet created | — |
| 30.3.2 | Cold-start | ⬜ | Not yet run | — |
| 30.3.3 | Bundled-pack | ⬜ | Not yet run | — |
| 30.3.4 | Learning | ⬜ | Not yet run | — |
| 30.3.5 | Cross-session | ⬜ | Not yet run | — |
| 30.3.6 | Long-horizon | ⬜ | Not yet run | — |
| 30.3.7 | Noisy trajectory | ⬜ | Not yet run | — |
| 30.3.8 | Human-correction | ⬜ | Not yet run | — |
| 30.3.9 | Demo field test | ⬜ | Not yet run | — |
| 30.3.10 | Repeat-failure reduction | ⬜ | Not yet run | — |
| 30.3.11 | Regression | ⬜ | Not yet run | — |

### 3.2 30.4 — Multi-Environment

| # | Task | Status | Results | Artifact |
|---|------|--------|---------|----------|
| 30.4.1 | macOS | ⬜ | Not yet run | — |
| 30.4.2 | Linux | ⬜ | Not yet run | — |
| 30.4.3 | Docker | ✅ | 104/104 Docker tests pass | `docker-test-results.md`, `docker-test-plan.md` |
| 30.4.4 | Homebrew | ⬜ | Not yet run | — |
| 30.4.5 | Standalone binary | ⬜ | Not yet run | — |

### 3.3 30.8 — Real Corpus Field Tests

| # | Task | Status | Results | Artifact |
|---|------|--------|---------|----------|
| 30.8.1 | Real corpus validation | ⬜ | Not yet run | — |
| 30.8.2 | Real corpus extraction | ⬜ | Not yet run | — |
| 30.8.3 | Real corpus replay | ⬜ | Not yet run | — |
| 30.8.4 | Real corpus promotion | ⬜ | Not yet run | — |
| 30.8.5 | Repeat-failure reduction | ⬜ | Not yet run | — |
| 30.8.6 | Cross-session memory | ⬜ | Not yet run | — |
| 30.8.7 | Golden set regression | ⬜ | Not yet run | — |
| 30.8.8 | Coverage measurement | ⬜ | Not yet run | — |
| 30.8.9 | Near-miss precision | ⬜ | Not yet run | — |
| 30.8.10 | Correction flow | ⬜ | Not yet run | — |
| 30.8.11 | Export to AGENTS.md | ⬜ | Not yet run | — |
| 30.8.12 | Cost measurement | ⬜ | Not yet run | — |

---

## 4. Bucket 3: Reporting

| # | Task | Status | Results | Artifact |
|---|------|--------|---------|----------|
| 30.5.1 | Field test methodology | ⬜ | Not yet written | — |
| 30.5.2 | Field test report | ⬜ | Not yet written | — |
| 30.5.3 | Known issues | ⬜ | Not yet written | — |
| 30.5.4 | Update release notes | ⬜ | Not yet written | — |

---

## 5. Results Detail

### 5.1 Baseline Metrics

| Metric | Value |
|--------|-------|
| Test suite size | 844 tests |
| Source files | 198 |
| Rules in store | 0 |
| Coverage | 87% |
| Milestones shipped | 25/32 |

### 5.2 Gold Family Validation

| Suite | Tests | Passed | Failed | Time |
|-------|-------|--------|--------|------|
| `tests/corpus/test_gold.py` | 5 | 5 | 0 | 0.03s |

### 5.3 Docker Field Tests

| Suite | Tests | Passed | Failed | Time |
|-------|-------|--------|--------|------|
| Build & install | 5 | 5 | 0 | — |
| CLI integration | 23 | 23 | 0 | — |
| TUI | 10 | 10 | 0 | — |
| MCP server | 10 | 10 | 0 | — |
| Pipeline E2E | 10 | 10 | 0 | — |
| Redaction | 6 | 6 | 0 | — |
| Export/import | 13 | 13 | 0 | — |
| Git integration | 10 | 10 | 0 | — |
| Loop orchestrator | 6 | 6 | 0 | — |
| Multi-env | 6 | 6 | 0 | — |
| Compose | 5 | 5 | 0 | — |
| **Total** | **104** | **104** | **0** | **69.8s** |

### 5.4 Performance Baselines

| Command | Min (ms) | Avg (ms) | Max (ms) | Threshold (ms) | Pass |
|---------|----------|----------|----------|----------------|------|
| `cauterule list` | 63.6 | 65.4 | 66.9 | 500 | ✅ |
| `cauterule health` | 64.1 | 64.4 | 64.7 | 500 | ✅ |
| `cauterule validate` | 63.3 | 64.5 | 65.4 | 500 | ✅ |
| `cauterule inject "git push"` | 64.6 | 65.7 | 67.2 | 500 | ✅ |

### 5.5 Export Validation

| Check | Result |
|-------|--------|
| 7 export formats (cursor, claude, agents, windsurf, aider, markdown, json) | ✅ All 7 pass |
| Active-only filter | ✅ Active rules only by default |
| Retired rules excluded | ✅ `include_retired=False` is default |
| Export tests total | 16/16 pass (0.02s) |

### 5.6 Golden Trajectory Set

| Metric | Value |
|--------|-------|
| Trajectories created | 10 |
| Expected rules documented | 10 (in `golden-manifest.json`) |
| Domains covered | git, python, docker, pip, kubernetes, test, API, terraform, selenium, deploy |

### 5.7 Negative Trajectories

| Metric | Value |
|--------|-------|
| Negative cases created | 10 |
| Types covered | success, opinion, cosmetic, env-info, log, warning, intermittent, operator-error, feature-request, flaky-pass |

### 5.8 CI Integration

| Metric | Value |
|--------|-------|
| JUnit XML output function | Created in `src/cauterule/cli/test.py` |
| Test coverage | 5 candidates (3 pass, 2 fail) |
| Exit code behavior | 0 when all pass, non-zero on failure |

---

## 6. Completed Work Items

### Documents Created

| File | Content |
|------|---------|
| `field-test/v0.1.0/baseline.md` | Baseline metrics |
| `field-test/v0.1.0/gold-families-results.md` | Gold family validation results |
| `field-test/v0.1.0/performance-baselines.json` | Performance baseline measurements |
| `field-test/v0.1.0/ci.md` | CI integration test documentation |
| `field-test/v0.1.0/export-validation.md` | Export format validation results |
| `field-test/v0.1.0/time-to-value.md` | Time-to-value targets and measurement |
| `field-test/v0.1.0/negative-test-plan.md` | 10 negative test trajectory descriptions |
| `field-test/v0.1.0/docker-test-results.md` | Docker field test results (104 tests) |
| `field-test/v0.1.0/corpus/golden/golden-manifest.json` | Golden trajectory manifest |
| `field-test/v0.1.0/corpus/curated/failures/negative/` | 10 negative JSONL trajectories |

### Scripts Created

| Script | Purpose |
|--------|---------|
| `scripts/measure_performance.py` | Performance baseline measurement |
| `scripts/measure_ttv.sh` | Time-to-value wall-clock measurement |

### Tests Created

| Test File | Purpose |
|-----------|---------|
| `tests/field/test_ci_integration.py` | CI integration (JUnit XML output) |

---

## 7. Next Test Block

These are the highest-priority remaining Pre-Field Validation tasks:

| Priority | Task | Issue | Why |
|----------|------|-------|-----|
| P1 | 30.7.2 Failure mode catalog (20 trajectories) | #386 | Needed for golden set and corpus tests |
| P2 | 30.2.4 Prompt bake-off | #242 | Needed to select best extractor prompt |
| P3 | 30.2.5 Coverage measurement | #243 | Must meet ≥80% target |
| P4 | 30.2.3 Model bake-off | #241 | Compare OMLX vs gpt-4o-mini quality |
| P5 | 30.2.7 Cost-per-iteration | #245 | Document costs |
| P6 | 30.7.3-30.7.8 | #387-#392 | Advanced validation tests |

After Pre-Field Validation: Field Tests (30.3, 30.4, 30.8)