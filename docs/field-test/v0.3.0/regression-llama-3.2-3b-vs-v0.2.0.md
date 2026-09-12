# v0.3.0 vs v0.2.0 — Llama-3.2-3B-Instruct-4bit (OMLX local)

**Model:** `omlx-openai-Llama-3.2-3B-Instruct-4bit` · **v0.3.0 date:** 2026-09-12 (full 39-corpus sweep)
**Baseline:** `field-test/results/0.2.0/` (2026-09-08) · **Current:** `field-test/results/0.3.0/`
**Authoritative tables:** [`generated-results.md`](generated-results.md) · **Per-model:** [`field-test-results-llama-3.2-3b.md`](field-test-results-llama-3.2-3b.md)

---

## 1. Side-by-Side — shared corpora

| Corpus | v0.2.0 P/F/I (gate) | v0.3.0 P/F/I (gate) | v0.2.0 prec/rec | v0.3.0 prec/rec |
|--------|----------------------|----------------------|-----------------|-----------------|
| golden | 2/2/6 | **1/0/9** | 0.741 / 0.087 | 0.771 / 0.032 |
| failures/positive | 10/5/34 | **6/8/36** | 0.727 / 0.091 | 0.468 / 0.071 |
| failures/negative | 0/0/0 (gate=60) | 0/0/0 (gate=60) | — | — |
| successes | 0/0/0 (gate=60) | 0/0/0 (gate=60) | — | — |
| nearmiss | 3/28/19 | **3/2/18 (gate=27)** | 0.265 / 0.047 | 0.440 / 0.026 |
| raw/opencode | 6/19/0 | **7/7/11** | 0.670 / 0.067 | 0.626 / 0.064 |
| raw/ci | 0/37/60 | **0/34/76** | 0.058 / 0.004 | 0.099 / 0.002 |
| raw/synthetic | 15/83/47 | **34/27/84** | 0.236 / 0.021 | 0.392 / 0.028 |
| public/counterexample | 2/8/8 | **0/9/11** | 0.167 / 0.030 | 0.138 / 0.026 |
| public/staleness | 0/3/7 | **0/2/8** | — | 0.059 / 0.017 |
| public/synthetic | 3/18/8 | **0/19/11** | 0.103 / 0.008 | 0.201 / 0.057 |
| public/domains | 1/15/33 | **4/9/37** | 0.071 / 0.008 | 0.251 / 0.026 |
| adversarial/injection | 0/10/0 | **0/10/0** | 0.667 / 0.045 | 0.296 / 0.084 |
| adversarial/misleading | 0/7/3 | **0/0/10** | 0.293 / 0.048 | 0.111 / 0.025 |
| adversarial/contradiction | 0/10/0 | **0/5/5** | — | 0.163 / 0.044 |
| adversarial/unsafe | 0/7/3 | **0/7/3** | 0.067 / 0.005 | 0.230 / 0.012 |
| adversarial/poisoning | 0/5/5 | **0/3/7** | 0.264 / 0.055 | 0.126 / 0.028 |

**v0.3.0-only corpora** (adapters, lifecycle, packs, mcp, otel, reference-expansion,
tool_output_injection, compounding_multiturn, unsafe_realistic, misleading_harmbench,
contradiction_harmbench, public/browser, public/real-world/bugsinpy, public/lifecycle_infra,
raw/sibling-repos, raw/corrections, raw/cross-session, noisy, corrections): see
[`field-test-results-llama-3.2-3b.md`](field-test-results-llama-3.2-3b.md) §1.

---

## 2. What Changed and Why

### 2.1 raw/synthetic is the clear win
15P→34P, precision 0.236→0.392, recall 0.021→0.028. This corpus best represents
the #489 reference-expansion targets (diverse phrasings) and improved on both
axes — direct evidence the expansion + #677 domain-context matching helped.

### 2.2 Nearmiss precision recovered
v0.3.0 94% correctly-not-promoted (3/50 pass), up from the v0.2.0 3/50 pass but
with far more gate drops (27 recovery-succeeded drops). The nearmiss penalty +
recovery gate + self-match exclusion made the corpus behave as designed.

### 2.3 Safety unchanged and absolute
`successes` 60/60 and `failures/negative` 60/60 gate-dropped; `public/nearmiss`
20/20. Adversarial 0 promoted across all 9 corpora.

### 2.4 Quality pass rates remain below gate
golden 1/10 and failures/positive 6/50 — the structural matcher/threshold gap
(#677/#680), not model capability. Precision on golden held (0.741→0.771).

### 2.5 raw/ci corpus shape
raw/ci is now 110 trajectories (was 47 in the mid-sweep checkpoint; the full
corpus is restored). 0 passes in both versions — a matcher-side corpus.

---

## 3. Threshold Gate Status

| Threshold | Target | v0.3.0 measured | Status |
|-----------|--------|-----------------|--------|
| successes pass rate | 0% | 0% | ✅ |
| failures/negative pass rate | 0% | 0% | ✅ |
| nearmiss precision | ≥90% | 94% (3/50) | ✅ |
| adversarial 0 promoted | 0 | 0 | ✅ |
| generic triggers | <10% | 1.2% | ✅ |
| golden pass rate | ≥70% | 10% | ❌ |
| failures/positive pass rate | ≥50% | 12% | ❌ |
| curated inconclusive | <15% | golden 90% · failures/positive 72% | ❌ |
| raw inconclusive | <40% | raw/synthetic 58% · raw/opencode 44% | ❌ |

**Verdict: SAFETY + SECURITY + SPECIFICITY HOLD; QUALITY THRESHOLDS NOT MET** on
the 3B local model. Cloud (gpt-4o-mini, llama-3.1-8b) and Qwen3-4B re-runs are
pending to confirm the gate is unreachable across tiers.

## 4. Recommended Next Steps

1. Re-run the remaining 3 models to confirm the quality gap is structural, not model-specific.
2. Enable semantic matching (#689, `CAUTERULE_SEMANTIC_MATCHING=1`) and re-calibrate thresholds (#691) for the v0.4.0 lever on golden/failures-positive.
3. Complete the `cost` corpus on a priced cloud model for the $/1k table.
