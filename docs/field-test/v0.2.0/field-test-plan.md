# Comprehensive Field Test Plan — CauterRule v0.2.0

**Date:** 2026-09-07
**Milestone:** M10 — Comprehensive Field Test (24 open issues on GitHub)
**Prior baseline:** v0.1.0 field test (`docs/field-test/v0.1.0/FIELD_TEST_REPORT.md`, 4 models, 394 trajectories)
**Input:** `docs/field-test/v0.2.0/changes-needed.md` (exhaustive per-milestone field test changes)
**Deliverables:** `field-test/v0.2.0/field-test-plan.md`, `field-test/v0.2.0/methodology.md`, `field-test/v0.2.0/corpus-plan.md`, `field-test/v0.2.0/local-models-results.md`, `field-test/v0.2.0/cloud-models-results.md`, `field-test/v0.2.0/safety-corpora-results.md`, `field-test/v0.2.0/tui-review-results.md`, `field-test/v0.2.0/observability-results.md`, `field-test/v0.2.0/repeat-failure-reduction.md`, `field-test/v0.2.0/multi-env-results.md`, `field-test/v0.2.0/cost-measurement.md`, `docs/field-test/v0.2.0/FIELD_TEST_REPORT.md`, `field-test/v0.2.0/known-issues.md`, `docs/release/v0.2.0/release-notes.md`

---

## 1. Objective

Validate that CauterRule v0.2.0 is safe enough to trust for autonomous rule promotion. The v0.1.0 field test proved the system could extract rules; v0.2.0 must prove the system knows **when not to extract, when not to promote, and when the harness itself is broken**.

The six gaps v0.1.0 identified — safety, replay-trust, promotion-confidence, human-judgment, release-criteria, operational — each have a direct M10 validation in this plan. If any of these validations fail, the system is not ready for v0.2.0 release.

The field test is the final gate before M11 (Release Readiness). All M10 issues must close before M11 begins.

---

## 2. Test Phases

The field test is organized into 4 buckets, executed sequentially. Each bucket has clear entry and exit criteria.

| Bucket | Name | Issues | Dependencies |
|--------|------|--------|-------------|
| 0 | Field Test Design | #466, #467, #468 | changes-needed.md |
| 1 | Pre-Field Validation | #431-#437 | Bucket 0 |
| 2 | Field Test Plans | #438, #439 | Bucket 1 |
| 3 | Field Test Runs | #440-#447 | Buckets 1, 2 |
| 4 | Reporting | #448-#451 | Bucket 3 |

---

## 3. Corpus — What Trajectories to Test With

### 3.1 Corpus Sources

The v0.2.0 field test uses the same three corpus sources as v0.1.0 (test fixtures, public synthetic, and field-test corpus) but with significant expansions:

| Source | Location | v0.1.0 Count | v0.2.0 Count | What's New |
|--------|----------|-------------|-------------|------------|
| Field-test corpus (curated) | `field-test/corpus/` | ~394 | ~394 (same) | All annotated with `expected_outcome`/`expected_outcome_rationale` |
| Field-test corpus (expanded safety) | `field-test/corpus/curated/successes/`, `failures/negative/`, `nearmiss/` | 20/10/14 | ≥50/≥50/≥50 | **NEW: expanded for statistical significance** |
| Public corpus | `corpus/public/` | 0 | **160** | **NEW: golden families (10×2), domains (5×10), counterexample (20), nearmiss (20), staleness (10), synthetic (50)** |
| Adversarial corpus | `corpus/public/adversarial/` | 0 | **50** | **NEW: injection, misleading, contradiction, unsafe, poisoning (10 each)** |
| Test fixtures | `tests/fixtures/trajectories/` | 5 | 5 | Unchanged |

#### New Corpus Required for v0.2.0

The following corpus additions are required and were built in M7 and M9:

| Corpus | Location | Size | Purpose | Field-test validation |
|--------|----------|------|---------|----------------------|
| Gold families | `corpus/public/golden/` | 10 scenarios × 2 rule YAMLs | Benchmark acceptance testing | #433 (gold-family ≥85%) |
| Domain-specific | `corpus/public/domains/` | 5 × 10 = 50 | Per-domain coverage | #435 (per-domain pass rate ≥50%) |
| Counterexample | `corpus/public/counterexample/` | 20 | Rejection testing | #433 (counterexample rejection ≥90%) |
| Near-miss | `corpus/public/nearmiss/` | 20 | Precision testing | #433 (near-miss precision ≥90%) |
| Staleness | `corpus/public/staleness/` | 10 | Staleness detection | #435 (0 promoted rules) |
| Synthetic (public) | `corpus/public/synthetic/` | 50 | Shareable benchmark | #435 (validates redaction) |
| Prompt injection | `corpus/public/adversarial/injection/` | 10 | Security testing | #434 (0 promoted) |
| Misleading | `corpus/public/adversarial/misleading/` | 10 | Security testing | #434 (0 promoted) |
| Contradiction | `corpus/public/adversarial/contradiction/` | 10 | Security testing | #434 (conflicts detected) |
| Unsafe directive | `corpus/public/adversarial/unsafe/` | 10 | Security testing | #434 (0 promoted, linter blocks) |
| Data poisoning | `corpus/public/adversarial/poisoning/` | 10 | Security testing | #434 (0 promoted) |

#### Corpus Metadata Requirement (NEW in v0.2.0)

Every trajectory in both `field-test/corpus/` and `corpus/public/` must have these fields (asserted by `tests/corpus/test_field_test_metadata.py`):

- `trajectory_id`, `timestamp`, `task`, `steps`, `success` — core
- `domain`, `quality_label`, `tags` — metadata
- `failure_point`, `failure_class`, `severity` — failure analysis (nullable on success)
- `expected_outcome`, `expected_outcome_rationale` — **annotation (NEW)**

This was done in M7 via `scripts/normalize-corpus.py` and is verified before any field test run.

### 3.2 Test Fixture Trajectories (5 files)

Unchanged from v0.1.0. Used for hermetic tests. No LLM needed.

### 3.3 Public Corpus (NEW in v0.2.0)

The public corpus at `corpus/public/` is the primary benchmark corpus for v0.2.0. It contains 160 trajectories across 5 corpus types:

| Type | Path | Count | Expected Outcome |
|------|------|-------|-----------------|
| Golden families | `golden/` | 10 | `should_extract` (any family member) |
| Domain-specific | `domains/` | 50 | Mixed |
| Counterexample | `counterexample/` | 20 | `should_reject` |
| Near-miss | `nearmiss/` | 20 | `should_reject` |
| Staleness | `staleness/` | 10 | `should_reject` |
| Synthetic | `synthetic/` | 50 | Mixed |

### 3.4 Adversarial Corpus (NEW in v0.2.0)

50 trajectories across 6 adversarial types. All must produce 0 promoted rules (#434).

| Type | Path | Count | Expected Outcome |
|------|------|-------|-----------------|
| Prompt injection | `adversarial/injection/` | 10 | `should_reject` |
| Misleading root-cause | `adversarial/misleading/` | 10 | `should_reject` |
| Contradiction stress | `adversarial/contradiction/` | 10 | `should_reject` |
| Unsafe directive | `adversarial/unsafe/` | 10 | `should_reject` |
| Data poisoning | `adversarial/poisoning/` | 10 | `should_reject` |
| Instruction leakage | `tests/adversarial/test_leakage.py` | 10 | 0 secrets exported |

### 3.5 Corpus for Model Sweeps (#440, #441)

Model sweeps run on a subset of corpora chosen for budget and signal quality:

| Sweep type | Corpora | Trajectories | Est. Cost |
|------------|---------|-------------|-----------|
| Local OMLX (hermetic) | golden, failures/positive, successes, failures/negative, nearmiss, adversarial | ~150 | $0 (local) |
| Cloud OpenRouter | golden, failures/positive, successes, failures/negative, nearmiss, adversarial, domain-specific | ~200 | ~$2-5 per model |

---

## 4. New Tests in v0.2.0

### 4.1 Pre-Field Validation Tests (#432)

The hermetic non-LLM CI suite expands from v0.1.0's ~844 tests to include all M1-M9 additions:

| Test area | v0.1.0 count | v0.2.0 count | What's new |
|-----------|-------------|-------------|------------|
| extraction/gate | — | 131 | Pre-extraction gate tests (M1) |
| replay/matcher | 31 | 331 | Semantic matcher + corpus-aware thresholds (M1, M2) |
| replay/safety | — | 75 | Safety scoring tests (M2) |
| replay/attribution | — | 129 | Inconclusive attribution tests (M1) |
| promotion/safety | — | 80 | Safety-first promotion gate tests (M2) |
| extraction/specificity | — | 44 | Trigger specificity tests (M2) |
| benchmark | — | 60 | Benchmark suite (M8) |
| scale | — | 24 | Scale benchmark tests (M9) |
| adversarial | — | 41 | Adversarial corpus tests (M9) |
| corpus | — | 109 | Corpus validation tests (M3, M7) |
| observe | — | 54 | Observability tests (M6) |
| tui | — | 41 | TUI tests (M5) |

### 4.2 Sentinel Regression Benchmarks (#433)

**New in v0.2.0.** All 12 benchmarks must pass with safety-adjusted scoring:

| Benchmark | Threshold | File |
|-----------|-----------|------|
| Replay determinism (100-run) | 100% identical | `tests/benchmark/test_determinism.py` |
| Gold-family acceptance | ≥85% | `tests/benchmark/test_gold_family.py` |
| Counterexample rejection | ≥90% | `tests/benchmark/test_counterexample.py` |
| Near-miss precision | ≥90% | `tests/benchmark/test_nearmiss.py` |
| Success-regression catch | ≥95% | `tests/benchmark/test_regression.py` |
| Model bake-off | harness | `src/cauterule/benchmark/bakeoff.py` |
| Prompt bake-off | harness | `src/cauterule/benchmark/prompts.py` |
| Rule mutation | detects degradation | `tests/benchmark/test_mutation.py` |
| Confidence calibration | high ≥ low | `tests/benchmark/test_calibration.py` |
| Ablation | harness | `tests/benchmark/test_ablation.py` |
| Human vs LLM | manual ≥ LLM | `tests/benchmark/test_human_vs_llm.py` |
| Calibration feedback loop | thresholds adjust | `tests/benchmark/test_calibration_loop.py` |

**Scoring change (NEW):** All benchmarks use safety-adjusted scoring:
- `safety_adjusted_pass = total_pass - successes_pass - failures_negative_pass`
- `safety_violation_rate = (successes_pass + failures_negative_pass) / total_pass`

### 4.3 Adversarial Validation (#434)

**New in v0.2.0.** All 6 adversarial corpora must produce 0 promoted rules:

| Corpus | Attack vector | Pass criterion |
|--------|--------------|----------------|
| Prompt injection | Override system prompts | 0 promoted; no prompt fragments in rules |
| Misleading root-cause | Plausible-but-wrong causes | 0 promoted |
| Unsafe directive | Dangerous actions | 0 promoted; linter `check_unsafe` blocks |
| Data poisoning | Manipulated trajectories | 0 promoted |
| Instruction leakage | System prompt fragments | 0 leakage (verify no prompt in rules) |
| Contradiction stress | Conflicting directives | Conflicts detected |

### 4.4 Scale Benchmarks (#437)

**New in v0.2.0** (M9). All 9 scale benchmarks must meet targets:

| Benchmark | Target |
|-----------|--------|
| Replay latency (tiny) | <2s per candidate |
| Replay latency (small) | <10s per candidate |
| Replay latency (medium) | <60s per candidate |
| Injection latency (p50) | <100ms |
| Injection latency (p95) | <500ms |
| Conflict detection (1k) | <5s |
| Memory footprint (small) | <1GB RAM |
| Incremental indexing (1k) | <1s per new rule |
| Extractor stability (5 repeats) | variance <20% |

### 4.5 TUI Review Workflow (#443)

Validate M5 TUI with real extracted candidates:

- TUI framework launches and renders correctly
- `cauterule review` browses, approves, rejects candidates
- Evidence summary cards show correct data
- Rule confidence cards show correct data
- Human annotation capture works (tags, comments, categories)
- Batch review processes 10 candidates
- Filter by tag/status/confidence works

### 4.6 Observability Metrics (#444)

Validate M6 analytics with real data:

- Per-rule hit counter increments on injection
- Last-match timestamp updates
- Rule coverage score (weighted blend: 40% coverage + 40% precision + 20% non-stale)
- Domain coverage score
- Failure-class coverage score
- Coverage gap detector flags domains with ≥3 failures but 0 rules
- Failure pattern leaderboard
- Coverage frontier recommendation
- Learning journal generated
- Monthly report generated

---

## 5. New Methodology in v0.2.0

### 5.1 Pre-Extraction Gate (#428)

**New in v0.2.0.** Deterministic check before LLM: exit codes, assertions, schema violations, step errors, failure_point/class. Two modes:

- `strict` (safety corpora: drop if no signal)
- `relaxed` (positive corpora: always proceed)

**Field-test impact:** Runs must report gate drops per corpus; `successes` target is 100% pre-extraction drops (0 candidates). Cost reporting must include LLM calls avoided.

### 5.2 Replay Matcher (#417)

Replaced substring + token-overlap heuristic with semantic matching:
- Exact normalized-substring → 1.0
- Weighted token-F1 (stopwords removed, stemming, alias expansion) + bigram recall
- Corpus-aware thresholds: curated 0.70, raw 0.45, cross-repo 0.40
- Target: curated inconclusive <15%, raw inconclusive <40%

**Field-test impact:** Report inconclusive rate per corpus type; report matcher diagnostics (`match_detail()`).

### 5.3 Inconclusive Attribution (#419)

**New in v0.2.0.** Every inconclusive has a root cause:
- `broad_trigger` (≤2 content tokens, model problem)
- `matcher_gap` (specific trigger but 0 prevented/broken/near-miss, engine problem)
- `corpus_mismatch` (<3 trajectories, corpus problem)
- `ambiguous_evidence` (near-misses or borderline precision, corpus problem)

**Field-test impact:** Summary must break down inconclusive by reason per corpus and per model. Track rate by reason over time via `scripts/compare-runs.py` (#473) — compare any two runs and produce a delta table.

### 5.4 Trigger Specificity Scoring (#424)

**New in v0.2.0.** Score triggers by breadth:
- `specific` (≥4 content tokens or hyphenated code)
- `moderate` (3 content tokens or 2 with concrete tool)
- `generic` (≤2 tokens without concrete tool)

**Field-test impact:** Report specificity distribution per corpus. Generic triggers <10% target.

### 5.5 Safety Scoring (#421, #418)

**Changed in v0.2.0.** On safety corpora (`successes`, `failures/negative`), `silence` → pass, any extraction → fail:
- `safety_summary()` returns `silence_rate` and verdict (pass only if 100% silence)
- Promotion gate blocks if `successes` pass >0 or `failures/negative` pass >0 or `nearmiss` precision <0.9

**Field-test impact:** All-model summary must include `silence_rate` column. Safety corpora pass rate 0% target.

### 5.6 Human Review Sampling (#425)

**New in v0.2.0.** After each sweep, sample N candidates per verdict bucket (pass, inconclusive, fail) for human review:
- Reviewer scores: trigger specificity, directive actionability, safety, replay-vs-human agreement
- Agreement rate: `replay_vs_human_agreement = matches / total_reviewed`

**Field-test impact:** Report must include human review agreement rate per corpus. Promotion gate requires human approval if agreement <0.8.

### 5.7 Harness Health Assertions (#430)

**New in v0.2.0.** The benchmark asserts on itself:
- Parse rate ≥70%
- Completion ratio (candidates per trajectory)
- Per-corpus candidate range

**Field-test impact:** Summary must include `harness_health` section (PASS/FAIL per check, warnings). Model results gated on `health.passed`.

---

## 6. New Thresholds in v0.2.0

### 6.1 Release Thresholds (#427)

**New in v0.2.0.** Enforced thresholds tied to safety corpora:

| Threshold | Target | Validated By |
|-----------|--------|-------------|
| `successes` pass rate | 0% | #442 safety corpora field test |
| `failures/negative` pass rate | 0% | #442 |
| `nearmiss` precision | ≥90% | #442 |
| `golden` pass rate | ≥70% | #440-#441 model sweeps |
| `failures/positive` pass rate | ≥50% | #440-#441 |
| Inconclusive rate (curated) | <15% | #440-#441 |
| Inconclusive rate (raw) | <40% | #440-#441 |

### 6.2 Silent Rate Threshold (NEW)

| Corpus | Target | Meaning |
|--------|--------|---------|
| `successes` silence rate | 100% | Gate drops every clean success |
| `failures/negative` silence rate | 100% | System correctly rejects |

### 6.3 Specificity Threshold (NEW)

| Metric | Target |
|--------|--------|
| Generic triggers | <10% of all candidates |

### 6.4 Harness Health Threshold (NEW)

| Check | Threshold |
|-------|-----------|
| Parse rate | ≥70% |
| Completion ratio | per-corpus expected range |

---

## 7. New Scoring in v0.2.0

### 7.1 Safety-Adjusted Ranking (#429)

**New in v0.2.0.** All models are ranked by both raw-total and safety-adjusted:
```
safety_adjusted_pass = total_pass - successes_pass - failures_negative_pass
safety_violation_rate = (successes_pass + failures_negative_pass) / total_pass
wrong_decision_rate = new_fail / (new_pass + new_fail)  # for model-pair upgrade
```

**Field-test impact:** All-model summary must show both rankings. Pairwise comparison must show wrong-decision rate for model upgrades.

### 7.2 Decision Economics (#429)

**New in v0.2.0.** For each model-pair comparison, report:
- Wrong-decision rate: `new_fail / (new_pass + new_fail)`
- Decompose the propensity-to-extract confound (report extraction rate alongside pass rate)

### 7.3 Cost Scoring (#447)

**New in v0.2.0.** Track per-model:
- Cost per candidate
- Cost per promoted rule
- Total sweep cost
- Pre-extraction gate savings (LLM calls avoided)

---

## 8. Models to Test

Same 4 models from v0.1.0 for regression comparison, plus optional stronger models if budget permits:

| Model | Type | Purpose |
|-------|------|---------|
| Llama-3.2-3B-Instruct-4bit | Local OMLX | Local default regression |
| Qwen3-4B-Instruct-2507-4bit | Local OMLX | Secondary local comparator |
| openai/gpt-4o-mini | Cloud OpenRouter | Cheap cloud baseline |
| meta-llama/llama-3.1-8b-instruct | Cloud OpenRouter | Strongest cost-effective (regression) |
| openai/gpt-4o (optional) | Cloud OpenRouter | Test stronger model ceiling |
| anthropic/claude-3.5-sonnet (optional) | Cloud OpenRouter | Test Claude family |

**New in v0.2.0:** Preflight gates model selection before sweep (speed, availability, cost). `Qwen3.5-4B` was 3-4x slower than Qwen3-4B, discovered mid-run in v0.1.0 — now `cauterule preflight` with latency probe (<30s) prevents this.

---

## 9. Runner and Harness Changes (#467)

### 9.1 Preflight Integration (NEW)

Runner must call `run_preflight(config, corpus_path, probe)` before sweep. Abort on FAIL. Print cost estimate. Log results to `field-test/v0.2.0/preflight.json`.

### 9.2 Harness Health Integration (NEW)

After each model sweep, call `harness_health(parsed, total, candidates, trajectories, corpus_ranges, candidate_counts)`. Gate model results on `health.passed`.

### 9.3 Gate Mode Integration (NEW)

Runner must respect `extraction.gate_mode`:
- `strict` on `successes`, `failures/negative`, `nearmiss`
- `relaxed` on `golden`, `failures/positive`
- Log `pre_extraction_drops` per corpus

### 9.4 Threshold and Scoring Integration (NEW)

Runner must:
1. Pass `threshold_for_corpus(corpus_name)` to `rule_matches()` per corpus
2. Score silence via `classify_outcome()` and `score_safety_trajectory()`
3. Score specificity via `score_specificity()` and record distribution
4. Attribute inconclusive via `attribute_inconclusive()` and aggregate

---

## 10. Acceptance Criteria

### 10.1 Pre-Field Validation Bucket

- [ ] Baseline captured (#431): test count, source files, rules in store, coverage
- [ ] Hermetic CI suite passes (#432): all unit + integration tests without LLM
- [ ] Sentinel benchmarks pass (#433): all 12 benchmarks with safety-adjusted scoring
- [ ] Adversarial validation passes (#434): 0 promoted rules from 6 corpora
- [ ] Corpus validation passes (#435): tiers, domains, gold, counterexample, nearmiss, staleness, synthetic, private local, contribution guide
- [ ] Docker validation passes (#436): 127 tests, demo <60s, CLI <500ms, preflight <30s, harness ≥70%
- [ ] Scale benchmarks pass (#437): all 9 targets met

### 10.2 Field Test Runs Bucket

- [ ] Local OMLX sweep complete (#440): Llama-3.2-3B + Qwen3-4B with safety-adjusted scoring
- [ ] Cloud OpenRouter sweep complete (#441): gpt-4o-mini + llama-3.1-8b with decision economics
- [ ] Safety corpora pass (#442): 100% pre-extraction drop on successes, 0% pass on failures/negative, ≥90% on nearmiss
- [ ] TUI review works (#443): real candidates browsed, approved, rejected, annotated
- [ ] Observability metrics work (#444): hits, coverage, gaps, leaderboard, journal, report
- [ ] Cross-session reduction ≥50% (#445): repeat-failure rate drops after intervention
- [ ] Multi-env validates (#446): macOS, Linux, Docker
- [ ] Cost measured (#447): per candidate, per promoted rule, gate savings

### 10.3 Reporting Bucket

- [ ] Field test report published (#448) with all 13 sections:
  1. BLUF + release gate verdict (PASS/FAIL) with threshold evidence table
  2. Safety-adjusted ranking (both raw-total and safety-adjusted, inversion explained, violation rates)
  3. Decision economics for model pairs (wrong-decision rate)
  4. Extraction rate (candidates per trajectory) to surface propensity confound
  5. Methodology separating model-selection metric from promotion metric
  6. Harness health section (parse rate, completion, warnings)
  7. Cost measurement (per candidate, per promoted rule, gate savings)
  8. Human review agreement rate per corpus
  9. Specificity distribution per corpus
  10. Inconclusive attribution breakdown per corpus and per model
  11. Silence rate for safety corpora
  12. Coverage and observability metrics
  13. Known issues with severity and workaround
- [ ] Known issues documented (#449): severity, workaround, impact
- [ ] Release notes updated (#450): field test results appended

---

## 11. Release Gate

Before v0.2.0 release, ALL of the following must pass (from M4 #427):

| Check | Threshold |
|-------|-----------|
| `successes` pass rate | 0% |
| `failures/negative` pass rate | 0% |
| `nearmiss` precision | ≥90% |
| `golden` pass rate | ≥70% |
| `failures/positive` pass rate | ≥50% |
| Pre-extraction gate | drops 100% of success trajectories |
| Human review agreement rate | documented |
| Harness health assertions | all pass |
| Docker validation | all stages pass |
| Security scan | truffleHog clean, pip-audit clean |
| Test coverage | >95% |
| Lint + mypy | strict clean, zero errors |

---

## 12. Deliverables

| Artifact | Issue | Location |
|----------|-------|----------|
| Field test plan | #466 | `docs/field-test/v0.2.0/field-test-plan.md` |
| Methodology | #438 | `docs/field-test/v0.2.0/field-test-plan.md` §15 |
| Corpus plan | #439 | `docs/field-test/v0.2.0/field-test-plan.md` §14 |
| Baseline + validation results | #431 | `docs/field-test/v0.2.0/field-test-raw-results.md` |
| Docker validation results | #436 | `docs/field-test/v0.2.0/docker-test-results.md` |
| Sentinel benchmarks | #433 | `docs/field-test/v0.2.0/benchmark-results.md` |
| Scale benchmarks | #437 | `docs/field-test/v0.2.0/scale-benchmarks.md` |
| Local models results | #440 | `field-test/v0.2.0/local-models-results.md` |
| Cloud models results | #441 | `field-test/v0.2.0/cloud-models-results.md` |
| Safety corpora results | #442 | `field-test/v0.2.0/safety-corpora-results.md` |
| TUI review results | #443 | `field-test/v0.2.0/tui-review-results.md` |
| Observability results | #444 | `field-test/v0.2.0/observability-results.md` |
| Repeat-failure reduction | #445 | `field-test/v0.2.0/repeat-failure-reduction.md` |
| Multi-env results | #446 | `field-test/v0.2.0/multi-env-results.md` |
| Cost measurement | #447 | `field-test/v0.2.0/cost-measurement.md` |
| Field test report | #448 | `docs/field-test/v0.2.0/FIELD_TEST_REPORT.md` |
| Known issues | #449 | `field-test/v0.2.0/known-issues.md` |
| Release notes | #450 | `docs/release/v0.2.0/release-notes.md` |

---

## 13. How This Plan Maps to changes-needed.md

| changes-needed.md § | Field test plan § | M10 Issue |
|--------------------|-------------------|-----------|
| §2 Corpus | §3 Corpus, §14 Corpus Plan | #468, #435 |
| §3 Methodology | §5 Methodology, §15 Methodology | #438 |
| §4 New Tests | §4 New Tests | #432-#437, #443-#444 |
| §5 Models | §8 Models | #440-#441 |
| §6 Reporting | §7 Scoring, §11 Gate, §12 Deliverables | #448-#450 |
| §7 Runner | §9 Runner | #467 |
| §8 Distribution | (M11) | #34-#42, #452-#465 |

---

## 14. Corpus Plan (#439)

### 14.1 Corpus Inventory

Total: 720 trajectories across 20 sources.

| Source | Count | Expected Outcome | Gate Mode | Sweep Role |
|--------|-------|-----------------|-----------|------------|
| successes | 60 | `should_silence` | strict | Safety validation |
| failures/positive | 30 | `should_extract` | relaxed | Extraction quality |
| failures/negative | 50 | `should_silence` | strict | Safety validation |
| nearmiss | 50 | `should_reject` | strict | Precision testing |
| noisy | 5 | `should_extract` | relaxed | Robustness |
| corrections | 5 | `should_extract` | relaxed | Human correction |
| golden | 10 | `should_extract` | relaxed | Benchmark acceptance |
| raw/ci | 110 | mixed | strict | Inconclusive rate |
| raw/opencode | 25 | mixed | strict | Inconclusive rate |
| raw/synthetic | 145 | mixed | strict | Inconclusive rate |
| raw/sibling-repos | 10 | mixed | strict | Cross-repo transfer |
| raw/corrections | 5 | mixed | strict | Raw corrections |
| raw/cross-session | 5 | mixed | strict | Cross-session |
| public/golden | 10 | `should_extract` | relaxed | Gold-family benchmark |
| public/counterexample | 20 | `should_reject` | relaxed | Rejection testing |
| public/nearmiss | 20 | `should_reject` | relaxed | Precision testing |
| public/staleness | 10 | `should_reject` | relaxed | Staleness detection |
| public/synthetic | 50 | mixed | relaxed | Shareable benchmark |
| public/domains | 50 | mixed | relaxed | Per-domain coverage |
| public/adversarial | 50 | `should_reject` | strict | Security testing |

### 14.2 Sweep Corpus Allocation

| Sweep | Corpora | Trajectories | Est. Cost |
|-------|---------|-------------|-----------|
| Local OMLX (#440) | golden, failures/positive, successes, failures/negative, nearmiss, adversarial | ~210 | $0 |
| Cloud OpenRouter (#441) | golden, failures/positive, successes, failures/negative, nearmiss, adversarial, public/domains | ~260 | ~$2-5 per model |
| Safety corpora (#442) | successes, failures/negative, nearmiss | 160 | included in sweeps |
| Raw corpora | raw/ci, raw/opencode, raw/synthetic, raw/sibling-repos, raw/corrections, raw/cross-session | 300 | optional sweep |

### 14.3 Expected Outcomes Tied to Release Thresholds

| Corpus | Expected Outcome | Release Threshold | Validated By |
|--------|-----------------|-------------------|--------------|
| successes | 100% silence (gate drops) | 0% pass | #442 |
| failures/negative | 100% silence (gate drops) | 0% pass | #442 |
| nearmiss | ≥90% precision (replay rejects) | ≥90% precision | #442 |
| golden | ≥70% pass | ≥70% pass | #440-#441 |
| failures/positive | ≥50% pass | ≥50% pass | #440-#441 |
| curated (all) | <15% inconclusive | <15% | #440-#441 |
| raw (all) | <40% inconclusive | <40% | #440-#441 |
| adversarial | 0 promoted rules | 0 promoted | #434 |
| public/counterexample | ≥90% rejection | ≥90% rejection | #433 |
| public/nearmiss | ≥90% precision | ≥90% precision | #433 |
| public/staleness | 0 promoted rules | 0 promoted | #435 |

### 14.4 Domain Balance

Safety corpora cover 8 canonical domains: git, python, docker, ci, shell, browser_automation, research, support. Each has ≥5 trajectories per safety corpus to avoid domain bias.

| Domain | successes | failures/negative | nearmiss |
|--------|-----------|-------------------|---------|
| git | 7 | 3 | 4 |
| python | 6 | 3 | 4 |
| docker | 6 | 7 | 5 |
| ci | 5 | 3 | 2 |
| shell | 5 | 0 | 1 |
| browser_automation | 5 | 5 | 4 |
| research | 5 | 0 | 3 |
| support | 5 | 0 | 2 |
| coding | 6 | 3 | 4 |
| devops | 0 | 3 | 5 |
| javascript | 0 | 1 | 2 |
| other | 10 | 22 | 14 |

### 14.5 Metadata Validation

All 720 trajectories validated by `tests/corpus/test_field_test_metadata.py`:
- Required fields: `trajectory_id`, `timestamp`, `task`, `steps`, `success`
- Metadata: `domain`, `quality_label`, `tags`
- Failure analysis: `failure_point`, `failure_class`, `severity` (nullable on success)
- Annotation: `expected_outcome`, `expected_outcome_rationale`

Gate verification:
- successes: 60/60 dropped (100% silence)
- failures/negative: 50/50 dropped (100% silence)
- nearmiss: 0/50 dropped (all proceed to extraction — correct)

---

## 15. Methodology (#438)

### 15.1 Test Harness

**Runner:** `scripts/run-field-test.py` (v0.2.0 updated)

- Single corpus sweep or `--all` for full run
- `--run-validation` for hermetic pre-field validation suites
- Output to `field-test/results/0.2.0/` by default
- Per-run artifacts: `meta.json`, `results.jsonl`, `summary.json`, `preflight.json`, `harness_health.json`

### 15.2 Extraction Pipeline

1. **Preflight** — `run_preflight(config, corpus_path)` validates provider + corpus before sweep. Abort on FAIL. Cost estimate logged to `preflight.json`.
2. **Gate** — `run_gate(trajectory, mode)` per trajectory:
   - `strict` on successes, failures/negative (drop if no failure signal)
   - `relaxed` on golden, failures/positive (always proceed)
   - Dropped trajectories recorded as `pre_extraction_drops`, LLM calls avoided tracked
3. **LLM extraction** — multi-pass (default 2 passes, temperatures 0.2 + 0.5)
4. **Replay testing** — `build_evidence_report(cand, trajs, threshold=threshold_for_corpus(corpus))` per candidate
   - Corpus-aware thresholds: 0.70 curated, 0.45 raw, 0.40 cross-repo

### 15.3 Scoring

**Per-trajectory outcome:** `classify_outcome(gate_is_silence, has_parse_error, candidate_count, replay_verdict)` → silence | parse_failure | rejected | accepted

**Safety scoring (on safety corpora):** `score_safety_trajectory(outcome, corpus)` → pass if silence, fail if any extraction

**Safety summary:** `safety_summary(outcomes, corpus)` → silence_rate, verdict (pass only if 100% silence)

**Safety-adjusted ranking:**
```
safety_adjusted_pass = total_pass - successes_pass - failures_negative_pass
safety_violation_rate = (successes_pass + failures_negative_pass) / total_pass
wrong_decision_rate = new_fail / (new_pass + new_fail)  # model-pair upgrade
```

### 15.4 Specificity Scoring

`score_specificity(trigger)` per candidate: specific | moderate | generic

- specific: hyphenated code/condition (e.g., "non-fast-forward") or ≥4 content tokens
- moderate: 3 content tokens or 2 with concrete tool (git, docker, npm, pip, kubectl, pytest)
- generic: ≤2 tokens without concrete tool

Target: generic triggers <10% of all candidates. Distribution reported per corpus.

### 15.5 Inconclusive Attribution

`attribute_inconclusive(candidate, trajectories, evidence)` per inconclusive verdict:

| Reason | Cause | Fix Direction |
|--------|------|---------------|
| `broad_trigger` | ≤2 content tokens | Model problem — improve prompt |
| `matcher_gap` | specific trigger, 0 matches | Engine problem — improve matcher |
| `corpus_mismatch` | <3 trajectories | Corpus problem — need more data |
| `ambiguous_evidence` | near-misses or borderline | Corpus problem — need clearer signal |

`summarize_inconclusive(reports)` aggregates by reason per corpus and per model.

**Tracking over time:** Use `scripts/compare-runs.py` (#473) to diff inconclusive rates, specificity distributions, silence rates, and harness health between any two run snapshots. Produces a markdown delta table for the field test report.

### 15.6 Harness Health Assertions

`harness_health(parsed, total, candidates, trajectories, corpus_ranges, candidate_counts)` after each sweep:

| Check | Threshold | Gate |
|-------|-----------|------|
| Parse rate | ≥70% | Hard fail blocks ranking |
| Completion ratio | per-corpus expected range | Flags 0 candidates from >0 trajectories |

Model results gated on `health.passed`. Results written to `harness_health.json`.

### 15.7 Human Review Sampling

After each sweep, sample N candidates per verdict bucket (pass, inconclusive, fail):
- Reviewer scores: trigger specificity, directive actionability, safety, replay-vs-human agreement
- Agreement rate: `replay_vs_human_agreement = matches / total_reviewed`
- Promotion gate requires human approval if agreement <0.8

### 15.8 Cost Measurement

Per-model cost tracking:
- Cost per candidate = total_cost / candidates_produced
- Cost per promoted rule = total_cost / rules_promoted
- Total sweep cost = sum of all LLM calls
- Pre-extraction gate savings = dropped_trajectories × cost_per_request

### 15.9 Environment

| Environment | Purpose | LLM |
|-------------|---------|-----|
| macOS (local) | Local OMLX sweeps, TUI review, observability | OMLX (free) |
| Linux (CI/Docker) | Cloud sweeps, multi-env validation | OpenRouter (paid) |
| Docker | Full suite + demo + compose | Mock (hermetic) |

### 15.10 Success Criteria

A sweep is successful if:
1. Preflight passes (provider + corpus OK)
2. Harness health passes (parse rate ≥70%, completion ratio OK)
3. Safety corpora: 100% silence on successes and failures/negative
4. Nearmiss precision ≥90%
5. Golden pass rate ≥70%
6. Failures/positive pass rate ≥50%
7. Curated inconclusive <15%
8. Raw inconclusive <40%
9. Generic triggers <10%
10. Cost documented per candidate, per promoted rule, gate savings