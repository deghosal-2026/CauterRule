#!/usr/bin/env bash
# Resume-able v0.3.0 field-test sweep on Llama-3.2-3B-Instruct-4bit.
# Runs corpora one-at-a-time; skips any that already have today's summary.json.
# Safe to interrupt and re-run — resumes where it left off.
set -u
MODEL="Llama-3.2-3B-Instruct-4bit"
BASE="http://localhost:8000/v1"
OUT="field-test/results/0.3.0"

CORPORA=(
  golden failures/positive failures/negative successes nearmiss noisy corrections
  raw/opencode raw/synthetic raw/ci raw/sibling-repos raw/corrections raw/cross-session
  public/golden public/counterexample public/nearmiss public/staleness public/synthetic public/domains
  adversarial/injection adversarial/misleading adversarial/contradiction adversarial/unsafe adversarial/poisoning
  adapters lifecycle packs mcp otel reference-expansion
)

n_done=0
n_run=0
for ct in "${CORPORA[@]}"; do
  key="${ct//\//_}"
  # Skip if ANY summary.json exists for this corpus (any date — runner uses
  # UTC date which can differ from host date by TZ).
  if [ -n "$(ls "$OUT/$key/$MODEL"/2026-*/summary.json 2>/dev/null | head -1)" ]; then
    echo "== skip  $ct (already done)"
    n_done=$((n_done+1))
    continue
  fi
  n_run=$((n_run+1))
  echo "===== RUN $ct ====="
  CAUTERULE_LLM_API_KEY=dummy \
    .venv/bin/python scripts/run-field-test.py "$ct" \
      --llm-provider openai --llm-model "$MODEL" \
      --llm-base-url "$BASE" --skip-preflight --max-workers 3 \
      --output-dir "$OUT" 2>&1 | tail -1
done
echo "DONE. skipped=$n_done ran=$n_run"