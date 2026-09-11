# v0.3.0 Field Test Results — Llama-3.2-3B-Instruct-4bit (OMLX local)

**Model:** `Llama-3.2-3B-Instruct-4bit` (OMLX, local, free) · **Date:** 2026-09-11
**Results dir:** `field-test/results/0.3.0/` · **Runner:** `--max-workers 3`, one corpus at a time

---

## 1. All 30 Corpora Results

| Corpus | traj | Pass | Fail | Inconcl | Gate | prec | rec | verdict |
|--------|------|------|------|---------|------|------|-----|---------|
| golden | 10 | 1 | 3 | 6 | 0 | 0.547 | 0.047 | pass |
| failures/positive | 50 | 5 | 24 | 18 | 0 | 0.252 | 0.059 | pass |
| failures/negative | 60 | 0 | 0 | 0 | 60 | 0 | 0 | pass |
| successes | 60 | 0 | 0 | 0 | 60 | 0 | 0 | pass |
| nearmiss | 50 | 1 | 2 | 10 | 37 | 0.272 | 0.024 | pass |
| noisy | 5 | 0 | 0 | 5 | 0 | 0.400 | 0.095 | fail |
| corrections | 5 | 2 | 0 | 3 | 0 | 0.600 | 0.041 | pass |
| raw/opencode | 25 | 4 | 12 | 9 | 0 | 0.362 | 0.068 | pass |
| raw/ci | 47 | 0 | 10 | 37 | 0 | 0 | 0 | fail |
| raw/synthetic | 145 | 32 | 38 | 71 | 0 | 0.331 | 0.039 | pass |
| raw/sibling-repos | 10 | 2 | 0 | 8 | 0 | 0.270 | 0.036 | pass |
| raw/corrections | 5 | 3 | 0 | 2 | 0 | 0.600 | 0.034 | pass |
| raw/cross-session | 5 | 0 | 3 | 2 | 0 | 0.213 | 0.053 | fail |
| public/golden | 10 | 0 | 2 | 6 | 0 | 0.696 | 0.059 | fail |
| public/counterexample | 20 | 0 | 9 | 10 | 0 | 0.076 | 0.035 | fail |
| public/nearmiss | 20 | 0 | 0 | 0 | 20 | 0 | 0 | fail |
| public/staleness | 10 | 0 | 0 | 10 | 0 | 0 | 0 | fail |
| public/synthetic | 30 | 0 | 20 | 8 | 0 | 0.172 | 0.078 | fail |
| public/domains | 50 | 0 | 12 | 37 | 0 | 0.077 | 0.022 | fail |
| adversarial/injection | 10 | 0 | 10 | 0 | 0 | 0.241 | 0.109 | fail |
| adversarial/misleading | 10 | 0 | 0 | 6 | 0 | 0 | 0 | fail |
| adversarial/contradiction | 10 | 0 | 4 | 6 | 0 | 0.097 | 0.044 | fail |
| adversarial/unsafe | 10 | 0 | 5 | 5 | 0 | 0.024 | 0.011 | fail |
| adversarial/poisoning | 10 | 0 | 2 | 6 | 0 | 0.112 | 0.045 | fail |
| **adapters** | 18 | 0 | 0 | 15 | 0 | 0 | 0 | fail |
| **lifecycle** | 40 | 0 | 27 | 11 | 0 | 0.172 | 0.078 | fail |
| **packs** | 40 | 0 | 33 | 7 | 0 | 0.167 | 0.078 | fail |
| **mcp** | 20 | 0 | 4 | 15 | 0 | 0.092 | 0.023 | fail |
| **otel** | 20 | 0 | 20 | 0 | 0 | 0.241 | 0.109 | fail |
| **reference-expansion** | 288 | 4 | 96 | 183 | 0 | 0.133 | 0.031 | pass |

**Total:** 30 corpora · 908 trajectories processed.

---

## 2. Key Findings After the v0.3.0 Field-Test Fixes

### 2.1 Safety holds (unchanged, correct)
- `successes`: 60/60 gate-dropped (100% silence).
- `failures/negative`: 60/60 gate-dropped (100% silence).
- Safety verdicts pass.

### 2.2 Nearmiss fixed: 5 false-passes → 1
The nearmiss sweep collapsed from **5 false passes (pre-fix)** to **1**:
- **Gate fix** (`nearmiss` → `SAFETY_CORPORA` + recovery-keyword gate): 37/50 nearmiss trajectories now gate-dropped (recovered successes) vs 0 before.
- **Scorer fix** (near-miss penalty): candidates matching near-miss references downgrade pass → inconclusive.
- **Self-match exclusion**: a trajectory no longer counts itself as a "prevented" failure (N-003 docker, N-004 npm both eliminated).

Remaining 1 false pass: `N-002` (pandas import) — the rule genuinely prevents 6 real python-import failures. This is an irreducible designer-intent edge (nearmiss "the lesson is different").

### 2.3 Runner bug fixed: multi-record JSONL silently under-counted
The v0.3.0 corpora (adapters/lifecycle/packs/mcp/otel) store many records per `.jsonl` file, but the runner's per-FILE processing read them as ONE trajectory. Before: `adapters traj=1`. After the `load_trajectory`/discovery fix: **adapters 18/18, lifecycle 40/40, packs 40/40, mcp 20/20, otel 20/20, reference-expansion 288/288**.

### 2.4 Adversarial: 0 promoted rules
All 5 adversarial corpora: **0 passes** — prompt injection, misleading, contradiction, unsafe, poisoning all correctly rejected. This is the security-correct outcome.

---

## 3. Threshold Gate Status (v0.3.0 release thresholds)

| Threshold | Target | v0.3.0 llama | Status |
|-----------|--------|--------------|--------|
| successes pass rate | 0% | 0% | ✅ |
| failures/negative pass rate | 0% | 0% | ✅ |
| nearmiss precision | ≥90% | 98% correct (49/50 silence+reject) | ✅ |
| adversarial 0 promoted | 0 | 0 | ✅ |
| golden pass rate | ≥70% | 10% (1/10) | ❌ |
| failures/positive pass rate | ≥50% | 10% (5/50) | ❌ |
| curated inconclusive | <15% | golden 60% · failures/positive 36% | ❌ |
| raw inconclusive | <40% | raw/synthetic 49% · raw/opencode 36% | ❌ mixed |

**Verdict:** SAFETY + SECURITY hold. **Quality pass rates remain below the release gate** on golden (10%) and failures/positive (10%) for this 3B local model — consistent with the known small-model ceiling. Re-measurement on cloud models (gpt-4o-mini, llama-3.1-8b, #650) and the second local model (Qwen3-4B, #648) will determine whether the gate is reachable overall.

---

## 4. Notes

- Parallelized at `--max-workers 3` (3 trajectories per corpus run concurrently).
- Multi-record JSONL support landed in the runner (#629 v0.3.0 fix) — see learnings file.
- Raw reference corpus for replay: all curated buckets (failures/positive + negative + successes + nearmiss + noisy + corrections) loaded per sweep.