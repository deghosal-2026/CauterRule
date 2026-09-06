# Corpus Field Test Results — Cloud LLMs (v0.1.0)

**Date:** 2026-09-06
**Models tested:** `openai/gpt-4o-mini`, `meta-llama/llama-3.1-8b-instruct`
**Model attempted but removed:** `google/gemini-2.0-flash-001`
**LLM Backend:** OpenRouter via OpenAI-compatible endpoint
**Runner:** `scripts/run-field-test.py` with `--temperatures 0.2` (single pass)

**Status after fixes:** these cloud runs happened after the parser, prompt, matcher, result-reset, and timestamp fixes that were validated in the local-model reruns.

---

## Methodology

Commands used:

```bash
CAUTERULE_LLM_API_KEY=$OMLX_KEY \
python3 scripts/run-field-test.py --all \
  --llm-provider openai \
  --llm-model openai/gpt-4o-mini \
  --llm-base-url https://openrouter.ai/api/v1 \
  --output-dir field-test/results/0.1.0 \
  --max-workers 4 \
  --temperatures 0.2

CAUTERULE_LLM_API_KEY=$OMLX_KEY \
python3 scripts/run-field-test.py --all \
  --llm-provider openai \
  --llm-model meta-llama/llama-3.1-8b-instruct \
  --llm-base-url https://openrouter.ai/api/v1 \
  --output-dir field-test/results/0.1.0 \
  --max-workers 4 \
  --temperatures 0.2
```

Execution notes:

- Both working cloud runs used the same corpus and runner configuration as the local-model reruns.
- These runs happened after the parser, prompt, matcher, result-reset, and timestamp fixes.
- Counts below reflect current on-disk files under `field-test/results/0.1.0/`.

## Metric Definitions

- **Trajs**: number of rows currently present in `results.jsonl` for that corpus/model pair.
- **Candidates**: total parsed candidate count across rows with `status == "done"`.
- **Pass / Inconclusive / Fail**: counts of the `best.verdict` field for rows with parsed candidates.
- **Parse Error Rate**: `no_candidates / total rows` in the current run output.

## Models

| Model | Source | Ran | Notes |
|---|---|---|---|
| `openai/gpt-4o-mini` | OpenRouter | ✅ | Cheapest successful cloud baseline |
| `meta-llama/llama-3.1-8b-instruct` | OpenRouter | ✅ | Cheap stronger open-weight cloud baseline |
| `google/gemini-2.0-flash-001` | OpenRouter | ❌ | Removed after 404 “No endpoints found” |

Results directories:

- `field-test/results/0.1.0/{corpus_type}/openai-openai_gpt-4o-mini/2026-09-06/`
- `field-test/results/0.1.0/{corpus_type}/openai-meta-llama_llama-3.1-8b-instruct/2026-09-06/`

---

## Before And After Fixes

This cloud report should be read as a follow-on to the local-model reruns. The earlier local document identified real parser, prompt, result-isolation, and timestamp problems. Those issues were fixed before the cloud runs below.

### What changed before the cloud run

| Area | Before | After |
|---|---|---|
| Result-file isolation | Same-day reruns could append duplicate rows | Results reset cleanly at run start |
| JSON extraction | Trailing commentary and multi-object outputs frequently broke parsing | First balanced JSON object extraction recovers valid primary output |
| `when.context` validation | Blank context entries caused hard parse failure | Blank context entries are filtered before validation |
| Prompt clarity | Minimal JSON example | Concrete filled example plus explicit JSON-only instruction |
| Raw corpus completeness | Some synthetic/harness assets were blocked by missing timestamps | Timestamp issue repaired before full cloud sweep |

### What the cloud runs therefore measure better

- semantic rule quality
- replay behavior
- safety on `successes`, `failures/negative`, and `nearmiss`
- comparative model quality rather than parser survival

## Curated Corpus Summary

### `openai/gpt-4o-mini`

| Corpus | Trajs | Candidates | Pass | Inconclusive | Fail | Parse Error Rate |
|---|---:|---:|---:|---:|---:|---:|
| golden | 10 | 10 | 6 | 4 | 0 | 0.0% |
| failures/positive | 30 | 30 | 14 | 13 | 3 | 0.0% |
| failures/negative | 10 | 10 | 0 | 4 | 6 | 0.0% |
| successes | 20 | 20 | 0 | 6 | 14 | 0.0% |
| nearmiss | 14 | 14 | 2 | 4 | 8 | 0.0% |
| noisy | 5 | 5 | 1 | 3 | 1 | 0.0% |
| corrections | 5 | 5 | 3 | 2 | 0 | 0.0% |

### `meta-llama/llama-3.1-8b-instruct`

| Corpus | Trajs | Candidates | Pass | Inconclusive | Fail | Parse Error Rate |
|---|---:|---:|---:|---:|---:|---:|
| golden | 10 | 10 | 7 | 0 | 3 | 0.0% |
| failures/positive | 30 | 30 | 22 | 5 | 3 | 0.0% |
| failures/negative | 10 | 10 | 3 | 1 | 6 | 0.0% |
| successes | 20 | 20 | 3 | 6 | 11 | 0.0% |
| nearmiss | 14 | 14 | 6 | 1 | 7 | 0.0% |
| noisy | 5 | 5 | 5 | 0 | 0 | 0.0% |
| corrections | 5 | 5 | 3 | 1 | 1 | 0.0% |

## Raw Corpus Summary

### `openai/gpt-4o-mini`

| Corpus | Trajs | Candidates | Pass | Inconclusive | Fail | Parse Error Rate |
|---|---:|---:|---:|---:|---:|---:|
| raw/opencode | 25 | 25 | 12 | 10 | 3 | 0.0% |
| raw/synthetic | 145 | 145 | 28 | 91 | 26 | 0.0% |
| raw/ci | 110 | 110 | 7 | 99 | 4 | 0.0% |
| raw/sibling-repos | 10 | 10 | 0 | 7 | 3 | 0.0% |
| raw/corrections | 5 | 5 | 2 | 3 | 0 | 0.0% |
| raw/cross-session | 5 | 5 | 2 | 2 | 1 | 0.0% |

### `meta-llama/llama-3.1-8b-instruct`

| Corpus | Trajs | Candidates | Pass | Inconclusive | Fail | Parse Error Rate |
|---|---:|---:|---:|---:|---:|---:|
| raw/opencode | 25 | 25 | 18 | 3 | 4 | 0.0% |
| raw/synthetic | 145 | 144 | 38 | 81 | 25 | 0.7% |
| raw/ci | 110 | 110 | 11 | 60 | 39 | 0.0% |
| raw/sibling-repos | 10 | 10 | 0 | 10 | 0 | 0.0% |
| raw/corrections | 5 | 4 | 3 | 0 | 1 | 20.0% |
| raw/cross-session | 5 | 5 | 4 | 0 | 1 | 0.0% |

---

## Observations

### 1. Cloud models removed parsing as a first-order problem

`gpt-4o-mini` achieved a 0.0% parse-error rate across all 394 trajectories.

`llama-3.1-8b-instruct` was nearly as good, with only 2 parse misses across the entire cloud sweep:

- `raw/synthetic`: 1 miss
- `raw/corrections`: 1 miss

Compared with the earlier local 3B-4B runs, cloud inference made the benchmark primarily about rule quality rather than format survival.

### 2. Cloud models were stronger than the local 3B-4B baselines on `golden` and `failures/positive`

The most important quality signal is that both cloud models produced stronger curated results, especially on:

- `golden`
- `failures/positive`

The strongest of the two cloud models here was `meta-llama/llama-3.1-8b-instruct`, which outperformed `gpt-4o-mini` on both pass count and breadth of useful candidate generation.

### 3. Safety corpora are still hard, even for cloud models

Neither cloud model “solved” the benchmark on:

- `successes`
- `failures/negative`
- `nearmiss`

This is important because it means the remaining problem is not just local-model weakness. It also reflects the current replay matcher and the difficulty of avoiding overgeneralized rules.

### 4. `meta-llama/llama-3.1-8b-instruct` looks like the best value cloud model in this batch

It was still cheap, but materially stronger than `gpt-4o-mini` on:

- `golden`
- `failures/positive`
- `noisy`
- `raw/opencode`
- `raw/synthetic`
- `raw/cross-session`

### 5. `gpt-4o-mini` still has value as a cheap, stable baseline

It was perfectly stable from a formatting perspective and finished quickly. Even when quality was weaker than `llama-3.1-8b-instruct`, it remains useful for:

- cheap recurring comparisons
- cloud sanity checks
- verifying that parser regressions have not returned

### 6. The failed Gemini run was a provider-availability issue, not a model-quality result

`google/gemini-2.0-flash-001` was removed because OpenRouter returned `404 No endpoints found`. That is not evidence about extraction quality; it is purely an availability/tier issue.

---

## Learnings

1. **Running cloud models was worth it.** After the parser and timestamp fixes, the cloud runs gave a clean comparison instead of just masking tooling problems.

2. **Local 3B-4B and cloud models are solving different problems.** Local models are now good enough for internal regression tracking, but cloud models provide a stronger quality ceiling.

3. **Replay quality remains the next real bottleneck.** Cloud models proved that better structured output does not automatically translate to good safety behavior or high replay pass rates.

4. **A stronger open-weight cloud model may be the best cost/performance point.** In this run, `meta-llama/llama-3.1-8b-instruct` looks more compelling than `gpt-4o-mini` for extraction quality.

5. **Provider availability must be checked before long runs.** `google/gemini-2.0-flash-001` was not available on this OpenRouter tier and should not be included in future comparisons unless availability is confirmed first.

---

## Key Takeaways

| Takeaway | Implication |
|---|---|
| Cloud models are useful even after local fixes | They provide cleaner and stronger quality comparisons, not just better formatting |
| `gpt-4o-mini` is a stable cheap baseline | Good default cloud comparator |
| `meta-llama/llama-3.1-8b-instruct` was the strongest cheap cloud model tested | Best current cost/performance candidate |
| Safety corpora still fail often | Replay and rule-specificity work remains necessary |
| Availability matters | OpenRouter model IDs should be smoke-tested before launching a full sweep |

---

## Per-Corpus Interpretation

### `golden`

Purpose: strongest regression anchor because each trajectory has a known expected rule.

Interpretation:

- Both cloud models were fully parse-stable here.
- `meta-llama/llama-3.1-8b-instruct` was stronger on pass count than `gpt-4o-mini`.
- This is a stronger sign of real extraction quality than the earlier local-only picture.

### `failures/positive`

Purpose: the main extraction workload where the system should learn useful rules.

Interpretation:

- Both cloud models are clearly usable here.
- `meta-llama/llama-3.1-8b-instruct` produced the best pass rate in this cloud batch.
- This corpus is currently the clearest quality discriminator between cheap cloud models.

### `failures/negative`

Purpose: ensure the extractor does not confidently turn bad inputs into rules.

Interpretation:

- This remains a weak area for both cloud models.
- Better parsing did not automatically produce good safety behavior.

### `successes`

Purpose: protect against regression-inducing or unnecessary rule extraction.

Interpretation:

- This remains one of the most important safety checks.
- Both cloud models still fail often here, meaning replay and rule specificity need more work.

### `nearmiss`

Purpose: check trigger precision in lookalike scenarios.

Interpretation:

- `meta-llama/llama-3.1-8b-instruct` was noticeably stronger than `gpt-4o-mini`.
- Even so, neither model is yet strong enough here to claim precision is solved.

### `noisy`

Purpose: test whether the model can extract signal from cluttered trajectories.

Interpretation:

- This was the strongest curated corpus for `meta-llama/llama-3.1-8b-instruct`.
- Cloud models appear comfortable with noisy surface detail once formatting is no longer an issue.

### `corrections`

Purpose: test the human-correction-to-rule workflow.

Interpretation:

- Both cloud models handled this better than the earlier local snapshots.
- `gpt-4o-mini` was slightly cleaner here; `llama-3.1-8b-instruct` was still strong but had one failure in curated and one parse miss in raw corrections.

### Raw corpora

Purpose: test breadth, generalization, and real-world-ish coverage beyond curated benchmark subsets.

Interpretation:

- `raw/opencode` and `raw/synthetic` best show model breadth.
- `raw/ci` shows a lot of inconclusive behavior, suggesting replay quality is now more limiting than extraction availability.
- `raw/sibling-repos` remains mostly inconclusive for both cloud models, meaning harness-transfer quality is still not strong.

## Test Effectiveness

The cloud runs were effective in a different way than the local runs.

What the cloud runs did well:

- They removed parsing as a confounder.
- They gave a cleaner estimate of model-quality ceiling above local 3B-4B baselines.
- They showed that better models improve `golden`, `failures/positive`, and broad raw coverage.
- They confirmed that safety corpora and replay heuristics remain the harder problem.

What the cloud runs did not yet prove:

- They did not prove that the current replay system is strong enough for promotion-quality claims.
- They did not prove that cloud models alone solve overgeneralization.
- They did not prove that the current benchmark is fully calibrated for safety evaluation.

Overall, the cloud runs were effective as quality-ceiling measurements and as a check that local-model limitations were real but not the only limitation.

## Cloud Model Effectiveness

Cloud models were effective in a broader sense than the local 3B-4B baselines.

Where they were effective:

- stable structured output
- complete candidate generation across the full corpus
- stronger curated benchmark performance
- clearer comparison across corpus families

Where they were still not sufficient by themselves:

- avoiding overgeneralization on safety corpora
- guaranteeing strong replay outcomes on `successes`, `negative`, and `nearmiss`
- replacing the need for replay-calibration work

Practical conclusion: cloud models are already useful as quality benchmark tools, not just parser-stability tools, but they do not eliminate the need to improve matching, replay, and safety evaluation.

## Issue Breakdown

### LLM issues

- `gpt-4o-mini` and `meta-llama/llama-3.1-8b-instruct` still produce rules that can be too broad for safety-sensitive corpora.
- `meta-llama/llama-3.1-8b-instruct` had a tiny number of remaining parse issues on raw corpora.
- Model quality differences now show up more in replay results than in output formatting.

### Corpus issues

- Raw corpora, especially `raw/ci`, produce many inconclusive outcomes because the current replay setup is a weak fit for that breadth.
- `raw/sibling-repos` remains low-signal for both cloud models, which may reflect corpus design as much as model weakness.

### Code issues

- The main parser and result-isolation issues are fixed.
- The next code bottleneck is replay quality and matcher calibration, not extraction availability.
- A provider availability preflight is still missing and should be added to avoid wasted runs like the failed Gemini attempt.

## Will Cloud LLMs Really Be Useful?

Yes. These runs make that clearer than the earlier local-only picture.

What cloud LLMs clearly improved:

- parse reliability
- consistency of candidate generation
- pass counts on `golden` and `failures/positive`
- overall usefulness of the benchmark as a quality signal

What cloud LLMs did **not** solve by themselves:

- overgeneralization on safety-sensitive corpora
- replay false positives / weak matching behavior
- the need for stronger promotion-quality evaluation criteria

Best interpretation: cloud LLMs are not required for basic pipeline functionality anymore, but they are still useful for quality benchmarking and for estimating the ceiling above the local 3B-4B baseline.

## Comparative Model Table

| Model | Speed | Parse reliability | Replay usefulness | Operational cost | Recommended use |
|---|---|---|---|---|---|
| `openai/gpt-4o-mini` | Fast | Excellent | Moderate | Low | Cheapest stable cloud baseline |
| `meta-llama/llama-3.1-8b-instruct` | Moderate | Excellent | Strongest of tested cloud models | Low | Best current cloud cost/performance pick |
| `google/gemini-2.0-flash-001` | N/A | N/A | N/A | N/A | Not usable on this OpenRouter tier |

## New Recommendations

1. Keep `gpt-4o-mini` as the default cheap cloud baseline.
2. Add `meta-llama/llama-3.1-8b-instruct` as the preferred stronger cloud comparator.
3. Update benchmark reporting to compare at least:
   - best local small model
   - cheap cloud baseline
   - stronger cloud/open-weight model
4. Focus the next round of engineering work on replay quality and safety corpora, not parsing.
5. Add a lightweight OpenRouter availability check before future long-running benchmark jobs.

## Raw Results

Results are stored per corpus type and model:

```
field-test/results/0.1.0/
  {corpus_type}/
    openai-openai_gpt-4o-mini/2026-09-06/
      meta.json
      results.jsonl
      summary.json
    openai-meta-llama_llama-3.1-8b-instruct/2026-09-06/
      meta.json
      results.jsonl
      summary.json
```
