# Corpus Field Test Results — Local Models (v0.1.0)

**Date:** 2026-09-06
**Models tested:** Llama-3.2-3B-Instruct-4bit, Qwen3-4B-Instruct-2507-4bit
**Model attempted (too slow):** Qwen3.5-4B-4bit
**LLM Backend:** OMLX (local, Apple Silicon)
**Runner:** `scripts/run-field-test.py` with `--temperatures 0.2` (single pass)

**Status after fixes:** parser, prompt, matcher, and same-day result-reset fixes were applied and the corpus was rerun.

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
- Counts in this document reflect current on-disk run files after the rerun with parser and runner fixes.

## Metric Definitions

- **Trajs**: number of rows currently present in `results.jsonl` for that corpus/model pair.
- **Candidates**: total parsed candidate count across rows with `status == "done"`.
- **Pass / Inconclusive / Fail**: counts of the `best.verdict` field for rows with parsed candidates.
- **Parse Error Rate**: effectively the `no_candidates` rate in the current runner output, computed as rows where extraction did not yield any candidate.
- **No candidate** does not mean the model had no idea; it means the runner did not obtain a valid parsed candidate from that attempt.

## Limitations

1. **Completed rerun supersedes the earlier contaminated snapshot**
   The runner now clears `results.jsonl` and `summary.json` at run start, so same-day reruns no longer append stale rows into the same file.

2. **Single-temperature evaluation**
   These results only reflect `--temperatures 0.2`. They do not characterize broader temperature behavior.

3. **Aborted third model**
   Qwen3.5-4B-4bit was not completed, so any statements about it are operational observations, not benchmark conclusions.

4. **Replay is not human judgment**
   Replay verdicts come from the current simulator and evidence builder, not manual expert grading.

5. **Raw counts over canonical counts**
   This document still reports current on-disk results, which is useful operationally but not yet ideal for publication-quality benchmarking.

6. **Historical raw timestamp issue is now fixed**
   The earlier missing-timestamp problem in `raw/synthetic` harness trajectories and `raw/sibling-repos` was repaired, and those corpora have now been rerun successfully.

## Models

| Model | Params | Ran | Reason Skipped |
|---|---|---|---|
| Llama-3.2-3B-Instruct-4bit | 3.2B | ✅ All curated corpora + most raw corpora | — |
| Qwen3-4B-Instruct-2507-4bit | 4B | ✅ All curated corpora + most raw corpora | — |
| Qwen3.5-4B-4bit | 4B | ❌ Started, aborted | ~3-4× slower than Qwen3-4B |

Results directories: `field-test/results/0.1.0/{corpus_type}/omlx-openai-{model}/2026-09-06/`

---

## Result Summary

**Update:** the earlier same-day append contamination issue was fixed. The tables below reflect the rerun after fixes, not the earlier contaminated snapshot.

## Before And After Fixes

The earlier observations and learnings are still worth preserving because they correctly identified real problems in the pipeline at the time. The difference now is that some of those issues have been fixed and the benchmark behavior changed materially after the rerun.

### What changed after fixes

| Area | Before | After |
|---|---|---|
| Result-file isolation | Same-day reruns could contaminate counts by appending duplicate rows | Same-day reruns now reset `results.jsonl` and `summary.json` at run start |
| JSON extraction | Many responses failed on trailing commentary or multi-object outputs | First balanced JSON object extraction made most valid responses recoverable |
| `when.context` validation | Blank context entries caused hard parse failure | Blank context entries are filtered before validation |
| Prompt clarity | Minimal output example encouraged inconsistent formatting | Concrete filled example plus explicit “JSON only” instruction improved compliance |
| Curated corpus parse reliability | Severe parse failure rates on both local models | Near-zero parse failures across most curated corpora |
| Raw corpus completeness | `raw/synthetic` harness items and `raw/sibling-repos` were blocked by missing timestamps | Timestamp issue was fixed and those corpora now run end to end |

### Which earlier learnings still stand unchanged

- Safety corpora still matter most for quality conclusions.
- Cloud baselines are still useful for stronger quality comparisons.
- Replay quality is still a real bottleneck even after parsing improves.
- Stronger local models are still worth testing.

### Which earlier learnings changed after the fixes

- Earlier: formatting reliability was the dominant problem.
  Now: formatting is much less of a blocker on valid inputs; replay quality and corpus hygiene matter more.
- Earlier: corrections looked especially bad because of parsing.
  Now: corrections parse fine, but their semantic/replay quality is still mixed.
- Earlier: the benchmark was hard to trust because of file contamination.
  Now: rerun isolation is better, so current counts are more trustworthy.

### Llama-3.2-3B-Instruct-4bit

| Corpus | Trajs | Candidates | Pass | Inconclusive | Fail | Parse Error Rate |
|---|---|---|---|---|---|---|
| golden | 10 | 10 | 8 | 0 | 2 | 0.0% |
| failures/positive | 30 | 30 | 15 | 3 | 12 | 0.0% |
| failures/negative | 10 | 8 | 1 | 2 | 5 | 20.0% |
| successes | 20 | 19 | 1 | 16 | 2 | 5.0% |
| nearmiss | 14 | 14 | 4 | 4 | 6 | 0.0% |
| noisy | 5 | 5 | 1 | 3 | 1 | 0.0% |
| corrections | 5 | 5 | 2 | 2 | 1 | 0.0% |

### Qwen3-4B-Instruct-2507-4bit

| Corpus | Trajs | Candidates | Pass | Inconclusive | Fail | Parse Error Rate |
|---|---|---|---|---|---|---|
| golden | 10 | 10 | 3 | 4 | 3 | 0.0% |
| failures/positive | 30 | 30 | 15 | 9 | 6 | 0.0% |
| failures/negative | 10 | 10 | 1 | 4 | 5 | 0.0% |
| successes | 20 | 20 | 2 | 8 | 10 | 0.0% |
| nearmiss | 14 | 14 | 5 | 5 | 4 | 0.0% |
| noisy | 5 | 5 | 4 | 1 | 0 | 0.0% |
| corrections | 5 | 5 | 2 | 1 | 2 | 0.0% |

### Raw corpus rerun coverage

These runs were added after the earlier version of this document and materially change the evaluation picture.

#### Llama-3.2-3B-Instruct-4bit

| Corpus | Trajs | Candidates | Pass | Inconclusive | Fail | Parse Error Rate |
|---|---|---|---|---|---|---|
| raw/opencode | 25 | 24 | 13 | 2 | 9 | 4.0% |
| raw/synthetic | 145 | 145 | 18 | 101 | 26 | 0.0% |
| raw/ci | 110 | 109 | 8 | 49 | 52 | 0.9% |
| raw/corrections | 5 | 5 | 2 | 2 | 1 | 0.0% |
| raw/cross-session | 5 | 5 | 2 | 1 | 2 | 0.0% |
| raw/sibling-repos | 10 | 10 | 0 | 9 | 1 | 0.0% |

#### Qwen3-4B-Instruct-2507-4bit

| Corpus | Trajs | Candidates | Pass | Inconclusive | Fail | Parse Error Rate |
|---|---|---|---|---|---|---|
| raw/opencode | 25 | 25 | 13 | 7 | 5 | 0.0% |
| raw/synthetic | 145 | 145 | 36 | 87 | 22 | 0.0% |
| raw/ci | 110 | 110 | 9 | 90 | 11 | 0.0% |
| raw/corrections | 5 | 5 | 3 | 1 | 1 | 0.0% |
| raw/cross-session | 5 | 5 | 1 | 2 | 2 | 0.0% |
| raw/sibling-repos | 10 | 10 | 0 | 9 | 1 | 0.0% |

---

## Observations

### 1. The parser and prompt fixes worked

Compared with the earlier run, parse reliability improved dramatically.

- Llama `golden` improved from severe parse failure to **10/10 parsed candidates**.
- Qwen `golden` improved from severe parse failure to **10/10 parsed candidates**.
- Most curated corpora now parse at or near 100% for both local models.
- The same-day rerun contamination issue was fixed: current tables no longer show duplicated rows from date-based append behavior.

The earlier dominant parser failures were reduced substantially:

- **`when.context item must be a non-blank string`** — the model emits a JSON array with empty strings, e.g. `"context": [""]`. The `RuleWhen` validator rejects blank context entries.
- **`Extra data: line N column M`** — the model emits valid JSON followed by additional commentary or a second JSON object. The parser (`json.loads`) rejects trailing data.
- **`No JSON object found in LLM output`** — the model returns plain text with no JSON at all, e.g. a narrative sentence explaining what rule to write.
- **`Invalid \escape`** — the model emits unescaped control characters inside JSON strings.

What was fixed in code:

- first balanced JSON object extraction instead of naive first-`{`/last-`}` slicing
- blank-context filtering before `RuleWhen` validation
- stronger prompt with a fully filled JSON example and explicit "JSON only" instruction
- reset of same-day output files before reruns

Net result: formatting is no longer the main blocker on curated corpora.

### 2. The bottleneck moved from parsing to replay quality and dataset quality

Now that candidates parse reliably, the remaining weakness is mostly downstream:

- over-broad triggers still fail or go inconclusive in replay
- safety-sensitive corpora (`successes`, `failures/negative`, `nearmiss`) still expose overgeneralization
- raw corpora reveal data-quality problems, especially missing timestamps

### 3. Replay scores improved, but safety and specificity are still uneven

Replay is now measuring real extracted candidates far more often, which is progress. But scores are still constrained by:
- Golden manifest rules are specific ("when git push fails with non-fast-forward")
- Extracted triggers are generic ("when a command fails") — correct but too broad to pass replay
- The matcher and simulator are still heuristic and can over- or under-fire on substring/token overlap

### 4. Model behavior diverged more clearly after parsing was fixed

- Llama became much stronger on `golden` and `failures/positive` than the earlier snapshot suggested.
- Qwen became much stronger on `noisy` and raw synthetic breadth, with 0 parse failures on processed rows.
- The earlier narrative that both local models were mostly blocked by formatting is now only partially true; after the fixes, they are mostly limited by rule quality, safety, and missing raw fields.

### 5. Corrections improved materially after the prompt/parser fixes

Both models now parse **5/5** correction trajectories in curated and raw correction sets. The corrections corpus is no longer blocked primarily by output formatting. It is still a quality discriminator, but it is no longer the worst parsing case.

### 6. Safety-oriented corpora remain the hardest meaningful benchmark

`successes`, `failures/negative`, and parts of `nearmiss` are where bad extraction behavior becomes most visible. These sets matter disproportionately because they tell us whether the system can avoid inventing harmful or noisy rules.

### 7. Raw corpus completeness issue was real and is now resolved for this run

The missing-timestamp issue in `raw/synthetic` harness trajectories and `raw/sibling-repos` was an input/corpus problem, not an LLM problem. After fixing those files, both corpora ran successfully end to end.

### 8. The current benchmark still mixes several failure modes together

Each end-to-end run currently measures multiple things at once:

- whether the model can follow structured-output instructions
- whether the parser accepts the output
- whether the candidate is semantically reasonable
- whether replay agrees with that candidate

That is useful operationally, but it means a poor headline score does not isolate root cause by itself.

---

## Learnings

1. **The parser and prompt fixes were worth doing.** They unlocked most curated-corpus evaluation and turned the benchmark from a formatting test into a more meaningful quality test.

2. **Single-pass low-temperature evaluation is now viable.** At `0.2`, both models can produce parseable outputs reliably enough on curated corpora to support comparative evaluation.

3. **A concrete example in the extraction prompt materially helped.** This should remain part of the prompt unless stronger evidence suggests otherwise.

4. **Speed and reliability both still matter.** Qwen3.5-4B was slow enough in early execution that we stopped the run. Qwen3-4B remains usable but noticeably slower than Llama across broad sweeps.

5. **Result-reset on rerun was necessary and worked.** The earlier duplicate-row contamination is no longer visible in the rerun outputs.

6. **Safety corpora should remain first-class even if they lower aggregate scores.** `successes`, `failures/negative`, and `nearmiss` are still where unsafe overgeneralization is most visible.

7. **The benchmark still needs a cleaner split between format compliance and semantic quality.** But after the fixes, that split is less urgent than corpus hygiene and replay calibration.

8. **Raw corpus validation should happen before LLM evaluation starts.** Even though the timestamp issue is now fixed, missing required fields like `timestamp` should be caught in a validation stage, not discovered half-way through a long model run.

---

## Key Takeaways

| Takeaway | Implication |
|---|---|
| Parser and prompt fixes unlocked most local-model evaluation | Earlier low scores were partly tooling artifacts, not just model weakness |
| Small local models are now usable for broader corpus evaluation | They are still not strong enough alone for publication-quality quality claims |
| Noisy trajectories are currently the most effective local-model test set | Keep them in the loop for fast regression checks |
| Safety-sensitive corpora remain the real hard gate | `successes`, `negative`, and `nearmiss` should drive safety conclusions |
| Raw corpus validation is still required even after the fix | Input hygiene problems can waste long model runs if not caught early |

---

## Per-Corpus Interpretation

### `golden`

Purpose: strongest regression anchor because each trajectory has a known expected rule.

Interpretation:

- Good for testing rule specificity.
- Bad performance here is especially meaningful.
- Current local-model results are now good enough to measure semantic quality more directly on curated corpora.

### `failures/positive`

Purpose: the main extraction workload where the system should learn useful rules.

Interpretation:

- This is the best corpus for measuring practical extraction throughput.
- Llama's pass count here was the strongest signal that some local extraction is possible.
- Qwen3-4B no longer appears formatting-limited on curated corpora; its remaining issues are mostly quality and specificity.

### `failures/negative`

Purpose: ensure the extractor does not confidently turn bad inputs into rules.

Interpretation:

- This is a safety corpus, not just a quality corpus.
- A parsed candidate here is often a warning sign unless it correctly ends up inconclusive or rejected.

### `successes`

Purpose: protect against regression-inducing or unnecessary rule extraction.

Interpretation:

- This may be the most important safety check in the set.
- Local-model performance here still shows over-triggering and overgeneralization are real concerns.

### `nearmiss`

Purpose: check trigger precision in lookalike scenarios.

Interpretation:

- This corpus reveals whether the extractor preserves the exact failure signature.
- Better performance here remains a good sign that larger models are producing more specific triggers.

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

The corpus field tests were useful before the fixes, and they are substantially more useful after the fixes.

What the tests did well:

- They exposed that extraction had been bottlenecked by output format compliance, and confirmed that the parser/prompt fixes removed much of that bottleneck.
- They identified which corpora stress small local models the most now: `successes`, `failures/negative`, `nearmiss`, and broad raw CI/synthetic sets.
- They showed the runner needed better observability: surfacing raw LLM responses and parse errors was necessary to make failures diagnosable.
- They produced a realistic floor baseline for local OMLX models.

What the tests did not yet prove:

- They still do not prove that the current extraction prompt is robust across all realistic local models.
- They did not prove that parsed local-model candidates are strong enough for promotion-quality replay performance.
- They now produce cleaner apples-to-apples metrics for reruns, but not yet for incomplete raw assets.

Overall, the tests are now effective both as a system-debugging tool and as a first-pass comparative benchmark for local models, though not yet a publication-quality benchmark.

## Local Model Effectiveness

Local 3-4B models are more useful after the fixes than the earlier document suggested.

Where they were useful:

- Cheap repeated runs on OMLX
- Quick validation that the runner, corpus layout, and result-writing flow work end to end
- Stress-testing the strictness of the extraction schema
- Finding prompt and parser weaknesses before spending cloud budget

Where they were not effective enough:

- Producing stable structured JSON across all valid curated corpora is now mostly working
- Generating high-confidence replay-passing candidates consistently on safety-sensitive corpora
- Handling correction-heavy or subtle corpora
- Serving as the main model for publishable field-test numbers

Practical conclusion: local 3-4B models are now good enough for broad internal corpus evaluation and regression tracking, but still not strong enough as the only basis for public quality claims.

## Issue Breakdown

This run exposed three different classes of problems. Separating them matters, because the fix path is different for each one.

### LLM issues

These are failures caused mainly by the model output itself.

- The model can still emit malformed JSON or non-object structures on some raw trajectories.
- The model still sometimes emits over-broad triggers or weak directives even when the output parses.
- Small local models often produced triggers that were too broad to replay well.
  Example pattern: extracting `when a command fails` instead of preserving the concrete failure signature.
- The corrections corpus appeared especially hard for local models because they tended to answer conversationally instead of returning strict rule JSON.

Interpretation: LLM output-discipline is no longer the dominant failure mode on curated corpora, but model quality and specificity still are.

### Corpus issues

These are problems in the dataset or test assets themselves.

- The corpora are not equally difficult. `noisy` appears easier for local models than `corrections`, `successes`, or `failures/negative`.
- Some trajectory names and generated curated filenames are messy or lossy, which makes manual inspection harder.
  Examples: truncated or awkward filenames such as `F-024-coding-ython_import_failure`.
- Some raw trajectories were structurally incomplete earlier, but the timestamp issue has now been repaired and rerun.
- The benchmark currently mixes several goals at once: parsing reliability, semantic extraction quality, and replay suitability.
  That is useful operationally, but it can blur root cause attribution.

Interpretation: the corpus is now fully runnable for the local-model sweep, but it still needs pre-run validation so future asset issues are caught earlier.

### Code issues

These are problems in the runner or extraction contract.

- The runner append contamination issue was fixed by clearing same-day result files at run start.
- The extraction contract was improved by filtering blank context entries and extracting the first balanced JSON object.
- The earlier runner version swallowed extraction errors, which made diagnosis much harder.
  This was improved during the session, but it was a real contributor to confusion.
- The benchmark path still depends on strict parser success before replay can even begin.
  That means many potentially useful responses are thrown away before semantic evaluation.

Interpretation: code changes already materially improved observed success rates. The next code-focused work should target replay calibration and pre-run raw corpus validation.

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

Best interpretation: cloud LLMs are still likely to help, but the recent rerun shows local-model results were being understated by tooling issues. Cloud models should now be compared against a much cleaner baseline.

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

1. Add a raw-corpus validation stage that rejects trajectories missing required fields before LLM evaluation starts.
2. Recompute a fully updated local-model summary that includes both curated and raw corpus results.
3. Run the same corpora on one stronger local model, ideally a 7B-9B class model.
4. Run a cloud baseline, preferably OpenRouter-hosted `openai/gpt-4o-mini`, against the same now-cleaner benchmark.
5. If cloud results are much better on safety corpora, use cloud or larger local models for benchmark reporting and keep 3B-4B models for regression tracking.

## Comparative Model Table

| Model | Speed | Parse reliability | Replay usefulness | Operational cost | Recommended use |
|---|---|---|---|---|---|
| Llama-3.2-3B-Instruct-4bit | Fastest of the completed local runs | Strong on valid curated inputs after fixes | Moderate, especially on `golden` and `failures/positive` | Very low | Broad internal regression testing and low-cost evaluation |
| Qwen3-4B-Instruct-2507-4bit | Moderate | Strong on valid curated inputs after fixes | Moderate, with broader but still mixed replay quality | Very low | Secondary local benchmark and comparison run |
| Qwen3.5-4B-4bit | Too slow for this batch run | Unknown from incomplete run | Unknown | Low, but time-expensive | Skip for broad sweeps unless speed improves |
| OpenRouter `openai/gpt-4o-mini` | Slower wall-clock than tiny local, but operationally predictable | Likely much stronger | Likely materially stronger | Low-to-moderate | Cloud baseline, benchmark reporting |
| Larger local 7B-9B class model | Slower and heavier than 3B/4B | Likely stronger | Likely stronger | Medium local resource cost | Main local benchmark candidate |

## Decision

Current recommendation by use case:

| Use case | Local 3B-4B models acceptable? | Recommendation |
|---|---|---|
| Smoke tests for runner wiring | Yes | Use Llama-3.2-3B |
| Prompt iteration and parser debugging | Yes | Use local models first to keep costs down |
| Internal corpus-level benchmark tracking | Yes | Use Llama and Qwen as a local baseline pair |
| Corpus-level benchmark reporting | Not by themselves | Use stronger local 7B-9B or cloud baseline |
| Promotion gating / publishable quality claims | No | Require stronger model and cleaner metrics |
| Safety-sensitive evaluation (`successes`, `negative`, `nearmiss`) | Not by themselves | Keep local runs, but validate with stronger model |

Bottom line: local 3B-4B models are now useful as real internal benchmark tools across the full currently-available corpus, not just infrastructure smoke tests. But they are still not sufficient as the sole evidence source for public CauterRule field-test quality claims.

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
