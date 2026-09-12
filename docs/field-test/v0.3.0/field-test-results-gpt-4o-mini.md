# v0.3.0 Field Test Results — openai/gpt-4o-mini (OpenRouter cloud)

**Model:** `openai/gpt-4o-mini` (OpenRouter, cloud) · **Date:** 2026-09-12
**Results dir:** `field-test/results/0.3.0/` (`openai-openai_gpt-4o-mini`)
**Runner:** `.venv312` (Python 3.12) + `CAUTERULE_SEMANTIC_MATCHING=1` · `--max-workers 6`
**Fixes applied:** #708 domain-scoped refs, #709 relaxed-gate clean success, pass threshold 0.5, #714 adversarial should_reject override, semantic matching active (MiniLM)
**Authoritative tables:** [`generated-results.md`](generated-results.md) · **Comparison:** [`field-test-results-cloud.md`](field-test-results-cloud.md) · **Learnings:** [`learnings-fixes.md`](learnings-fixes.md)

---

## 1. Post-fix results (small corpora, re-run with all fixes)

| Corpus | traj | Pass | Fail | Inconcl | Gate | recall | Notes |
|--------|------|------|------|---------|------|--------|-------|
| golden | 10 | 4 | 0 | 6 | 0 | 0.170 | **40% pass**; near-miss tolerance band applied |
| failures/positive | 50 | 4 | 6 | 40 | 0 | 0.182 | 8% pass; recall 2.5× |
| nearmiss | 50 | 1 | 2 | 20 | 27 | 0.035 | 98% precision ✅ |
| noisy | 5 | 2 | 0 | 3 | 0 | 0.218 | 40% pass |
| corrections | 5 | 2 | 0 | 3 | 0 | 0.110 | 40% pass |
| adversarial/injection | 10 | **0** | 8 | 2 | 0 | 0.153 | ✅ 0 promotions (was 2) |

## 2. Pre-fix vs post-fix comparison

| Corpus | Pre-fix P/F/I | Post-fix P/F/I | Pre-fix recall | Post-fix recall | Change |
|--------|---------------|----------------|----------------|-----------------|--------|
| golden | 3/0/7 | **4/0/6** | 0.068 | 0.170 | +1 pass (tolerance band), recall 2.5× |
| failures/positive | 4/6/40 | 4/6/40 | 0.068 | 0.182 | recall 2.5× |
| nearmiss | 1/3/19/27G | 1/2/20/27G | 0.026 | 0.035 | safety held ✅ |
| noisy | 2/0/3 | 2/0/3 | 0.050 | 0.218 | recall 4× |
| corrections | 2/0/3 | 2/0/3 | 0.012 | 0.110 | recall 9× |
| adversarial/injection | **2**/6/2 | **0**/8/2 | 0.084 | 0.153 | ✅ fixed |

## 3. Threshold gate status (post-fix)

| Threshold | Target | gpt-4o-mini | Status |
|-----------|--------|-------------|--------|
| successes pass rate | 0% | 0% | ✅ |
| failures/negative pass rate | 0% | 0% | ✅ |
| nearmiss precision | ≥90% | 98% (1/50) | ✅ |
| generic triggers | <10% | 0.7% | ✅ |
| adversarial 0 promoted | 0 | **0** | ✅ **fixed** |
| golden pass rate | ≥70% | 40% (4/10) | ❌ (improved from 30%) |
| failures/positive pass rate | ≥50% | 8% (4/50) | ❌ |

**Verdict:** safety + adversarial + specificity now all pass. Quality still below gate — the near-miss/broad-trigger penalty is downgrading high-precision candidates (precision 0.62–0.89 → inconclusive). Tuning the penalty tolerance is the next lever.
