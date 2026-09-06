# CauterRule v0.1.0 — Field Test Directory

This directory contains all field test plans, execution results, corpus, and reference artifacts for M30. It is organized for **repeatability** — anyone can run the field tests again by following the instructions below.

---

## Directory Structure

```
docs/field-test/v0.1.0/          ← Plans, specs, and summary reports (in docs)
├── README.md                    ← This file — directory index
├── field-test-plan.md           ← Master field test plan (Phases 1-6)
├── corpus-plan.md               ← Corpus acquisition plan
├── corpus-test-plan.md          ← Real corpus field test plan (Phase 7, 30.8)
├── docker-test-plan.md          ← Docker-specific field test plan
├── docker-test-results.md       ← Docker test results (104 tests, 0 failed)
└── results-summary.md           ← Consolidated results tracker (all buckets)

field-test/v0.1.0/               ← Execution artifacts, results, corpus (in repo root)
├── README.md                    ← (this file — see docs/field-test/v0.1.0/README.md)
├── baseline.md                  ← 30.1.1 Baseline metrics
├── gold-families-results.md     ← 30.2.2 Gold family validation results
├── performance-baselines.json   ← 30.7.1 Performance baseline measurements
├── export-validation.md         ← 30.7.14 Export format validation results
├── time-to-value.md             ← 30.7.12 Time-to-value targets and measurement
├── negative-test-plan.md        ← 30.7.9 Negative test trajectory descriptions
├── corpus/
│   ├── golden/                  ← 30.7.10 Golden trajectory set (10 + manifest)
│   │   ├── golden-manifest.json
│   │   ├── G-001-*.jsonl ... G-010-*.jsonl
│   └── curated/
│       └── failures/
│           └── negative/        ← 30.7.9 Negative trajectories (10 files)
│               ├── N-001-*.jsonl ... N-010-*.jsonl
```

---

## What Each File Contains

### Plans (for reading, not modifying)

| File | Content | Pages |
|------|---------|-------|
| `docs/field-test/v0.1.0/field-test-plan.md` | Master plan: all 5 phases, corpus, LLM config, acceptance criteria | ~35 pages |
| `docs/field-test/v0.1.0/corpus-plan.md` | Where to get real corpus, collection process, sources, targets | ~15 pages |
| `docs/field-test/v0.1.0/corpus-test-plan.md` | Real corpus field tests (30.8.1-30.8.12) — extract, replay, promote, reduce | ~12 pages |
| `docs/field-test/v0.1.0/docker-test-plan.md` | 15-stage Docker test plan with pass/fail criteria | ~10 pages |

### Results (executed artifacts)

| File | Content | Status |
|------|---------|--------|
| `docs/field-test/v0.1.0/results-summary.md` | Consolidated results, all buckets, next priorities | ✅ Updated |
| `docs/field-test/v0.1.0/docker-test-results.md` | Docker: 104 tests, 0 failures, 69.8s | ✅ Complete |
| `field-test/v0.1.0/baseline.md` | Baseline: 844 tests, 0 rules, 87% coverage | ✅ Complete |
| `field-test/v0.1.0/gold-families-results.md` | Gold families: 5/5 tests pass | ✅ Complete |
| `field-test/v0.1.0/performance-baselines.json` | All commands <70ms (threshold 500ms) | ✅ Complete |
| `field-test/v0.1.0/export-validation.md` | Export: 16/16 tests pass, all 7 formats | ✅ Complete |
| `field-test/v0.1.0/time-to-value.md` | TTV targets: install <30s, first rule <5min | ✅ Complete |

### Corpus (test data)

| Path | Content | Count |
|------|---------|-------|
| `field-test/v0.1.0/corpus/golden/` | Golden trajectories with expected rules | 10 |
| `field-test/v0.1.0/corpus/golden/golden-manifest.json` | Mapping of trajectory to expected rule | 1 |
| `field-test/v0.1.0/corpus/curated/failures/negative/` | Negative trajectories (should NOT produce rules) | 10 |

---

## How To Run Field Tests

### Prerequisites

```bash
pip install -e ".[dev]"
docker build -t cauterule:field-test .
# For real-LLM tests: ensure OMLX is running
# export CAUTERULE_LLM_PROVIDER=openai
# export CAUTERULE_MODEL=llama-3.2-3b-instruct
# export OPENAI_API_KEY=dummy
# export OPENAI_BASE_URL=http://localhost:8000/v1
```

### Run Pre-Field Validation

```bash
# System validation (30.1)
pytest tests/ -v -m "not slow" --tb=short
pytest tests/adversarial/ -v
pytest tests/cli/ -v
pytest tests/tui/ -v
pytest tests/mcp/ -v
pytest tests/export/ -v
pytest tests/import_/ -v
pytest tests/store/ -v -k "rollback"

# Corpus & benchmark validation (30.2)
pytest tests/corpus/ -v
pytest tests/benchmark/ -v

# Docker validation (30.6)
pytest tests/field/ -v --tb=short

# Performance baselines (30.7.1)
python scripts/measure_performance.py

# Advanced validation (30.7)
pytest tests/field/test_ci_integration.py -v
```

### Run Field Tests

```bash
# Single-agent (30.3) — requires OMLX or similar
# python field-test/v0.1.0/harness.py
# See docs/field-test/v0.1.0/field-test-plan.md Section 11 for details

# Multi-environment (30.4)
# Run on macOS, Linux, Docker, Homebrew, binary
# See docs/field-test/v0.1.0/field-test-plan.md Section 12

# Real corpus tests (30.8)
# See docs/field-test/v0.1.0/corpus-test-plan.md for full instructions
```

---

## M30 Field Test Taxonomy

```
Bucket 1: Pre-Field Validation (30.1, 30.2, 30.6, 30.7)
  └── NOT field tests — regression, benchmark, infra checks
  └── Must pass before field tests begin

Bucket 2: Field Tests (30.3, 30.4, 30.8)
  └── Actual field tests — real corpus, real LLM, real agents
  └── Core validation that the system learns from failures

Bucket 3: Reporting (30.5)
  └── Documentation of methodology, results, known issues
```

---

## GitHub Issues

All field test tasks are tracked under M30 milestone (milestone #31):

| Range | Task Group | Status |
|-------|-----------|--------|
| #231-#238 | 30.1 System validation | 7/8 closed |
| #239-#245 | 30.2 Corpus & benchmarks | 2/7 closed |
| #246-#255, #31 | 30.3 Single-agent | 0/11 closed |
| #256-#260 | 30.4 Multi-environment | 0/5 closed |
| #261-#264 | 30.5 Reporting | 0/4 closed |
| #370-#384 | 30.6 Docker validation | 15/15 closed ✅ |
| #385-#398 | 30.7 Advanced validation | 5/14 closed |
| #399-#410 | 30.8 Real corpus | 0/12 closed |

---

## Key Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Test suite | 844 | ≥781 |
| Docker tests | 104/104 | ≥100 |
| Pre-field validation | 12/33 | 33 |
| Field tests | 0/32 | 32 |
| Coverage | 87% | ≥95% |
| CLI performance | <70ms | <500ms |
| Repeat-failure reduction | — | ≥50% |
| Time-to-value | — | <15 min |

---

## Notes

- The `docs/field-test/v0.1.0/` directory contains plans and summary reports.
- The `field-test/v0.1.0/` directory at the repo root contains execution artifacts and corpus data.
- Results are tracked in `docs/field-test/v0.1.0/results-summary.md` — update after each test run.
- Corpus acquisition is tracked in `docs/field-test/v0.1.0/corpus-plan.md`.
- Docker tests are the only 100% complete section (104/104, all passing).