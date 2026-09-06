# CauterRule User Guide

## Overview

CauterRule extracts actionable standing rules from agent execution failures. The system captures a failure trajectory, extracts a candidate rule, replay-tests it against historical data, and stores it for future injection.

This guide covers:

- Running CauterRule with local or cloud LLMs
- Understanding the corpus structure
- Running field tests against any corpus
- Interpreting results
- Generating synthetic trajectories for testing

---

## Quick Start

### Prerequisites

- Python 3.12+
- For local LLM: OMLX running at `http://localhost:8000/v1`
- For cloud LLM: OpenRouter or OpenAI API key

### Installation

```bash
git clone https://github.com/deghosal-2026/CauterRule.git
cd CauterRule
pip install -e .
```

### Run the Demo

```bash
cauterule demo --failures 1
```

---

## Extracting Rules from a Trajectory

### Single trajectory extraction

```bash
# With local OMLX
CAUTERULE_LLM_API_KEY=dummy \
cauterule extract field-test/corpus/golden/G-001-git-push-non-ff.jsonl \
  --llm-provider openai --llm-model llama-3.2-3b-instruct \
  --llm-base-url http://localhost:8000/v1

# With cloud LLM via OpenRouter
CAUTERULE_LLM_API_KEY=sk-or-... \
cauterule extract field-test/corpus/golden/G-001-git-push-non-ff.jsonl \
  --llm-provider openai --llm-model openai/gpt-4o-mini \
  --llm-base-url https://openrouter.ai/api/v1
```

### Dry-run extraction (no LLM call)

```bash
cauterule extract field-test/corpus/golden/G-001-git-push-non-ff.jsonl --dry-run
```

---

## Running Field Tests

The field-test runner (`scripts/run-field-test.py`) runs extraction across entire corpora, replay-tests candidates against the full reference set, and produces incremental results.

### Corpus Types

| Type | Path | Trajectories | Purpose |
|---|---|---|---|
| `golden` | `field-test/corpus/golden/` | 10 | Regression anchor — expected rules known |
| `failures/positive` | `field-test/corpus/curated/failures/positive/` | 30 | Real failure trajectories that should produce rules |
| `failures/negative` | `field-test/corpus/curated/failures/negative/` | 10 | Failure traces that should NOT produce rules |
| `successes` | `field-test/corpus/curated/successes/` | 20 | Success trajectories — rules must not break them |
| `nearmiss` | `field-test/corpus/curated/nearmiss/` | 14 | Looks like a failure but should not trigger |
| `noisy` | `field-test/corpus/curated/noisy/` | 5 | Misleading/ambiguous traces — robustness test |
| `corrections` | `field-test/corpus/curated/corrections/` | 5 | Human-correction-to-rule flow |
| `raw/opencode` | `field-test/corpus/raw/opencode/` | 25 | Real OpenCode session trajectories |
| `raw/synthetic` | `field-test/corpus/raw/synthetic/` | 145 | Generated synthetic scenarios |
| `raw/ci` | `field-test/corpus/raw/ci/` | 110 | GitHub Actions CI failure logs |
| `raw/sibling-repos` | `field-test/corpus/raw/sibling-repos/` | 10 | Agent runs on sibling repos |
| `raw/corrections` | `field-test/corpus/raw/corrections/` | 5 | Manual correction transcripts |
| `raw/cross-session` | `field-test/corpus/raw/cross-session/` | 5 | Cross-session repeat failures |

### With Local OMLX (Apple Silicon)

```bash
# Single corpus type
CAUTERULE_LLM_API_KEY=dummy \
python scripts/run-field-test.py golden \
  --llm-provider openai --llm-model llama-3.2-3b-instruct \
  --llm-base-url http://localhost:8000/v1 \
  --output-dir field-test/results/0.1.0

# All curated corpus types
CAUTERULE_LLM_API_KEY=dummy \
python scripts/run-field-test.py --all \
  --llm-provider openai --llm-model llama-3.2-3b-instruct \
  --llm-base-url http://localhost:8000/v1 \
  --output-dir field-test/results/0.1.0
```

### With Cloud LLM (OpenRouter)

```bash
# Single corpus type
CAUTERULE_LLM_API_KEY=sk-or-... \
python scripts/run-field-test.py golden \
  --llm-provider openai --llm-model openai/gpt-4o-mini \
  --llm-base-url https://openrouter.ai/api/v1 \
  --output-dir field-test/results/0.1.0

# All 13 corpus types
CAUTERULE_LLM_API_KEY=sk-or-... \
python scripts/run-field-test.py --all \
  --llm-provider openai --llm-model openai/gpt-4o-mini \
  --llm-base-url https://openrouter.ai/api/v1 \
  --output-dir field-test/results/0.1.0
```

### With Ollama (Local)

```bash
CAUTERULE_LLM_API_KEY=dummy \
python scripts/run-field-test.py golden \
  --llm-provider ollama --llm-model llama3 \
  --output-dir field-test/results/0.1.0
```

---

## Output Structure

Results are written to `{output-dir}/{corpus_type}/{llm_label}/{date}/`:

```
field-test/results/0.1.0/
  golden/
    omlx-openai-Llama-3.2-3B-Instruct-4bit/
      2026-09-06/
        meta.json         # run configuration
        results.jsonl     # per-trajectory results (appended live)
        summary.json      # aggregate metrics (rewritten live)
    openai-openai_gpt-4o-mini/
      2026-09-06/
        ...
  failures_positive/
    ...
```

### Results Format

Each line in `results.jsonl` is a JSON object with:

```json
{
  "trajectory_id": "G-001-git-push-non-ff",
  "status": "done",
  "candidate_count": 1,
  "candidates": [
    {
      "when": "when git push fails with non-fast-forward",
      "do": "pull latest changes before pushing",
      "confidence": 0.85,
      "extraction_pass": 1,
      "temperature": 0.2,
      "llm_response": "{\"when\": {\"trigger\": \"...\"}}"
    }
  ],
  "best": {
    "precision": 1.0,
    "recall": 0.05,
    "verdict": "pass"
  }
}
```

---

## Options

| Flag | Default | Description |
|---|---|---|
| `corpus_type` | — | `golden`, `failures/positive`, `failures/negative`, `successes`, `nearmiss`, `noisy`, `corrections`, `raw/opencode`, `raw/synthetic`, `raw/ci`, `raw/sibling-repos`, `raw/corrections`, `raw/cross-session` |
| `--all` | off | Run all corpus types |
| `--llm-provider` | `openai` | `openai`, `anthropic`, `ollama`, `litellm` |
| `--llm-model` | `gpt-4o-mini` | Model name |
| `--llm-base-url` | `""` | Base URL (OMLX: `http://localhost:8000/v1`, OpenRouter: `https://openrouter.ai/api/v1`) |
| `--output-dir` | `field-test/results/0.1.0` | Output directory |
| `--max-workers` | `4` | Parallel trajectories |
| `--temperatures` | `0.2,0.5` | Comma-separated temperatures |
| `CAUTERULE_LLM_API_KEY` | env var | API key for cloud LLMs |

---

## Generating Synthetic Trajectories

CauterRule includes a generator for creating synthetic trajectory corpora:

```bash
# Generate full corpus (200-250 trajectories)
python scripts/generate-corpus.py

# Dry-run: show counts without writing
python scripts/generate-corpus.py --dry-run

# Validate existing corpus
python scripts/generate-corpus.py --validate
```

The generator produces trajectories across domains:

- **git** — push, merge, rebase, detached HEAD, auth failures
- **python** — import errors, syntax errors, type errors, venv issues
- **docker** — build failures, port conflicts, OOM, missing dockerfiles
- **test** — assertion failures, timeouts, flaky tests
- **deploy** — health checks, image pull failures, configmap issues
- **env** — missing variables, wrong paths, permission denied
- **shell** — command not found, disk full, process killed
- **workflow** — wrong file targeting, stale assumptions, misleading errors
- **browser automation** — element not found, stale elements, timeouts
- **research** — API rate limits, timeouts, missing data

---

## Interpreting Results

### Verdict Meanings

| Verdict | Meaning |
|---|---|
| **pass** | Candidate would have prevented failures without breaking successes |
| **inconclusive** | No clear evidence either way — usually means the candidate is plausible but too broad |
| **fail** | Candidate would break successes or is too weak to prevent failures |

### Metrics

| Metric | Description |
|---|---|
| `candidates` | Number of extracted candidates from a trajectory |
| `precision` | Ratio of prevented failures to total triggered outcomes |
| `recall` | Ratio of prevented failures to total historical failures |
| `failures_prevented` | Trajectories where the candidate would have prevented a failure |
| `successes_broken` | Trajectories where the candidate would have broken a success |

---

## Examples

### Example 1: Basic Golden Set Evaluation

```bash
CAUTERULE_LLM_API_KEY=dummy \
python scripts/run-field-test.py golden \
  --llm-provider openai --llm-model llama-3.2-3b-instruct \
  --llm-base-url http://localhost:8000/v1 \
  --output-dir field-test/results/0.1.0
```

### Example 2: Cloud Model Bake-off

```bash
# Run all 3 models on the same corpus
for MODEL in "openai/gpt-4o-mini" "meta-llama/llama-3.1-8b-instruct" "anthropic/claude-3.5-sonnet"; do
  CAUTERULE_LLM_API_KEY=sk-or-... \
  python scripts/run-field-test.py golden \
    --llm-provider openai --llm-model "$MODEL" \
    --llm-base-url https://openrouter.ai/api/v1 \
    --output-dir field-test/results/0.1.0
done
```

### Example 3: Safety-Corpus Focus

```bash
CAUTERULE_LLM_API_KEY=sk-or-... \
python scripts/run-field-test.py successes \
  --llm-provider openai --llm-model openai/gpt-4o-mini \
  --llm-base-url https://openrouter.ai/api/v1 \
  --output-dir field-test/results/0.1.0
```

### Example 4: Raw Corpus Breadth

```bash
CAUTERULE_LLM_API_KEY=dummy \
python scripts/run-field-test.py raw/synthetic \
  --llm-provider openai --llm-model llama-3.2-3b-instruct \
  --llm-base-url http://localhost:8000/v1 \
  --output-dir field-test/results/0.1.0
```

### Example 5: Watch Progress Mid-Run

```bash
tail -f field-test/results/0.1.0/golden/omlx-openai-Llama-3.2-3B-Instruct-4bit/2026-09-06/summary.json
tail -f field-test/results/0.1.0/golden/omlx-openai-Llama-3.2-3B-Instruct-4bit/2026-09-06/results.jsonl
```

---

## Advanced: Multi-Pass Extraction

The runner supports multiple extraction passes at different temperatures:

```bash
CAUTERULE_LLM_API_KEY=dummy \
python scripts/run-field-test.py golden \
  --llm-provider openai --llm-model llama-3.2-3b-instruct \
  --llm-base-url http://localhost:8000/v1 \
  --temperatures 0.2,0.5,0.8 \
  --output-dir field-test/results/0.1.0
```

---

## Corpus Structure Reference

```
field-test/corpus/
├── README.md
├── catalog.yaml
├── golden/                    # 10 regression-anchor trajectories
├── curated/
│   ├── failures/positive/     # 30 failure trajectories
│   ├── failures/negative/     # 10 negative/control cases
│   ├── successes/             # 20 success trajectories
│   ├── nearmiss/              # 14 near-miss scenarios
│   ├── noisy/                 # 5 noisy/misleading trajectories
│   └── corrections/           # 5 human-correction examples
└── raw/
    ├── opencode/              # 25 real OpenCode sessions
    ├── synthetic/             # 145 generated scenarios
    ├── ci/                    # 110 CI failure logs
    ├── sibling-repos/         # 10 Cursor/Claude harness runs
    ├── corrections/           # 5 manual correction transcripts
    └── cross-session/         # 5 cross-session repeats
```

---

## File Format

### Trajectory JSONL (one JSON object per line)

```json
{
  "trajectory_id": "G-001-git-push-non-ff",
  "timestamp": "2026-09-06T00:00:00Z",
  "task": "Push local feature branch commits to remote main",
  "domain": "git",
  "failure_class": "git/push/non-fast-forward",
  "quality_label": "clear",
  "severity": "high",
  "success": false,
  "failure_point": "! [rejected] non-fast-forward",
  "steps": [
    {
      "step_number": 1,
      "tool": "git",
      "input": "git add . && git commit -m 'update'",
      "output": "1 file changed",
      "error": null
    },
    {
      "step_number": 2,
      "tool": "git",
      "input": "git push origin main",
      "output": null,
      "error": "! [rejected] non-fast-forward"
    }
  ],
  "tags": ["git", "push"],
  "source": "opencode",
  "source_repo": "CauterRule",
  "redacted": false
}
```

---

## Troubleshooting

### "Missing Authentication header" (401)

Your `CAUTERULE_LLM_API_KEY` is not set or is invalid. For OMLX, set it to any dummy value:

```bash
export CAUTERULE_LLM_API_KEY=dummy
```

### No endpoints found (404)

The model is not available on your OpenRouter tier. Try a different model:

```bash
# Try these instead
--llm-model openai/gpt-4o-mini
--llm-model meta-llama/llama-3.1-8b-instruct
```

### "No balanced JSON object found"

The LLM returned non-JSON output. This is a model quality issue. Try:
- Using a stronger model
- Adding `--temperatures 0.2` (lower temperature)
- Checking the `llm_response` field in results for debugging

### Results file is empty after rerun

The runner now clears `results.jsonl` at the start of each run. If you rerun on the same day, the previous results are cleared. Use a different output directory or rename the old results.

### Slow extraction

- Reduce `--max-workers` if your LLM provider rate-limits you
- Use a smaller corpus type
- Use a local model instead of cloud
- Set `--temperatures 0.2` (single pass instead of multiple)