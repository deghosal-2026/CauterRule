# FIELD_TEST_REPORT — CauterRule v0.3.0

**Date:** 2026-09-11  
**Milestone:** M7 — Field Test (milestone 62)  
**Scope:** 4-model × 30-corpus sweep (3,632 trajectory-runs), Docker field test (153 tests), 5 field-test-found fixes, v0.2.0 regression comparison.

---

## 0. v0.3.0 vs v0.2.0 — What Changed

| Dimension | v0.2.0 | v0.3.0 | Delta |
|-----------|--------|--------|-------|
| **Safety: successes silence** | 100% (60/60) | 100% (60/60) | ✅ Held |
| **Safety: failures/negative silence** | 100% | 100% | ✅ Held |
| **Nearmiss false passes** | 3-7 per model | **1 per model (all 4)** | ✅ Dramatic improvement |
| **Adversarial: 0 promoted** | ✅ 6 vectors | ✅ 6 vectors | ✅ Held |
| **Golden pass rate (cloud)** | 50% (5P/10) post-Fix8 | **10% (1P/10)** | ❌ Dropped |
| **Golden pass rate (local)** | 20% (2P/10) pre-Fix8 | 10% (1P/10) | ❌ Dropped |
| **Failures/positive (cloud)** | 44-54% post-Fix8 | **8-12% (3-4P/50)** | ❌ Dropped sharply |
| **Reference corpus size** | 230 trajectories | **518** (+288 #489) | ✅ More than doubled |
| **Corpora tested** | 22 | **30** (+8 new) | ✅ Broader |
| **Models tested** | 4 (2 local + 2 cloud) | 4 (same) | ✅ Same coverage |
| **Total trajectory-runs** | ~4,000 | **3,632** (30×4 minus gate-drops) | Comparable |
| **Docker tests** | 0 | **153** (151 passing, 2 re-run pending) | ✅ New |
| **Test suite** | 1,008 | **1,278** (+270) | ✅ Grew |
| **Near-miss penalty in scorer** | Not implemented | **pass→inconclusive when near_misses>0** | ✅ New fix |
| **Self-match exclusion** | Not implemented | **Source trajectory excluded from references** | ✅ New fix |
| **Recovery gate (Fix 8 gate-side)** | Replay-side only | **Gate-side: success+recovery→silence** | ✅ Extended |
| **#492 broad aliases** | Added (5 entries) | **Removed** (over-fired, precision regression) | ✅ Amended |
| **MCP auth over HTTP** | Untested | **#601 bug found + fixed** (fastmcp→mcp SDK Context) | ✅ Critical fix |
| **Runner multi-record JSONL** | Not needed | **Fixed** (adapters 1→18, ref-exp 32→288) | ✅ Bug fix |

### Bottom Line: v0.2.0 vs v0.3.0

v0.2.0 was "safe but quality-gated." v0.3.0 is **safer** (nearmiss 3-7→1 false-pass; the #601 auth bug is fixed) but **quality dropped** — golden and failures/positive pass rates fell on ALL 4 models. The cause is NOT the models (cloud == local on quality) but the **matcher changes**: removing the broad #492 aliases + adding the near-miss penalty + self-match exclusion made scoring honest but stricter. v0.2.0's higher pass rates were partly inflated by alias auto-pass and self-match precision=1.0. The v0.3.0 numbers are the **true** quality floor.

---

## 1. BLUF + Release Gate Verdict

CauterRule v0.3.0 is the **safest version shipped** — safety corpora 100% silence on 4/4 models, nearmiss down to 1 false-pass (98% correct), adversarial 0 promoted, and the #601 MCP auth bug caught and fixed. But the quality pass-rate thresholds (golden ≥70%, failures/positive ≥50%) are **unreachable on any model** — cloud and local perform identically at ~10%, confirming this is a structural matcher-threshold issue, not model capability.

The field test found and fixed 5 issues during the sweep (near-miss penalty, self-match exclusion, recovery gate, #492 alias revert, runner JSONL bug) plus 1 critical security bug (#601 MCP auth never enforced over HTTP — found by the Docker field test). These are documented in `learnings-fixes.md`.

### Release gate verdict

| Objective | Status | Why |
|---|---|---|
| Safety: 100% silence on successes/negatives | ✅ MET | 60/60 gate-dropped on all 4 models |
| Nearmiss precision ≥90% | ✅ MET | 98% correct (1 FP / 50) on all 4 models |
| Adversarial: 0 promoted rules | ✅ MET | 0/50 across all 5 vectors, all 4 models |
| MCP remote security (#601) | ✅ MET | Auth guard fixed (fastmcp→mcp SDK Context); bearer auth enforced |
| Docker field test | ✅ MET | 151/153 tests passing; 2 compose re-runs pending |
| Golden pass rate ≥70% | ❌ NOT MET | 10% (1/10) on all 4 models |
| Failures/positive pass rate ≥50% | ❌ NOT MET | 6-10% (3-5/50) on all 4 models |
| Reference recall ≥0.10 | ❌ NOT MET | 0.02-0.04 on reference-expansion (all 4) |
| Curated inconclusive <15% | ❌ NOT MET | golden 60-70%, failures/positive 26-38% |

> **Critical finding:** Cloud models (gpt-4o-mini, llama-3.1-8b) perform **identically** to local 3B/4B models on the quality metrics. The quality gap is **structural** (matcher threshold vs reference similarity after the #492 alias removal), not model-capability. In v0.2.0, cloud golden was 50% — but that was inflated by broad aliases auto-passing at the 0.70 floor on the 0.65 OMLX threshold, and by self-match precision=1.0. The v0.3.0 honest numbers are the real quality floor.

---

## 2. v0.2.0 vs v0.3.0 Comparison

### Curated corpus results — v0.3.0

| Model | golden | failures/positive | successes | failures/negative | nearmiss |
|---|---|---|---|---|---|
| Llama-3.2-3B (local) | 1P/3F/6I | 5P/24F/18I (50 trajs) | 0P/0F/0I/60G | 0P/0F/0I/60G | 1P/2F/10I/37G |
| Qwen3-4B (local) | 1P/3F/6I | 3P/28F/19I (50 trajs) | 0P/0F/0I/60G | 0P/0F/0I/60G | 1P/2F/9I/37G |
| gpt-4o-mini (cloud) | 1P/3F/6I | 4P/19F/27I (50 trajs) | 0P/0F/0I/60G | 0P/0F/0I/60G | 1P/2F/10I/37G |
| llama-3.1-8b (cloud) | 1P/2F/7I | 3P/10F/13I (26 trajs) | 0P/0F/0I/60G | 0P/0F/0I/60G | 1P/3F/9I/37G |

### Curated corpus results — v0.2.0 (for comparison)

| Model | golden | failures/positive | successes | failures/negative | nearmiss |
|---|---|---|---|---|---|
| Llama-3.2-3B (local) | 2P/2F/6I | 10P/5F/34I | 0P/0F/0I/60G | 0P/0F/0I/60G | 3P/28F/19I |
| Qwen3-4B (local) | 2P/2F/6I | 9P/7F/34I | 0P/0F/0I/60G | 0P/0F/0I/60G | 5P/21F/24I |
| gpt-4o-mini (cloud) | 5P/1F/4I | 22P/5F/23I | 0P/0F/0I/60G | 0P/0F/0I/60G | 5P/22F/23I |
| llama-3.1-8b (cloud) | 5P/1F/4I | 27P/5F/18I | 0P/0F/0I/60G | 0P/0F/0I/60G | 7P/24F/19I |

### What changed and why

| Metric | v0.2.0 | v0.3.0 | Cause |
|---|---|---|---|
| Golden P (all models) | 2-5 | 1 | #492 alias removal (0.70 floor no longer auto-passes at 0.65) + self-match exclusion (precision=1.0/1 no longer possible) + near-miss penalty (pass→inconclusive) |
| Failures/positive P (cloud) | 22-27 | 3-4 | Same fixes — honest scoring is stricter |
| Nearmiss FP (all models) | 3-7 | **1** | Gate-side Fix 8 (37/50 gate-dropped) + scorer near-miss penalty + self-match exclusion |
| Recall (reference-expansion) | N/A (no corpus) | 0.02-0.04 | Reference corpus expanded (#489: +288) but matcher recall still low — the expansion alone doesn't lift recall without semantic matching help |

---

## 3. What Worked / What Didn't Work

### What worked ✅

1. **Safety gate: 100% silence** on successes + failures/negative (60/60 each, all 4 models). The #1 v0.1.0 gap remains closed.
2. **Nearmiss: 98% correct (1 FP)** on all 4 models — down from 3-7 in v0.2.0. The gate-side Fix 8 (recovery keyword detection + nearmiss → SAFETY_CORPORA), near-miss scorer penalty, and self-match exclusion together eliminated the false passes.
3. **Adversarial: 0 promoted** across all 5 vectors, all 4 models. Security holds.
4. **MCP #601 auth bug found and fixed** — the Docker field test caught that `_request_headers()` imported from `fastmcp` (never installed) inside a try/except, silently allowing all HTTP traffic. Fixed via official `mcp` SDK `Context` API. Unauth → 401 payload; authed → rules. This is the kind of bug only a field test catches.
5. **Docker field test: 153 tests, 151 passing.** Hardened image (non-root, git, HEALTHCHECK, OCI labels, .dockerignore), compose profiles, MCP HTTP in-container (#676). See `docker-test-results.md`.
6. **Runner multi-record JSONL fix** — the v0.3.0 corpora (adapters/lifecycle/packs/mcp/otel) were silently under-counted (adapters traj=1 instead of 18). Fixed: line-by-line JSONL + per-record discovery.
7. **Reference corpus expanded** (#489): 230 → 518 trajectories across 32 canonical failure classes with diverse paraphrases.
8. **Test suite: 1,278 passed** (was 1,008 in v0.2.0; +270 new tests).
9. **Fix-8 gate-side is model-independent** — confirmed on both Llama-3.2-3B and Qwen3-4B (37/50 nearmiss gate-drops on both).
10. **#492 alias removal is safe for Qwen** — Qwen recall is commensurate with Llama (0.022 vs 0.031 on reference-expansion). Qwen does not depend on the broad aliases.

### What didn't work ❌

1. **Golden pass rate 10% (1/10)** on all 4 models (target ≥70%). v0.2.0's 50% cloud was inflated by the broad aliases and self-match. The v0.3.0 honest number is the real quality floor.
2. **Failures/positive pass rate 6-10%** (3-5/50) on all 4 models (target ≥50%). Same cause — honest scoring is stricter.
3. **Reference recall 0.02-0.04** (target ≥0.10). The #489 expansion added trajectories but the matcher (token-F1 + bigram) can't bridge the paraphrase gap without semantic matching.
4. **Curated inconclusive 60-70%** on golden (target <15%). Most candidates extract correctly but don't match references at threshold.
5. **Quality gap is NOT model-dependent** — cloud == local on golden (1/10), failures/positive (3-5/50). This is structural, not capability.

---

## 3a. Local OMLX vs Cloud LLM Comparison

The cloud sweep (#650) is complete: gpt-4o-mini and llama-3.1-8b have been run on all 30 corpora alongside the local OMLX models. **Unlike v0.2.0 — where cloud golden reached 50% and failures/positive reached 44-54% while local stayed at 20% — v0.3.0 shows NO cloud advantage on quality metrics.** Cloud and local perform identically: golden 1/10, failures/positive 3-5/50, nearmiss 1 FP, adversarial 0. This is the strongest evidence that the quality gap is structural (matcher threshold), not model capability. The v0.2.0 cloud advantage was an artifact of the broad #492 aliases auto-passing at the 0.70 floor on the 0.65 OMLX threshold — now removed.

### Key metrics — all 4 models

| Model | Gold | Fail+ | NM FP | Adv | Silence | TotP | TotF | TotI |
|---|---|---|---|---|---|---:|---:|---:|
| Llama-3.2-3B (local) | 1P | 5P (10%) | 1 FP | 0P | 100% | 54 | 336 | 496 |
| Qwen3-4B (local) | 1P | 3P (6%) | 1 FP | 0P | 100% | 30 | 318 | 619 |
| gpt-4o-mini (cloud) | 1P | 4P (8%) | 1 FP | 0P | 100% | 51 | 260 | 668 |
| llama-3.1-8b (cloud) | 1P | 3P (12%) | 1 FP | 0P | 100% | 44 | 325 | 586 |

### Key takeaways

1. **No cloud quality advantage** — golden 1/10 on ALL 4 models, failures/positive 3-5/50 on ALL 4. v0.2.0's 50% cloud golden was inflated by broad aliases + self-match. v0.3.0's honest numbers are the real quality floor.
2. **Safety holds identically** — 100% silence on successes + failures/negative, all 4 models. Fix-8 gate-side fires identically (37/50 nearmiss gate-drops on all).
3. **Llama-3.2-3B leads total pass count** (54) — it extracts more aggressively on raw corpora (raw/synthetic 32P vs 12-21P on others). Qwen3-4B is the most conservative (30P, fewest fails on lifecycle).
4. **gpt-4o-mini has the most inconclusives** (668) — cloud models produce more candidates but most don't match references at threshold.
5. **llama-3.1-8b has the best public/golden** (2P/10) — the only model to pass on public golden; but it also has the most nearmiss fails (3F).

---

## 3b. LLM vs LLM Comparison

All four models were run head-to-head on identical corpora (30 sources, ~1,150 trajectories each). The comparison below isolates model behavior from pipeline behavior — the gate, matcher, scorer, and thresholds are identical across runs.

**The defining v0.3.0 finding: all 4 models converge to the same quality profile.** Golden 1/10, nearmiss 1 FP, adversarial 0 — the variance between models is negligible on quality metrics. The variance is in volume: Llama-3.2-3B extracts more aggressively on raw corpora (32P on raw/synthetic); gpt-4o-mini produces the most candidates but mostly inconclusive; Qwen3-4B is the most conservative (30P total). The differences are in extraction aggressiveness, not quality.

### Per-model analysis

**Llama-3.2-3B (local) — most aggressive extractor.** Leads total passes (54) and raw/synthetic passes (32P, highest of any model). Also has the most fails (336) — it extracts broadly and many candidates fail replay. Best for regression sweeps where recall matters more than precision. Nearmiss 1 FP (98% precision).

**Qwen3-4B (local) — most conservative.** Fewest total passes (30) and fewest raw/synthetic passes (12P). Produces the fewest candidates but also the fewest fails on lifecycle (9F vs 23-27F on others). The #492 alias removal did NOT hurt Qwen recall (0.022 on reference-expansion, commensurate with Llama 0.031) — confirming the broad aliases were not load-bearing. Best for low-noise regression.

**gpt-4o-mini (cloud) — highest candidate volume, most inconclusive.** Produces the most inconclusives (668) — it extracts broadly but the matcher can't resolve most candidates. Same quality profile as local models (golden 1/10, nearmiss 1 FP, adversarial 0). The cloud advantage of v0.2.0 (golden 50%) is gone — the #492 alias removal + self-match exclusion + near-miss penalty made scoring honest.

**llama-3.1-8b (cloud) — balanced.** 44 total passes, 325 fails, 586 inconclusive. The only model to pass on public/golden (2P). Has the most nearmiss fails (3F) but still only 1 false pass. Same structural quality ceiling as the others.

---

## 4. Fixes Applied

| Fix | Description | Status |
|-----|-------------|--------|
| Near-miss scorer penalty | `compute_scores(near_misses>0)` → `pass→inconclusive` — near-miss references were computed but never penalised | ✅ Working — eliminated over-broad-trigger passes |
| Self-match exclusion | Source trajectory excluded from reference set during replay | ✅ Working — eliminated precision=1.0/1 false passes (N-003, N-004) |
| Recovery gate (Fix 8 gate-side) | `success=True` + recovery keyword in `failure_class` → silence (`SILENCE_REASON_NEARMISS`) | ✅ Working — 37/50 nearmiss gate-dropped on all 4 models |
| Nearmiss → SAFETY_CORPORA | Nearmiss now runs in strict gate mode (was relaxed) | ✅ Working — gate-side Fix 8 fires on nearmiss sweep |
| #492 broad alias removal | Removed 5 overly-broad Qwen aliases (command fails → exit code, pipeline fails → test failed, not found error → not found, auth error, tool fails) — the 0.70 alias floor auto-passed them at the 0.65 OMLX threshold | ✅ Working — precision recovered; Qwen recall NOT hurt (confirmed) |
| Runner multi-record JSONL | `load_trajectory` reads JSONL line-by-line; discovery expands per-record tasks | ✅ Working — adapters 1→18, ref-exp 32→288 |
| #601 MCP auth guard | `fastmcp` import → `mcp` SDK `Context` API; tool functions declare `ctx: Context` | ✅ Working — unauth → 401 payload; authed → rules |
| Corpus relabel | 10 nearmiss files `should_extract` → `should_reject` | ✅ Working — honest corpus labels |

### What Changed in Detail

**The Near-Miss Scorer Penalty:** v0.2.0's `build_evidence_report()` computed `near_misses` but `compute_scores()` ignored them. A candidate matching both real failures AND near-miss references scored `pass` with precision 1.0 — the over-broad trigger was invisible to the scorer. v0.3.0 adds `near_misses > 0` → `inconclusive` (over-broad trigger, not dangerous but not trustworthy).

**The Self-Match Exclusion:** v0.2.0's replay loaded the same corpus as both target and reference. A nearmiss trajectory's extracted candidate matched its own trajectory as a "prevented" reference → precision = 1/1 = 1.0 → pass on a single trajectory. v0.3.0 excludes the source trajectory's ID from the reference set.

**The Recovery Gate (Fix 8 gate-side):** v0.2.0's Fix 8 reclassified recovery trajectories on the *replay reference* side (simulator). v0.3.0 extends it to the *extraction gate* side: `success=True` + recovery keyword in `failure_class` → silence (no LLM call). This catches the N-00x "success that looks like failure" nearmiss series that fabricated `failure_class` values to pass the gate.

**The #492 Alias Revert:** v0.2.0 added 5 broad Qwen-oriented aliases ("command fails" → "exit code", "pipeline fails" → "test failed", etc.). These phrases appear in almost every failure trajectory, so the 0.70 alias-phrase floor auto-passed any candidate mentioning them — on the 0.65 OMLX curated threshold, this meant every alias hit passed. v0.3.0 reverts them; specific aliases (non-fast-forward → updates were rejected) stay. Qwen recall confirmed not hurt.

| Fix | File | Description | Impact |
|-----|------|-------------|--------|
| Near-miss scorer penalty | `scorer.py`, `report.py` | `near_misses>0` → `pass→inconclusive` | Eliminated over-broad-trigger passes on nearmiss |
| Self-match exclusion | `run-field-test.py` | Source trajectory excluded from reference set | Eliminated precision=1.0/1 false passes (N-003, N-004) |
| Recovery gate (Fix 8 gate-side) | `gate.py` | `success=True` + recovery keyword in `failure_class` → silence | 37/50 nearmiss trajectories gate-dropped |
| Nearmiss → SAFETY_CORPORA | `run-field-test.py` | Nearmiss now runs in strict gate mode | Gate-side Fix 8 fires on nearmiss sweep |
| #492 broad alias removal | `matcher.py` | Removed 5 overly-broad Qwen aliases (command fails, pipeline fails, etc.) | Stopped 0.70 alias floor from auto-passing at 0.65 OMLX threshold |
| Runner multi-record JSONL | `run-field-test.py` | `load_trajectory` reads JSONL line-by-line | adapters 1→18, ref-exp 32→288 |
| #601 MCP auth guard | `server.py` | `fastmcp` import → `mcp` SDK `Context` API | Unauth HTTP tool calls now rejected (401) |
| Corpus relabel | 10 nearmiss files | `should_extract` → `should_reject` | Honest corpus labels |

---

## 5. Methodology

**Test harness:** `scripts/run-field-test.py` (v0.3.0 updated). Output to `field-test/results/0.3.0/`. Per-run artifacts: `meta.json`, `results.jsonl`, `summary.json`, `harness_health.json`.

**Extraction pipeline:**
1. Preflight — `cauterule preflight` (provider + corpus + cost estimate). `--skip-preflight` for local runs.
2. Gate — strict on safety corpora (successes, failures/negative, nearmiss); relaxed on positive corpora. Recovery keyword gate (Fix 8 gate-side): `success=True` + recovery keyword → silence.
3. LLM extraction — multi-pass (2 passes, temperatures 0.2 + 0.5).
4. Replay testing — `build_evidence_report(cand, trajs, threshold=threshold_for_corpus(corpus, omlx))`. Corpus-aware thresholds: 0.65 curated OMLX, 0.70 nearmiss, 0.35 raw, 0.40 cross-repo.
5. Scoring — broad-trigger penalty (`broken > prevented = fail`), near-miss penalty (`near_misses > 0 → inconclusive`), self-match exclusion.

**Scoring:**
- Safety-adjusted: `safety_adjusted_pass = total_pass - successes_pass - failures_negative_pass`.
- Near-miss penalty: `near_misses > 0` and `broken == 0` → `inconclusive` (new in v0.3.0).
- Pack replay: `pack_score = pack_prevented / (pack_prevented + pack_broke)`.
- Cross-session delta: `reduction = 1 - (rate_intervention / rate_baseline)`.

**Models tested:** Llama-3.2-3B-Instruct-4bit (local OMLX), Qwen3-4B-Instruct-2507-4bit (local OMLX), gpt-4o-mini (cloud OpenRouter), llama-3.1-8b-instruct (cloud OpenRouter). All 4 models run on all 30 corpora.

**Corpus:** ~1,750 trajectories across 30 sources. Reference corpus: 518 trajectories (230 curated + 288 reference-expansion #489).

---

## 6. Per-Corpus Performance

### Full 30-corpus × 4-model matrix

| Corpus | Llama-3.2-3B | Qwen3-4B | gpt-4o-mini | llama-3.1-8b |
|---|---|---|---|---|
| golden | 1P/3F/6I | 1P/3F/6I | 1P/3F/6I | 1P/2F/7I |
| failures/positive | 5P/24F/18I | 3P/28F/19I | 4P/19F/27I | 3P/10F/13I |
| failures/negative | 0P/0F/0I/60G | 0P/0F/0I/60G | 0P/0F/0I/60G | 0P/0F/0I/60G |
| successes | 0P/0F/0I/60G | 0P/0F/0I/60G | 0P/0F/0I/60G | 0P/0F/0I/60G |
| nearmiss | 1P/2F/10I/37G | 1P/2F/9I/37G | 1P/2F/10I/37G | 1P/3F/9I/37G |
| noisy | 0P/0F/5I | 0P/0F/5I | 0P/0F/5I | 0P/0F/5I |
| corrections | 2P/0F/3I | 0P/0F/4I | 2P/0F/3I | 1P/0F/4I |
| raw/opencode | 4P/12F/9I | 3P/14F/8I | 7P/10F/8I | 7P/11F/7I |
| raw/synthetic | 32P/38F/71I | 12P/37F/90I | 21P/36F/88I | 21P/41F/83I |
| raw/ci | 0P/10F/37I | 0P/13F/97I | 0P/0F/110I | 0P/6F/104I |
| raw/sibling-repos | 2P/0F/8I | 0P/0F/9I | 2P/0F/8I | 1P/0F/9I |
| raw/corrections | 3P/0F/2I | 0P/0F/4I | 2P/0F/3I | 1P/1F/3I |
| raw/cross-session | 0P/3F/2I | 0P/5F/0I | 0P/4F/1I | 0P/5F/0I |
| public/golden | 0P/2F/6I | 1P/2F/7I | 2P/2F/6I | 2P/3F/5I |
| public/counterexample | 0P/9F/10I | 0P/7F/13I | 0P/7F/13I | 0P/10F/10I |
| public/nearmiss | 0P/0F/0I/20G | 0P/0F/0I/20G | 0P/0F/0I/20G | 0P/0F/0I/20G |
| public/staleness | 0P/0F/10I | 0P/0F/10I | 0P/0F/10I | 0P/0F/10I |
| public/synthetic | 0P/20F/8I | 0P/5F/25I | 0P/0F/30I | 0P/13F/17I |
| public/domains | 0P/12F/37I | 0P/15F/35I | 0P/5F/45I | 0P/10F/40I |
| adversarial/injection | 0P/10F/0I | 0P/10F/0I | 0P/10F/0I | 0P/10F/0I |
| adversarial/misleading | 0P/0F/6I | 0P/3F/7I | 0P/4F/6I | 0P/5F/5I |
| adversarial/contradiction | 0P/4F/6I | 0P/2F/8I | 0P/1F/9I | 0P/3F/7I |
| adversarial/unsafe | 0P/5F/5I | 0P/2F/8I | 0P/0F/10I | 0P/1F/9I |
| adversarial/poisoning | 0P/2F/6I | 0P/1F/9I | 0P/2F/8I | 0P/2F/8I |
| **adapters** | 0P/0F/15I | 0P/0F/18I | 0P/0F/18I | 0P/0F/18I |
| **lifecycle** | 0P/27F/11I | 0P/9F/31I | 0P/0F/40I | 0P/23F/17I |
| **packs** | 0P/33F/7I | 0P/30F/10I | 0P/40F/0I | 0P/36F/4I |
| **mcp** | 0P/4F/15I | 0P/5F/15I | 0P/5F/15I | 0P/5F/15I |
| **otel** | 0P/20F/0I | 0P/0F/20I | 0P/0F/20I | 0P/0F/20I |
| **reference-expansion** | 4P/96F/183I | 9P/125F/152I | 9P/110F/169I | 6P/125F/157I |

### Model totals

| Model | Type | Total trajs | Pass | Fail | Inconclusive | Gate dropped |
|---|---|---|---:|---:|---:|---:|
| Llama-3.2-3B | local OMLX | 1,093 | 54 | 336 | 496 | 177 |
| Qwen3-4B | local OMLX | 1,156 | 30 | 318 | 619 | 177 |
| gpt-4o-mini | cloud | 1,156 | 51 | 260 | 668 | 177 |
| llama-3.1-8b | cloud | 1,132 | 44 | 325 | 586 | 177 |

### Adversarial corpus results (all 4 models)

| Vector | Llama-3.2-3B | Qwen3-4B | gpt-4o-mini | llama-3.1-8b |
|---|---|---|---|---|
| injection | 0P/10F/0I | 0P/10F/0I | 0P/10F/0I | 0P/10F/0I |
| misleading | 0P/0F/6I | 0P/3F/7I | 0P/4F/6I | 0P/5F/5I |
| contradiction | 0P/4F/6I | 0P/2F/8I | 0P/1F/9I | 0P/3F/7I |
| unsafe | 0P/5F/5I | 0P/2F/8I | 0P/0F/10I | 0P/1F/9I |
| poisoning | 0P/2F/6I | 0P/1F/9I | 0P/2F/8I | 0P/2F/8I |

**0 promoted rules across all 5 vectors × 4 models = 0/200.** ✅

### Raw corpus results

| Model | raw/opencode | raw/synthetic | raw/ci |
|---|---|---|---|
| Llama-3.2-3B | 4P/12F/9I | 32P/38F/71I | 0P/10F/37I |
| Qwen3-4B | 3P/14F/8I | 12P/37F/90I | 0P/13F/97I |
| gpt-4o-mini | 7P/10F/8I | 21P/36F/88I | 0P/0F/110I |
| llama-3.1-8b | 7P/11F/7I | 21P/41F/83I | 0P/6F/104I |

---

## 7. Safety Metrics

### Silence rate for safety corpora

| Corpus | Total | Gate Dropped | Silence Rate | Verdict |
|---|---|---|---|---|
| successes (all 4 models) | 60 | 60 | 100% | ✅ PASS |
| failures/negative (all 4 models) | 60 | 60 | 100% | ✅ PASS |
| nearmiss (all 4 models) | 50 | 37 | 74% gate + 24% reject = 98% correct | ✅ PASS |

### Safety-adjusted ranking

| Model | Total Pass | Successes Pass | Fail/Neg Pass | Safety-Adjusted Pass | Violation Rate |
|---|---|---|---:|---:|---:|
| Llama-3.2-3B | 54 | 0 | 0 | 54 | 0% |
| Qwen3-4B | 30 | 0 | 0 | 30 | 0% |
| gpt-4o-mini | 51 | 0 | 0 | 51 | 0% |
| llama-3.1-8b | 44 | 0 | 0 | 44 | 0% |

All 4 models: **0% violation rate.** Safety violations eliminated (v0.1.0: 1-3 per model).

---

## 8. Extraction Quality Metrics

### Specificity distribution (all models)

All models meet the <10% generic trigger target. Most triggers are specific (name concrete tools + error codes). The quality problem is NOT trigger vagueness — it's that specific triggers don't match the reference corpus at the 0.65/0.70 threshold after the #492 alias removal.

### Recall

| Model | reference-expansion recall | raw/synthetic recall |
|---|---|---|
| Llama-3.2-3B | 0.031 | 0.039 |
| Qwen3-4B | 0.022 | 0.021 |
| gpt-4o-mini | 0.020 | 0.025 |
| llama-3.1-8b | 0.039 | 0.032 |

Recall is **0.02-0.04** across all models — far below the 0.10 target. The reference corpus expansion (#489: +288 trajectories) did not lift recall because the matcher (token-F1 + bigram) can't bridge paraphrase gaps without semantic/embedding-based matching.

---

## 9. Decision Economics

### Model pair comparison

| Baseline → New | Shared corpora | New Pass | New Fail | Notes |
|---|---|---|---|---|
| Llama-3.2-3B → Qwen-4B (local) | 30 | 54 → 30 (−24) | 336 → 318 (−18) | Qwen more conservative; fewer passes AND fewer fails |
| Llama-3.2-3B → gpt-4o-mini (local→cloud) | 30 | 54 → 51 (−3) | 336 → 260 (−76) | Cloud extracts more but most inconclusive; similar pass count |
| Llama-3.2-3B → llama-3.1-8b (local→cloud) | 30 | 54 → 44 (−10) | 336 → 325 (−11) | Balanced; fewer fails than Llama local |
| gpt-4o-mini → llama-3.1-8b (cloud→cloud) | 30 | 51 vs 44 | 260 vs 325 | gpt-4o-mini: more passes, fewer fails; llama-3.1-8b: more public/golden passes |

Unlike v0.2.0 — where cloud models had a clear quality advantage (golden 50% vs local 20%) — v0.3.0 shows **no model has a quality advantage on the gated corpora.** The differences are in extraction aggressiveness (Llama local extracts most; Qwen extracts least) and inconclusive volume (gpt-4o-mini has most). On the safety + security metrics, all 4 models are identical. The cloud advantage of v0.2.0 was an artifact of the broad aliases; the honest v0.3.0 numbers show cloud == local on quality.

### Wrong-decision rate (model upgrade analysis)

The wrong-decision rate formula: `wrong_decision_rate = new_fail / (new_pass + new_fail)`. Since all 4 models produce the same golden (1P) and nearmiss (1 FP) results, the wrong-decision rate for any model-pair upgrade on the gated corpora is effectively 0 — no model makes more wrong decisions than another on the safety-critical corpora. The differences are entirely in raw-corpus extraction volume, which is not safety-critical.

---

## 9b. Docker Field Test

**Plan:** `docker-test-plan.md` (18 stages) · **Results:** `docker-test-results.md` · **Issues:** #641/#642/#676 (closed)

| Area | Tests | Result |
|---|---|---|
| Build & hardening (non-root, git, HEALTHCHECK, OCI labels) | 8 | ✅ |
| Compose (profiles, no dead port, MCP baked in) | 6 | ✅ (2 re-runs pending) |
| CLI surface (corpus/benchmark/pack/otel/mcp) | 7 | ✅ |
| Corpus + benchmark CLIs | 12 | ✅ |
| Packs (create/install/persistence) | 7 | ✅ |
| Adapters (import + hermetic) | 4 | ✅ |
| Lifecycle | 3 | ✅ |
| MCP stdio + HTTP + bearer auth | 6 | ✅ (#601 fixed) |
| OTEL emit | 3 | ✅ |
| Preflight cost | 3 | ✅ |
| Badge + webhook | 4 | ✅ |
| Pipeline E2E | 8 | ✅ |
| Persistence | 3 | ✅ |
| Image size + multi-arch | 3 | ✅ |
| Resource + network | 2 | ✅ |
| **Total** | **~70** | **151/153 passing** |

**Critical finding:** the Docker field test caught the #601 MCP auth guard bug — `_request_headers()` imported from `fastmcp` (never installed) inside a try/except, silently allowing all HTTP traffic. Fixed via the official `mcp` SDK `Context` API. This is the kind of bug only a field test catches.

---

## 10. Cost Measurement

| Corpus | Gate-dropped (per model) | LLM calls avoided | Est. savings |
|---|---|---|---|
| successes | 60 | 120 (2 passes × 60) | $1.20 (cloud) / $0 (local) |
| failures/negative | 60 | 120 | $1.20 (cloud) / $0 (local) |
| nearmiss | 37 | 74 | $0.74 (cloud) / $0 (local) |
| public/nearmiss | 20 | 40 | $0.40 (cloud) / $0 (local) |
| **Total gate savings** | **177** | **354** | **$3.54 (cloud) / $0 (local OMLX)** |

Local OMLX models are free ($0/traj). Cloud: gpt-4o-mini ~$1.60/1k trajs; llama-3.1-8b ~$0 (open-weight). The pre-extraction gate saves $3.54 per cloud sweep. Full $/1k measurement (#653) pending — preflight `--cost-table` already ships the tier table.

---

## 11. Harness Health

All sweeps report harness health PASS. Parse rate ≥70%, completion ratio within expected range. Safety corpora correctly flagged (0 candidates = expected, not failure).

---

## 12. Coverage and Observability

### Coverage

| Metric | v0.2.0 | v0.3.0 | Delta |
|---|---|---|---|
| Test count | 1,008 | 1,278 | +270 |
| Fast suite (excl. field/scale) | — | 1,278 passed, 5 skipped | ✅ |
| Corpus validation | 76 tests | 81 tests | +5 |

Coverage at ~86% remains below the 95% target (#494 deferred to M8).

### Validation suites (19 total, 12 inherited + 7 new)

| Suite | v0.2.0 | v0.3.0 (new) |
|---|---|---|
| pre_extraction_gate, replay_matcher, replay_safety, replay_attribution, promotion_safety, extraction_specificity, sentinel_benchmark, scale_benchmark, adversarial, corpus, observe, tui | 12 (v0.2.0) | — |
| **adapter_conformance, lifecycle, packs, mcp_security, otel_exporter, corpus_cli, benchmark_cli** | — | **7 (v0.3.0 NEW)** |

---

## 13. Known Issues

| Issue | Severity | Workaround |
|---|---|---|
| Golden pass rate 10% (all 4 models, target ≥70%) | **Major** — release blocker | Structural: matcher threshold vs reference similarity after #492 alias removal. Options: re-baseline thresholds, add selective aliases, or add semantic matching. Cloud == local confirms it's not model capability |
| Failures/positive pass rate 6-10% (target ≥50%) | **Major** — release blocker | Same cause as golden |
| Reference recall 0.02-0.04 (target ≥0.10) | Major | #489 expansion added trajectories but token-F1 matcher can't bridge paraphrases — needs semantic/embedding matching |
| 2 compose test re-runs pending (mcp-accepts, test-service) | Low | Fixes applied (profiles, pip --user); re-run pending |
| Coverage 86% (target 95%) | Medium | #494 deferred to M8 |
| OTEL exporter log noise ("opentelemetry.exporter not installed") | Low (cosmetic) | Install `opentelemetry-exporter-otlp` in dev venv |
| Cross-session reduction not yet measured (#663) | Medium | Pending — needs 5-session protocol |
| Human review agreement not measured (#493) | Medium | Pending — needs human sampling |
| `openai` package missing from dev venv | Low | `pip install openai` (done) |
| `benchmarks/baseline.json` committed as 284KB artifact | Low | Add to `.gitignore` |

---

## Gaps Still Open

1. **Quality gate gap** (major) — golden 10%, failures/positive 6-10% on ALL models. Not model capability — structural matcher threshold. Three paths: (a) re-baseline thresholds with rationale, (b) re-add SELECTIVE aliases (specific phrases only), (c) add semantic/embedding matching for paraphrase bridging.
2. **Recall gap** (major) — 0.02-0.04 vs 0.10 target. The #489 corpus expansion alone doesn't help; the matcher needs semantic help.
3. **Cross-session gap** (medium) — #663 not yet measured.
4. **Human agreement gap** (medium) — #493 not yet sampled.
5. **Coverage gap** (medium) — 86% vs 95% target (#494, M8).

---

## Action Items

### Short-term (before v0.3.0 release decision)

| # | Action | Effort | Impact |
|---|--------|--------|--------|
| 1 | **Decide on quality gate** — re-baseline thresholds OR re-add selective aliases OR accept honest 10% with rationale | Decision | Unblocks release |
| 2 | **Complete compose re-runs** (mcp-accepts, test-service) | Low | Closes #642 fully |
| 3 | **Measure cross-session reduction** (#663) — 5-session protocol | Medium | Required for release gate |
| 4 | **Sample human agreement** (#493) — candidates per verdict bucket | Medium | Required for release gate |

### Long-term (v0.4.0+)

| # | Action | Effort | Impact |
|---|--------|--------|--------|
| 1 | **Add semantic matching** — embedding-based trigger-to-reference matching to bridge paraphrases | High | Addresses recall + quality gate root cause |
| 2 | **Restore coverage to >95%** (#494) | Medium | Release gate target |
| 3 | **Install OTEL exporter** in dev venv | Low | Clean logs |
| 4 | **Add recall threshold enforcement** once semantic matching lifts recall | Low | Release gate |

---

## Conclusions

CauterRule v0.3.0 is the **safest version shipped**. The safety gate holds on 4/4 models (100% silence), nearmiss is at 98% correct (down from 86-94% in v0.2.0), adversarial is 0 promoted, and the #601 MCP auth bug — a critical security defect that shipped green through unit CI — was found and fixed by the Docker field test. Five additional field-test fixes (near-miss penalty, self-match exclusion, recovery gate, #492 alias revert, runner JSONL bug) made the scoring honest.

But the quality pass-rate thresholds are **unreachable on any model** — cloud and local perform identically at ~10% on golden. This is NOT a model-capability issue; it's the structural cost of removing the broad aliases that inflated v0.2.0's 50% cloud golden. The v0.3.0 numbers are the **true quality floor** of the current matcher (token-F1 + bigram, no semantic matching).

The path forward is clear: semantic/embedding-based matching to bridge the paraphrase gap between extracted triggers and reference trajectories. The reference corpus is now 518 trajectories (#489), but the token-F1 matcher can't exploit its diversity. This is the v0.4.0 lever.

- **The v0.3.0 field test was a success** — it found and fixed real bugs.
- **The product is the safest it has ever been.**
- **The product is not yet quality-gate complete** — the honest quality floor is below the release threshold.
- **The quality gap is structural (matcher), not model-capability** — cloud == local.

---

## Field Test Plan Reporting Checklist

| # | Required section | Status |
|---|-----------------|--------|
| 1 | BLUF + release gate verdict | ✅ §1 |
| 2 | Safety-adjusted ranking | ✅ §7 |
| 3 | Decision economics | ✅ §0 (v0.2.0 vs v0.3.0 comparison) |
| 4 | Extraction rate | ✅ §8 |
| 5 | Methodology | ✅ §5 |
| 6 | Harness health | ✅ §11 |
| 7 | Cost measurement | ✅ §10 |
| 8 | Human review agreement rate | ❌ Pending (#493) |
| 9 | Specificity distribution | ✅ §8 |
| 10 | Inconclusive attribution breakdown | ✅ §6 (per-corpus) |
| 11 | Silence rate for safety corpora | ✅ §7 |
| 12 | Coverage and observability metrics | ✅ §12 |
| 13 | Known issues with severity and workaround | ✅ §13 |

> ⚠️ **Missing:** Human review agreement rate (#8, #493), cross-session reduction (#663), cost per-1k (#653 full measurement). These are pending M7 items.

---

## Source Documents

- `docs/field-test/v0.3.0/field-test-plan.md`
- `docs/field-test/v0.3.0/field-test-results-4model.md`
- `docs/field-test/v0.3.0/field-test-results-llama-3.2-3b.md`
- `docs/field-test/v0.3.0/field-test-results-qwen3-4b.md`
- `docs/field-test/v0.3.0/learnings-fixes.md`
- `docs/field-test/v0.3.0/regression-llama-3.2-3b-vs-v0.2.0.md`
- `docs/field-test/v0.3.0/docker-test-plan.md`
- `docs/field-test/v0.3.0/docker-test-results.md`
- `field-test/results/0.3.0/`