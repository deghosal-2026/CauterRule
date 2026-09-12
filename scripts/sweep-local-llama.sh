#!/usr/bin/env bash
# Resume-able v0.3.0 field-test sweep on Llama-3.2-3B-Instruct-4bit.
# Runs corpora one-at-a-time; skips any that already have a summary.json.
# Safe to interrupt and re-run — resumes where it left off.
#
# Usage: bash scripts/sweep-local-llama.sh
# Logs (when launched via nohup) -> field-test/results/0.3.0/sweep-llama.log
set -u
MODEL="Llama-3.2-3B-Instruct-4bit"
BASE="http://localhost:8000/v1"
OUT="field-test/results/0.3.0"
WORKERS=4

# Full CORPUS_TYPES set from scripts/run-field-test.py (37), cost corpus last.
CORPORA=(
  golden failures/positive failures/negative successes nearmiss noisy corrections
  raw/opencode raw/synthetic raw/ci raw/sibling-repos raw/corrections raw/cross-session
  public/golden public/counterexample public/nearmiss public/staleness public/synthetic public/domains
  adversarial/injection adversarial/misleading adversarial/contradiction adversarial/unsafe adversarial/poisoning
  adversarial/tool_output_injection adversarial/compounding_multiturn
  adversarial/unsafe_realistic adversarial/misleading_harmbench adversarial/contradiction_harmbench
  adapters lifecycle packs mcp otel
  reference-expansion reference-expansion/paraphrase-diversity
  cost
)

n_done=0
n_run=0
LLM_LABEL="omlx-openai-$MODEL"
for ct in "${CORPORA[@]}"; do
  key="${ct//\//_}"
  run_dir=$(ls -d "$OUT/$key/$LLM_LABEL"/2026-* 2>/dev/null | head -1)
  # Skip only when a *complete* run exists. summary.json's `total` is just the
  # number of completed results, so completeness must be judged against
  # meta.json's target_trajectories. A killed corpus leaves a partial summary.
  if [ -n "$run_dir" ] && [ -f "$run_dir/summary.json" ] && [ -f "$run_dir/meta.json" ]; then
    complete=$(.venv/bin/python - "$run_dir" <<'PY' 2>/dev/null || echo no
import json,sys
from pathlib import Path
d=Path(sys.argv[1])
meta=json.loads((d/"meta.json").read_text())
summ=json.loads((d/"summary.json").read_text())
target=meta.get("target_trajectories") or 0
finished=(summ.get("done") or 0)+(summ.get("gate_dropped") or 0)
print("yes" if target and finished>=target else "no")
PY
)
    if [ "$complete" = "yes" ]; then
      echo "== skip  $ct (complete)"
      n_done=$((n_done+1))
      continue
    fi
    echo "== rerun $ct (partial)"
  fi
  n_run=$((n_run+1))
  echo "===== RUN $ct ====="
  CAUTERULE_LLM_API_KEY=dummy \
    .venv/bin/python scripts/run-field-test.py "$ct" \
      --llm-provider openai --llm-model "$MODEL" \
      --llm-base-url "$BASE" --skip-preflight --max-workers "$WORKERS" \
      --output-dir "$OUT" 2>&1 | tail -1
done
echo "DONE. skipped=$n_done ran=$n_run"
