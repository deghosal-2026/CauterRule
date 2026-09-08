#!/usr/bin/env python3
"""Run full corpus sweep for a single model — all defined CORPUS_TYPES."""
import sys, os
sys.path.insert(0, 'scripts')
from run_field_test import CORPUS_TYPES

LLM_MODEL = sys.argv[1] if len(sys.argv) > 1 else "Llama-3.2-3B-Instruct-4bit"
LLM_LABEL = LLM_MODEL.replace("/", "_")

for corpus_type in sorted(CORPUS_TYPES):
    print(f"\n{'='*60}")
    print(f"RUNNING: {corpus_type}")
    print(f"{'='*60}")
    out = os.path.join("field-test/results/0.2.0", corpus_type.replace("/", "_"))
    # Skip if already completed (has summary.json)
    import glob
    existing = glob.glob(f"{out}/omlx-openai-{LLM_LABEL}/**/summary.json")
    if existing:
        print(f"  SKIP (already has results)")
        continue
    rc = os.system(
        f"CAUTERULE_LLM_API_KEY=omlx-test python3 scripts/run-field-test.py \"{corpus_type}\" "
        f"--llm-provider openai --llm-model \"{LLM_MODEL}\" "
        f"--llm-base-url http://localhost:8000/v1 "
        f"--output-dir field-test/results/0.2.0"
    )
    if rc != 0:
        print(f"  FAILED with code {rc}")