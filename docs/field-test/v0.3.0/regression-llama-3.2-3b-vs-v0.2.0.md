# v0.3.0 vs v0.2.0 — Llama-3.2-3B-Instruct-4bit (OMLX local)

**Model:** `omlx-openai-Llama-3.2-3B-Instruct-4bit` · **Date:** 2026-09-11
**Baseline:** `field-test/results/0.2.0/` (2026-09-08) · **Current:** `field-test/results/0.3.0/` (2026-09-11)
**Corpora run in both:** failures_negative, failures_positive, golden, nearmiss, raw_ci, raw_opencode, raw_synthetic, successes

---

## 1. Side-by-Side — ALL v0.3.0 plan corpora

Status legend: ✅ = results captured · ⏳ = not yet run (queued/skipped in sweep)

| Corpus | v0.2.0 P/F/I (gate) | v0.3.0 P/F/I (gate) | v0.2.0 prec/rec | v0.3.0 prec/rec | Status |
|--------|----------------------|----------------------|----------------|----------------|--------|
| golden | 2/2/6 | **4/3/3** | 0.741 / 0.087 | 0.547 / 0.044 | ✅ |
| failures/positive | 10/5/34 | **12/23/15** | 0.727 / 0.091 | 0.394 / 0.062 | ✅ |
| failures/negative | 0/0/0 (gate=60) | 0/0/0 (gate=60) | — | — | ✅ |
| successes | 0/0/0 (gate=60) | 0/0/0 (gate=60) | — | — | ✅ |
| nearmiss | 3/28/19 | **5/33/12** | 0.265 / 0.047 | 0.204 / 0.016 | ✅ |
| noisy | — | 3/0/1 | — | 0.750 / 0.129 | ✅ |
| corrections | — | 2/0/3 | — | 0.400 / 0.028 | ✅ |
| raw/opencode | 6/19/0 | **7/12/6** | 0.670 / 0.067 | 0.421 / 0.066 | ✅ |
| raw/ci | 0/37/60 | 0/8/36 | 0.058 / 0.004 | 0.000 / 0.000 | ✅ |
| raw/synthetic | 15/83/47 | **29/41/73** | 0.236 / 0.021 | 0.310 / 0.041 | ✅ |
| raw/corrections | 0/0/0 | — | — | — | ⏳ |
| raw/cross-session | 0/0/0 | — | — | — | ⏳ |
| raw/sibling-repos | 0/0/0 | — | — | — | ⏳ |
| public/golden | 0/0/0 | — | — | — | ⏳ |
| public/counterexample | 2/8/8 | — | 0.167 / 0.030 | — | ⏳ |
| public/nearmiss | 0/20/0 | — | — | — | ⏳ |
| public/staleness | 0/3/7 | — | — | — | ⏳ |
| public/synthetic | 3/18/8 | — | 0.103 / 0.008 | — | ⏳ |
| public/domains | 1/15/33 | — | 0.071 / 0.008 | — | ⏳ |
| adversarial/injection | 0/10/0 | — | 0.667 / 0.045 | — | ⏳ |
| adversarial/misleading | 0/7/3 | — | 0.293 / 0.048 | — | ⏳ |
| adversarial/contradiction | 0/10/0 | — | — | — | ⏳ |
| adversarial/unsafe | 0/7/3 | — | 0.067 / 0.005 | — | ⏳ |
| adversarial/poisoning | 0/5/5 | — | 0.264 / 0.055 | — | ⏳ |
| **adapters** | — | — | — | — | ⏳ (v0.3.0 new) |
| **lifecycle** | — | — | — | — | ⏳ (v0.3.0 new) |
| **packs** | — | — | — | — | ⏳ (v0.3.0 new) |
| **mcp** | — | — | — | — | ⏳ (v0.3.0 new) |
| **otel** | — | — | — | — | ⏳ (v0.3.0 new) |
| **reference-expansion** | — | — | — | — | ⏳ (v0.3.0 new, 288 trajs) |

**v0.2.0 baseline corpora with no v0.3.0 counterpart listed:** raw/corrections, raw/cross-session, raw/sibling-repos, public/golden, public/nearmiss, public/staleness, adversarial/* — all ⏳ pending.

---

## 2. What Changed and Why

### 2.1 The system is more aggressive: inconclusive → decided, at a precision cost

The clearest pattern: **inconclusive counts dropped where v0.2.0 was conservative, and pass rates rose** (golden +20pp, raw/synthetic +10pp, failures/positive +4pp, nearmiss +4pp, raw/opencode +4pp). v0.3.0's M1-M3 changes (matcher fixes, reference expansion #489, extraction quality gates) make the matcher decide more often instead of shelving candidates as inconclusive.

The cost is **precision**. Every corpus that gained passes also lost precision:

| Corpus | v0.2.0 prec | v0.3.0 prec | what happened |
|--------|-------------|-------------|---------------|
| golden | 0.741 | 0.547 | 2 more candidates passed; more false positives among them |
| failures/positive | 0.727 | 0.394 | 23 fails vs 5 — aggressive extraction surfaces bad candidates |
| nearmiss | 0.265 | 0.204 | more near-misses incorrectly accepted (5P vs 3P) |
| raw/opencode | 0.670 | 0.421 | more passes, more fails |

**root cause hypothesis:** the #489 reference expansion (230 → 518 trajectories) raised matcher recall, which pulls more references into evidence reports. A candidate is now more likely to find *some* matching reference — but not necessarily the *right* one → more passes AND more false positives. This is the classic recall/precision tradeoff that #489 explicitly accepted ("precision not regressing" is an AC that is currently **at risk** on golden: 0.741→0.547).

### 2.2 raw/ci corpus changed shape (110 → 47 trajectories)

raw/ci went from 110 to 47 trajectories between versions — the corpus itself was cut/re-divided. **Not a model regression** (the remaining 47 produce 0 passes in both). The v0.2.0 37 fails / 60 inconclusive came from i-47 of them.

### 2.3 raw/synthetic is the clear win

15P→29P (+10pp), prec 0.236→0.31, rec 0.021→0.041. This is the corpus most representative of the #489 expansion targets (diverse phrasings) and it improved on **both** axes. This is the strongest direct evidence that the reference expansion helped.

### 2.4 Corpora new/rare in v0.3.0

| Corpus | P/F/I | prec/rec | note |
|--------|-------|----------|------|
| corrections | 2/0/3 | 0.400 / 0.028 | small sample (5) |
| noisy | 3/0/1 | 0.750 / 0.129 | small sample (5) |

The v0.3.0-only corpora (adapters, lifecycle, packs, mcp, otel, reference-expansion) and the remaining adversarial/public corpora are ⏳ pending — the sweep was aborted mid-run. Their rows are in the full table (§1) awaiting results.

---

## 3. Threshold Gate Status (release thresholds)

| Threshold | Target | v0.3.0 measured | Status |
|-----------|--------|-----------------|--------|
| successes pass rate | 0% | 0% | ✅ |
| failures/negative pass rate | 0% | 0% | ✅ |
| nearmiss precision | ≥90% | 20.4% | ❌ **far below** (5P; 33 breaks) |
| golden pass rate | ≥70% | 40% | ❌ **below** (4/10) |
| failures/positive pass rate | ≥50% | 24% | ❌ **below** (12/50) |
| curated inconclusive | <15% | golden 30% · failures/positive 30% | ❌ |
| raw inconclusive | <40% | raw/synthetic 50% · raw/opencode 24% | ❌ mixed |
| generic triggers | <10% | golden 0% · failures/positive 2% · raw/synthetic 6.5% | ✅ |

**Verdict: SAFETY HOLDS, QUALITY THRESHOLDS NOT MET.** 1/8 model thresholds pass (safety + generic triggers). The pass-rate shortfall on golden/failures/positive is the known #489 price; near miss precision at 20% is the biggest concern — it means 33/50 near-misses **break successes** if promoted.

---

## 4. Recommended Next Steps

1. **Before re-running all 4 models**, decide whether the aggressive-extraction behavior is intended. If pass rates stay ~40%/24%, the v0.3.0 release gate (golden ≥70%, failures/positive ≥50%) won't be met even on the cloud models — it's not just OMLX.
2. **Nearmiss precision 20% is a release blocker** — 33/50 near-misses falsely pass. Root-cause: reference expansion likely inflates near-miss evidence. Direction: tighten the near-miss corpus threshold or match-distance floor.
3. **Finish the sweep** for the remaining corpora (public_*, adversarial_*, new v0.3.0 corpora) so the delta table is complete.
4. Track precision regression vs #489 AC ("precision not regressing") — **currently violated on golden (0.741→0.547) and failures/positive (0.727→0.394)**.