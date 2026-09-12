# v0.3.0 Field Test — Cloud Model Comparison (gpt-4o-mini vs llama-3.1-8b)

> **Post-fix (2026-09-12):** all 3 fixes applied — domain-scoped refs (#708), pass threshold 0.5, adversarial `should_reject` override (#714) + semantic matching active (MiniLM via `.venv312`).
> Per-model: [`field-test-results-gpt-4o-mini.md`](field-test-results-gpt-4o-mini.md) · [`field-test-results-llama-3.1-8b.md`](field-test-results-llama-3.1-8b.md) · Learnings: [`learnings-fixes.md`](learnings-fixes.md) · Generated: [`generated-results.md`](generated-results.md)

---

## 1. Post-fix side-by-side (small corpora, both cloud models)

| Corpus | gpt-4o-mini | llama-3.1-8b | Better |
|--------|-------------|--------------|--------|
| golden | **4P/0F/6I**, rec 0.170 | **5P/0F/5I**, rec 0.228 | llama (more passes + recall) |
| failures/positive | 4P/6F/40I, rec 0.182 | 5P/6F/39I, rec 0.277 | llama (+1 pass, +recall) |
| nearmiss | 1P/2F/20I/27G, 98% | 0P/2F/21I/27G, **100%** | llama (0 FP) |
| noisy | 2P/0F/3I, rec 0.218 | 2P/0F/3I, rec 0.218 | tied |
| corrections | 2P/0F/3I, rec 0.110 | 1P/0F/4I, rec 0.202 | gpt-4o-mini (+1 pass) |
| adversarial/injection | **0P**/8F/2I ✅ | **0P**/8F/2I ✅ | tied (both fixed) |

## 2. Pre-fix vs post-fix (both models)

| Metric | gpt-4o-mini pre-fix | gpt-4o-mini post-fix | llama-3.1-8b pre-fix | llama-3.1-8b post-fix |
|--------|---------------------|----------------------|----------------------|----------------------|
| golden pass | 3 (30%) | **4 (40%)** | 4 (40%) | **5 (50%)** |
| golden recall | 0.068 | **0.170** | 0.104 | **0.228** |
| failures/positive pass | 4 (8%) | 4 (8%) | 3 (6%) | **5 (10%)** |
| failures/positive recall | 0.068 | **0.182** | 0.104 | **0.277** |
| nearmiss precision | 98% | 98% | 98% | **100%** |
| adversarial promoted | 2 | **0** ✅ | 2 | **0** ✅ |

## 3. Threshold gate status (post-fix)

| Threshold | Target | gpt-4o-mini | llama-3.1-8b |
|-----------|--------|-------------|--------------|
| successes pass rate | 0% | 0% ✅ | 0% ✅ |
| failures/negative pass rate | 0% | 0% ✅ | 0% ✅ |
| nearmiss precision | ≥90% | 98% ✅ | **100%** ✅ |
| generic triggers | <10% | 0.7% ✅ | 0.7% ✅ |
| adversarial 0 promoted | 0 | **0** ✅ | **0** ✅ |
| golden pass rate | ≥70% | 40% ❌ | 50% ❌ |
| failures/positive pass rate | ≥50% | 8% ❌ | 10% ❌ |

**Post-fix: 5/7 thresholds pass on both models** (was 4/7). Adversarial is now fixed. Quality remains the holdout.

## 4. Findings

1. **Adversarial promotion fixed** — 0 passes on both models (was 2 each). The `should_reject` override catches legitimate-looking rules from adversarial sources.
2. **Recall improved 2–3×** — semantic matching + domain scoping are working. llama-3.1-8b benefits more (0.228 vs 0.170 on golden).
3. **llama-3.1-8b nearmiss improved to 100%** (0 false passes) — the stronger model + semantic matching + penalty combination eliminated the last false pass.
4. **llama-3.1-8b failures/positive gained +2 passes** (3→5) — the stronger model extracts better triggers that semantic matching can bridge.
5. **Pass counts mostly unchanged on gpt-4o-mini** — the near-miss/broad-trigger penalty is still downgrading high-precision candidates. This is the next lever.
6. **gpt-4o-mini is still the safety-first choice** — fewer fails (6 vs 6, tied now), comparable nearmiss, 0 adversarial. But llama-3.1-8b is closing the gap and may be the better extraction model post-fix.
