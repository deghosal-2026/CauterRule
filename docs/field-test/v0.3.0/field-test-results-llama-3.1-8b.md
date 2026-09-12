# v0.3.0 Field Test Results — meta-llama/llama-3.1-8b-instruct (OpenRouter cloud)

**Model:** `meta-llama/llama-3.1-8b-instruct` (OpenRouter, cloud) · **Date:** 2026-09-12
**Results dir:** `field-test/results/0.3.0/` (`openai-meta-llama_llama-3.1-8b-instruct`)
**Runner:** `.venv312` (Python 3.12) + `CAUTERULE_SEMANTIC_MATCHING=1` · `--max-workers 6`
**Fixes applied:** #708 domain-scoped refs, #709 relaxed-gate clean success, pass threshold 0.5, #714 adversarial should_reject override, semantic matching active (MiniLM)
**Authoritative tables:** [`generated-results.md`](generated-results.md) · **Comparison:** [`field-test-results-cloud.md`](field-test-results-cloud.md) · **Learnings:** [`learnings-fixes.md`](learnings-fixes.md)

---

## 1. Post-fix results (small corpora, re-run with all fixes)

| Corpus | traj | Pass | Fail | Inconcl | Gate | recall | Notes |
|--------|------|------|------|---------|------|--------|-------|
| golden | 10 | 5 | 0 | 5 | 0 | 0.228 | **50% pass** (v0.2.0 level); near-miss tolerance band applied |
| failures/positive | 50 | 5 | 6 | 39 | 0 | 0.277 | 10% pass; +2 passes vs pre-fix |
| nearmiss | 50 | 0 | 2 | 21 | 27 | 0.037 | 100% precision ✅ (was 98%) |
| noisy | 5 | 2 | 0 | 3 | 0 | 0.218 | 40% pass |
| corrections | 5 | 1 | 0 | 4 | 0 | 0.202 | 20% pass |
| adversarial/injection | 10 | **0** | 8 | 2 | 0 | 0.153 | ✅ 0 promotions (was 2) |

## 2. Pre-fix vs post-fix comparison

| Corpus | Pre-fix P/F/I | Post-fix P/F/I | Pre-fix recall | Post-fix recall | Change |
|--------|---------------|----------------|----------------|-----------------|--------|
| golden | 4/0/6 | **5/0/5** | 0.104 | 0.228 | +1 pass (tolerance band), recall 2.2× |
| failures/positive | 3/7/40 | 5/6/39 | 0.104 | 0.277 | +2 passes, recall 2.7× |
| nearmiss | 1/1/21/27G | 0/2/21/27G | 0.026 | 0.037 | 100% precision ✅ |
| noisy | 2/0/3 | 2/0/3 | 0.050 | 0.218 | recall 4× |
| corrections | 2/0/3 | 1/0/4 | 0.019 | 0.202 | recall 10× |
| adversarial/injection | **2**/6/2 | **0**/8/2 | 0.084 | 0.153 | ✅ fixed |

## 3. Threshold gate status (post-fix)

| Threshold | Target | llama-3.1-8b | Status |
|-----------|--------|--------------|--------|
| successes pass rate | 0% | 0% | ✅ |
| failures/negative pass rate | 0% | 0% | ✅ |
| nearmiss precision | ≥90% | **100%** (0/50) | ✅ **improved** |
| generic triggers | <10% | 0.7% | ✅ |
| adversarial 0 promoted | 0 | **0** | ✅ **fixed** |
| golden pass rate | ≥70% | 50% (5/10) | ❌ (improved from 40%; back to v0.2.0 level) |
| failures/positive pass rate | ≥50% | 10% (5/50) | ❌ |

**Verdict:** safety + adversarial + specificity now all pass. nearmiss improved to 100% (0 false passes). Quality improved (+2 passes on failures/positive, recall 2.7×). Still below gate — same near-miss penalty bottleneck as gpt-4o-mini.
