# Real Corpus Field Test Plan — CauterRule v0.1.0

**Date:** 2026-09-05
**Milestone:** M30 — Comprehensive Field Test (Phase 7)
**GitHub Issues:** #399-#410 (12 issues, 30.8.1 through 30.8.12)
**Depends on:** `corpus-plan.md` (corpus acquisition), Phase 1-4 of `field-test-plan.md`

---

## 1. Overview

These tests exercise the **real corpus** collected per `corpus-plan.md`. They are the ultimate proof that CauterRule learns from real agent work, not just synthetic fixtures. While Phases 1-6 of the main field test plan use synthetic or mock data, Phase 7 uses real trajectories from OpenCode sessions, CI logs, and sibling repo agent runs.

**Corpus:** `field-test/corpus/curated/` (30 failures, 20 successes, 10 near-miss, 5 noisy, 5 corrections, 10 golden)
**LLM:** OMLX (local, free) for all extraction. gpt-4o-mini for golden set comparison only.
**Cost:** $0-2 total (OMLX is free; gpt-4o-mini only for golden set)
**Duration:** ~2.5 hours

---

## 2. LLM Configuration

All extraction uses OMLX (Apple Silicon local LLM server). No Anthropic. Minimal cloud cost.

```bash
# OMLX (primary — local, free)
export CAUTERULE_LLM_PROVIDER=openai
export CAUTERULE_MODEL=llama-3.2-3b-instruct
export OPENAI_API_KEY=dummy
export OPENAI_BASE_URL=http://localhost:8000/v1

# gpt-4o-mini (comparison only — cheap cloud)
export CAUTERULE_LLM_PROVIDER=openai
export CAUTERULE_MODEL=gpt-4o-mini
export OPENAI_API_KEY=sk-...
```

---

## 3. Test Execution Order

Tests must run in this order — each depends on the previous one:

```
30.8.1 (validate corpus)
  └─> 30.8.2 (extract from real failures with OMLX)
        └─> 30.8.3 (replay-test candidates)
              └─> 30.8.4 (promote + inject)
                    ├─> 30.8.5 (repeat-failure reduction)
                    ├─> 30.8.6 (cross-session memory)
                    ├─> 30.8.8 (coverage measurement)
                    ├─> 30.8.9 (near-miss precision)
                    ├─> 30.8.10 (correction flow)
                    └─> 30.8.11 (export to AGENTS.md)
30.8.7 (golden set regression — independent)
30.8.12 (cost measurement — independent)
```

---

## 4. Test Details

### 4.1 Task 30.8.1: Real Corpus Validation (#399)

**What:** Validate every real trajectory in the curated corpus is well-formed, redacted, and correctly labeled.

**Corpus:** `field-test/corpus/curated/` (all 70 trajectories)
**LLM:** None
**Duration:** <5 minutes

**Tests:**
1. All 70 JSONL files parse as valid Trajectory objects
2. Every trajectory has required metadata (id, timestamp, task, domain, failure_class, quality_label, steps, success)
3. No secrets in any field (grep for API key patterns, tokens, passwords)
4. Domain distribution matches target (git 28%, python 25%, docker 17%, etc.)
5. Quality label distribution matches target (clear 60%, ambiguous 20%, etc.)
6. Every failure trajectory has a non-empty `failure_point`
7. Every success trajectory has `success: true`
8. Every correction trajectory has a `human_correction` field

**Acceptance Criteria:**
- [ ] All 70 trajectories pass validation
- [ ] 0 secrets detected in any file
- [ ] Domain and quality label distributions within ±5% of target
- [ ] Validation report saved to `field-test/corpus-validation.md`

### 4.2 Task 30.8.2: Real Corpus Extraction with OMLX (#400)

**What:** Run LLM extraction on every real failure trajectory using OMLX (local, free). Verify the extractor produces valid candidate rules from real agent failures.

**Corpus:** 30 real failure trajectories
**LLM:** OMLX (local Llama or MLX model on Apple Silicon)
**Duration:** ~15 minutes (30 trajectories × 3 passes)

**Tests:**
1. Run `cauterule extract` on each of the 30 real failure trajectories
2. Verify a CandidateRule is produced for each (valid when/do/confidence)
3. Verify extraction success rate ≥70% (≥21 of 30 produce valid candidates)
4. Verify extracted triggers are specific (not "when task fails" — should be "when git push fails with non-fast-forward")
5. Verify confidence scores are in [0.5, 0.95] range (not all 0.8, not all 0.5)
6. Compare extraction quality across quality labels:
   - "clear" label: ≥85% extraction success
   - "ambiguous" label: ≥60% extraction success
   - "misleading" label: ≥40% extraction success

**Acceptance Criteria:**
- [ ] OMLX/local LLM successfully extracts candidates from real trajectories
- [ ] ≥70% overall extraction success rate
- [ ] Extracted triggers are specific (not generic)
- [ ] Confidence scores vary across trajectories (not all identical)
- [ ] Extraction quality correlates with quality_label (clear > ambiguous > misleading)
- [ ] Results saved to `field-test/v0.1.0/extraction-results.md`

### 4.3 Task 30.8.3: Real Corpus Replay Testing (#401)

**What:** Replay-test every extracted candidate against the real success + failure trajectories. Verify the replay engine produces correct evidence reports.

**Corpus:** Candidates from 30.8.2 + 20 real success trajectories + 30 real failure trajectories
**LLM:** None (replay is deterministic, no LLM needed)
**Duration:** ~10 minutes

**Tests:**
1. For each extracted candidate, run `cauterule test` against all 50 real trajectories (30F + 20S)
2. Verify EvidenceReport is produced with precision, recall, verdict
3. Verify no candidate breaks a real success (precision must be 1.0 for promotion)
4. Verify candidates with "clear" quality label have higher replay pass rate than "ambiguous"
5. Verify replay is deterministic (same candidate + same corpus = same report)

**Acceptance Criteria:**
- [ ] All candidates produce valid EvidenceReports
- [ ] ≥50% of candidates pass replay (precision=1.0, prevented≥1)
- [ ] 0 real successes broken by any candidate
- [ ] Candidates from "clear" trajectories have ≥70% pass rate
- [ ] Replay is deterministic across 3 runs
- [ ] Results saved to `field-test/v0.1.0/replay-results.md`

### 4.4 Task 30.8.4: Real Corpus Promotion & Injection (#402)

**What:** Promote the best candidates from real corpus to the rule store. Then inject them on matching tasks and verify they fire.

**Corpus:** Passing candidates from 30.8.3
**LLM:** None (promotion and injection are deterministic)
**Duration:** ~10 minutes

**Tests:**
1. Promote all passing candidates via `cauterule promote`
2. Verify rule YAML files created in `rules/` with real git hashes
3. Run `cauterule list` — verify all promoted rules appear
4. Run `cauterule validate` — verify store integrity
5. For each promoted rule, run `cauterule inject --task <matching task>`
6. Verify the rule fires (appears in injection output)
7. Run `cauterule inject --task <non-matching task>` — verify rule does NOT fire

**Acceptance Criteria:**
- [ ] ≥10 rules promoted from real corpus
- [ ] All rule YAMLs have 40-char hex `promotion_commit`
- [ ] `cauterule validate` passes
- [ ] Every promoted rule fires on at least 1 matching task
- [ ] No rule fires on a non-matching task
- [ ] Results saved to `field-test/v0.1.0/promotion-results.md`

### 4.5 Task 30.8.5: Real Corpus Repeat-Failure Reduction (#403)

**What:** The headline metric — measure how much the learned rules reduce repeat failures using the real corpus.

**Corpus:** 30 real failure trajectories + 20 real success trajectories
**LLM:** OMLX (for extraction in run 1 only; rules already exist for run 2)
**Duration:** ~20 minutes

**Tests:**
1. **Run 1 (no rules):** Run all 30 failure tasks with empty rule store. Count failures.
2. **Extract + promote:** Extract rules from failures, replay-test, promote passing ones.
3. **Run 2 (with rules):** Re-run all 30 tasks with rules injected. Count failures.
4. **Compare:** Calculate repeat-failure reduction percentage.

**Metrics:**

| Metric | Run 1 (no rules) | Run 2 (with rules) | Target |
|--------|-----------------|-------------------|--------|
| Tasks failed | 30 (all) | ? | ≤15 |
| Repeat failures | 30 | ? | ≤15 |
| Repeat-failure rate | 100% | ? | ≤50% |
| Reduction | — | ? | ≥50% |
| Rules fired | 0 | ? | ≥10 |
| Failures prevented | 0 | ? | ≥15 |

**Acceptance Criteria:**
- [ ] Repeat-failure rate drops by ≥50% from run 1 to run 2
- [ ] ≥15 of 30 failures prevented by injected rules
- [ ] ≥10 rules fired during run 2
- [ ] 0 real successes broken (no regression)
- [ ] Results saved to `field-test/v0.1.0/repeat-failure-reduction.md`

### 4.6 Task 30.8.6: Real Corpus Cross-Session Memory (#404)

**What:** Verify rules learned from real corpus in one session persist and fire in a fresh session.

**Corpus:** 10 real failure trajectories (5 from CauterRule sessions, 5 from sibling repos)
**LLM:** OMLX (session 1 only)
**Duration:** ~15 minutes

**Tests:**
1. **Session 1:** Extract and promote rules from 5 CauterRule failures
2. **Session 2:** Open fresh Python process, load rules from store
3. Run the same 5 tasks — verify all 5 failures prevented
4. **Session 3:** Extract rules from 5 sibling-repo failures
5. **Session 4:** Open fresh process, verify sibling-repo rules also fire

**Acceptance Criteria:**
- [ ] Rules from session 1 persist to session 2 (YAML files on disk)
- [ ] All 5 CauterRule failures prevented in session 2
- [ ] Rules from session 3 persist to session 4
- [ ] All 5 sibling-repo failures prevented in session 4
- [ ] Rule store grows correctly across sessions (5 → 10+ rules)
- [ ] Results saved to `field-test/v0.1.0/cross-session-results.md`

### 4.7 Task 30.8.7: Real Corpus Golden Set Regression (#405)

**What:** Run the 10 golden trajectories through extraction with OMLX and gpt-4o-mini. Verify the extracted rules match the expected rules.

**Corpus:** 10 golden trajectories from `corpus/golden/` with `golden-manifest.json`
**LLM:** OMLX (primary) + gpt-4o-mini (comparison)
**Duration:** ~15 minutes

**Tests:**
1. Load golden-manifest.json — get expected rules for each trajectory
2. Run extraction with OMLX on all 10 golden trajectories
3. Compare extracted rules to expected rules (trigger similarity, directive match)
4. Run extraction with gpt-4o-mini on same 10 trajectories
5. Compare OMLX vs gpt-4o-mini extraction quality

**Metrics:**

| Metric | OMLX (local) | gpt-4o-mini (cloud) | Target |
|--------|-------------|--------------------|----|
| Extraction success | ? | ? | ≥80% / ≥85% |
| Trigger match rate | ? | ? | ≥70% / ≥75% |
| Directive match rate | ? | ? | ≥60% / ≥65% |
| Avg confidence | ? | ? | 0.7-0.9 |

**Acceptance Criteria:**
- [ ] OMLX: ≥80% extraction success, ≥70% trigger match
- [ ] gpt-4o-mini: ≥85% extraction success, ≥75% trigger match
- [ ] Golden set can be re-run for future version regression testing
- [ ] Results saved to `field-test/v0.1.0/golden-regression-results.md`

### 4.8 Task 30.8.8: Real Corpus Coverage Measurement (#406)

**What:** Measure how well the promoted rules cover the real corpus failure domains.

**Corpus:** 30 real failure trajectories + promoted rules from 30.8.4
**LLM:** None
**Duration:** <5 minutes

**Tests:**
1. Run `cauterule health` — get coverage score
2. Run `cauterule observe domain_coverage` — coverage by domain
3. Run `cauterule observe class_coverage` — coverage by failure class
4. Run `cauterule observe coverage_gap` — identify uncovered domains
5. Run `cauterule observe coverage_frontier` — next most valuable domain to learn

**Metrics:**

| Metric | Target | How to Improve |
|--------|--------|----------------|
| Rule coverage score | ≥70% | Promote more rules in uncovered domains |
| Domain coverage | ≥60% | Add rules for uncovered domains |
| Failure-class coverage | ≥60% | Add rules for uncovered failure classes |
| Coverage gaps | Document | List domains with failures but no rules |
| Coverage frontier | Document | Suggest next domain to learn from |

**Acceptance Criteria:**
- [ ] Rule coverage score ≥70% (real corpus is smaller than synthetic, so threshold is lower)
- [ ] Domain coverage ≥60%
- [ ] Failure-class coverage ≥60%
- [ ] Coverage gaps and frontier documented
- [ ] Results saved to `field-test/v0.1.0/coverage-results.md`

### 4.9 Task 30.8.9: Real Corpus Near-Miss Precision (#407)

**What:** Verify promoted rules do NOT fire on near-miss trajectories — scenarios that look similar but should not trigger.

**Corpus:** 10 near-miss trajectories from `corpus/curated/nearmiss/`
**LLM:** None
**Duration:** <5 minutes

**Tests:**
1. For each near-miss trajectory, run `cauterule inject --task <near-miss task>`
2. Verify no promoted rule fires (or if one fires, it's the wrong rule)
3. Calculate near-miss precision: % of near-miss scenarios where NO rule fires

**Acceptance Criteria:**
- [ ] ≥90% of near-miss scenarios do NOT trigger any rule
- [ ] Any rule that fires on a near-miss is flagged for review (trigger may be too broad)
- [ ] Results saved to `field-test/v0.1.0/nearmiss-results.md`

### 4.10 Task 30.8.10: Real Corpus Correction Flow (#408)

**What:** Verify the human-correction flow works with real correction examples.

**Corpus:** 5 correction trajectories from `corpus/curated/corrections/`
**LLM:** OMLX
**Duration:** ~10 minutes

**Tests:**
1. For each correction trajectory, run `cauterule extract --correction "<correction text>"`
2. Verify a CandidateRule is produced with a specific trigger
3. Replay-test each candidate
4. Promote passing candidates
5. Verify the promoted rule's trigger is specific (not "when task fails")

**Acceptance Criteria:**
- [ ] All 5 corrections produce CandidateRules
- [ ] ≥4 of 5 corrections produce rules that pass replay
- [ ] ≥4 of 5 corrections promoted to rule store
- [ ] Correction triggers are specific (e.g., "when git push fails with non-fast-forward" not "when git fails")
- [ ] Results saved to `field-test/v0.1.0/correction-results.md`

### 4.11 Task 30.8.11: Real Corpus Export to AGENTS.md (#409)

**What:** Export the rules learned from real corpus to `AGENTS.md` and verify they work with OpenCode.

**Corpus:** Promoted rules from 30.8.4
**LLM:** None
**Duration:** ~15 minutes

**Tests:**
1. Run `cauterule export --format agents --output AGENTS.md`
2. Verify AGENTS.md contains all active rules in OpenCode-readable format
3. Verify no retired/superseded rules in export
4. Place AGENTS.md in a test project directory
5. Open the project in OpenCode
6. Run a task that matches a promoted rule trigger
7. Verify the rule appears in OpenCode's context and is followed

**Acceptance Criteria:**
- [ ] AGENTS.md produced with all active rules
- [ ] No retired/superseded rules in export
- [ ] AGENTS.md is valid markdown
- [ ] OpenCode reads AGENTS.md and rules appear in context
- [ ] Rules are followed by OpenCode on matching tasks
- [ ] Results saved to `field-test/v0.1.0/export-agents-results.md`

### 4.12 Task 30.8.12: Real Corpus Cost Measurement (#410)

**What:** Measure the actual LLM cost of running the full field test with OMLX (local, free) vs gpt-4o-mini (cheap cloud).

**Corpus:** 30 real failure trajectories
**LLM:** OMLX (primary) + gpt-4o-mini (comparison)
**Duration:** ~20 minutes

**Tests:**
1. Run extraction on all 30 trajectories with OMLX — record time and token count
2. Run extraction on all 30 trajectories with gpt-4o-mini — record time, token count, and cost
3. Calculate cost per extracted candidate, per promoted rule
4. Compare OMLX (free) vs gpt-4o-mini (paid)

**Metrics:**

| Metric | OMLX (local) | gpt-4o-mini (cloud) |
|--------|-------------|--------------------|
| Extraction time per candidate | ? | ? |
| Total extraction time | ? | ? |
| Token count per candidate | ? | ? |
| Cost per candidate | $0 | ? |
| Cost per promoted rule | $0 | ? |
| Total cost | $0 | ? |

**Acceptance Criteria:**
- [ ] OMLX total cost: $0
- [ ] gpt-4o-mini total cost documented
- [ ] Cost per candidate and per promoted rule documented for both
- [ ] OMLX extraction time is reasonable (<10s per candidate)
- [ ] Results saved to `field-test/v0.1.0/cost-results.md`

---

## 5. Summary

| Task | Issue | Corpus | LLM | Cost | Duration |
|------|-------|--------|-----|------|----------|
| 30.8.1 Corpus validation | #399 | 70 trajectories | None | $0 | 5 min |
| 30.8.2 Extraction with OMLX | #400 | 30 failures | OMLX | $0 | 15 min |
| 30.8.3 Replay testing | #401 | 50 trajectories | None | $0 | 10 min |
| 30.8.4 Promotion & injection | #402 | Passing candidates | None | $0 | 10 min |
| 30.8.5 Repeat-failure reduction | #403 | 30F + 20S | OMLX | $0 | 20 min |
| 30.8.6 Cross-session memory | #404 | 10 failures | OMLX | $0 | 15 min |
| 30.8.7 Golden set regression | #405 | 10 golden | OMLX + gpt-4o-mini | ~$1 | 15 min |
| 30.8.8 Coverage measurement | #406 | 30 failures | None | $0 | 5 min |
| 30.8.9 Near-miss precision | #407 | 10 near-miss | None | $0 | 5 min |
| 30.8.10 Correction flow | #408 | 5 corrections | OMLX | $0 | 10 min |
| 30.8.11 Export to AGENTS.md | #409 | Promoted rules | None | $0 | 15 min |
| 30.8.12 Cost measurement | #410 | 30 failures | OMLX + gpt-4o-mini | ~$1 | 20 min |
| **Total** | **12** | | | **~$2** | **~2.5 hours** |

---

## 6. GitHub Issue Mapping

| Issue # | Task | Description |
|---------|------|-------------|
| #399 | 30.8.1 | Real corpus validation (70 trajectories) |
| #400 | 30.8.2 | Real corpus extraction with OMLX (local LLM) |
| #401 | 30.8.3 | Real corpus replay testing (50 trajectories) |
| #402 | 30.8.4 | Real corpus promotion and injection |
| #403 | 30.8.5 | Real corpus repeat-failure reduction (headline metric) |
| #404 | 30.8.6 | Real corpus cross-session memory |
| #405 | 30.8.7 | Real corpus golden set regression (OMLX vs gpt-4o-mini) |
| #406 | 30.8.8 | Real corpus coverage measurement |
| #407 | 30.8.9 | Real corpus near-miss precision |
| #408 | 30.8.10 | Real corpus correction flow (5 corrections) |
| #409 | 30.8.11 | Real corpus export to AGENTS.md (OpenCode) |
| #410 | 30.8.12 | Real corpus cost measurement (OMLX vs gpt-4o-mini) |

---

## 7. Prerequisites

Before running these tests, the following must be complete:

- [ ] Corpus acquisition complete per `corpus-plan.md` (70 curated trajectories)
- [ ] OMLX running locally (`omlx start` or `omlx serve <model> --port 8000`)
- [ ] CauterRule installed (`pip install -e .`)
- [ ] Phase 1 (Foundations) of main field test plan complete
- [ ] Phase 4 (Single-Agent) of main field test plan complete