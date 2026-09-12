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
| `generate-v030-corpus.py` | Generate the v0.3.0 corpora (#635): `field-test/corpus/{adapters,lifecycle,packs,mcp,otel}` with full annotation metadata | `python scripts/generate-v030-corpus.py` |
| `generate-reference-expansion.py` | Generate the paraphrase reference corpus (270+ trajectories, #489) into `corpus/public/reference-expansion/` | `python scripts/generate-reference-expansion.py` |
| `convert_agentharm_to_corpus.py` | Convert AgentHarm (Hugging Face, #699) harmful/benign cases → `corpus/public/adversarial/unsafe_realistic/` + `corpus/public/successes/` | `python scripts/convert_agentharm_to_corpus.py --harmful <jsonl> --benign <jsonl> --output <dir>` |
| `convert_injecagent_to_corpus.py` | Convert InjecAgent indirect-injection cases (tool-output borne, #700) → `corpus/public/adversarial/tool_output_injection/` | `python scripts/convert_injecagent_to_corpus.py --user-cases <jsonl> --attacker-cases <jsonl> --output <dir>` |
| `convert_harmbench_to_corpus.py` | Convert HarmBench behaviors → `corpus/public/adversarial/{misleading,contradiction}_harmbench/` (15 each, #701) | `python scripts/convert_harmbench_to_corpus.py --behaviors <csv> --output <dir>` |
| `convert_otel_issues_to_corpus.py` | Mine OTel Demo GH issues for span-export/collector failures → `corpus/public/otel/` (#702) | `python scripts/convert_otel_issues_to_corpus.py --issues <json> --output corpus/public/otel` |
| `convert_mcp_issues_to_corpus.py` | Mine MCP servers GH issues for auth/transport failures → `corpus/public/mcp/` (#703) | `python scripts/convert_mcp_issues_to_corpus.py --issues <json> --output corpus/public/mcp` |
| `convert_terraform_issues_to_corpus.py` | Mine Terraform provider GH issues for lifecycle/infra failures → `corpus/public/lifecycle_infra/` (#704) | `python scripts/convert_terraform_issues_to_corpus.py --issues <json> --output corpus/public/lifecycle_infra` |
| `convert_webarena_to_corpus.py` | Mine WebArena browser-tool failures (stale element, frame, alert) → `corpus/public/browser/` (#705) | `python scripts/convert_webarena_to_corpus.py --issues <json> --output corpus/public/browser` |
| `convert_bugsinpy_to_corpus.py` | Convert BugsInPy real Python bugs (pytest failures + paired successes, #706) → `corpus/public/real-world/bugsinpy/` | `python scripts/convert_bugsinpy_to_corpus.py --bugs <jsonl> --output corpus/public/real-world/bugsinpy` |

## Field Test Run

| Script | Purpose | Usage |
|--------|---------|-------|
| `run-field-test.py` | Run v0.3.0 field test sweeps (single corpus, `--all`, or hermetic validation suites). Outputs to `field-test/results/0.3.0/` | `python scripts/run-field-test.py golden --output-dir field-test/results/0.3.0` |
| `run-field-test.py --run-validation` | Run all hermetic pre-field validation suites (#432-#437, #443-#444): gate, matcher, safety, attribution, specificity, sentinel benchmarks, scale, adversarial, corpus, observe, tui | `python scripts/run-field-test.py --run-validation --output-dir field-test/results/0.3.0/` |
| `run-field-test.py --validation-suite <name>` | Run a single validation suite only | `python scripts/run-field-test.py --run-validation --validation-suite sentinel_benchmark` |
| `run-field-test.py --skip-preflight` | Skip provider/corpus preflight checks (for hermetic local runs) | `python scripts/run-field-test.py successes --llm-provider openai --llm-base-url http://localhost:8000/v1 --skip-preflight --output-dir field-test/results/0.3.0` |
| `run-field-test.py --regression-v020` | Emit a per-corpus delta table vs the v0.2.0 baseline | `python scripts/run-field-test.py --regression-v020 --output-dir field-test/results/0.3.0` |

**v0.3.0 runner features:**
- Pre-extraction gate (strict on `successes`/`failures/negative`/`nearmiss`, relaxed elsewhere)
- Corpus-aware matcher thresholds (`strict` 0.70, `loose` 0.35, `semantic` 0.60, `transfer` 0.40 — see `replay/matcher.py`), with an OMLX override
- Safety-adjusted scoring — `silence_rate`, `safety_summary` per corpus
- Trigger specificity distribution (specific/moderate/generic, generic target <10%)
- Inconclusive attribution breakdown (`broad_trigger`/`matcher_gap`/`corpus_mismatch`/`ambiguous_evidence`)
- **Gate-drop reason breakdown (#697)** — `gate_dropped_by_reason` in `summary.json`, per-trajectory `gate.reason` in `results.jsonl`
- **Wilson confidence intervals (#695)** — `confidence_intervals` for `pass_rate` / `safety_silence_rate` in `summary.json`
- Preflight checks with cost estimate → `preflight.json`; harness health → `harness_health.json`
- LLM call avoidance tracking (pre-extraction gate savings)
- **Adversarial vectors (#696)** — `adversarial/tool_output_injection` and `adversarial/compounding_multiturn` alongside the 5 base vectors
- Per-run artifacts: `meta.json`, `results.jsonl`, `summary.json`, `preflight.json`, `harness_health.json`
| `compare-runs.py` | Compare two field-test run snapshots — diff inconclusive rates, specificity, silence rates, harness health | `python scripts/compare-runs.py <dir-1> <dir-2> [label1] [label2]` |
| `generate-safety-corpus.py` | Generate expanded safety corpora (successes, negatives, nearmiss) to meet ≥50 targets | `python scripts/generate-safety-corpus.py` |
| `sweep-local-llama.sh` | Resume-able v0.3.0 sweep over all corpora on local OMLX Llama-3.2-3B (skips corpora already run); add `run-field-test.py` model-config for other models | `bash scripts/sweep-local-llama.sh` |

## Field-Test Analysis & Calibration

| Script | Purpose | Usage |
|--------|---------|-------|
| `generate_field_test_report.py` | Single source of truth for field-test tables — renders model totals + per-model/per-corpus P/F/I (with CIs) from raw `results.jsonl` into `docs/field-test/v0.3.0/generated-results.md` (#686) | `python scripts/generate_field_test_report.py [--output <doc>]` |
| `generate_field_test_report.py --check` | Fail (exit 1) if the committed generated report drifts from a fresh render — wired into CI | `python scripts/generate_field_test_report.py --check` |
| `diagnose_corpus.py` | Root-cause a 0-pass corpus: reference coverage (incl. the #698 public reference corpora), uncovered target domains, and (via `--results`) the candidate pre-filter funnel (#690) | `python scripts/diagnose_corpus.py [--corpus otel] [--results <results.jsonl>]` |
| `calibrate_thresholds.py` | Sweep matcher thresholds over the golden/nearmiss sample and render precision/recall evidence (#691) | `python scripts/calibrate_thresholds.py --output docs/field-test/v0.3.0/threshold-calibration.md` |
| `check_corpus_balance.py` | Flag failure-only `source_repo` values across `corpus/public` so new sources pair failures with successes (#707) | `python scripts/check_corpus_balance.py [--strict]` |

## Performance & Measurement

| Script | Purpose | Usage |
|--------|---------|-------|
| `measure_performance.py` | Measure CLI command response times (list, health, validate, inject) | `python scripts/measure_performance.py` |
| `measure_ttv.sh` | Measure time-to-value wall-clock duration (install → first prevented failure) | `bash scripts/measure_ttv.sh` |
| `compare_benchmarks.py` | Compare pytest-benchmark runs against a baseline; fail on >15% regression (#605) | `python scripts/compare_benchmarks.py <baseline.json> <.benchmarks/current.json>` |
| `compare_benchmarks.py --write-baseline` | Regenerate the minimal committed baseline (name→mean) from a full pytest-benchmark JSON — keeps `benchmarks/baseline.json` tiny instead of the multi-MB raw dump (#679) | `python scripts/compare_benchmarks.py --write-baseline .benchmarks/current.json benchmarks/baseline.json` |

## Build & Distribution

| Script | Purpose | Usage |
|--------|---------|-------|
| `build.sh` | Build Python distribution artifacts (wheel) | `bash scripts/build.sh` |
| `build_binary.sh` | Build standalone binary via PyInstaller | `bash scripts/build_binary.sh` |
| `docker_field_test.sh` | Build the hardened image and run the v0.3.0 docker-marked pytest suite (results → `field-test/results/0.3.0/docker/`); `--legacy` runs the v0.2.0-era 15 shell stages | `bash scripts/docker_field_test.sh [--skip-build] [--legacy [--stage N]]` |

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
python scripts/run-field-test.py --run-validation --output-dir field-test/results/0.3.0

# Run a field-test sweep on the golden corpus
CAUTERULE_LLM_API_KEY=dummy \
python scripts/run-field-test.py golden \
  --llm-provider openai --llm-model llama-3.2-3b-instruct \
  --llm-base-url http://localhost:8000/v1 \
  --output-dir field-test/results/0.3.0

# Regenerate the field-test result tables (single source of truth) and check for drift
python scripts/generate_field_test_report.py
python scripts/generate_field_test_report.py --check

# Root-cause a 0-pass corpus (reference coverage + candidate pre-filter funnel)
python scripts/diagnose_corpus.py --corpus otel

# Re-sweep and record matcher threshold calibration evidence
python scripts/calibrate_thresholds.py --output docs/field-test/v0.3.0/threshold-calibration.md

# Warn on failure-only corpus sources (add --strict to fail)
python scripts/check_corpus_balance.py

# Refresh the minimal perf baseline from a benchmark run (#679)
python scripts/compare_benchmarks.py --write-baseline .benchmarks/current.json benchmarks/baseline.json
```