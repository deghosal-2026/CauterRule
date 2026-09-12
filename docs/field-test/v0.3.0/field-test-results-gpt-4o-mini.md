# v0.3.0 Field Test Results — openai/gpt-4o-mini (OpenRouter cloud)

**Model:** `openai/gpt-4o-mini` (OpenRouter, cloud) · **Date:** 2026-09-12
**Results dir:** `field-test/results/0.3.0/` (`openai-openai_gpt-4o-mini`) · **Runner:** `--max-workers 4/6`
**Authoritative tables:** [`generated-results.md`](generated-results.md) · **Comparison:** [`field-test-results-cloud.md`](field-test-results-cloud.md)
**Note:** local OMLX models are excluded from the v0.3.0 reports (#713).

---

## 1. Totals

| Metric | Value |
|--------|-------|
| Corpora | 40 |
| Trajectories | 2,384 |
| Pass | 116 |
| Fail | 65 |
| Inconclusive | 1,623 (90% of scored) |
| Gate-dropped | 580 |
| LLM calls avoided | 1,160 |
| Avg precision (scored) | 0.149 |
| Avg recall (scored) | 0.068 |
| Specificity | specific 2,012 · moderate 356 · generic 16 (0.7%) |

## 2. Per-corpus (selected)

| Corpus | traj | Pass | Fail | Inconcl | Gate |
|--------|------|------|------|---------|------|
| golden | 10 | 3 | 0 | 7 | 0 |
| failures/positive | 50 | 4 | 6 | 40 | 0 |
| failures/negative | 60 | 0 | 0 | 0 | 60 |
| successes | 60 | 0 | 0 | 0 | 60 |
| nearmiss | 50 | 1 | 3 | 19 | 27 |
| public/golden | 10 | 3 | 1 | 6 | 0 |
| public/browser | 20 | 12 | 0 | 8 | 0 |
| public/real-world/bugsinpy | 36 | 29 | 0 | 7 | 0 |
| public/lifecycle_infra | 20 | 1 | 0 | 19 | 0 |
| adapters | 60 | 0 | 0 | 60 | 0 |
| lifecycle | 40 | 0 | 0 | 40 | 0 |
| packs | 40 | 0 | 10 | 30 | 0 |
| mcp | 20 | 0 | 5 | 15 | 0 |
| otel | 20 | 0 | 0 | 0 | 20 |
| cost | 1000 | 0 | 0 | 667 | 333 |
| raw/opencode | 25 | 10 | 1 | 14 | 0 |
| raw/synthetic | 145 | 22 | 15 | 108 | 0 |
| raw/ci | 110 | 0 | 0 | 110 | 0 |
| adversarial/injection | 10 | **2** | 6 | 2 | 0 |
| adversarial/misleading | 10 | 0 | 2 | 8 | 0 |
| reference-expansion | 303 | 19 | 12 | 272 | 0 |

Full 40-corpus table: [`generated-results.md`](generated-results.md).

## 3. Threshold gate status

| Threshold | Target | gpt-4o-mini | Status |
|-----------|--------|-------------|--------|
| successes pass rate | 0% | 0% | ✅ |
| failures/negative pass rate | 0% | 0% | ✅ |
| nearmiss precision | ≥90% | 98% (1/50 pass) | ✅ |
| generic triggers | <10% | 0.7% | ✅ |
| adversarial 0 promoted | 0 | **2 (injection)** | ❌ |
| golden pass rate | ≥70% | 30% (3/10) | ❌ |
| failures/positive pass rate | ≥50% | 8% (4/50) | ❌ |
| curated inconclusive | <15% | 90% | ❌ |

**Verdict:** safety corpora hold, specificity holds, but quality is far below gate and the adversarial corpus now shows **2 promotions** (not seen on local). Inconclusive is 90% — candidates rarely reach a decision. `public/real-world/bugsinpy` (29/36) and `public/browser` (12/20) are the strongest positive signals.
