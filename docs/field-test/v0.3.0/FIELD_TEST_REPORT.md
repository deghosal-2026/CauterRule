# FIELD_TEST_REPORT — CauterRule v0.3.0

**Date:** 2026-09-12
**Milestone:** M7 — Field Test (milestone 62)
**Scope:** 2 cloud OpenRouter models × 40 corpora = 4,768 trajectory-runs (gpt-4o-mini + llama-3.1-8b). Local OMLX models abandoned (#713 — too slow / hung on `raw/ci`).
**Authoritative tables:** [`generated-results.md`](generated-results.md) (auto-generated from raw `results.jsonl`).
**Per-model:** [`field-test-results-gpt-4o-mini.md`](field-test-results-gpt-4o-mini.md) · [`field-test-results-llama-3.1-8b.md`](field-test-results-llama-3.1-8b.md) · [`field-test-results-cloud.md`](field-test-results-cloud.md) (2-model comparison).

---

## 1. BLUF + Release Gate Verdict

CauterRule v0.3.0 is **safer on nearmiss and broader in coverage than v0.2.0**, but it has **regressed on extraction quality and introduced a new adversarial promotion regression on cloud models**. It is **not ready for autonomous rule promotion**.

The single most important improvement in v0.3.0 is the **nearmiss precision fix**. v0.2.0 produced 5–7 false passes per cloud model on nearmiss (86–90% precision). v0.3.0's near-miss penalty + recovery gate + self-match exclusion reduced that to **1 false pass (98% precision)** on both cloud models — the safety-correct outcome.

The second improvement is the **domain-scoped reference pool (#708)**. v0.2.0 tested candidates against the full 230-trajectory reference pool, making recall near-zero. v0.3.0 scopes to same-domain references (444 total, ~20–50 per domain), lifting recall from ~0.03 to ~0.07–0.10 on cloud. Golden pass rate on local OMLX improved 10%→40% after the fix; cloud shows 30–40%.

The third is the **#601 MCP auth bug fix**. The Docker field test caught that the HTTP auth guard was never enforced (imported `fastmcp.server.dependencies` — a package not installed — inside a blanket `try/except` that silently returned `{}`). Fixed by switching to the official `mcp` SDK `Context` API. Unit tests passed; deployment was broken.

But the product still struggles where trust matters most: **golden pass rate is 30–40%** (target ≥70%), **failures/positive is 6–8%** (target ≥50%), **inconclusive is ~90%**, and **adversarial corpora now produce 2–4 promotions** (v0.2.0 had 0).

### Release gate verdict

| Objective | Status | Why |
|---|---|---|
| Safety: 100% silence on successes/negatives | ✅ MET | Gate drops all clean trajectories (60/60 successes, 60/60 failures-negative) |
| Nearmiss precision ≥90% | ✅ MET | 98% (1 FP / 50) on both cloud models — v0.2.0 was 86–90% |
| Generic triggers <10% | ✅ MET | 0.7% (16 generic out of 2,384) |
| Adversarial: 0 promoted rules | ❌ NOT MET | gpt-4o-mini 2, llama-3.1-8b 4 — v0.2.0 had 0 |
| Golden pass rate ≥70% | ❌ NOT MET | gpt-4o-mini 30% (3/10), llama-3.1-8b 40% (4/10) — v0.2.0 was 50% |
| Failures/positive pass rate ≥50% | ❌ NOT MET | gpt-4o-mini 8% (4/50), llama-3.1-8b 6% (3/50) — v0.2.0 was 44–54% |
| Curated inconclusive <15% | ❌ NOT MET | ~80–90% — v0.2.0 was 23–40% |
| Infrastructure: preflight, harness, cost tracking | ✅ MET | All built and verified; cost corpus (1,000 trajs) ran on both cloud models |

### v0.2.0 gap closure

| v0.2.0 gap | v0.3.0 status | Evidence |
|---|---|---|
| Nearmiss "wrong failure" FPs | ✅ CLOSED | 5–7 FPs → 1 FP (98% precision); near-miss penalty + self-match exclusion + recovery gate |
| Reference corpus too small (230) | ✅ CLOSED | Expanded to 444 + domain-scoped (#708, #698–#706) |
| MCP auth untested over HTTP | ✅ CLOSED | #601 bug found + fixed (Docker field test) |
| Corpus coverage narrow (22 corpora) | ✅ CLOSED | 40 corpora (+18 new: adapters, lifecycle, packs, mcp, otel, cost, browser, bugsinpy, lifecycle_infra, reference-expansion, adversarial vectors) |
| Golden pass rate ≥70% | ❌ NOT MET | 30–40% — structural matcher/threshold issue |
| Failures/positive ≥50% | ❌ NOT MET | 6–8% — same root cause; #492 alias removal made scoring honest but stricter |
| Adversarial 0 promoted | ❌ REGRESSED | 2–4 promotions on cloud — new regression, gate does not silence adversarial corpora |
| Cross-session reduction ≥50% | ⚠️ TOOLING READY | `scripts/cross_session.py` + runner `--cross-session`; 5-session protocol not yet run |
| Human agreement | ⚠️ TOOLING READY | `scripts/human_agreement.py` + runner `--human-review`; reviewer scoring not yet done |

---

## 2. v0.2.0 vs v0.3.0 Comparison

### Is v0.3.0 better than v0.2.0? Mixed.

| Dimension | v0.2.0 (cloud) | v0.3.0 (cloud) | Better? |
|-----------|----------------|----------------|---------|
| Safety: successes silence | 100% (60/60) | 100% (60/60) | ✅ Held |
| Safety: failures/negative silence | 100% (60/60) | 100% (60/60) | ✅ Held |
| Nearmiss precision | 86–90% (5–7 FPs) | **98% (1 FP)** | ✅ Dramatically improved |
| Nearmiss gate-dropped | 0 | 27/50 (recovery detection) | ✅ New |
| Adversarial: 0 promoted | 0 (5 corpora) | **2–4** (10 corpora) | ❌ **Regression** |
| Golden pass rate | 50% (5/10) | 30–40% (3–4/10) | ❌ Dropped |
| Failures/positive pass rate | 44–54% (22–27/50) | 6–8% (3–4/50) | ❌ Dropped sharply |
| Inconclusive rate (curated) | 23–40% | ~80–90% | ❌ Doubled |
| Trigger specificity (generic) | 0–5.6% | 0.7% | ✅ Improved |
| Reference corpus | 230 | 444 (+ domain-scoped) | ✅ Near-doubled |
| Corpora tested | 22 | 40 | ✅ Broader |
| Trajectory-runs per model | ~750 | 2,384 | ✅ 3× larger |
| Docker validation | None | 159 tests (157 pass) | ✅ New |
| MCP auth over HTTP | Untested | Bug found + fixed | ✅ Critical |
| Cost corpus (1k) | None | Ran on both cloud models | ✅ New |
| Measurement tooling | None | 5 scripts + 7 runner flags | ✅ New |
| raw/opencode passes | 7–12 | 7–10 | ≈ Flat |
| raw/synthetic passes | 20–37 | 22–24 | ❌ Dropped |

### Curated corpus results — v0.3.0 (cloud)

| Model | golden | failures/positive | successes | failures/negative | nearmiss |
|---|---|---|---|---|---|
| gpt-4o-mini | 3P / 0F / 7I | 4P / 6F / 40I | 0P / 0F / 0I / 60G | 0P / 0F / 0I / 60G | 1P / 3F / 19I / 27G |
| llama-3.1-8b | 4P / 0F / 6I | 3P / 7F / 40I | 0P / 0F / 0I / 60G | 0P / 0F / 0I / 60G | 1P / 1F / 21I / 27G |

### Curated corpus results — v0.2.0 (cloud, post-Fix8)

| Model | golden | failures/positive | successes | failures/negative | nearmiss |
|---|---|---|---|---|---|
| gpt-4o-mini | 5P / 1F / 4I | 22P / 5F / 23I | 0P / 0F / 0I / 60G | 0P / 0F / 0I / 100G | 5P / 22F / 23I |
| llama-3.1-8b | 5P / 1F / 4I | 27P / 5F / 18I | 0P / 0F / 0I / 60G | 0P / 0F / 0I / 100G | 7P / 24F / 19I |

### What changed from v0.2.0 to v0.3.0

| Dimension | v0.2.0 | v0.3.0 | Delta |
|---|---|---|---|
| Corpora | 22 | 40 | +18 new |
| Trajectory-runs per model | ~750 | 2,384 | +1,634 |
| Reference corpus | 230 | 444 | +214 |
| Nearmiss FPs (cloud) | 5–7 | 1 | ✅ -4–6 |
| Adversarial promotions | 0 | 2–4 | ❌ New regression |
| Golden pass rate (cloud) | 50% | 30–40% | ❌ -10–20pp |
| Failures/positive (cloud) | 44–54% | 6–8% | ❌ -36–48pp |
| Inconclusive rate | 23–40% | ~90% | ❌ +50–67pp |
| Docker tests | 0 | 159 (157 pass) | ✅ New |
| #492 broad aliases | Added (5) | Removed | ✅ Honest scoring |
| Near-miss penalty | Not implemented | pass→inconclusive when near_misses>0 | ✅ New |
| Self-match exclusion | Not implemented | Source trajectory excluded from references | ✅ New |
| Recovery gate (Fix 8 gate-side) | Replay-side only | Gate-side: success+recovery→silence | ✅ Extended |
| MCP auth over HTTP | Untested | #601 bug found + fixed | ✅ Critical |
| Domain-scoped references | No | Yes (#708) | ✅ New |
| Semantic matching | None | Opt-in (#689, `[matching]` extra) | ✅ New (off by default) |
| Measurement scripts | None | 5 scripts + 7 runner flags | ✅ New |
| Runner per-trajectory timeout | None | 120s default (#713) | ✅ New |
| Runner quarantine | None | `CAUTERULE_QUARANTINE_IDS` env | ✅ New |

---

## 3. What Worked / What Didn't Work

### What worked ✅

1. **Safety gate: 100% silence** on successes (60/60) and failures/negative (60/60) — held from v0.2.0. 580 gate-dropped, 1,160 LLM calls avoided per model.
2. **Nearmiss precision: 98%** (1 FP / 50) on both cloud models — v0.2.0 was 86–90%. The near-miss penalty + recovery gate + self-match exclusion are the biggest safety improvement in v0.3.0.
3. **Recovery gate (#709):** clean successes (`success=True`, no failure signals) are now silenced even in relaxed mode — fixed the otel corpus (20/20 gate-dropped, was 0P/20F).
4. **Domain-scoped references (#708):** candidates are tested against same-domain references, not the full 444-pool. Verified to lift recall 7× on local (0.032→0.242); cloud shows 0.068–0.104.
5. **#601 MCP auth bug caught + fixed:** the Docker field test found the HTTP auth guard was never enforced. Fixed via `mcp` SDK `Context` API.
6. **Docker field test: 157/159 pass** — hardened image, compose profiles, MCP HTTP + bearer auth, OTEL, preflight cost, badge/webhook, persistence, multi-arch.
7. **Corpus expansion: 40 corpora** (was 22) — adapters, lifecycle, packs, mcp, otel, cost (1,000), browser, bugsinpy, lifecycle_infra, reference-expansion (303), 5 new adversarial vectors.
8. **Reference corpus: 444 trajectories** (was 230) — +214 from #698–#706 (adapters, lifecycle, mcp, otel, browser, bugsinpy, lifecycle_infra, successes).
9. **Measurement tooling:** 5 scripts (`measure_cost`, `cross_session`, `human_agreement`, `pack_replay`, `fix8_recovery`) + 7 runner block flags. Pack replay: 4/4 packs score 1.00. Fix-8 recovery exclusion: 0.671.
10. **Specificity: 0.7% generic** (16/2,384) — well under 10% target.
11. **public/real-world/bugsinpy: 28–29/36 pass (78–81%)** — strongest positive signal; real-world python test failures extract well.
12. **public/browser: 12–16/20 pass (60–80%)** — browser-automation failures extract well.
13. **Token usage capture:** `LLMResponse` now carries `prompt_tokens`/`completion_tokens` from the OpenAI provider — enables real cost measurement.

### What didn't work ❌

1. **Adversarial promotion: 2–4 passes** (v0.2.0 had 0). gpt-4o-mini: 2 (injection). llama-3.1-8b: 4 (injection ×2, compounding multi-turn, unsafe). The gate does not silence adversarial corpora (not in `SAFETY_CORPORA`). **Release blocker.**
2. **Golden pass rate 30–40%** (target ≥70%). v0.2.0 was 50%. The #492 alias removal made scoring honest but stricter; the domain-scoping helped but the token-F1 matcher still can't bridge paraphrases.
3. **Failures/positive pass rate 6–8%** (target ≥50%). v0.2.0 was 44–54%. Same root cause — the scorer's pass threshold (precision ≥0.8) is rarely reached because candidates match few references.
4. **Inconclusive rate ~90%.** v0.2.0 was 23–40%. Candidates reach `match_score()` (per `corpus-diagnostics.md`) but match 0–1 references → `prevented=0, broken=0` → inconclusive. The token-F1 matcher cannot bridge the paraphrase gap between LLM-extracted triggers and reference phrasings.
5. **Adapters 100% inconclusive** (0P/0F/60I on both models). 93 candidates scored, 0 decided. Pure matcher paralysis.
6. **raw/ci 0 passes** (was 7 on gpt-4o-mini in v0.2.0). 110 trajectories, all inconclusive. CI traceback-heavy prompts produce triggers the matcher can't match.
7. **Cost corpus: 667 inconclusive, 333 gate-dropped, 0 pass.** The 1,000-trajectory mixed sample produced no useful candidates — the matcher issue is systemic.
8. **Semantic matching (#689) has no effect.** `sentence-transformers` is not installed (the `[matching]` extra). Enabling `CAUTERULE_SEMANTIC_MATCHING=1` silently no-ops. Fixed to warn (#710), but the feature cannot be evaluated without installing the dependency.
9. **Cross-session / human-agreement not measured.** Tooling is complete but the 5-session protocol and reviewer scoring have not been run.

---

## 3a. Cloud Model Comparison (gpt-4o-mini vs llama-3.1-8b)

Both cloud models were run head-to-head on identical corpora (40 sources, 2,384 trajectories each). The gate, matcher, scorer, and thresholds are identical across runs.

### Key metrics — both cloud models

| Metric | gpt-4o-mini | llama-3.1-8b |
|---|---|---|
| Total trajectories | 2,384 | 2,384 |
| Total pass | 116 | 119 |
| Total fail | 65 | 72 |
| Total inconclusive | 1,623 (90%) | 1,613 (89%) |
| Gate-dropped | 580 | 580 |
| LLM calls avoided | 1,160 | 1,160 |
| Golden pass | 3/10 (30%) | 4/10 (40%) |
| Failures/positive pass | 4/50 (8%) | 3/50 (6%) |
| Nearmiss FP | 1 (98%) | 1 (98%) |
| Adversarial promotions | **2** | **4** |
| Avg precision (scored) | 0.149 | 0.192 |
| Avg recall (scored) | 0.068 | 0.104 |
| Generic triggers | 16 (0.7%) | 16 (0.7%) |
| public/browser | 12/20 (60%) | 16/20 (80%) |
| public/real-world/bugsinpy | 29/36 (81%) | 28/36 (78%) |

### Key takeaways

1. **llama-3.1-8b extracts more** (higher recall 0.104 vs 0.068, more passes 119 vs 116, more candidates) but is **more susceptible to adversarial promotion** (4 vs 2). The stronger model is not the safer model.
2. **gpt-4o-mini is the safety-first choice** — fewer adversarial promotions (2), fewer fails (65 vs 72), comparable nearmiss precision.
3. **Both models are identical on safety corpora** — 100% silence on successes/failures-negative, 98% nearmiss precision. The gate is model-independent.
4. **The 90% inconclusive rate is model-independent** — both models produce candidates that reach scoring but match too few references. This is a matcher/threshold issue, not a model capability issue.
5. **public/real-world/bugsinpy is the strongest signal** — 78–81% pass rate on both models. Real-world python test failures extract and replay well.

---

## 3b. LLM vs LLM Comparison

### Full results matrix (all 40 corpora)

| Corpus | gpt-4o-mini | llama-3.1-8b |
|---|---|---|
| golden | 3P/0F/7I/0G | 4P/0F/6I/0G |
| failures/positive | 4P/6F/40I/0G | 3P/7F/40I/0G |
| failures/negative | 0P/0F/0I/60G | 0P/0F/0I/60G |
| successes | 0P/0F/0I/60G | 0P/0F/0I/60G |
| nearmiss | 1P/3F/19I/27G | 1P/1F/21I/27G |
| noisy | 2P/0F/3I/0G | 2P/0F/3I/0G |
| corrections | 2P/0F/3I/0G | 2P/0F/3I/0G |
| raw/opencode | 10P/1F/14I/0G | 7P/1F/17I/0G |
| raw/synthetic | 22P/15F/108I/0G | 24P/12F/109I/0G |
| raw/ci | 0P/0F/110I/0G | 0P/1F/109I/0G |
| raw/sibling-repos | 0P/0F/10I/0G | 0P/0F/10I/0G |
| raw/corrections | 2P/0F/3I/0G | 2P/0F/3I/0G |
| raw/cross-session | 0P/1F/4I/0G | 0P/0F/5I/0G |
| public/golden | 3P/1F/6I/0G | 3P/0F/7I/0G |
| public/counterexample | 0P/0F/0I/20G | 0P/0F/0I/20G |
| public/nearmiss | 0P/0F/0I/20G | 0P/0F/0I/20G |
| public/staleness | 0P/0F/10I/0G | 0P/0F/10I/0G |
| public/synthetic | 0P/0F/10I/20G | 0P/0F/10I/20G |
| public/domains | 0P/0F/30I/20G | 0P/0F/30I/20G |
| public/browser | 12P/0F/8I/0G | 16P/0F/4I/0G |
| public/real-world/bugsinpy | 29P/0F/7I/0G | 28P/0F/8I/0G |
| public/lifecycle_infra | 1P/0F/19I/0G | 0P/0F/20I/0G |
| adversarial/injection | **2P**/6F/2I/0G | **2P**/6F/2I/0G |
| adversarial/misleading | 0P/2F/8I/0G | 0P/2F/8I/0G |
| adversarial/contradiction | 0P/0F/10I/0G | 0P/1F/9I/0G |
| adversarial/unsafe | 0P/0F/10I/0G | **1P**/0F/9I/0G |
| adversarial/poisoning | 0P/0F/10I/0G | 0P/0F/10I/0G |
| adversarial/tool_output_injection | 0P/0F/20I/0G | 0P/0F/20I/0G |
| adversarial/compounding_multiturn | 0P/0F/10I/0G | **1P**/0F/9I/0G |
| adversarial/unsafe_realistic | 0P/0F/20I/0G | 0P/0F/20I/0G |
| adversarial/misleading_harmbench | 0P/0F/15I/0G | 0P/0F/15I/0G |
| adversarial/contradiction_harmbench | 0P/0F/15I/0G | 0P/0F/15I/0G |
| adapters | 0P/0F/60I/0G | 0P/0F/60I/0G |
| lifecycle | 0P/0F/40I/0G | 0P/10F/30I/0G |
| packs | 0P/10F/30I/0G | 1P/7F/32I/0G |
| mcp | 0P/5F/15I/0G | 0P/5F/15I/0G |
| otel | 0P/0F/0I/20G | 0P/0F/0I/20G |
| cost | 0P/0F/667I/333G | 0P/0F/667I/333G |
| reference-expansion | 19P/12F/272I/0G | 19P/17F/267I/0G |
| reference-expansion/paraphrase-diversity | 4P/3F/8I/0G | 3P/2F/10I/0G |

### Per-model analysis

**gpt-4o-mini — safety-first choice.** Fewer adversarial promotions (2 vs 4), fewer fails (65 vs 72), comparable nearmiss precision (98%). Golden 30% (3/10), failures/positive 8% (4/50). Strongest on public/real-world/bugsinpy (29/36, 81%). The clear choice for a safety-first release gate.

**llama-3.1-8b — extraction-first choice.** Higher recall (0.104 vs 0.068), more passes (119 vs 116), golden 40% (4/10). But 4 adversarial promotions (injection ×2, compounding multi-turn, unsafe) — the stronger model extracts more convincing-looking candidates from adversarial trajectories. Better for extraction coverage where adversarial filtering is handled separately.

---

## 4. Fixes Applied

| Fix | Description | Status |
|-----|-------------|--------|
| #708 | Domain-scope reference pool — `replay_test_candidate` scopes to same-domain refs (≥3, else full pool) | ✅ Recall 7× on local; cloud 0.068–0.104 |
| #709 | Relaxed gate silences clean successes — `success=True` + no failure signals → silence even in relaxed mode | ✅ otel 0P/20F → 20/20 gate-dropped |
| #710 | Semantic matching warns when `[matching]` extra missing — was silently no-op | ✅ Warning logged |
| #692 | Recovery-keyword whole-token match — prevents substring false-positive silencing | ✅ Working |
| #693 | `_step_shows_success` checks exit_code before output — error text in output no longer treated as success | ✅ Working |
| #694 | `check_domain_mismatch` wired into `rule_matches` — failure trajectories only | ✅ Working |
| #677 | Domain-aware context matching — matcher context matches trajectory `domain` field | ✅ Calibration golden recall 0.50→0.90 |
| #601 | MCP auth guard fixed — `fastmcp` → `mcp` SDK `Context` API | ✅ Critical security fix |
| Near-miss penalty | `pass→inconclusive` when `near_misses>0` | ✅ Nearmiss 5–7 FP → 1 FP |
| Self-match exclusion | Source trajectory excluded from references | ✅ Eliminated precision=1.0 self-match inflation |
| #492 alias removal | 5 broad aliases removed | ✅ Honest scoring (pass rates dropped but are real) |
| Runner multi-record JSONL | `load_trajectory` reads multi-record `.jsonl` | ✅ adapters 1→60, ref-exp 32→303 |
| Runner per-trajectory timeout | `future.result(timeout=120)` + `shutdown(wait=False)` | ✅ #713 raw/ci hang fixed |
| Runner quarantine | `CAUTERULE_QUARANTINE_IDS` env skips trajectories | ✅ #713 |
| Token usage capture | `LLMResponse.prompt_tokens`/`completion_tokens` from OpenAI provider | ✅ Enables real cost measurement |

### What Changed in Detail

**The Domain-Scoped Reference Pool (#708):** v0.2.0 tested every candidate against the full 230-trajectory reference pool. With 200 failures in the pool, a candidate that prevented 3 failures got `recall = 3/200 = 0.015` — near zero on every corpus. v0.3.0 scopes `reference_trajs` to the source trajectory's domain (e.g., `git` → 19 refs, `python` → 30 refs, `docker` → 30 refs), reducing the denominator to ~10–30 relevant failures. Recall improved from ~0.03 to ~0.07–0.10 on cloud; on local OMLX it improved 0.032→0.242 (7×). The fix falls back to the full pool when the domain slice is < 3 references. This is the single most impactful code change in v0.3.0 — it addresses the root cause of the 90% inconclusive rate.

**The Near-Miss Penalty + Self-Match Exclusion:** v0.2.0's nearmiss corpus produced 5–7 false passes per cloud model because: (1) candidates matched near-miss references (recovered failures) but the scorer didn't penalize this, and (2) a trajectory counted itself as a "prevented" failure (self-match), inflating precision to 1.0. v0.3.0 adds: (a) `near_misses > 0 → pass→inconclusive` in the scorer, (b) the source trajectory's ID is excluded from the reference set, (c) the gate detects recovery patterns (`success=True` + early error + later success → silence). Combined effect: nearmiss false passes dropped from 5–7 to 1 (98% precision). The remaining 1 false pass is an irreducible "wrong failure" scenario (pandas import — the rule genuinely prevents 6 real python-import failures).

**The #492 Broad-Alias Removal:** v0.2.0 added 5 broad aliases (SSL, DNS/NXDOMAIN, npm, network, cache) that auto-matched triggers without real token-F1 scoring. This inflated golden (50%) and failures/positive (44–54%) pass rates. v0.3.0 removed them — scoring is now honest. The pass-rate drop (golden 50%→30–40%, failures/positive 44–54%→6–8%) is partly real (the aliases were gaming) and partly a collateral precision cost (some legitimate matches lost the alias boost). The domain-scoping fix (#708) partially compensates.

**The Relaxed-Gate Clean-Success Fix (#709):** v0.2.0's relaxed gate always returned `should_extract=True` — even for clean successes (`success=True`, no failure signals). The otel corpus (20 success trajectories with `expected_outcome="should_silence"`) was extracted and every candidate broke reference successes → 0P/20F. v0.3.0 silences clean successes even in relaxed mode (`success=True AND not signals → silence`). otel is now 20/20 gate-dropped. Failures without signals still proceed (relaxed mode stays permissive for raw corpora).

**The MCP Auth Bug Fix (#601):** The Docker field test found that `_request_headers()` in `src/cauterule/mcp/server.py` imported `fastmcp.server.dependencies` — a package that is not (and never was) installed — inside a blanket `try/except Exception: return {}`. The guard then treated every HTTP request as stdio (local transport) and allowed it through. An unauthenticated `list_rules` call from outside the container returned the full rule list. Unit tests passed because they monkeypatched `_request_headers` directly. Fixed by switching to the official `mcp` SDK `Context` API (tool functions declare `ctx: Context`; headers come from `ctx.request_context.request`). Post-fix, unauthenticated tool calls receive the structured `{"status": 401}` rejection and authenticated calls succeed.

**The Runner Hardening (#713):** v0.2.0's runner used `as_completed(futures)` with no timeout — a single hung LLM call (e.g., OMLX on `raw/ci` ci-fail-015) blocked the whole corpus. v0.3.0 adds: (a) `future.result(timeout=120)` per trajectory — hung workers are recorded as `timeout` and the sweep continues, (b) `executor.shutdown(wait=False, cancel_futures=True)` — the process doesn't wait for stuck threads on exit, (c) `CAUTERULE_QUARANTINE_IDS` env — skip specific trajectories by ID, (d) `max_tokens=4096` on `chat.completions.create()` — prevents OMLX from generating infinitely, (e) timeouts are non-retryable in `_is_transient()` — a timeout means the prompt triggers pathological generation, not a transient server issue.

---

## 5. Methodology

**Test harness:** `scripts/run-field-test.py` — single corpus or `--all`. Output to `field-test/results/0.3.0/`. Per-run artifacts: `meta.json`, `results.jsonl`, `summary.json`, `harness_health.json`.

**Extraction pipeline:**
1. Preflight — `run_preflight(config, corpus_path, cost_per_request_usd)` validates provider + corpus + cost. Abort on FAIL. `--skip-preflight` for sweeps.
2. Gate — `run_gate(trajectory, mode)` per trajectory: strict (safety corpora: drop if no signal), relaxed (positive corpora: proceed, but silence clean successes #709). Dropped trajectories tracked as `gate_dropped`, LLM calls avoided counted.
3. LLM extraction — multi-pass (default 2 passes, temperatures 0.2 + 0.5). `max_tokens=4096`, `timeout=30` on `chat.completions.create()`.
4. Replay testing — `build_evidence_report(cand, domain_scoped_refs, threshold=threshold_for_corpus(corpus))`. Domain-scoped references (#708): same-domain refs (≥3, else full pool). Corpus-type-aware thresholds: 0.70 curated, 0.60 public, 0.45 raw, 0.40 cross-repo.
5. Broad-trigger penalty — `broken > prevented = fail`, `broken ≤ prevented = inconclusive`, `broken == 0 = pass` (if precision ≥0.8).
6. Near-miss penalty — `near_misses > 0 → pass→inconclusive`.
7. Specificity scoring — `score_specificity(trigger)`: specific/moderate/generic. Generic <10% target.
8. Inconclusive attribution — `attribute_inconclusive()`: broad_trigger / matcher_gap / corpus_mismatch / ambiguous_evidence.

**Scoring:**
- Safety scoring: `silence → pass`, any extraction → fail. `safety_summary()` returns `silence_rate` and verdict.
- Safety-adjusted ranking: `safety_adjusted_pass = total_pass - successes_pass - failures_negative_pass`.
- Decision economics: `wrong_decision_rate = new_fail / (new_pass + new_fail)` for model-pair upgrade.
- Confidence intervals: Wilson CI on `pass_rate` and `safety_silence_rate` (`src/cauterule/stats.py`, #695).
- Gate-drop by reason: `gate_dropped_by_reason` in `summary.json` (#697).

**Models tested:** gpt-4o-mini (cloud OpenRouter), llama-3.1-8b-instruct (cloud OpenRouter). Both run on all 40 corpora. Local OMLX models abandoned (#713).

**Corpus:** 2,384 trajectories per model across 40 sources. Reference corpus: 444 trajectories (domain-scoped per run).

---

## 6. Per-Corpus Performance

### gpt-4o-mini (v0.3.0)

| Corpus | Trajs | Candidates | Pass | Fail | Inconclusive | Gate | Notes |
|---|---|---|---|---|---|---|---|
| golden | 10 | 20 | 3 | 0 | 7 | 0 | 30% pass; 4 matcher_gap, 10 ambiguous_evidence |
| failures/positive | 50 | 100 | 4 | 6 | 40 | 0 | 8% pass; 22 matcher_gap, 58 ambiguous_evidence |
| successes | 60 | 0 | 0 | 0 | 0 | 60 | 100% silence ✅ |
| failures/negative | 60 | 0 | 0 | 0 | 0 | 60 | 100% silence ✅ |
| nearmiss | 50 | 46 | 1 | 3 | 19 | 27 | 98% precision ✅; 27 recovery gate-drops |
| noisy | 5 | 10 | 2 | 0 | 3 | 0 | 40% pass |
| corrections | 5 | 10 | 2 | 0 | 3 | 0 | 40% pass |
| public/golden | 10 | 20 | 3 | 1 | 6 | 0 | 30% pass |
| public/browser | 20 | 40 | 12 | 0 | 8 | 0 | 60% pass ✅ strongest; prec 0.850 |
| public/real-world/bugsinpy | 36 | 72 | 29 | 0 | 7 | 0 | 81% pass ✅ strongest; prec 0.806 |
| public/lifecycle_infra | 20 | 40 | 1 | 0 | 19 | 0 | 5% pass |
| public/counterexample | 20 | 0 | 0 | 0 | 0 | 20 | 100% gate-dropped ✅ |
| public/nearmiss | 20 | 0 | 0 | 0 | 0 | 20 | 100% gate-dropped ✅ |
| public/synthetic | 30 | 20 | 0 | 0 | 10 | 20 | 0% pass; 20 gate-dropped |
| public/domains | 50 | 60 | 0 | 0 | 30 | 20 | 0% pass; 20 gate-dropped |
| public/staleness | 10 | 20 | 0 | 0 | 10 | 0 | 0% pass |
| adapters | 60 | 120 | 0 | 0 | 60 | 0 | 100% inconclusive ❌; 120 matcher_gap |
| lifecycle | 40 | 80 | 0 | 0 | 40 | 0 | 100% inconclusive ❌; 80 matcher_gap |
| packs | 40 | 80 | 0 | 10 | 30 | 0 | 0% pass; 60 ambiguous_evidence |
| mcp | 20 | 40 | 0 | 5 | 15 | 0 | 0% pass; 30 matcher_gap |
| otel | 20 | 0 | 0 | 0 | 0 | 20 | 100% gate-dropped ✅ (#709) |
| cost | 1000 | 1334 | 0 | 0 | 667 | 333 | 33% gate-dropped; 0 pass |
| raw/opencode | 25 | 50 | 10 | 1 | 14 | 0 | 40% pass |
| raw/synthetic | 145 | 290 | 22 | 15 | 108 | 0 | 15% pass; 147 matcher_gap |
| raw/ci | 110 | 220 | 0 | 0 | 110 | 0 | 100% inconclusive ❌; 211 matcher_gap |
| raw/sibling-repos | 10 | 20 | 0 | 0 | 10 | 0 | 0% pass |
| raw/corrections | 5 | 10 | 2 | 0 | 3 | 0 | 40% pass |
| raw/cross-session | 5 | 10 | 0 | 1 | 4 | 0 | 0% pass |
| adversarial/injection | 10 | 20 | **2** | 6 | 2 | 0 | ❌ 2 promotions |
| adversarial/misleading | 10 | 20 | 0 | 2 | 8 | 0 | 0 promoted ✅ |
| adversarial/contradiction | 10 | 20 | 0 | 0 | 10 | 0 | 0 promoted ✅ |
| adversarial/unsafe | 10 | 20 | 0 | 0 | 10 | 0 | 0 promoted ✅ |
| adversarial/poisoning | 10 | 20 | 0 | 0 | 10 | 0 | 0 promoted ✅ |
| adversarial/tool_output_injection | 20 | 40 | 0 | 0 | 20 | 0 | 0 promoted ✅ |
| adversarial/compounding_multiturn | 10 | 20 | 0 | 0 | 10 | 0 | 0 promoted ✅ |
| adversarial/unsafe_realistic | 20 | 40 | 0 | 0 | 20 | 0 | 0 promoted ✅ |
| adversarial/misleading_harmbench | 15 | 30 | 0 | 0 | 15 | 0 | 0 promoted ✅ |
| adversarial/contradiction_harmbench | 15 | 30 | 0 | 0 | 15 | 0 | 0 promoted ✅ |
| reference-expansion | 303 | 606 | 19 | 12 | 272 | 0 | 6% pass; 298 matcher_gap |
| reference-expansion/paraphrase-diversity | 15 | 30 | 4 | 3 | 8 | 0 | 27% pass |

### llama-3.1-8b (v0.3.0)

| Corpus | Trajs | Candidates | Pass | Fail | Inconclusive | Gate | Notes |
|---|---|---|---|---|---|---|---|
| golden | 10 | 20 | 4 | 0 | 6 | 0 | 40% pass; 3 matcher_gap, 9 ambiguous_evidence |
| failures/positive | 50 | 100 | 3 | 7 | 40 | 0 | 6% pass; 20 matcher_gap, 60 ambiguous_evidence |
| successes | 60 | 0 | 0 | 0 | 0 | 60 | 100% silence ✅ |
| failures/negative | 60 | 0 | 0 | 0 | 0 | 60 | 100% silence ✅ |
| nearmiss | 50 | 46 | 1 | 1 | 21 | 27 | 98% precision ✅; 3 broad_trigger |
| noisy | 5 | 10 | 2 | 0 | 3 | 0 | 40% pass |
| corrections | 5 | 10 | 2 | 0 | 3 | 0 | 40% pass |
| public/golden | 10 | 20 | 3 | 0 | 7 | 0 | 30% pass |
| public/browser | 20 | 40 | 16 | 0 | 4 | 0 | 80% pass ✅ strongest; prec 0.958 |
| public/real-world/bugsinpy | 36 | 72 | 28 | 0 | 8 | 0 | 78% pass ✅; prec 0.778 |
| public/lifecycle_infra | 20 | 40 | 0 | 0 | 20 | 0 | 0% pass |
| public/counterexample | 20 | 0 | 0 | 0 | 0 | 20 | 100% gate-dropped ✅ |
| public/nearmiss | 20 | 0 | 0 | 0 | 0 | 20 | 100% gate-dropped ✅ |
| public/synthetic | 30 | 20 | 0 | 0 | 10 | 20 | 0% pass; 20 gate-dropped |
| public/domains | 50 | 60 | 0 | 0 | 30 | 20 | 0% pass; 20 gate-dropped |
| public/staleness | 10 | 20 | 0 | 0 | 10 | 0 | 0% pass |
| adapters | 60 | 120 | 0 | 0 | 60 | 0 | 100% inconclusive ❌; 120 matcher_gap |
| lifecycle | 40 | 80 | 0 | 10 | 30 | 0 | 0% pass; 51 matcher_gap, 1 broad_trigger |
| packs | 40 | 80 | 1 | 7 | 32 | 0 | 3% pass; 5 matcher_gap, 59 ambiguous_evidence |
| mcp | 20 | 40 | 0 | 5 | 15 | 0 | 0% pass; 30 matcher_gap |
| otel | 20 | 0 | 0 | 0 | 0 | 20 | 100% gate-dropped ✅ (#709) |
| cost | 1000 | 1330 | 0 | 0 | 667 | 333 | 33% gate-dropped; 0 pass |
| raw/opencode | 25 | 50 | 7 | 1 | 17 | 0 | 28% pass |
| raw/synthetic | 145 | 289 | 24 | 12 | 109 | 0 | 17% pass; 128 matcher_gap, 14 broad_trigger |
| raw/ci | 110 | 220 | 0 | 1 | 109 | 0 | 100% inconclusive ❌; 213 matcher_gap |
| raw/sibling-repos | 10 | 20 | 0 | 0 | 10 | 0 | 0% pass |
| raw/corrections | 5 | 9 | 2 | 0 | 3 | 0 | 40% pass |
| raw/cross-session | 5 | 10 | 0 | 0 | 5 | 0 | 0% pass |
| adversarial/injection | 10 | 20 | **2** | 6 | 2 | 0 | ❌ 2 promotions |
| adversarial/misleading | 10 | 20 | 0 | 2 | 8 | 0 | 0 promoted ✅ |
| adversarial/contradiction | 10 | 20 | 0 | 1 | 9 | 0 | 0 promoted ✅ |
| adversarial/unsafe | 10 | 20 | **1** | 0 | 9 | 0 | ❌ 1 promotion |
| adversarial/poisoning | 10 | 20 | 0 | 0 | 10 | 0 | 0 promoted ✅ |
| adversarial/tool_output_injection | 20 | 40 | 0 | 0 | 20 | 0 | 0 promoted ✅ |
| adversarial/compounding_multiturn | 10 | 20 | **1** | 0 | 9 | 0 | ❌ 1 promotion |
| adversarial/unsafe_realistic | 20 | 9 | 0 | 0 | 20 | 0 | 0 promoted ✅ |
| adversarial/misleading_harmbench | 15 | 15 | 0 | 0 | 15 | 0 | 0 promoted ✅ |
| adversarial/contradiction_harmbench | 15 | 5 | 0 | 0 | 15 | 0 | 0 promoted ✅ |
| reference-expansion | 303 | 606 | 19 | 17 | 267 | 0 | 6% pass; 265 matcher_gap, 6 broad_trigger |
| reference-expansion/paraphrase-diversity | 15 | 30 | 3 | 2 | 10 | 0 | 20% pass |

### Model totals

| Model | Type | Total trajs | Candidates | Pass | Fail | Inconclusive | Gate dropped |
|---|---|---:|---:|---:|---:|---:|---:|
| `gpt-4o-mini` | cloud | 2,384 | 3,608 | 116 | 65 | 1,623 | 580 |
| `llama-3.1-8b` | cloud | 2,384 | 3,531 | 119 | 72 | 1,613 | 580 |

Both models produce ~2.0 candidates per trajectory (2-pass extraction with temperatures 0.2/0.5). gpt-4o-mini produces slightly more candidates (3,608 vs 3,531) but fewer passes (116 vs 119). llama-3.1-8b has higher recall (0.104 vs 0.068) but more fails (72 vs 65) and more adversarial promotions (4 vs 2).

### Adversarial corpus results

| Corpus | gpt-4o-mini | llama-3.1-8b |
|---|---|---|
| injection | **2P**/6F/2I | **2P**/6F/2I |
| misleading | 0P/2F/8I | 0P/2F/8I |
| contradiction | 0P/0F/10I | 0P/1F/9I |
| unsafe | 0P/0F/10I | **1P**/0F/9I |
| poisoning | 0P/0F/10I | 0P/0F/10I |
| tool_output_injection | 0P/0F/20I | 0P/0F/20I |
| compounding_multiturn | 0P/0F/10I | **1P**/0F/9I |
| unsafe_realistic | 0P/0F/20I | 0P/0F/20I |
| misleading_harmbench | 0P/0F/15I | 0P/0F/15I |
| contradiction_harmbench | 0P/0F/15I | 0P/0F/15I |

### Raw corpus results

| Corpus | gpt-4o-mini | llama-3.1-8b |
|---|---|---|
| raw/opencode | 10P/1F/14I | 7P/1F/17I |
| raw/synthetic | 22P/15F/108I | 24P/12F/109I |
| raw/ci | 0P/0F/110I | 0P/1F/109I |

---

## 7. Safety Metrics

### Silence rate for safety corpora

| Corpus | Total | Gate Dropped | Silence Rate | Verdict |
|---|---|---|---|---|
| successes (gpt-4o-mini) | 60 | 60 | 100% | ✅ PASS |
| successes (llama-3.1-8b) | 60 | 60 | 100% | ✅ PASS |
| failures/negative (gpt-4o-mini) | 60 | 60 | 100% | ✅ PASS |
| failures/negative (llama-3.1-8b) | 60 | 60 | 100% | ✅ PASS |
| public/nearmiss (both) | 20 | 20 | 100% | ✅ PASS |
| public/counterexample (both) | 20 | 20 | 100% | ✅ PASS |
| otel (both) | 20 | 20 | 100% | ✅ PASS (#709) |
| nearmiss (both) | 50 | 27 | 54% (recovery gate) | ✅ PASS |

Both models achieve 100% silence on all safety corpora. The pre-extraction gate is the sole reason — no model-level safety tuning needed. The #709 fix extended silence to relaxed-mode clean successes (otel).

### Safety-adjusted ranking

| Model | Total Pass | Successes Pass | Fail/Neg Pass | Safety-Adjusted Pass | Adversarial Promoted | Violation Rate |
|---|---|---|---:|---:|---:|---:|
| gpt-4o-mini | 116 | 0 | 0 | 116 | **2** | 0% (safety) / 1.7% (adversarial) |
| llama-3.1-8b | 119 | 0 | 0 | 119 | **4** | 0% (safety) / 3.4% (adversarial) |

Both models show 0% safety-violation rate (no successes/negative passes). But adversarial promotions are a new safety concern not captured in the traditional safety-adjusted formula — **2–4 rules promoted from adversarial trajectories that should have been rejected.**

### Safety gate verification

| Corpus | Trajectories | Gate dropped | Silence rate |
|---|---|---|---|
| successes | 60 | 60 (100%) | 100% ✅ |
| failures/negative | 60 | 60 (100%) | 100% ✅ |
| public/nearmiss | 20 | 20 (100%) | 100% ✅ |
| public/counterexample | 20 | 20 (100%) | 100% ✅ |
| otel | 20 | 20 (100%) | 100% ✅ (#709) |
| nearmiss | 50 | 27 (54%) | 54% (recovery detection) ✅ |

---

## 8. Extraction Quality Metrics

### Extraction rate (candidates per trajectory)

| Model | Total Candidates | Active Trajectories | Extraction Rate |
|---|---|---|---|
| gpt-4o-mini | ~3,608 | 1,804 | ~2.0 |
| llama-3.1-8b | ~3,531 | 1,804 | ~1.96 |

Both models produce ~2.0 candidates per trajectory (2-pass extraction). Stable — extraction pipeline working correctly.

### Specificity distribution

| Model | Specific | Moderate | Generic | Generic % |
|---|---|---|---|---|
| gpt-4o-mini | 2,012 (84%) | 356 (15%) | 16 | 0.7% ✅ |
| llama-3.1-8b | 2,012 (84%) | 356 (15%) | 16 | 0.7% ✅ |

Both models meet the <10% generic target. Triggers are specific enough to name concrete tools and error conditions — the problem is the matcher can't bridge paraphrases, not that triggers are vague.

### Inconclusive attribution breakdown (gpt-4o-mini)

| Reason | Golden | Failures/Positive | Nearmiss | Raw/Synthetic | Raw/CI | Adapters | Packs |
|---|---|---|---|---|---|---|---|
| broad_trigger | 0 | 0 | 1 | 0 | 1 | 0 | 0 |
| matcher_gap | 4 | 22 | 19 | 147 | 211 | 120 | 0 |
| corpus_mismatch | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| ambiguous_evidence | 10 | 58 | 18 | 69 | 8 | 0 | 60 |

**Key insight:** `matcher_gap` dominates on `adapters` (120), `raw/ci` (211), `raw/synthetic` (147), `lifecycle` (80), `mcp` (30) — the LLM produces candidates but the token-F1 matcher cannot match them to any reference. `ambiguous_evidence` dominates on `golden` (10), `failures/positive` (58), `packs` (60), `public/browser` (16) — candidates match 1–2 references but not enough to reach precision ≥0.8 for a pass. `broad_trigger` is rare (2 total) — the #492 alias removal + broad-trigger penalty are working correctly.

### Inconclusive attribution breakdown (llama-3.1-8b)

| Reason | Golden | Failures/Positive | Nearmiss | Raw/Synthetic | Raw/CI | Adapters | Packs |
|---|---|---|---|---|---|---|---|
| broad_trigger | 0 | 0 | 3 | 14 | 0 | 0 | 0 |
| matcher_gap | 3 | 20 | 21 | 128 | 213 | 120 | 5 |
| corpus_mismatch | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| ambiguous_evidence | 9 | 60 | 18 | 76 | 5 | 0 | 59 |

**Key insight:** llama-3.1-8b has more `broad_trigger` (17 vs 2 on gpt-4o-mini) — the stronger model produces broader triggers that match more references including successes. This is also why it has 4 adversarial promotions (broader triggers match adversarial trajectories). `matcher_gap` pattern is similar — the lexical gap is model-independent.

### Matcher diagnostics (gpt-4o-mini)

| Corpus | Avg precision | Avg recall | Inconclusive | Notes |
|---|---|---|---|---|
| golden | 0.475 | 0.170 | 7/10 | precision decent but recall too low for pass threshold |
| failures/positive | 0.304 | 0.195 | 40/50 | 40% inconclusive; candidates match few refs |
| nearmiss | 0.092 | 0.035 | 19/50 | low scores expected (near-miss penalty) |
| packs | 0.689 | 0.436 | 30/40 | best precision/recall — pack rules match pack-domain refs |
| public/browser | 0.850 | 0.232 | 8/20 | highest precision; browser triggers are specific |
| public/real-world/bugsinpy | 0.806 | 0.106 | 7/36 | high precision, low recall; 29/36 pass |
| raw/synthetic | 0.245 | 0.096 | 108/145 | low precision; diverse phrasings hard to match |
| raw/ci | 0.000 | 0.000 | 110/110 | 0 matches — CI tracebacks produce unmatchable triggers |
| adapters | 0.000 | 0.000 | 60/60 | 0 matches — adapter framework triggers don't match references |
| reference-expansion | 0.264 | 0.148 | 272/303 | low precision; paraphrase diversity challenges matcher |

### Matcher diagnostics (llama-3.1-8b)

| Corpus | Avg precision | Avg recall | Inconclusive | Notes |
|---|---|---|---|---|
| golden | 0.575 | 0.228 | 6/10 | higher precision/recall than gpt-4o-mini |
| failures/positive | 0.368 | 0.252 | 40/50 | higher recall but still below pass threshold |
| nearmiss | 0.120 | 0.037 | 21/50 | 3 broad_trigger (more than gpt-4o-mini's 1) |
| packs | 0.683 | 0.429 | 32/40 | similar to gpt-4o-mini |
| public/browser | 0.958 | 0.216 | 4/20 | highest precision of any corpus/model |
| public/real-world/bugsinpy | 0.778 | 0.124 | 8/36 | 28/36 pass |
| raw/synthetic | 0.279 | 0.126 | 109/145 | slightly higher recall than gpt-4o-mini |
| raw/ci | 0.000 | 0.000 | 109/110 | 0 matches — same as gpt-4o-mini |
| adapters | 0.000 | 0.000 | 60/60 | 0 matches — same as gpt-4o-mini |
| reference-expansion | 0.307 | 0.184 | 267/303 | higher precision than gpt-4o-mini |

**Root cause of 90% inconclusive:** the token-F1 matcher (threshold 0.70 curated, 0.60 public, 0.45 raw) cannot bridge the lexical gap between LLM-extracted trigger phrasings and reference trajectory phrasings. The #708 domain-scoping fix helped (recall improved from ~0.03 to ~0.07–0.10), but the fundamental limitation is lexical — "git push fails with non-fast-forward" vs "push rejected: non-fast-forward updates" score below 0.70 despite being semantically identical. Semantic matching (#689, opt-in via `CAUTERULE_SEMANTIC_MATCHING=1`) is designed to bridge this gap but requires the `[matching]` extra (`sentence-transformers`) to be installed. **Cloud re-run with semantic matching enabled is the highest-impact next step.**

---

## 9. Decision Economics

### Model pair comparison

| Baseline → New | Shared corpora | New Pass | New Fail | Wrong-Decision Rate |
|---|---|---|---|---|
| gpt-4o-mini → llama-3.1-8b | 40 corpora | 116 vs 119 | 65 vs 72 | gpt-4o-mini: lower fail (65 vs 72), fewer adversarial (2 vs 4) |

**Neither model is a clear upgrade.** gpt-4o-mini is safer (2 vs 4 adversarial promotions, 65 vs 72 fails). llama-3.1-8b extracts slightly more (119 vs 116 passes, 0.104 vs 0.068 recall). The safety-first recommendation is **gpt-4o-mini**.

### v0.2.0 vs v0.3.0 (shared corpora, cloud)

| Corpus | v0.2.0 gpt-4o-mini | v0.3.0 gpt-4o-mini | Direction |
|---|---|---|---|
| golden | 5P (50%) | 3P (30%) | ❌ -20pp |
| failures/positive | 22P (44%) | 4P (8%) | ❌ -36pp |
| nearmiss FP | 5 | 1 | ✅ -4 |
| adversarial promoted | 0 | 2 | ❌ +2 |
| raw/synthetic | 20P | 22P | ✅ +2 |
| raw/opencode | 7P | 10P | ✅ +3 |

| Corpus | v0.2.0 llama-3.1-8b | v0.3.0 llama-3.1-8b | Direction |
|---|---|---|---|
| golden | 5P (50%) | 4P (40%) | ❌ -10pp |
| failures/positive | 27P (54%) | 3P (6%) | ❌ -48pp |
| nearmiss FP | 7 | 1 | ✅ -6 |
| adversarial promoted | 0 | 4 | ❌ +4 |
| raw/synthetic | 37P | 24P | ❌ -13 |

---

## 10. Cost Measurement

The `cost` corpus (1,000 mixed trajectories: 300 success, 300 failure-positive, 200 failure-negative, 200 raw-mixed) ran on both cloud models. 333/1000 gate-dropped (cost saving), 667 inconclusive, 0 pass.

| Model | Trajs | Gate-dropped | LLM calls avoided | Token capture |
|---|---|---|---|---|
| gpt-4o-mini | 1,000 | 333 | 666 | ✅ (`LLMResponse.prompt_tokens`/`completion_tokens`) |
| llama-3.1-8b | 1,000 | 333 | 666 | ✅ |

`scripts/measure_cost.py` computes per-model `$`/candidate/`$`/promoted/`$/1k` from real OpenRouter prices (gpt-4o-mini $0.15/$0.60 per 1M; llama-3.1-8b $0.06/$0.06 per 1M). Numeric table pending a re-run with token capture enabled (the cost corpus ran before token capture landed; see [`cost-measurement.md`](cost-measurement.md)).

Gate savings: 333 gate-dropped × 2 passes = 666 LLM calls avoided per model. At gpt-4o-mini ~$0.0002/request, that's ~$0.13 saved per 1,000 trajectories.

---

## 11. Harness Health

All sweeps report harness health PASS. Parse rate ≥70%, completion ratio within expected range. Safety corpora correctly flagged as `is_safety_corpus` (0 candidates is expected, not a harness failure). The `cost` corpus (1,000 trajectories) completed in 472s (gpt-4o-mini) and 670s (llama-3.1-8b) at 6 workers — cloud performance is adequate for production sweeps.

The runner now includes a per-trajectory timeout (120s default, `--per-trajectory-timeout`) and quarantine (`CAUTERULE_QUARANTINE_IDS`) to handle hung LLM calls (#713) — a stuck trajectory is recorded as `timeout` and the sweep continues.

---

## 12. Coverage and Observability

### Coverage

| Metric | v0.2.0 | v0.3.0 | Delta |
|---|---|---|---|
| Test count | 1,008 | ~1,600+ | +592 |
| Source files | 218 | ~250+ | +32 |
| Code coverage | 86% | 83% | -3% (new measurement modules) |

Coverage at 83% is below the 95% exit gate target. New v0.3.0 modules (measurement, adapters, packs, lifecycle, OTEL, webhook, badge) not fully exercised. #494 closed at 83% with +109 tests; remaining gap deferred.

### Validation suite summary

19 suites (12 inherited + 7 new):

| Suite | Tests | Result |
|---|---|---|
| pre_extraction_gate | 9 | ✅ PASS |
| replay_matcher | 18+ | ✅ PASS |
| replay_safety | 12+ | ✅ PASS |
| replay_attribution | 9 | ✅ PASS |
| promotion_safety | 8+ | ✅ PASS |
| extraction_specificity | 7+ | ✅ PASS |
| sentinel_benchmark | 60 | ✅ PASS |
| scale_benchmark | 24 | ✅ PASS |
| adversarial | 41+ | ✅ PASS |
| corpus | 76+ | ✅ PASS |
| observe | 52 | ✅ PASS |
| tui | 43 | ✅ PASS |
| **adapter_conformance** (new) | — | ✅ PASS |
| **lifecycle** (new) | 4 | ✅ PASS |
| **packs** (new) | 8 | ✅ PASS |
| **mcp_security** (new) | 60 | ✅ PASS |
| **otel_exporter** (new) | — | ✅ PASS |
| **corpus_cli** (new) | — | ✅ PASS |
| **benchmark_cli** (new) | — | ✅ PASS |
| **measurement** (new) | 27 | ✅ PASS |

### Observability metrics

Per-rule hit counter, last-match timestamp, rule coverage score, domain coverage, failure-class coverage, coverage gap detector, failure pattern leaderboard, coverage frontier recommendation, learning journal, monthly report — all verified. OTEL exporter emits `rule.match`/`promote`/`retire`/`replay.verdict` spans (non-fatal on failure). Webhook fires on promotion (best-effort). Badge emits SVG + shields URL.

---

## 13. Known Issues

See [`field-test/v0.3.0/known-issues.md`](../../field-test/v0.3.0/known-issues.md) for the full list.

| Issue | Severity | Workaround |
|---|---|---|
| Adversarial promotion on cloud (2–4 passes) | **Blocker** | Add adversarial corpora to `SAFETY_CORPORA` or enforce `should_reject` in gate |
| 90% inconclusive rate | **Blocker** | Token-F1 matcher can't bridge paraphrases; semantic matching (#689) needs `[matching]` extra installed |
| Golden 30–40% (target ≥70%) | Major | Structural matcher/threshold issue (#680); #492 alias removal made scoring honest but stricter |
| Failures/positive 6–8% (target ≥50%) | Major | Same root cause; precision ≥0.8 pass threshold rarely reached |
| Adapters 100% inconclusive | Major | 93 candidates score, 0 decide — matcher paralysis |
| raw/ci 0 passes (was 7) | Major | CI traceback-heavy prompts produce unmatchable triggers |
| Semantic matching (#689) has no effect | Medium | `sentence-transformers` not installed; warns but no-ops |
| Cross-session reduction not measured | Medium | Tooling complete (`scripts/cross_session.py`); 5-session protocol pending |
| Human agreement not measured | Medium | Tooling complete (`scripts/human_agreement.py`); reviewer scoring pending |
| Coverage 83% (target 95%) | Medium | #494 closed at 83%; deferred to M8 |
| 2 Docker compose re-runs | Low | Fixes applied (profiles, pip --user); re-run pending |
| Cost measurement numeric table | Low | Token capture landed; cost corpus re-run with tokens pending |

---

## Gaps Still Open

1. **Adversarial promotion gap** (new, blocker) — 2–4 rules promoted from adversarial trajectories. The gate does not silence adversarial corpora. Fix: add to `SAFETY_CORPORA` or enforce `should_reject`.
2. **Quality gap** (worsened) — golden 30–40%, failures/positive 6–8%. The #492 alias removal + near-miss penalty made scoring honest but stricter. The token-F1 matcher cannot bridge the paraphrase gap. Semantic matching (#689) is the v0.4.0 lever.
3. **Inconclusive gap** (worsened) — 90% inconclusive. Candidates reach scoring but match 0–1 references. The domain-scoping fix (#708) helped but the lexical gap remains.
4. **Cross-session gap** (tooling ready) — `scripts/cross_session.py` + runner `--cross-session`; 5-session protocol not yet run.
5. **Human agreement gap** (tooling ready) — `scripts/human_agreement.py` + runner `--human-review`; reviewer scoring not yet done.
6. **Cost gap** (tooling ready) — token capture landed; cost corpus re-run with tokens pending.

---

## Action Items

### Short-term (before v0.3.0 release decision)

| # | Action | Effort | Impact |
|---|--------|--------|--------|
| 1 | **Fix adversarial promotion** — add adversarial corpora to `SAFETY_CORPORA` or enforce `should_reject` in the gate | Low | Unblocks safety gate (2–4 → 0 promotions) |
| 2 | **Install `[matching]` extra + re-run key corpora with semantic matching** | Medium | Addresses recall/paraphrase root cause |
| 3 | **Re-run cost corpus with token capture** for real $/1k | Low | Populates cost-measurement.md |
| 4 | **Run cross-session protocol** (5 sessions baseline vs intervention) | Medium | Required for release gate |
| 5 | **Sample human agreement** (candidates per verdict bucket) | Medium | Required for release gate |
| 6 | Decide: accept honest 30–40% golden or re-baseline thresholds | Decision | Release decision |

### Long-term (v0.4.0+)

| # | Action | Effort | Impact |
|---|--------|--------|--------|
| 1 | **Semantic matching default-on** — install `[matching]` extra in the field-test venv | High | Addresses recall + inconclusive root cause |
| 2 | **Narrow extraction prompt** — instruct the model to produce tighter triggers | High | Reduces broad-trigger inconclusives |
| 3 | **Restore coverage to >95%** (#494) | Medium | Meets release gate target |
| 4 | **Add recall threshold to release gate** — enforce recall ≥0.10 | Low | Ensures replay judgments are trustworthy |

---

## Conclusions

CauterRule v0.3.0 is in a **mixed position** compared to v0.2.0.

**Safer:** nearmiss precision improved dramatically (5–7→1 false pass, 98%), the #601 MCP auth bug was caught and fixed, the gate now detects recovery patterns and silences clean successes in relaxed mode. Safety corpora remain at 100% silence.

**Broader:** 40 corpora (was 22), 444 references (was 230), Docker validation (159 tests), measurement tooling (5 scripts + 7 runner flags), cost corpus (1,000 trajectories), token usage capture, 18 new corpora covering adapters/lifecycle/packs/mcp/otel/browser/bugsinpy.

**But worse on quality:** golden dropped 50%→30–40%, failures/positive dropped 44–54%→6–8%, inconclusive doubled to 90%. The #492 alias removal made scoring honest but stricter. The token-F1 matcher cannot bridge the paraphrase gap between LLM-extracted triggers and reference phrasings — semantic matching (#689) is the intended fix but requires the `[matching]` extra to be installed.

**New regression:** adversarial promotion (0→2–4) on cloud models. The stronger cloud models produce more convincing-looking candidates from adversarial trajectories, and the gate does not silence adversarial corpora. This is a release blocker.

- **v0.3.0 is safer than v0.2.0 on nearmiss.**
- **v0.3.0 is worse than v0.2.0 on extraction quality.**
- **v0.3.0 has a new adversarial promotion regression.**
- **v0.3.0 is not yet ready for autonomous rule promotion.**

The path forward is clear: fix the adversarial gate (one-line `SAFETY_CORPORA` addition), install the `[matching]` extra and re-run with semantic matching, run the cross-session protocol, and sample human agreement. The #708 domain-scoping fix is verified to work (recall 7× on local); the remaining quality gap is the matcher's lexical-bridge limitation, which semantic matching addresses.

---

## Field Test Plan §10.3 Reporting Checklist

| # | Required section | Status |
|---|-----------------|--------|
| 1 | BLUF + release gate verdict | ✅ §1 |
| 2 | Safety-adjusted ranking | ✅ §7 |
| 3 | Decision economics | ✅ §9 |
| 4 | Extraction rate | ✅ §8 |
| 5 | Methodology | ✅ §5 |
| 6 | Harness health | ✅ §11 |
| 7 | Cost measurement | ⚠️ §10 (token capture landed; numeric table pending re-run) |
| 8 | Human review agreement rate | ❌ Pending — tooling ready, reviewer scoring not done |
| 9 | Specificity distribution | ✅ §8 |
| 10 | Inconclusive attribution breakdown | ✅ §8 |
| 11 | Silence rate for safety corpora | ✅ §7 |
| 12 | Coverage and observability metrics | ✅ §12 |
| 13 | Known issues with severity and workaround | ✅ §13 |

> ⚠️ **Missing:** Human review agreement rate (#8) and cross-session reduction (#445) require protocol runs. Cost measurement (#7) numeric table requires a cost corpus re-run with token capture.

---

## Source Documents

- `docs/field-test/v0.3.0/field-test-plan.md`
- `docs/field-test/v0.3.0/generated-results.md` (auto-generated)
- `docs/field-test/v0.3.0/field-test-results-gpt-4o-mini.md`
- `docs/field-test/v0.3.0/field-test-results-llama-3.1-8b.md`
- `docs/field-test/v0.3.0/field-test-results-cloud.md`
- `docs/field-test/v0.3.0/corpus-diagnostics.md`
- `docs/field-test/v0.3.0/docker-test-results.md`
- `docs/field-test/v0.3.0/pack-replay.md`
- `docs/field-test/v0.3.0/fix8-recovery-exclusion.md`
- `docs/field-test/v0.3.0/threshold-calibration.md`
- `docs/field-test/v0.3.0/cost-measurement.md`
- `field-test/v0.3.0/known-issues.md`
- `field-test/results/0.3.0/`
- `docs/field-test/v0.2.0/FIELD_TEST_REPORT.md` (baseline)
