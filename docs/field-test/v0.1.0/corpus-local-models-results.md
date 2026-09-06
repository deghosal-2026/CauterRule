# Corpus Field Test Results — Local Models (v0.1.0)

**Date:** 2026-09-06
**Models tested:** Llama-3.2-3B-Instruct-4bit, Qwen3-4B-Instruct-2507-4bit
**Model attempted (too slow):** Qwen3.5-4B-4bit
**LLM Backend:** OMLX (local, Apple Silicon)
**Runner:** `scripts/run-field-test.py` with `--temperatures 0.2` (single pass)

---

## Methodology

Commands used:

```bash
CAUTERULE_LLM_API_KEY=omlx-test \
python3 scripts/run-field-test.py --all \
  --llm-provider openai \
  --llm-model Llama-3.2-3B-Instruct-4bit \
  --llm-base-url http://localhost:8000/v1 \
  --output-dir field-test/results/0.1.0 \
  --max-workers 2 \
  --temperatures 0.2

CAUTERULE_LLM_API_KEY=omlx-test \
python3 scripts/run-field-test.py --all \
  --llm-provider openai \
  --llm-model Qwen3-4B-Instruct-2507-4bit \
  --llm-base-url http://localhost:8000/v1 \
  --output-dir field-test/results/0.1.0 \
  --max-workers 2 \
  --temperatures 0.2

CAUTERULE_LLM_API_KEY=omlx-test \
python3 scripts/run-field-test.py --all \
  --llm-provider openai \
  --llm-model Qwen3.5-4B-4bit \
  --llm-base-url http://localhost:8000/v1 \
  --output-dir field-test/results/0.1.0 \
  --max-workers 2 \
  --temperatures 0.2
```

Execution notes:

- All runs used OMLX through the OpenAI-compatible endpoint.
- The API key was a dummy value because OMLX does not require a real key.
- The runner used one explicit temperature value: `0.2`.
- Results in this document are taken from on-disk `results.jsonl` and `summary.json` files.
- Counts in this document reflect raw operational files, not a cleaned export.

## Metric Definitions

- **Trajs**: number of rows currently present in `results.jsonl` for that corpus/model pair.
- **Candidates**: total parsed candidate count across rows with `status == "done"`.
- **Pass / Inconclusive / Fail**: counts of the `best.verdict` field for rows with parsed candidates.
- **Parse Error Rate**: effectively the `no_candidates` rate in the current runner output, computed as rows where extraction did not yield any candidate.
- **No candidate** does not mean the model had no idea; it means the runner did not obtain a valid parsed candidate from that attempt.

## Limitations

1. **Same-day rerun contamination**
   The runner currently appends to date-based result files. Repeating a run on the same day can duplicate rows.

2. **Single-temperature evaluation**
   These results only reflect `--temperatures 0.2`. They do not characterize broader temperature behavior.

3. **Aborted third model**
   Qwen3.5-4B-4bit was not completed, so any statements about it are operational observations, not benchmark conclusions.

4. **Replay is not human judgment**
   Replay verdicts come from the current simulator and evidence builder, not manual expert grading.

5. **Raw counts over canonical counts**
   This document reports current on-disk results, which is useful operationally but not yet ideal for publication-quality benchmarking.

## Models

| Model | Params | Ran | Reason Skipped |
|---|---|---|---|
| Llama-3.2-3B-Instruct-4bit | 3.2B | ✅ All 7 corpus types | — |
| Qwen3-4B-Instruct-2507-4bit | 4B | ✅ All 7 corpus types | — |
| Qwen3.5-4B-4bit | 4B | ❌ Started, aborted | ~3-4× slower than Qwen3-4B |

Results directories: `field-test/results/0.1.0/{corpus_type}/omlx-openai-{model}/2026-09-06/`

---

## Result Summary

**Important note:** the current runner writes into date-only directories and appends to `results.jsonl`. Because `golden` was rerun on the same day for Llama, that one file contains a duplicate row and shows 11 rows for a 10-trajectory corpus. Counts below reflect the current on-disk files as they exist today, not a deduped canonical dataset.

### Llama-3.2-3B-Instruct-4bit

| Corpus | Trajs | Candidates | Pass | Inconclusive | Fail | Parse Error Rate |
|---|---|---|---|---|---|---|
| golden | 11 | 3 | 1 | 2 | 0 | 72.7% |
| failures/positive | 30 | 12 | 4 | 7 | 1 | 60.0% |
| failures/negative | 10 | 4 | 0 | 1 | 3 | 60.0% |
| successes | 20 | 11 | 0 | 5 | 6 | 45.0% |
| nearmiss | 14 | 4 | 1 | 1 | 2 | 71.4% |
| noisy | 5 | 5 | 4 | 0 | 1 | 0% |
| corrections | 5 | 1 | 0 | 0 | 1 | 80.0% |

### Qwen3-4B-Instruct-2507-4bit

| Corpus | Trajs | Candidates | Pass | Inconclusive | Fail | Parse Error Rate |
|---|---|---|---|---|---|---|
| golden | 10 | 3 | 0 | 3 | 0 | 70% |
| failures/positive | 30 | 9 | 0 | 9 | 0 | 70.0% |
| failures/negative | 10 | 5 | 0 | 5 | 0 | 50% |
| successes | 20 | 7 | 0 | 7 | 0 | 65.0% |
| nearmiss | 14 | 7 | 0 | 7 | 0 | 50.0% |
| noisy | 5 | 2 | 0 | 2 | 0 | 60.0% |
| corrections | 5 | 1 | 0 | 1 | 0 | 80% |

---

## Observations

### 1. Extreme JSON parse failure rate

Both 3-4B models fail to produce valid JSON in ~60% of extraction attempts. The most common errors:

- **`when.context item must be a non-blank string`** — the model emits a JSON array with empty strings, e.g. `"context": [""]`. The `RuleWhen` validator rejects blank context entries.
- **`Extra data: line N column M`** — the model emits valid JSON followed by additional commentary or a second JSON object. The parser (`json.loads`) rejects trailing data.
- **`No JSON object found in LLM output`** — the model returns plain text with no JSON at all, e.g. a narrative sentence explaining what rule to write.
- **`Invalid \escape`** — the model emits unescaped control characters inside JSON strings.

These are primarily formatting failures, not pure semantic failures. The models often appear to identify the right kind of lesson, but they cannot reliably satisfy the extractor's strict JSON and validation requirements.

### 2. Parsed candidates are sometimes plausible, but replay quality is still weak

Spot-checking the `llm_response` fields shows many parsed candidates are directionally reasonable, but the replay results do not support the stronger claim that they are generally correct. A large share of parsed outputs are still `fail` or `inconclusive`, especially on `successes`, `corrections`, and `failures/negative`. The `context` field format is still one of the biggest false-negative sources, but parse success alone is not enough.

### 3. Replay scores are poor but expected

Most candidates score precision=0.00 or 0.50 because:
- Golden manifest rules are specific ("when git push fails with non-fast-forward")
- Extracted triggers are generic ("when a command fails") — correct but too broad to pass replay
- The simple substring-match simulator inflates false positives

### 4. Noisy corpus had the best local-model pass rate

Llama produced passing candidates on 4/5 noisy trajectories. This suggests the noisy set contains failures with especially explicit surface signals, making them easier for small local models to summarize into rules.

### 5. Corrections corpus had the worst local-model effectiveness

Only 1/5 correction trajectories produced a parsed candidate for each tested local model. The presence of both trajectory evidence and explicit human advice seems to push small models into commentary-style output instead of strict rule JSON.

### 6. Safety-oriented corpora remain weak

`successes`, `failures/negative`, and parts of `nearmiss` are where bad extraction behavior becomes most visible. These sets matter disproportionately because they tell us whether the system can avoid inventing harmful or noisy rules.

### 7. The current benchmark mixes several failure modes together

Each end-to-end run currently measures multiple things at once:

- whether the model can follow structured-output instructions
- whether the parser accepts the output
- whether the candidate is semantically reasonable
- whether replay agrees with that candidate

That is useful operationally, but it means a poor headline score does not isolate root cause by itself.

---

## Learnings

1. **Format constraints must match model capability.** The `RuleWhen.context` array with non-blank validation is too strict for 3-4B models. Consider relaxing to `context: list[str]` with optional entries, or adding a JSON schema validation step that provides a second-chance parse.

2. **Multi-temperature passes are not justified yet for small models.** At 0.2 temperature, both tested local models already fail mainly on formatting and validation. More passes at higher temperatures are likely to add cost and noise before they add value.

3. **The extraction prompt should include an explicit JSON schema example.** Current prompt shows the structure but small models benefit from a concrete filled-in example.

4. **Speed and reliability both matter.** Qwen3.5-4B was slow enough in early execution that we stopped the run. Even before quality comparison, that makes it a poor default for broad corpus sweeps.

5. **Date-only output folders need run-level reset or dedupe.** The current runner appends into the same day's `results.jsonl`, which contaminated at least one summary with duplicate rows after reruns.

6. **Safety corpora should remain first-class even if they lower aggregate scores.** `successes`, `failures/negative`, and `nearmiss` are exactly where an unsafe extractor should struggle if it overgeneralizes.

7. **The benchmark needs a cleaner split between format compliance and semantic quality.** Right now those are coupled tightly enough that local-model evaluation can look worse than the underlying reasoning quality really is.

---

## Key Takeaways

| Takeaway | Implication |
|---|---|
| Small local models (3-4B) are not yet reliable enough for end-to-end corpus extraction | They may be useful for cheap exploratory runs, but not for headline benchmark numbers |
| Parse and validation failures dominate | Improving output handling may unlock more value than changing replay logic first |
| Noisy trajectories are currently the most effective local-model test set | Keep them in the loop for fast regression checks |
| Corrections and safety-sensitive corpora are weak spots | These need better prompting or stronger models before claims are credible |
| Runner output handling affects trust in the metrics | Same-day reruns must not silently append into the same aggregate files |

---

## Per-Corpus Interpretation

### `golden`

Purpose: strongest regression anchor because each trajectory has a known expected rule.

Interpretation:

- Good for testing rule specificity.
- Bad performance here is especially meaningful.
- Current local-model results show that formatting reliability is preventing a fair read on semantic quality for many cases.

### `failures/positive`

Purpose: the main extraction workload where the system should learn useful rules.

Interpretation:

- This is the best corpus for measuring practical extraction throughput.
- Llama's pass count here was the strongest signal that some local extraction is possible.
- Qwen3-4B still underperformed because formatting failures remained dominant.

### `failures/negative`

Purpose: ensure the extractor does not confidently turn bad inputs into rules.

Interpretation:

- This is a safety corpus, not just a quality corpus.
- A parsed candidate here is often a warning sign unless it correctly ends up inconclusive or rejected.

### `successes`

Purpose: protect against regression-inducing or unnecessary rule extraction.

Interpretation:

- This may be the most important safety check in the set.
- Weak local-model performance here means over-triggering and overgeneralization remain real concerns.

### `nearmiss`

Purpose: check trigger precision in lookalike scenarios.

Interpretation:

- This corpus reveals whether the extractor preserves the exact failure signature.
- Better performance here would be a good sign that larger models are producing more specific triggers.

### `noisy`

Purpose: test whether the model can extract signal from cluttered trajectories.

Interpretation:

- Surprisingly, this was the easiest corpus for Llama.
- The likely reason is that these trajectories still contain strong explicit failure clues despite their clutter.

### `corrections`

Purpose: test the human-correction-to-rule workflow.

Interpretation:

- This is a synthesis task, not just an extraction task.
- It is a good discriminator for stronger models because it requires combining evidence and explicit guidance.

## Test Effectiveness

The corpus field tests were still useful, even with weak local-model performance.

What the tests did well:

- They exposed that extraction is bottlenecked more by output format compliance than by raw model availability.
- They identified which corpora stress small local models the most: `corrections`, `successes`, and `failures/negative`.
- They showed the runner needed better observability: surfacing raw LLM responses and parse errors was necessary to make failures diagnosable.
- They produced a realistic floor baseline for local OMLX models.

What the tests did not yet prove:

- They did not prove that the current extraction prompt is robust across realistic local models.
- They did not prove that parsed local-model candidates are strong enough for promotion-quality replay performance.
- They did not produce clean apples-to-apples metrics for rerun-contaminated folders without deduplication.

Overall, the tests were effective as a system-debugging tool, but only partially effective as a benchmark of final extraction quality.

## Local Model Effectiveness

Local 3-4B models were useful in a narrow sense and weak in the broader one.

Where they were useful:

- Cheap repeated runs on OMLX
- Quick validation that the runner, corpus layout, and result-writing flow work end to end
- Stress-testing the strictness of the extraction schema
- Finding prompt and parser weaknesses before spending cloud budget

Where they were not effective enough:

- Producing stable structured JSON across all corpora
- Generating high-confidence replay-passing candidates consistently
- Handling correction-heavy or subtle corpora
- Serving as the main model for publishable field-test numbers

Practical conclusion: local 3-4B models are good for infrastructure shakedown and low-cost experimentation, but not yet good enough as the primary extraction benchmark for CauterRule.

## Issue Breakdown

This run exposed three different classes of problems. Separating them matters, because the fix path is different for each one.

### LLM issues

These are failures caused mainly by the model output itself.

- The model frequently emitted malformed JSON.
  Examples: trailing commentary after the JSON object, invalid escape sequences, or no JSON object at all.
- The model often emitted structurally valid-looking output that still violated schema constraints.
  Most common case: `when.context` included blank strings.
- Small local models often produced triggers that were too broad to replay well.
  Example pattern: extracting `when a command fails` instead of preserving the concrete failure signature.
- The corrections corpus appeared especially hard for local models because they tended to answer conversationally instead of returning strict rule JSON.

Interpretation: these are primarily model capability and output-discipline problems. A stronger model should reduce them, though not eliminate every one.

### Corpus issues

These are problems in the dataset or test assets themselves.

- The corpora are not equally difficult. `noisy` appears easier for local models than `corrections`, `successes`, or `failures/negative`.
- Some trajectory names and generated curated filenames are messy or lossy, which makes manual inspection harder.
  Examples: truncated or awkward filenames such as `F-024-coding-ython_import_failure`.
- The current summary is based on operational run files rather than a deduped canonical evaluation export.
  That makes it easier for reruns to contaminate interpretation.
- The benchmark currently mixes several goals at once: parsing reliability, semantic extraction quality, and replay suitability.
  That is useful operationally, but it can blur root cause attribution.

Interpretation: the corpus is usable, but it would benefit from cleaner canonical naming, deduped evaluation snapshots, and clearer separation between format-validation tasks and semantic-quality tasks.

### Code issues

These are problems in the runner or extraction contract.

- The runner appends into date-only `results.jsonl` files, so reruns on the same day can duplicate rows and contaminate summaries.
- The extraction contract is strict in ways that amplify local-model failure rates.
  The clearest case is rejecting blank items in `when.context` rather than recovering or normalizing them.
- The earlier runner version swallowed extraction errors, which made diagnosis much harder.
  This was improved during the session, but it was a real contributor to confusion.
- The benchmark path still depends on strict parser success before replay can even begin.
  That means many potentially useful responses are thrown away before semantic evaluation.

Interpretation: code changes can materially improve observed success rates even without changing models, especially around parsing resilience, result isolation, and normalization of near-valid outputs.

## Will Cloud LLMs Really Be Useful?

Yes, probably, but mainly for reliability and output discipline rather than magic reasoning.

Why cloud LLMs are likely to help:

1. **Better structured output compliance.** Models like `openai/gpt-4o-mini` and stronger Claude-class models are much more likely to return valid single-object JSON with stable fields.
2. **Better trigger specificity.** The current failures show local models often generalize too broadly. Stronger cloud models are more likely to preserve the specific error signature from the trajectory.
3. **Better correction handling.** The corrections corpus requires combining observed failure evidence with explicit human instruction. That synthesis is exactly where stronger models tend to outperform small local ones.
4. **Less operator time spent diagnosing parser failures.** If the model output is valid more often, the benchmark becomes about rule quality instead of formatter cleanup.

What cloud LLMs will not solve automatically:

- A too-strict schema can still reject good answers.
- Weak replay heuristics can still mark plausible rules as `fail` or `inconclusive`.
- Same-day append behavior in results can still contaminate metrics.

Best interpretation: cloud LLMs are very likely to make these tests more useful, but they do not replace fixing the runner and extraction contract.

## Representative Failure Examples

Typical local-model failure patterns seen in `llm_response` and parser errors:

1. **Trailing commentary after JSON**
   The model returns a JSON object and then adds an explanation paragraph. Parser result: `Extra data`.

2. **Blank context entries**
   The model emits `"context": [""]`. Parser result: `when.context item must be a non-blank string`.

3. **Narrative answer with no JSON**
   The model explains the lesson in prose without returning an object. Parser result: `No JSON object found in LLM output`.

4. **Bad escaping inside strings**
   The model includes backslashes or quote patterns that are not valid JSON. Parser result: `Invalid \escape`.

5. **Over-broad trigger**
   The model returns something like `when a command fails`, which parses but performs poorly in replay because it is too general.

Representative good pattern:

- A single JSON object with a specific trigger tied to a concrete error signature and a directive that names the next action.

Representative bad-but-interesting pattern:

- A semantically reasonable rule wrapped in extra explanation text that makes the whole response fail parsing.

## Why Larger Models Will Fare Better

1. **Instruct-following for structured output usually improves above 7B parameters.** Models like Qwen3.5-8B, Llama-3.1-8B, and Qwen3.5-9B-class local models are more likely to produce valid JSON consistently.

2. **Context field handling.** Larger models are more likely to produce non-empty `context` arrays with meaningful entries, avoiding one of the most common validation failures in these runs.

3. **Multi-turn coherence.** Larger models maintain the JSON structure across longer trajectory descriptions (20+ steps), while 3B models often degenerate into narrative text mid-trajectory.

4. **Better trigger specificity.** Golden manifest rules reference specific error messages (e.g. "git push fails with non-fast-forward"). Small models produce "when a task fails". 8B+ models are more likely to extract the specific failure signal because they can better identify the salient error in the trajectory.

5. **Lower-temperature robustness.** Stronger models tend to preserve format discipline at low temperature better than small local models.

**Recommended next steps:**

1. Fix same-day rerun contamination by clearing or versioning `results.jsonl` per run.
2. Recompute the local-model summary from deduped per-trajectory results.
3. Run the same corpora on one stronger local model, ideally a 7B-9B class model.
4. Run a cloud baseline, preferably OpenRouter-hosted `openai/gpt-4o-mini`, to measure how much improvement comes from model quality versus parser strictness.
5. If cloud results are much better, keep local small models for smoke tests and use cloud or larger local models for benchmark reporting.

## Comparative Model Table

| Model | Speed | Parse reliability | Replay usefulness | Operational cost | Recommended use |
|---|---|---|---|---|---|
| Llama-3.2-3B-Instruct-4bit | Fastest of the completed local runs | Weak | Limited but non-zero | Very low | Smoke tests, runner validation, cheap experiments |
| Qwen3-4B-Instruct-2507-4bit | Moderate | Weak | Mostly inconclusive | Very low | Secondary local comparison, prompt/parser experiments |
| Qwen3.5-4B-4bit | Too slow for this batch run | Unknown from incomplete run | Unknown | Low, but time-expensive | Skip for broad sweeps unless speed improves |
| OpenRouter `openai/gpt-4o-mini` | Slower wall-clock than tiny local, but operationally predictable | Likely much stronger | Likely materially stronger | Low-to-moderate | Cloud baseline, benchmark reporting |
| Larger local 7B-9B class model | Slower and heavier than 3B/4B | Likely stronger | Likely stronger | Medium local resource cost | Main local benchmark candidate |

## Decision

Current recommendation by use case:

| Use case | Local 3B-4B models acceptable? | Recommendation |
|---|---|---|
| Smoke tests for runner wiring | Yes | Use Llama-3.2-3B |
| Prompt iteration and parser debugging | Yes | Use local models first to keep costs down |
| Corpus-level benchmark reporting | No | Use stronger local 7B-9B or cloud baseline |
| Promotion gating / publishable quality claims | No | Require stronger model and cleaner metrics |
| Safety-sensitive evaluation (`successes`, `negative`, `nearmiss`) | Not by themselves | Keep local runs, but validate with stronger model |

Bottom line: local 3B-4B models are useful as development infrastructure tools, but not sufficient as the primary evidence source for CauterRule field-test quality claims.

---

## Raw Results

Results are stored per corpus type and model:

```
field-test/results/0.1.0/
  {corpus_type}/
    omlx-openai-Llama-3.2-3B-Instruct-4bit/2026-09-06/
      meta.json       — run configuration
      results.jsonl   — per-trajectory results with llm_response
      summary.json    — aggregate metrics
    omlx-openai-Qwen3-4B-Instruct-2507-4bit/2026-09-06/
      ...
```

Each `results.jsonl` entry includes:
- `trajectory_id`, `status`, `candidate_count`
- `candidates[].when`, `do`, `confidence`, `llm_response` (raw LLM text)
- `best.precision`, `recall`, `verdict`
