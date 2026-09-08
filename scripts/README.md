# CauterRule Scripts

Utility scripts for development, testing, corpus management, and field test execution.

## Corpus Acquisition

| Script | Purpose | Usage |
|--------|---------|-------|
| `seed-corpus.py` | Seed the field-test corpus from test fixtures, golden trajectories, and failure mode catalog | `python scripts/seed-corpus.py` |
| `seed-corpus.py --status` | Show corpus stats (counts per source) | `python scripts/seed-corpus.py --status` |
| `seed-corpus.py --validate` | Validate all trajectories in the corpus | `python scripts/seed-corpus.py --validate` |
| `create-trajectory.py` | Interactive wizard to create a single trajectory JSONL file | `python scripts/create-trajectory.py` |
| `create-trajectory.py --list` | List all existing trajectories in the corpus | `python scripts/create-trajectory.py --list` |
| `create-trajectory.py --batch <file.json>` | Batch-import trajectories from a JSON array file | `python scripts/create-trajectory.py --batch data.json` |
| `collect-ci-corpus.sh` | Download CI failure logs from GitHub Actions and convert to trajectory JSONL | `bash scripts/collect-ci-corpus.sh [--limit N]` |
| `generate-m7-corpus.py` | Regenerate `corpus/public/` (golden families, counterexample, nearmiss, staleness, synthetic) from canonical scenarios | `python scripts/generate-m7-corpus.py` |
| `normalize-corpus.py` | Backfill missing trajectory metadata fields (incl. `expected_outcome`) — idempotent | `python scripts/normalize-corpus.py --path corpus/public` |
| `normalize-corpus.py --dry-run` | Report what would change without writing | `python scripts/normalize-corpus.py --dry-run` |

## Field Test Run

| Script | Purpose | Usage |
|--------|---------|-------|
| `run-field-test.py` | Run v0.2.0 field test sweeps (single corpus, `--all`, or hermetic validation suites). Outputs to `field-test/results/0.2.0/` | `python scripts/run-field-test.py golden --output-dir field-test/results/0.2.0` |
| `run-field-test.py --run-validation` | Run all hermetic pre-field validation suites (#432-#437, #443-#444): gate, matcher, safety, attribution, specificity, sentinel benchmarks, scale, adversarial, corpus, observe, tui | `python scripts/run-field-test.py --run-validation --output-dir field-test/results/0.2.0/` |
| `run-field-test.py --validation-suite <name>` | Run a single validation suite only | `python scripts/run-field-test.py --run-validation --validation-suite sentinel_benchmark` |
| `run-field-test.py --skip-preflight` | Skip provider/corpus preflight checks (for hermetic local runs) | `python scripts/run-field-test.py successes --llm-provider openai --llm-base-url http://localhost:8000/v1 --skip-preflight --output-dir field-test/results/0.2.0` |

**v0.2.0 runner features:**
- Pre-extraction gate (strict on `successes`/`failures/negative`, relaxed elsewhere) — logs `pre_extraction_drops`
- Corpus-aware matcher thresholds (0.70 curated, 0.45 raw, 0.40 cross-repo)
- Safety-adjusted scoring — `silence_rate`, `safety_summary` per corpus
- Trigger specificity distribution (specific/moderate/generic, generic target <10%)
- Inconclusive attribution breakdown (`broad_trigger`/`matcher_gap`/`corpus_mismatch`/`ambiguous_evidence`)
- Preflight checks with cost estimate, written to `preflight.json`
- Harness health assertions after each sweep, written to `harness_health.json`
- LLM call avoidance tracking (pre-extraction gate savings)
- Per-run artifacts: `meta.json`, `results.jsonl`, `summary.json`, `preflight.json`, `harness_health.json`
| `compare-runs.py` | Compare two field-test run snapshots — diff inconclusive rates, specificity, silence rates, harness health | `python scripts/compare-runs.py <dir-1> <dir-2> [label1] [label2]` |
| `generate-safety-corpus.py` | Generate expanded safety corpora (successes, negatives, nearmiss) to meet ≥50 targets | `python scripts/generate-safety-corpus.py` |

## Performance & Measurement

| Script | Purpose | Usage |
|--------|---------|-------|
| `measure_performance.py` | Measure CLI command response times (list, health, validate, inject) | `python scripts/measure_performance.py` |
| `measure_ttv.sh` | Measure time-to-value wall-clock duration (install → first prevented failure) | `bash scripts/measure_ttv.sh` |

## Build & Distribution

| Script | Purpose | Usage |
|--------|---------|-------|
| `build.sh` | Build Python distribution artifacts (wheel) | `bash scripts/build.sh` |
| `build_binary.sh` | Build standalone binary via PyInstaller | `bash scripts/build_binary.sh` |
| `docker_field_test.sh` | Run all Docker field test stages sequentially | `bash scripts/docker_field_test.sh [--stage N] [--skip-build]` |

## Quick Start

```bash
# Seed the corpus from all available sources
python scripts/seed-corpus.py

# Normalize corpus metadata (fills expected_outcome)
python scripts/normalize-corpus.py --path field-test/corpus
python scripts/normalize-corpus.py --path corpus/public

# Show corpus stats
python scripts/seed-corpus.py --status

# Validate all trajectories
python scripts/seed-corpus.py --validate

# Collect CI failure logs
bash scripts/collect-ci-corpus.sh --limit 10

# Create a trajectory interactively
python scripts/create-trajectory.py

# Measure performance
python scripts/measure_performance.py

# Run hermetic validation suites (pre-field validation, ~#432-#437, #443-#444)
python scripts/run-field-test.py --run-validation --output-dir field-test/results/0.2.0

# Run a field-test sweep on the golden corpus
CAUTERULE_LLM_API_KEY=dummy \
python scripts/run-field-test.py golden \
  --llm-provider openai --llm-model llama-3.2-3b-instruct \
  --llm-base-url http://localhost:8000/v1 \
  --output-dir field-test/results/0.2.0
```