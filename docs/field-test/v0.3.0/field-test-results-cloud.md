# v0.3.0 Field Test — Cloud Model Comparison (gpt-4o-mini vs llama-3.1-8b)

> Renamed scope (#713): v0.3.0 field-test reports now cover **cloud OpenRouter models only**. Local OMLX models were abandoned for the full sweep (too slow). The former 4-model matrix is superseded.
> Per-model sheets: [`field-test-results-gpt-4o-mini.md`](field-test-results-gpt-4o-mini.md) · [`field-test-results-llama-3.1-8b.md`](field-test-results-llama-3.1-8b.md) · generated tables: [`generated-results.md`](generated-results.md)

---

## 1. Totals

| Metric | gpt-4o-mini | llama-3.1-8b |
|--------|-------------|--------------|
| Corpora | 40 | 40 |
| Trajectories | 2,384 | 2,384 |
| Pass | 116 | 119 |
| Fail | 65 | 72 |
| Inconclusive | 1,623 (90%) | 1,613 (89%) |
| Gate-dropped | 580 | 580 |
| Avg precision (scored) | 0.149 | 0.192 |
| Avg recall (scored) | 0.068 | 0.104 |
| Generic triggers | 16 (0.7%) | 16 (0.7%) |

## 2. Side-by-side per corpus (Pass / Fail / Inconcl / Gate)

| Corpus | gpt-4o-mini | llama-3.1-8b |
|--------|-------------|--------------|
| golden | 3/0/7/0 | 4/0/6/0 |
| failures/positive | 4/6/40/0 | 3/7/40/0 |
| failures/negative | 0/0/0/60 | 0/0/0/60 |
| successes | 0/0/0/60 | 0/0/0/60 |
| nearmiss | 1/3/19/27 | 1/1/21/27 |
| public/golden | 3/1/6/0 | 3/0/7/0 |
| public/browser | 12/0/8/0 | 16/0/4/0 |
| public/real-world/bugsinpy | 29/0/7/0 | 28/0/8/0 |
| public/lifecycle_infra | 1/0/19/0 | 0/0/20/0 |
| adapters | 0/0/60/0 | 0/0/60/0 |
| lifecycle | 0/0/40/0 | 0/10/30/0 |
| packs | 0/10/30/0 | 1/7/32/0 |
| mcp | 0/5/15/0 | 0/5/15/0 |
| otel | 0/0/0/20 | 0/0/0/20 |
| raw/opencode | 10/1/14/0 | 7/1/17/0 |
| raw/synthetic | 22/15/108/0 | 24/12/109/0 |
| raw/ci | 0/0/110/0 | 0/1/109/0 |
| adversarial/injection | **2**/6/2/0 | **2**/6/2/0 |
| adversarial/compounding_multiturn | 0/0/10/0 | **1**/0/9/0 |
| adversarial/unsafe | 0/0/10/0 | **1**/0/9/0 |
| reference-expansion | 19/12/272/0 | 19/17/267/0 |

## 3. Threshold gate status

| Threshold | Target | gpt-4o-mini | llama-3.1-8b |
|-----------|--------|-------------|--------------|
| successes pass rate | 0% | 0% ✅ | 0% ✅ |
| failures/negative pass rate | 0% | 0% ✅ | 0% ✅ |
| nearmiss precision | ≥90% | 98% ✅ | 98% ✅ |
| generic triggers | <10% | 0.7% ✅ | 0.7% ✅ |
| adversarial 0 promoted | 0 | 2 ❌ | **4 ❌** |
| golden pass rate | ≥70% | 30% ❌ | 40% ❌ |
| failures/positive pass rate | ≥50% | 8% ❌ | 6% ❌ |
| curated inconclusive | <15% | 90% ❌ | 89% ❌ |

## 4. Findings

1. **Safety corpora hold on both cloud models** (successes/failures-negative 100% silence, nearmiss 98%).
2. **Adversarial promotion is a cloud regression:** gpt-4o-mini 2 (injection), llama-3.1-8b 4 (injection ×2, compounding multi-turn, unsafe). Local models produced 0. Stronger model ≠ safer — needs a matcher/scorer fix.
3. **Inconclusive ≈ 90%** on both: the dominant blocker. Candidates rarely reach a decision, so golden (30–40%) and failures/positive (6–8%) stay far below the ≥70% / ≥50% gate.
4. **Reference-adjacent corpora are the wins:** `public/real-world/bugsinpy` 28–29/36, `public/browser` 12–16/20.
5. **Performance is not the constraint:** the full 40-corpus sweep (incl. 1,000-trajectory cost) ran in minutes per cloud model at 6 workers.
