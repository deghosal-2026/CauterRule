# CauterRule Field Tests

## Corpus types

| Type | Path | Trajectories | What it tests |
|---|---|---|---|
| `golden` | `corpus/golden/` | 10 | Regression anchor — expected rules known |
| `failures/positive` | `corpus/curated/failures/positive/` | 30 | Real failure trajectories that should produce rules |
| `failures/negative` | `corpus/curated/failures/negative/` | 10 | Failure traces that should NOT produce rules |
| `successes` | `corpus/curated/successes/` | 20 | Success trajectories — rules must not break them |
| `nearmiss` | `corpus/curated/nearmiss/` | 14 | Looks like a failure but should not trigger |
| `noisy` | `corpus/curated/noisy/` | 5 | Misleading/ambiguous traces — robustness test |
| `corrections` | `corpus/curated/corrections/` | 5 | Human-correction-to-rule flow |

All 84 curated trajectories in `corpus/curated/` are used as the reference set for replay-testing every candidate.

## Test scenarios

Each scenario below is a complete command line. Choose the one that matches your setup.

### Local OMLX (Apple Silicon, free, no API key)

**Prerequisite:** OMLX running at `http://localhost:8000/v1` with a Llama/MLX model loaded.  
**API key:** OMLX doesn't need one, but the OpenAI-compatible client expects a key. Set it to any dummy value.

```bash
# Golden regression (10 trajectories)
CAUTERULE_LLM_API_KEY=dummy \
python scripts/run-field-test.py golden \
  --llm-provider openai --llm-model llama-3.2-3b-instruct \
  --llm-base-url http://localhost:8000/v1 \
  --output-dir field-test/results/0.1.0

# Curated failures — the headline metric (30 trajectories)
CAUTERULE_LLM_API_KEY=dummy \
python scripts/run-field-test.py failures/positive \
  --llm-provider openai --llm-model llama-3.2-3b-instruct \
  --llm-base-url http://localhost:8000/v1 \
  --output-dir field-test/results/0.1.0

# Full sweep — all 7 corpus types
CAUTERULE_LLM_API_KEY=dummy \
python scripts/run-field-test.py --all \
  --llm-provider openai --llm-model llama-3.2-3b-instruct \
  --llm-base-url http://localhost:8000/v1 \
  --output-dir field-test/results/0.1.0
```

Output: `field-test/results/0.1.0/{corpus_type}/omlx-openai-llama-3.2-3b-instruct/{date}/`

### Cloud LLM (OpenRouter)

**Requires:** `CAUTERULE_LLM_API_KEY` (your OpenRouter API key).

Uses the OpenAI-compatible endpoint at `https://openrouter.ai/api/v1`. Any OpenRouter model works — just set `--llm-model` to the model slug.

```bash
# Golden regression with GPT-4o-mini via OpenRouter
CAUTERULE_LLM_API_KEY=sk-or-... \
python scripts/run-field-test.py golden \
  --llm-provider openai --llm-model openai/gpt-4o-mini \
  --llm-base-url https://openrouter.ai/api/v1 \
  --output-dir field-test/results/0.1.0

# Curated failures with Claude 3.5 Sonnet via OpenRouter
CAUTERULE_LLM_API_KEY=sk-or-... \
python scripts/run-field-test.py failures/positive \
  --llm-provider openai --llm-model anthropic/claude-3.5-sonnet \
  --llm-base-url https://openrouter.ai/api/v1 \
  --output-dir field-test/results/0.1.0

# All corpus types with GPT-4o-mini
CAUTERULE_LLM_API_KEY=sk-or-... \
python scripts/run-field-test.py --all \
  --llm-provider openai --llm-model openai/gpt-4o-mini \
  --llm-base-url https://openrouter.ai/api/v1 \
  --output-dir field-test/results/0.1.0
```

Output: `field-test/results/0.1.0/{corpus_type}/openai-openai_gpt-4o-mini/{date}/`

### Local Ollama

```bash
python scripts/run-field-test.py golden \
  --llm-provider ollama --llm-model llama3 \
  --output-dir field-test/results/0.1.0
```

## Per-corpus-type commands

```bash
# Failure extraction quality (via OpenRouter)
CAUTERULE_LLM_API_KEY=sk-or-... \
python scripts/run-field-test.py failures/positive \
  --llm-provider openai --llm-model openai/gpt-4o-mini \
  --llm-base-url https://openrouter.ai/api/v1

CAUTERULE_LLM_API_KEY=sk-or-... \
python scripts/run-field-test.py failures/negative \
  --llm-provider openai --llm-model openai/gpt-4o-mini \
  --llm-base-url https://openrouter.ai/api/v1

# Safety: rules must not break successes
CAUTERULE_LLM_API_KEY=sk-or-... \
python scripts/run-field-test.py successes \
  --llm-provider openai --llm-model openai/gpt-4o-mini \
  --llm-base-url https://openrouter.ai/api/v1

# Precision: near-miss rejection
CAUTERULE_LLM_API_KEY=sk-or-... \
python scripts/run-field-test.py nearmiss \
  --llm-provider openai --llm-model openai/gpt-4o-mini \
  --llm-base-url https://openrouter.ai/api/v1

# Robustness: noisy/misleading traces
CAUTERULE_LLM_API_KEY=sk-or-... \
python scripts/run-field-test.py noisy \
  --llm-provider openai --llm-model openai/gpt-4o-mini \
  --llm-base-url https://openrouter.ai/api/v1

# Human-correction flow
CAUTERULE_LLM_API_KEY=sk-or-... \
python scripts/run-field-test.py corrections \
  --llm-provider openai --llm-model openai/gpt-4o-mini \
  --llm-base-url https://openrouter.ai/api/v1
```

## Model bake-off (compare models on same corpus via OpenRouter)

```bash
# Run golden set on 3 different models through OpenRouter
python scripts/run-field-test.py golden \
  --llm-provider openai --llm-model openai/gpt-4o \
  --llm-base-url https://openrouter.ai/api/v1 \
  --output-dir field-test/results/0.1.0

python scripts/run-field-test.py golden \
  --llm-provider openai --llm-model openai/gpt-4o-mini \
  --llm-base-url https://openrouter.ai/api/v1 \
  --output-dir field-test/results/0.1.0

python scripts/run-field-test.py golden \
  --llm-provider openai --llm-model anthropic/claude-3.5-sonnet \
  --llm-base-url https://openrouter.ai/api/v1 \
  --output-dir field-test/results/0.1.0

# Results land side-by-side:
#   field-test/results/0.1.0/golden/openai-openai_gpt-4o/<date>/
#   field-test/results/0.1.0/golden/openai-openai_gpt-4o-mini/<date>/
#   field-test/results/0.1.0/golden/openai-anthropic_claude-3.5-sonnet/<date>/
```

## Parallelism

```bash
# Process 8 trajectories concurrently
python scripts/run-field-test.py failures/positive \
  --llm-provider openai --llm-model gpt-4o-mini \
  --max-workers 8 \
  --output-dir field-test/results/0.1.0
```

## Output structure

```
field-test/results/0.1.0/
  golden/
    omlx-openai-Llama-3.2-3B-Instruct-4bit/
      2026-09-06/
        meta.json         # run config (LLM, corpus, timestamps)
        results.jsonl     # one result per trajectory (appended live)
        summary.json      # aggregate metrics (rewritten live)
    openai-openai_gpt-4o-mini/
      2026-09-06/
        ...
    openai-anthropic_claude-3.5-sonnet/
      2026-09-06/
        ...
  failures_positive/
    openai-openai_gpt-4o-mini/
      2026-09-06/
        ...
  successes/
    openai-openai_gpt-4o-mini/
      2026-09-06/
        ...
```

## Watching progress mid-run

```bash
# Tail the incremental summary
tail -f field-test/results/0.1.0/golden/omlx-openai-Llama-3.2-3B-Instruct-4bit/2026-09-06/summary.json

# Watch results as they arrive
tail -f field-test/results/0.1.0/golden/omlx-openai-Llama-3.2-3B-Instruct-4bit/2026-09-06/results.jsonl
```

## Options

| Flag | Default | Description |
|---|---|---|
| `corpus_type` | — | `golden`, `failures/positive`, `failures/negative`, `successes`, `nearmiss`, `noisy`, `corrections` |
| `--all` | off | Run all 7 corpus types sequentially |
| `--llm-provider` | `openai` | `openai`, `anthropic`, `ollama`, `litellm` |
| `--llm-model` | `gpt-4o-mini` | Model name |
| `--llm-base-url` | `""` | Base URL for custom endpoints (OMLX: `http://localhost:8000/v1`) |
| `--output-dir` | `field-test/results/0.1.0` | Output directory root |
| `--max-workers` | `4` | Parallel trajectories per corpus type |
| `--temperatures` | `0.2,0.5` | Comma-separated multi-pass temperatures |
| `CAUTERULE_LLM_API_KEY` | env var | API key. Required for OpenRouter/OpenAI/Anthropic. Not needed for OMLX or Ollama — set to any dummy value for OMLX (e.g. `CAUTERULE_LLM_API_KEY=dummy`). |