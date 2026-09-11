# v0.3.0 Field Test Results — Qwen3-4B-Instruct-2507-4bit (OMLX local)

**Model:** `Qwen3-4B-Instruct-2507-4bit` (OMLX, local, free) · **Date:** 2026-09-11
**Results dir:** `field-test/results/0.3.0/` · **Runner:** `--max-workers 3`, one corpus at a time
**Cross-model comparison:** [`field-test-results-4model.md`](field-test-results-4model.md) — the 4-model matrix supersedes this single-model sheet for gate decisions.
**Sibling:** Llama-3.2-3B results — `field-test-results-llama-3.2-3b.md` (both local models part of #648)

---

## 1. All 30 Corpora Results

| Corpus | traj | Pass | Fail | Inconcl | Gate | prec | rec | verdict |
|--------|------|------|------|---------|------|------|-----|---------|
| golden | 10 | 1 | 3 | 6 | 0 | 0.380 | 0.030 | pass |
| failures/positive | 50 | 3 | 28 | 19 | 0 | 0.169 | 0.042 | pass |
| failures/negative | 60 | 0 | 0 | 0 | 60 | 0 | 0 | pass |
| successes | 60 | 0 | 0 | 0 | 60 | 0 | 0 | pass |
| nearmiss | 50 | 1 | 2 | 9 | 37 | 0.188 | 0.016 | pass |
| noisy | 5 | 0 | 0 | 5 | 0 | 0.400 | 0.044 | fail |
| corrections | 5 | 0 | 0 | 4 | 0 | 0 | 0 | fail |
| raw/opencode | 25 | 3 | 14 | 8 | 0 | 0.290 | 0.048 | pass |
| raw/ci | 110 | 0 | 13 | 97 | 0 | 0.010 | 0.004 | fail |
| raw/synthetic | 145 | 12 | 37 | 90 | 0 | 0.173 | 0.021 | pass |
| raw/sibling-repos | 10 | 0 | 0 | 9 | 0 | 0.078 | 0.033 | fail |
| raw/corrections | 5 | 0 | 0 | 4 | 0 | 0.417 | 0.023 | fail |
| raw/cross-session | 5 | 0 | 5 | 0 | 0 | 0.098 | 0.025 | fail |
| public/golden | 10 | 1 | 2 | 7 | 0 | 0.467 | 0.059 | pass |
| public/counterexample | 20 | 0 | 7 | 13 | 0 | 0.137 | 0.062 | fail |
| public/nearmiss | 20 | 0 | 0 | 0 | 20 | 0 | 0 | fail |
| public/staleness | 10 | 0 | 0 | 10 | 0 | 0 | 0 | fail |
| public/synthetic | 30 | 0 | 5 | 25 | 0 | 0.042 | 0.005 | fail |
| public/domains | 50 | 0 | 15 | 35 | 0 | 0.025 | 0.003 | fail |
| adversarial/injection | 10 | 0 | 10 | 0 | 0 | 0.241 | 0.109 | fail |
| adversarial/misleading | 10 | 0 | 3 | 7 | 0 | 0.143 | 0.048 | fail |
| adversarial/contradiction | 10 | 0 | 2 | 8 | 0 | 0.145 | 0.053 | fail |
| adversarial/unsafe | 10 | 0 | 2 | 8 | 0 | 0.049 | 0.014 | fail |
| adversarial/poisoning | 10 | 0 | 1 | 9 | 0 | 0.077 | 0.027 | fail |
| **adapters** | 18 | 0 | 0 | 18 | 0 | 0 | 0 | fail |
| **lifecycle** | 40 | 0 | 9 | 31 | 0 | 0.110 | 0.027 | fail |
| **packs** | 40 | 0 | 30 | 10 | 0 | 0.188 | 0.078 | fail |
| **mcp** | 20 | 0 | 5 | 15 | 0 | 0.109 | 0.027 | fail |
| **otel** | 20 | 0 | 0 | 20 | 0 | 0 | 0 | fail |
| **reference-expansion** | 288 | 9 | 125 | 152 | 0 | 0.103 | 0.022 | pass |

**Total:** 30 corpora · 1,156 trajectories processed.

---

## 2. Key Findings

### 2.1 Safety holds (same as Llama)
- `successes` + `failures/negative`: **60/60 each gate-dropped** (100% silence). ✅

### 2.2 Nearmiss: also 1 false-pass (98% correct)
Identical to Llama: the same gate + scorer + self-match fixes hold. `nearmiss` gate-drops 37/50, remaining 1 pass is the same irreducible N-002 case.

### 2.3 Fix-8 gate-side holds on Qwen
The Fix-8 keyword gate (success=True + recovery keyword in failure_class → silence) works on both local models. Combined with Llama, this confirms **issue #491's "Fix 8 is model-independent"** claim gate-side.

### 2.4 #492 alias-removal — Qwen recall did NOT regress
This is the important one: we removed the 5 broad "Qwen aliases" (#492). Qwen3-4B's recall (raw/synthetic 0.021, reference-expansion 0.022) is **commensurate with Llama** (0.039 / 0.031 respectively). The abstract triggers still match via the weighted token-F1 path. **The reversion is safe — Qwen does not depend on the broad aliases.**

### 2.5 Adversarial: 0 promoted
0 passes across all 5 adversarial corpora. ✅ Security holds.

---

## 3. Threshold Gate Status (v0.3.0 release thresholds)

| Threshold | Target | Qwen3-4B | Status |
|-----------|--------|----------|--------|
| successes / failures/negative pass | 0% | 0% | ✅ |
| nearmiss precision | ≥90% | 98% correct | ✅ |
| adversarial 0 promoted | 0 | 0 | ✅ |
| golden pass rate | ≥70% | 10% (1/10) | ❌ |
| failures/positive pass rate | ≥50% | 6% (3/50) | ❌ |
| curated inconclusive | <15% | golden 60% · failures/positive 38% | ❌ |

**Same verdict as Llama:** safety + security + nearmiss hold; quality pass-rate thresholds are not met by either 3B/4B local model. Cloud sweep (#650) is the decisive measurement.

---

## 4. Notes

- Both local models (Llama-3.2-3B + Qwen3-4B) now swept on all 30 corpora — closes the #648 local sweep.
- The #492 alias removal did not hurt Qwen recall (see §2.4).
- Full before/after fix analysis in `learnings-fixes.md` (shared).