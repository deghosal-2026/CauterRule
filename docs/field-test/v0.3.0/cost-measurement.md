# Cost Measurement — CauterRule v0.3.0

**Issue:** #653/#486 · **Plan:** §5.4/§7.4 · **Runner:** `scripts/measure_cost.py`
**Status:** 🟡 Tooling complete; measured table pending the v0.3.0 model re-run.

---

## 1. Method

The fixed 1,000-trajectory cost corpus (`field-test/corpus/cost/cost.jsonl`) runs
once per model. `scripts/measure_cost.py` reads every
`field-test/results/0.3.0/<corpus>/<model>/<date>/results.jsonl` and computes:

| Metric | Formula |
|--------|---------|
| `total_cost` | token-based (`prompt_tokens/1k · in_price + completion_tokens/1k · out_price`) when prices given, else `llm_requests · cost_per_request_usd` |
| `cost_per_candidate` | `total_cost / candidates_produced` |
| `cost_per_promoted_rule` | `total_cost / rules_promoted` |
| `cost_per_1k_trajectories` | `total_cost / trajectories · 1000` |
| `gate_savings` | `gate_dropped · cost_per_request` |

`llm_requests` is taken from each result record (`llm_requests`) or defaults to
the sweep's `--extraction-passes`; gate-dropped trajectories cost zero.

## 2. Run

```bash
python scripts/run-field-test.py --cost-corpus --output-dir field-test/results/0.3.0
# or directly:
python scripts/measure_cost.py --results field-test/results/0.3.0 \
  --input-price 0.00015 --output-price 0.0006 --cost-per-request 0.01
```

## 3. Measured table (pending)

| Model | Trajs | LLM reqs | Candidates | Promoted | Total $ | $/candidate | $/promoted | $/1k trajs | Gate savings |
|-------|-------|----------|------------|----------|---------|-------------|------------|------------|--------------|
| _pending re-run_ | | | | | | | | | |

## 4. Tiering cross-check (§6.2)

The measured `$/1k trajs` must match `cauterule preflight --cost-table`:

| Model tier | Expected $/1k | Expected p95 extract |
|-----------|---------------|----------------------|
| local (Llama-3.2-3B, Qwen3-4B) | ~$0 | ~1.0-1.1s |
| cheap cloud (gpt-4o-mini) | ~$1.60 | ~1.2s |
| flagship (gpt-4o) | ~$20 | ~2.5s |

**Status:** table populated by the re-run; `measure_cost.py` is wired into
`run-field-test.py --cost-corpus`.
