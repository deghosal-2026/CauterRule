# v0.3.0 Field Test Results — 4-Model Comparison (all 30 corpora)

**Date:** 2026-09-11 · **Models:** Llama-3.2-3B + Qwen3-4B (OMLX local, #648) · gpt-4o-mini + llama-3.1-8b (OpenRouter cloud, #650)
**Results dir:** `field-test/results/0.3.0/` · **Runner:** `--max-workers 3-6`, one corpus at a time
**All models swept on all 30 corpora (908 trajectories each; 3,632 total runs).**

---

## 1. Key Corpora — 4-Model Matrix

| Corpus | Llama-3.2-3B | Qwen3-4B | gpt-4o-mini | llama-3.1-8b | Target |
|--------|--------------|-----------|-------------|--------------|--------|
| golden P/F/I | 1/3/6 | 1/3/6 | 1/3/6 | 1/2/7 | ≥70% P (7/10) |
| failures/positive P/F/I | 5/24/18 | 3/28/19 | 4/19/27 | 3/10/13 | ≥50% P (25/50) |
| failures/negative gate | 60/60 | 60/60 | 60/60 | 60/60 | 100% silence |
| successes gate | 60/60 | 60/60 | 60/60 | 60/60 | 100% silence |
| nearmiss P + gate | 1 / 37 | 1 / 37 | 1 / 37 | 1 / 37 | ≥90% correct |
| adversarial/injection P | 0 | 0 | 0 | 0 | 0 promoted |
| adversarial/unsafe P | 0 | 0 | 0 | 0 | 0 promoted |
| adapters P | 0 | 0 | 0 | 0 | 0 promoted |
| packs P | 0 (33F) | 0 (30F) | 0 (40F) | 0 (36F) | 0 unsafe |
| reference-expansion prec/rec | 0.133/0.031 | 0.103/0.022 | 0.099/0.020 | 0.142/0.039 | recall ≥0.10 |
| raw/synthetic prec/rec | 0.331/0.039 | 0.173/0.021 | 0.244/0.025 | 0.246/0.032 | — |

---

## 2. Consistent Across All 4 Models (the strong signal)

The 4-model sweep is **remarkably uniform**:

1. **Safety: 100% gate-silence on all 4 models.** `successes` + `failures/negative` 60/60 dropped each. The recovery-keyword gate (success=True + recovery class → silence) holds identically across every model — Fix-8 gate-side is definitively model-independent.

2. **Nearmiss: exactly 1 false-pass on all 4 models** (98% correct, gate 37/50 each). The same irreducible N-002 pandas-import edge. The gate+scorer+self-match fixes generalize perfectly.

3. **Adversarial: 0 promoted on all 4 models** across all 5 adversarial corpora. Security holds on every model.

4. **Packs: 0 promoted, 33-40 failed** on all 4. Pack rules correctly REPLAY-fail against the pack-replay corpus (they don't spuriously match).

5. **Adapters: 0 promoted, 0 failed, 15-18 inconclusive** — the adapter trajectories produce candidates that don't match references → inconclusive. Not a pass bug; they surfaced exactly at the nearmiss-designed threshold.

## 3. The Real Finding: Quality Gate Is UNREACHABLE at the Current Matcher Thresholds

| Threshold | Target | Best model | Worse model | Status |
|-----------|--------|-----------|-------------|--------|
| golden pass ≥70% | 7/10 | 1/10 | 1/10 | ❌ all models |
| failures/positive ≥50% | 25/50 | 5/50 | 3/50 | ❌ all models |
| curated inconclusive <15% | <1.5/10 | golden 6-7/10 | | ❌ all models |
| nearmiss ≥90% | | 98% | 98% | ✅ all models |
| reference recall ≥0.10 | | 0.031 | 0.020 | ❌ all models |

**This is not a small-model problem.** The two cloud models (gpt-4o-mini, llama-3.1-8b) perform identically to the local 3B/4B models on the quality metrics. The bottleneck is the **matcher threshold vs. the reference corpus similarity**, not model capability: extracted candidates simply don't score ≥ threshold against references (the follow-on effect of removing the broad #492 aliases — precision recovered but the cost is that valid-but-generic triggers now fail).

**The near-miss penalty + self-match exclusion + alias removal made precision honest but dropped the pass-rate.** Golden 1/10 across ALL models confirms this is structural, not model-specific.

## 4. Recommended Next Step (feed #667 report + release decision)

1. **Re-baseline the release gate.** With safety + nearmiss + adversarial all green on 4/4 models, the "quality" thresholds (golden ≥70%, fp ≥50%) were calibrated on the pre-#492-alias-removal matcher. Either:
   a. Tune the matcher score blend (0.6 token-F1 + 0.4 bigram) or raise the DEFAULT pass floor, OR
   b. Re-baseline thresholds to golden ≥20% + fp ≥20% with a documented rationale, OR
   c. Re-introduce SELECTIVE aliases (specific phrases only) for the canonical failures (#492 targets).

2. The #489 recall target (≥0.10) is unmet on reference-expansion (0.02-0.04) — the expanded corpus alone does not lift recall; the matcher needs the alias/semantic help it lost.

3. **Field test verdict for v0.3.0 = SAFE BUT QUALITY-GATED.** Safety, nearmiss, adversarial, pack, adapter outcomes are all secure on 4/4. The quality pass-rate thresholds are a release-blocker documented here for #667/#673 triage.

---

## 5. Per-Model Detail Docs

- Llama-3.2-3B: `field-test-results-llama-3.2-3b.md`
- Qwen3-4B: `field-test-results-qwen3-4b.md`
- Learnings/fixes: `learnings-fixes.md`