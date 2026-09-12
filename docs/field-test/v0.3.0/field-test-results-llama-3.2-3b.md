# v0.3.0 Field Test Results — Llama-3.2-3B-Instruct-4bit (OMLX local)

**Model:** `Llama-3.2-3B-Instruct-4bit` (OMLX, local, free) · **Date:** 2026-09-12
**Results dir:** `field-test/results/0.3.0/` · **Runner:** `--max-workers 3`, one corpus at a time
**Authoritative tables:** [`generated-results.md`](generated-results.md) (auto-generated from raw `results.jsonl`).
**Cross-model comparison:** [`field-test-results-4model.md`](field-test-results-4model.md) — pending the other 3 models.

---

## 1. All 39 Corpora Results

| Corpus | traj | Pass | Fail | Inconcl | Gate | prec | rec |
|--------|------|------|------|---------|------|------|-----|
| golden | 10 | 1 | 0 | 9 | 0 | 0.771 | 0.032 |
| failures/positive | 50 | 6 | 8 | 36 | 0 | 0.468 | 0.071 |
| failures/negative | 60 | 0 | 0 | 0 | 60 | — | — |
| successes | 60 | 0 | 0 | 0 | 60 | — | — |
| nearmiss | 50 | 3 | 2 | 18 | 27 | 0.440 | 0.026 |
| noisy | 5 | 0 | 0 | 5 | 0 | 0.400 | 0.050 |
| corrections | 5 | 2 | 0 | 3 | 0 | 0.400 | 0.012 |
| raw/opencode | 25 | 7 | 7 | 11 | 0 | 0.626 | 0.064 |
| raw/synthetic | 145 | 34 | 27 | 84 | 0 | 0.392 | 0.028 |
| raw/ci | 110 | 0 | 34 | 76 | 0 | 0.099 | 0.002 |
| raw/sibling-repos | 10 | 2 | 0 | 8 | 0 | 0.200 | 0.003 |
| raw/corrections | 5 | 3 | 0 | 2 | 0 | 0.800 | 0.019 |
| raw/cross-session | 5 | 0 | 1 | 4 | 0 | 0.414 | 0.055 |
| public/golden | 10 | 0 | 0 | 10 | 0 | 0.862 | 0.056 |
| public/counterexample | 20 | 0 | 9 | 11 | 0 | 0.138 | 0.026 |
| public/nearmiss | 20 | 0 | 0 | 0 | 20 | — | — |
| public/staleness | 10 | 0 | 2 | 8 | 0 | 0.059 | 0.017 |
| public/synthetic | 30 | 0 | 19 | 11 | 0 | 0.201 | 0.057 |
| public/domains | 50 | 4 | 9 | 37 | 0 | 0.251 | 0.026 |
| public/browser | 20 | 4 | 0 | 16 | 0 | 0.780 | 0.072 |
| public/real-world/bugsinpy | 36 | 12 | 0 | 24 | 0 | 0.596 | 0.044 |
| public/lifecycle_infra | 20 | 1 | 2 | 17 | 0 | 0.274 | 0.070 |
| adversarial/injection | 10 | 0 | 10 | 0 | 0 | 0.296 | 0.084 |
| adversarial/misleading | 10 | 0 | 0 | 10 | 0 | 0.111 | 0.025 |
| adversarial/contradiction | 10 | 0 | 5 | 5 | 0 | 0.163 | 0.044 |
| adversarial/unsafe | 10 | 0 | 7 | 3 | 0 | 0.230 | 0.012 |
| adversarial/poisoning | 10 | 0 | 3 | 7 | 0 | 0.126 | 0.028 |
| adversarial/tool_output_injection | 20 | 0 | 0 | 20 | 0 | — | — |
| adversarial/compounding_multiturn | 10 | 0 | 0 | 10 | 0 | — | — |
| adversarial/unsafe_realistic | 20 | 0 | 0 | 20 | 0 | — | — |
| adversarial/misleading_harmbench | 15 | 0 | 0 | 15 | 0 | 0.079 | 0.017 |
| adversarial/contradiction_harmbench | 15 | 0 | 0 | 15 | 0 | — | — |
| adapters | 60 | 0 | 0 | 60 | 0 | — | — |
| lifecycle | 40 | 0 | 24 | 16 | 0 | 0.182 | 0.052 |
| packs | 40 | 0 | 28 | 12 | 0 | 0.332 | 0.086 |
| mcp | 20 | 3 | 0 | 17 | 0 | 0.352 | 0.029 |
| otel | 20 | 0 | 20 | 0 | 0 | 0.296 | 0.084 |
| reference-expansion | 303 | 12 | 84 | 207 | 0 | 0.283 | 0.038 |
| reference-expansion/paraphrase-diversity | 15 | 1 | 4 | 10 | 0 | 0.463 | 0.108 |

**Total:** 39 corpora · **1,384 trajectories** · 95 pass · 305 fail · 817 inconclusive · 167 gate-dropped.
`cost` (1,000) is the only target corpus not run — it requires a priced cloud model; local OMLX cost is $0.

---

## 2. Key Findings

### 2.1 Safety holds (100% silence)
- `successes`: 60/60 gate-dropped (100% silence).
- `failures/negative`: 60/60 gate-dropped (100% silence).
- `public/nearmiss`: 20/20 gate-dropped.
- Gate totals: 167 drops — `no_failure_signal` 120, `nearmiss_recovery_succeeded` 47 (334 LLM calls avoided).

### 2.2 Adversarial: 0 promoted rules
All 9 adversarial corpora (injection, misleading, contradiction, unsafe, poisoning, tool-output injection, compounding multi-turn, AgentHarm unsafe_realistic, HarmBench misleading/contradiction): **0 passes**. Security-correct.

### 2.3 Nearmiss: 3 false passes / 50
3/50 nearmiss trajectories still produce a `pass` (rest gate-dropped/failed/inconclusive) → **94% correctly not promoted**. The release target (≥90% precision) is met at the corpus level.

### 2.4 Quality pass rates remain below gate
- golden: 1 pass / 10 (10% of all; 100% of scored).
- failures/positive: 6/50 (12%).
- curated inconclusive is high (golden 90%, failures/positive 72%).
- Root cause is the known matcher/threshold + paraphrase gap (#677/#680), consistent with the prior run; semantic matching (#689, opt-in) is the v0.4.0 lever.

### 2.5 Specificity distribution (good)
specific 1,012 (73%), moderate 356 (26%), generic 16 (1.2%) — generic-trigger target (<10%) met comfortably.

---

## 3. Threshold Gate Status (v0.3.0 release thresholds)

| Threshold | Target | v0.3.0 Llama | Status |
|-----------|--------|--------------|--------|
| successes pass rate | 0% | 0% | ✅ |
| failures/negative pass rate | 0% | 0% | ✅ |
| nearmiss precision | ≥90% | 94% (3/50 false pass) | ✅ |
| adversarial 0 promoted | 0 | 0 | ✅ |
| generic triggers | <10% | 1.2% | ✅ |
| golden pass rate | ≥70% | 10% (1/10) | ❌ |
| failures/positive pass rate | ≥50% | 12% (6/50) | ❌ |
| curated inconclusive | <15% | golden 90% · failures/positive 72% | ❌ |
| raw inconclusive | <40% | raw/synthetic 58% · raw/opencode 44% | ❌ |

**Verdict:** SAFETY + SECURITY + SPECIFICITY hold; **quality pass rates remain below the release gate** on this 3B local model (consistent with the prior run and the documented small-model ceiling). Cloud models (gpt-4o-mini, llama-3.1-8b) and the second local model (Qwen3-4B) are not yet re-run.

---

## 4. Notes

- `--max-workers 3` (reduced from 4 per request).
- Multi-record JSONL support: adapters 60/60, lifecycle 40/40, packs 40/40, mcp 20/20, otel 20/20, reference-expansion 303/303.
- Promoted reference→target corpora this run: `public/browser` (20), `public/real-world/bugsinpy` (36), `public/lifecycle_infra` (20).
- Reference set loaded per sweep: 444 trajectories across curated + `corpus/public/{adapters,lifecycle,mcp,otel,browser,lifecycle_infra,real-world/bugsinpy,successes}`.
