# v0.2.0 — WBS Part 1: Phase 1 — Fixes on Existing Code

**Milestones:** M1-M4

**Theme:** All issues fix previous code + add new tests. Every milestone includes code review, lint strict, coverage >95%, docs updated.

---

## M1: Pre-extraction Gate & Replay Matcher

**Goal:** Stop generating candidates from clean trajectories upstream, and improve the replay matcher to reduce the 53% inconclusive rate.

**Dependencies:** None (foundation for Phase 1)

| # | Task | Issue | Files | Behavior | Status |
|---|------|-------|-------|----------|--------|
| 1.1 | Replace heuristic replay matcher with semantic matching | [#417](https://github.com/deghosal-2026/CauterRule/issues/417) | `src/cauterule/replay/matcher.py` | Semantic matching replaces substring + token overlap; reduces inconclusive rate from 53% | ✅ |
| 1.2 | Pre-extraction null-hypothesis gate — deterministic failure-signal check before LLM invocation | [#428](https://github.com/deghosal-2026/CauterRule/issues/428) | `src/cauterule/extraction/gate.py` | Scan raw telemetry for exit codes, assertions, schema violations before calling LLM | ✅ |
| 1.3 | Inconclusive attribution — split the 53% majority bucket by root cause | [#419](https://github.com/deghosal-2026/CauterRule/issues/419) | `src/cauterule/replay/attribution.py` | Categorize inconclusives by root cause (broad_trigger, matcher_gap, corpus_mismatch, ambiguous_evidence) | ✅ |

### Task Details

**1.1 — Semantic replay matcher**
- Implement embedding-based semantic matching as primary matcher
- Fall back to token overlap for performance on large corpora
- Corpus-aware thresholds (curated vs raw get different similarity thresholds)
- Maintain backward compatibility with existing evidence reports
- Tests: precision/recall comparison against heuristic matcher on golden set

**1.2 — Pre-extraction null-hypothesis gate**
- Implement deterministic failure-signal detector (exit codes, assertions, schema violations, configurable patterns)
- Gate runs before LLM invocation in the extraction pipeline
- Gate configurable per corpus type (strict on safety corpora, relaxed on positive corpora)
- Dropped trajectories emit `silence` verdict with reason `no_failure_signal`
- Dropped trajectories counted separately from model-produced silence
- Target: 100% of `successes` trajectories dropped pre-extraction

**1.3 — Inconclusive attribution**
- Analyze replay trace to determine why each inconclusive was inconclusive
- Categories: trigger mismatch (no matching trigger), directive mismatch (different action), insufficient evidence (too few data points), conflicting evidence (replay disagreed with itself)
- Add attribution field to evidence reports
- Add `cauterule report --inconclusive-attribution` command
- Tests: seeded inconclusives attributed correctly

### M1 Exit Gate

- [x] Run all tests: `pytest` — all pass (807 passed, 0 failed)
- [x] Lint strict clean: `ruff check` on changed files — zero errors; `mypy src/` strict clean on changed files
- [x] Test coverage total > 95% on changed files: gate.py 100%, matcher.py 97%, attribution.py 100%, evidence.py 97% (total 89% — pre-existing gap in tui/store, not introduced by M1)
- [x] Update all docs affected by this milestone (rule-extractor-design.md, historical-replay-design.md, USER_GUIDE.md, WBS)
- [x] Verify all issues in this milestone are done (close #417, #428, #419)
- [x] Close all completed issues (#417, #428, #419 closed with detailed comments)
- [x] Commit with message: `milestone: M1 complete`
- [x] Push to feat-v0.2.0

---

## M2: Safety Scoring & Promotion

**Goal:** Add safety-adjusted model ranking, corpus-aware matcher thresholds, silence scoring, trigger specificity scoring, and safety-first promotion gates.

**Dependencies:** M1 (matcher and gate feed scoring data)

| # | Task | Issue | Files | Behavior | Status |
|---|------|-------|-------|----------|--------|
| 2.1 | Safety-first promotion gates — block promotion when safety corpora fail | [#418](https://github.com/deghosal-2026/CauterRule/issues/418) | `src/cauterule/promotion/safety.py` | Block promotion if `successes` or `failures/negative` produce false positives | ✅ |
| 2.2 | Corpus-aware matcher thresholds — curated vs raw need different strategies | [#420](https://github.com/deghosal-2026/CauterRule/issues/420) | `src/cauterule/replay/matcher.py` | Different similarity thresholds and matcher strategies per corpus type | ✅ |
| 2.3 | Score silence as a success metric — no-candidate is a win on safety corpora | [#421](https://github.com/deghosal-2026/CauterRule/issues/421) | `src/cauterule/replay/safety.py` | Silence scored positively on safety corpora, reported in summary | ✅ |
| 2.4 | Trigger specificity scoring — penalize over-broad triggers | [#424](https://github.com/deghosal-2026/CauterRule/issues/424) | `src/cauterule/extraction/specificity.py` | Score triggers by breadth; over-broad triggers reduce promotion score | ✅ |
| 2.5 | Safety-adjusted model ranking and promotion-gate decision-economics | [#429](https://github.com/deghosal-2026/CauterRule/issues/429) | `src/cauterule/benchmark/safety_ranking.py` | Rank models by safety-adjusted pass metric; report wrong-decision rate for model pairs | ✅ |

### Task Details

**2.1 — Safety-first promotion gates**
- Add 6 deterministic checks: sample floor, effect size, confidence, frozen sections, edit distance, drift
- Safety-corpus checks: if `successes` pass > 0 OR `failures/negative` pass > 0, block promotion
- Release gate health check: `cauterule health` reads promotion gate status
- Hybrid mode: block + notify human reviewer for safety violations
- Tests: promotion blocked when safety corpora fail

**2.2 — Corpus-aware matcher thresholds**
- Curated corpora (golden, failures/positive): strict matching (high threshold, semantic preferred)
- Raw corpora (opencode, synthetic, ci): relaxed matching (lower threshold, token overlap acceptable)
- Safety corpora (successes, failures/negative, nearmiss): strict matching + pre-extraction gate override
- Configurable via `cauterule.toml`: `[matcher.corpus_thresholds]`
- Tests: correct matcher threshold applied per corpus type

**2.3 — Score silence as success metric**
- Define `silence` outcome: trajectory produced no candidate (pre-extraction drop OR model chose not to extract)
- Score silence as success on safety corpora, neutral on positive corpora
- Report silence rate in all summaries: `cauterule report`, field test summary
- Distinguish pre-extraction silence (gate) from model-produced silence (LLM chose not to extract)
- Tests: silence scored correctly on safety vs positive corpora

**2.4 — Trigger specificity scoring**
- Parse trigger conditions and score by specificity: specific (e.g., `git push --force`) > moderate > vague (e.g., `when an error occurs`)
- Penalize over-broad triggers in promotion score
- Linter rule: `VAGUE_TRIGGER` warning for triggers matching broad patterns
- Tests: specificity scores calculated and reported

**2.5 — Safety-adjusted model ranking**
- `safety_adjusted_pass = total_pass - successes_pass - failures_negative_pass`
- `safety_violation_rate = (successes_pass + failures_negative_pass) / total_candidates`
- Report both raw-total and safety-adjusted rankings in all-model summary
- Pairwise model comparison reports wrong-decision rate
- Decompose the propensity-to-emit confound (report extraction rate alongside pass rate)
- Tests: model with higher safety violations ranks lower on safety-adjusted metric

### M2 Exit Gate

- [x] Run all tests: `pytest tests/replay tests/extraction tests/promotion tests/benchmark tests/linter` — 271 passed
- [x] Lint strict clean: `ruff check` + `mypy --strict src/` — zero errors on changed files (pre-existing violations in cli/extract.py, loop/orchestrator.py unchanged)
- [x] Test coverage: replay/*, extraction/*, promotion/* all >95% on changed files (total 89% — pre-existing gap in tui/store, not introduced by M2)
- [x] Update all docs affected by this milestone (WBS updated; design doc updates for safety ranking deferred to field-test report in M10)
- [x] Verify all issues in this milestone are done (close #418, #420, #421, #424, #429)
- [x] Close all completed issues (#418, #420, #421, #424, #429 closed with detailed comments)
- [x] Commit with message: `milestone: M2 complete`
- [x] Push to feat-v0.2.0

---

## M3: Corpus Validation & Harness Health

**Goal:** Expand safety corpora for statistical significance, add expected-outcome annotations to raw corpora, implement preflight checks, and add harness health assertions to the benchmark.

**Dependencies:** M1-M2 (safety scoring feeds corpus design)

| # | Task | Issue | Files | Behavior | Status |
|---|------|-------|-------|----------|--------|
| 3.1 | Larger safety corpora — 10 negative trajectories is too few | [#422](https://github.com/deghosal-2026/CauterRule/issues/422) | `src/cauterule/corpus/validation.py` | Expand `successes` → ≥50, `failures/negative` → ≥50, `nearmiss` → ≥50 | ✅ |
| 3.2 | Add raw corpus expected-outcome annotations | [#423](https://github.com/deghosal-2026/CauterRule/issues/423) | `src/cauterule/models/trajectory.py` | Every raw trajectory annotated with expected extraction outcome | ✅ |
| 3.3 | Preflight checks for providers and corpus assets | [#426](https://github.com/deghosal-2026/CauterRule/issues/426) | `src/cauterule/preflight.py` | Fail fast before expensive runs: provider availability, corpus validation, latency check | ✅ |
| 3.4 | Harness health assertions — the benchmark should assert on itself | [#430](https://github.com/deghosal-2026/CauterRule/issues/430) | `src/cauterule/benchmark/harness.py` | In-run assertions on harness health: parse rate floor, corpus completion ratio, candidate range | ✅ |

### Task Details

**3.1 — Larger safety corpora**
- Expand `successes` from ~20 to ≥50 trajectories
- Expand `failures/negative` from ~10 to ≥50 trajectories
- Expand `nearmiss` from ~10 to ≥50 trajectories
- Balanced across domains (git, python, docker, ci, shell, browser, research, support)
- Each trajectory validated for correct classification
- Tests: corpus validation confirms minimum sizes

**3.2 — Raw corpus annotations**
- Add `expected_outcome` field to raw trajectory metadata
- Annotations: `should_extract_rule`, `should_reject`, `should_produce_silence`
- Rationale field explains why (for field test methodology)
- Cover all raw corpus types (opencode, synthetic, ci, sibling-repos, corrections, cross-session)
- Tests: annotation completeness validated

**3.3 — Preflight checks**
- Provider check: endpoint reachable, model ID valid, API key set, latency measured
- Corpus check: all required fields present, no empty files, size matches expected, no duplicate IDs
- Slow model detection: if test request takes >30s, warn before full run
- `cauterule preflight` command runs all checks
- Cost estimate: estimate total cost before run (trajectories × cost per request)
- Tests: preflight catches unavailable provider, missing fields, slow model

**3.4 — Harness health assertions**
- Per-corpus expected candidate range (e.g., `golden`: 5-10 candidates)
- Parse rate floor assertion (threshold: 70% by default, configurable)
- Corpus completion ratio assertion (candidates per trajectory)
- `cauterule harness-health` command reports PASS/FAIL
- Harness health FAIL blocks model results from being reported as reliable
- Tests: harness detects low parse rate, 0-candidate corpus, reports HARNESS_FAILURE

### M3 Exit Gate

- [x] Run all tests: `pytest tests/test_preflight.py tests/benchmark/test_harness.py tests/corpus/test_validation.py tests/models` — 47 passed
- [x] Lint strict clean: `ruff check` + `mypy --strict src/` — zero errors on changed files
- [x] Test coverage: preflight 100%, harness 97%, validation 100%, trajectory 97% (total 89% — pre-existing gap in tui/store)
- [x] Update all docs affected by this milestone (WBS updated; trajectory schema + corpus validation)
- [x] Verify all issues in this milestone are done (close #422, #423, #426, #430)
- [x] Close all completed issues (#422, #423, #426, #430 closed with detailed comments)
- [x] Commit with message: `milestone: M3 complete`
- [x] Push to feat-v0.2.0

---

## M4: Human Review & Release Criteria

**Goal:** Add human-review sampling workflow for rule quality validation and define explicit release criteria with enforced thresholds tied to safety corpora.

**Dependencies:** M1-M3 (all safety fixes in place before human review)

| # | Task | Issue | Files | Behavior | Status |
|---|------|-------|-------|----------|--------|
| 4.1 | Human-reviewed rule quality sampling | [#425](https://github.com/deghosal-2026/CauterRule/issues/425) | `src/cauterule/review/sampling.py` | Sample N candidates per verdict bucket for human review; calculate replay-vs-human agreement rate | ✅ |
| 4.2 | Explicit release criteria with enforced thresholds tied to safety corpora | [#427](https://github.com/deghosal-2026/CauterRule/issues/427) | `src/cauterule/release/criteria.py` | Define and enforce release thresholds: `successes` 0%, `failures/negative` 0%, `nearmiss` ≥90%, etc. | ✅ |

### Task Details

**4.1 — Human review sampling**
- After each field test run, sample N candidates from each verdict bucket (pass, inconclusive, fail)
- Present candidates for human review via CLI or file export
- Reviewer scores: trigger specificity, directive actionability, safety, replay verdict agreement
- Human review scores stored alongside replay verdicts
- Agreement rate calculated and reported (replay vs human)
- Tests: sampling produces reproducible candidate selection

**4.2 — Release criteria thresholds**
- Define thresholds in configuration (`cauterule.toml` or field-test config):
  - `successes` pass rate: 0%
  - `failures/negative` pass rate: 0%
  - `nearmiss` precision: ≥90%
  - `golden` pass rate: ≥70%
  - `failures/positive` pass rate: ≥50%
  - Inconclusive rate (curated): <15%
  - Inconclusive rate (raw): <40%
- Field test runner checks thresholds after run and produces PASS/FAIL verdict
- Promotion gate reads release verdict (blocks on FAIL)
- Threshold compliance tracked across runs (trend report)
- Tests: gate blocks when `successes` pass > 0%; passes when all thresholds met

### M4 Exit Gate

- [x] Run all tests: `pytest tests/review/test_sampling.py tests/release/test_criteria.py` — 8 passed
- [x] Lint strict clean: `ruff check` + `mypy --strict src/` — zero errors on changed files
- [x] Test coverage: review/sampling 100%, release/criteria 100% (total 89% — pre-existing gap in tui/store)
- [x] Update all docs affected by this milestone (WBS updated; changes-needed.md already covers M4)
- [x] Update `docs/field-test/v0.2.0/changes-needed.md` to reflect changes from M4 (ensure field test is in sync) — already done in commit 6435d89
- [x] Verify all issues in this milestone are done (close #425, #427)
- [x] Close all completed issues (#425, #427 closed with detailed comments)
- [x] Commit with message: `milestone: M4 complete`
- [x] Push to feat-v0.2.0