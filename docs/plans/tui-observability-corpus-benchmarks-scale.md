# M21-M25: TUI Review, Observability, Corpus, Benchmarks & Scale Implementation Plan

**Goal:** Build 5 remaining infrastructure milestones (M21-M25, 49 tasks) in parallel.

**Architecture:** 5 independent modules — TUI (Textual), observability (hit counters/coverage scores), corpus (tiered trajectories), benchmarks (hermetic pytest), scale benchmarks (latency/capacity).

**Tech Stack:** Python 3.11+, Textual>=1.0, Click, YAML, pytest, mypy strict, ruff

**Global Constraints:**
- All new code: mypy strict, ruff clean, ANN-annotated
- All new tests: pytest with cov
- No LLM calls in CI tests (mock or hermetic fixtures)
- Follow existing patterns: frozen dataclasses, `to_dict`/`from_dict`, `_require_nonblank`
- `textual>=1.0` added to `[project.dependencies]`

---

## Milestone M21: TUI Review (7 tasks)

**Module:** `src/cauterule/tui/` — Textual-based terminal UI for `cauterule review`

### Task 21.1: TUI Framework

**Files:** Create `src/cauterule/tui/__init__.py`, `src/cauterule/tui/app.py`

- [ ] **Create `src/cauterule/tui/__init__.py`** — empty init
- [ ] **Create `src/cauterule/tui/app.py`** — Textual `App` subclass with basic screen routing, keybindings (q=quit, r=review, f=filter, a=approve, x=reject), inherits from `textual.app.App`
- [ ] **Write test** `tests/tui/test_app.py` — test app instantiates, test keybindings registered
- [ ] **Add `textual>=1.0` to `pyproject.toml` `[project.dependencies]`**
- [ ] **Run: `pytest tests/tui/test_app.py -v`** — PASS

### Task 21.2: Review Screen

**Files:** Create `src/cauterule/tui/review.py`

- [ ] **Create `src/cauterule/tui/review.py`** — `ReviewScreen` Textual `Screen` showing pending candidate queue from store, approve/reject actions
- [ ] **Write test** `tests/tui/test_review.py` — test screen loads with empty queue, test mock candidate renders
- [ ] **Run** `pytest tests/tui/test_review.py -v` — PASS

### Task 21.3: Evidence Summary Cards

**Files:** Create `src/cauterule/tui/cards.py`

- [ ] **Create `src/cauterule/tui/cards.py`** — `EvidenceCard` widget showing "Prevented N failures, broke 0 successes" summary
- [ ] **Write test** `tests/tui/test_cards.py` — test card renders with mock evidence
- [ ] **Run** `pytest tests/tui/test_cards.py -v` — PASS

### Task 21.4: Rule Confidence Cards

**Files:** Create `src/cauterule/tui/confidence.py`

- [ ] **Create `src/cauterule/tui/confidence.py`** — `ConfidenceCard` widget showing confidence, prevented/broken counts, last hit, tags
- [ ] **Write test** `tests/tui/test_confidence.py` — test card renders with mock rule
- [ ] **Run** `pytest tests/tui/test_confidence.py -v` — PASS

### Task 21.5: Human Annotation Capture

**Files:** Create `src/cauterule/tui/annotate.py`

- [ ] **Create `src/cauterule/tui/annotate.py`** — `AnnotationScreen` with tag input, comment field, failure category selector
- [ ] **Write test** `tests/tui/test_annotate.py` — test annotation screen renders, test tag submission
- [ ] **Run** `pytest tests/tui/test_annotate.py -v` — PASS

### Task 21.6: Batch Review Mode

**Files:** Create `src/cauterule/tui/batch.py`

- [ ] **Create `src/cauterule/tui/batch.py`** — `BatchReviewScreen` showing 10 candidates at once with approve/reject-all
- [ ] **Write test** `tests/tui/test_batch.py` — test batch review with 10 mock candidates
- [ ] **Run** `pytest tests/tui/test_batch.py -v` — PASS

### Task 21.7: Filter by Tag/Status/Confidence

**Files:** Create `src/cauterule/tui/filter.py`

- [ ] **Create `src/cauterule/tui/filter.py`** — `FilterWidget` with tag, status, confidence range inputs
- [ ] **Write test** `tests/tui/test_filter.py` — test filter applies correctly
- [ ] **Run** `pytest tests/tui/test_filter.py -v` — PASS

---

## Milestone M22: Observability (10 tasks)

**Module:** `src/cauterule/observe/`

### Task 22.1: Per-rule Hit Counter

**Files:** Create `src/cauterule/observe/__init__.py`, `src/cauterule/observe/hits.py`

- [ ] **Create `src/cauterule/observe/__init__.py`** — empty init
- [ ] **Create `src/cauterule/observe/hits.py`** — `get_hit_counts(store: StoreManager) -> dict[str, int]` reads `rule.hit_count` for all rules
- [ ] **Write test** `tests/observe/test_hits.py` — test returns counts for seeded rules
- [ ] **Run** `pytest tests/observe/test_hits.py -v` — PASS

### Task 22.2: Last-match Timestamp

**Files:** Create `src/cauterule/observe/timestamps.py`

- [ ] **Create `src/cauterule/observe/timestamps.py`** — `update_last_match(store: StoreManager, rule_id: str)` updates rule's `last_match` field
- [ ] **Write test** `tests/observe/test_timestamps.py` — test timestamp updates after injection
- [ ] **Run** `pytest tests/observe/test_timestamps.py -v` — PASS

### Task 22.3: Failure Pattern Leaderboard

**Files:** Create `src/cauterule/observe/leaderboard.py`

- [ ] **Create `src/cauterule/observe/leaderboard.py`** — `get_leaderboard(store: StoreManager) -> dict` returns most prevented failures, most broken successes, top gaps
- [ ] **Write test** `tests/observe/test_leaderboard.py` — test leaderboard ranks correctly
- [ ] **Run** `pytest tests/observe/test_leaderboard.py -v` — PASS

### Task 22.4: Coverage Gap Detector

**Files:** Create `src/cauterule/observe/coverage_gap.py`

- [ ] **Create `src/cauterule/observe/coverage_gap.py`** — `find_coverage_gaps(store: StoreManager, trajectories: list[Trajectory]) -> list[str]` domains with repeated failures but no matching rules
- [ ] **Write test** `tests/observe/test_coverage_gap.py` — test detects gaps from failure data
- [ ] **Run** `pytest tests/observe/test_coverage_gap.py -v` — PASS

### Task 22.5: Rule Coverage Score

**Files:** Create `src/cauterule/observe/coverage_score.py`

- [ ] **Create `src/cauterule/observe/coverage_score.py`** — `compute_coverage_score(store: StoreManager) -> float` weighted blend of coverage%, precision%, stale%
- [ ] **Write test** `tests/observe/test_coverage_score.py` — test score computation
- [ ] **Run** `pytest tests/observe/test_coverage_score.py -v` — PASS

### Task 22.6: Learning Journal

**Files:** Create `src/cauterule/observe/journal.py`

- [ ] **Create `src/cauterule/observe/journal.py`** — `generate_journal(store: StoreManager) -> str` auto-generate markdown log: failure → rule → replay → promotion
- [ ] **Write test** `tests/observe/test_journal.py` — test generates markdown with mock data
- [ ] **Run** `pytest tests/observe/test_journal.py -v` — PASS

### Task 22.7: Domain Coverage Score

**Files:** Create `src/cauterule/observe/domain_coverage.py`

- [ ] **Create `src/cauterule/observe/domain_coverage.py`** — `domain_coverage(store: StoreManager) -> dict[str, float]` coverage by domain
- [ ] **Write test** `tests/observe/test_domain_coverage.py` — test coverage per domain
- [ ] **Run** `pytest tests/observe/test_domain_coverage.py -v` — PASS

### Task 22.8: Failure-class Coverage Score

**Files:** Create `src/cauterule/observe/class_coverage.py`

- [ ] **Create `src/cauterule/observe/class_coverage.py`** — `class_coverage(store: StoreManager, trajectories: list[Trajectory]) -> dict[str, float]` % of recurring failure classes with validated rules
- [ ] **Write test** `tests/observe/test_class_coverage.py` — test coverage by class
- [ ] **Run** `pytest tests/observe/test_class_coverage.py -v` — PASS

### Task 22.9: Coverage Frontier

**Files:** Create `src/cauterule/observe/coverage_frontier.py`

- [ ] **Create `src/cauterule/observe/coverage_frontier.py`** — `suggest_next_frontier(store: StoreManager, trajectories: list[Trajectory]) -> str` identifies next most valuable domain/failure family
- [ ] **Write test** `tests/observe/test_coverage_frontier.py` — test suggests correct frontier
- [ ] **Run** `pytest tests/observe/test_coverage_frontier.py -v` — PASS

### Task 22.10: Monthly Learning Report

**Files:** Create `src/cauterule/observe/monthly_report.py`

- [ ] **Create `src/cauterule/observe/monthly_report.py`** — `generate_monthly_report(store: StoreManager) -> str` auto-generate report: rules learned, failures reduced, coverage gaps
- [ ] **Write test** `tests/observe/test_monthly_report.py` — test report generation
- [ ] **Run** `pytest tests/observe/test_monthly_report.py -v` — PASS

---

## Milestone M23: Corpus (11 tasks)

**Module:** `src/cauterule/corpus/`

### Task 23.1: Corpus Format Spec

**Files:** Create `src/cauterule/corpus/__init__.py`, `src/cauterule/corpus/format.py`

- [ ] **Create `src/cauterule/corpus/__init__.py`** — export all public symbols
- [ ] **Create `src/cauterule/corpus/format.py`** — `CorpusMetadata` frozen dataclass: `id, tier, domain, quality_label, trajectory_count, gold_rule_ids`, JSONL schema constants
- [ ] **Write test** `tests/corpus/test_format.py` — test metadata validation
- [ ] **Run** `pytest tests/corpus/test_format.py -v` — PASS

### Task 23.2: Tiered Corpus Builder

**Files:** Create `src/cauterule/corpus/tiers.py`

- [ ] **Create `src/cauterule/corpus/tiers.py`** — `build_tiered_corpus(base_dir: str, tiers: dict[str, int])` builds tiny (25), small (100), medium (1k), large (10k+) with balanced success/failure
- [ ] **Write test** `tests/corpus/test_tiers.py` — test tiers have correct counts
- [ ] **Run** `pytest tests/corpus/test_tiers.py -v` — PASS

### Task 23.3: Domain-specific Corpora

**Files:** Create `src/cauterule/corpus/domains/__init__.py` and domain files

- [ ] **Create `src/cauterule/corpus/domains/`** — `coding.py`, `devops.py`, `research.py`, `support.py`, `browser_automation.py` each exports domain-specific trajectory generators
- [ ] **Write test** `tests/corpus/domains/test_domains.py` — test each domain generates valid trajectories
- [ ] **Run** `pytest tests/corpus/domains/test_domains.py -v` — PASS

### Task 23.4: Trajectory Quality Labels

**Files:** Create `src/cauterule/corpus/labels.py`

- [ ] **Create `src/cauterule/corpus/labels.py`** — `label_trajectory(trajectory: Trajectory, label: QualityLabel) -> Trajectory` sets quality label, validates against `QualityLabel` literal type
- [ ] **Write test** `tests/corpus/test_labels.py` — test each quality label sets correctly
- [ ] **Run** `pytest tests/corpus/test_labels.py -v` — PASS

### Task 23.5: Gold Rule Families

**Files:** Create `src/cauterule/corpus/gold.py`

- [ ] **Create `src/cauterule/corpus/gold.py`** — `GoldRuleFamily` dataclass with `scenario_id, trajectories: list[Trajectory], acceptable_rules: list[StandingRule]`; `load_gold_families(path: str) -> list[GoldRuleFamily]`
- [ ] **Write test** `tests/corpus/test_gold.py` — test load and validate gold families
- [ ] **Run** `pytest tests/corpus/test_gold.py -v` — PASS

### Task 23.6: Counterexample Corpus

**Files:** Create `src/cauterule/corpus/counterexample.py`

- [ ] **Create `src/cauterule/corpus/counterexample.py`** — `build_counterexample_corpus()` generates trajectories where plausible rules should be rejected
- [ ] **Write test** `tests/corpus/test_counterexample.py` — test trajectories are plausible-looking but should fail replay
- [ ] **Run** `pytest tests/corpus/test_counterexample.py -v` — PASS

### Task 23.7: Near-miss Corpus

**Files:** Create `src/cauterule/corpus/nearmiss.py`

- [ ] **Create `src/cauterule/corpus/nearmiss.py`** — `build_nearmiss_corpus()` generates similar-looking scenarios that should not trigger
- [ ] **Write test** `tests/corpus/test_nearmiss.py` — test near-miss trajectories have specific differences
- [ ] **Run** `pytest tests/corpus/test_nearmiss.py -v` — PASS

### Task 23.8: Staleness Corpus

**Files:** Create `src/cauterule/corpus/staleness.py`

- [ ] **Create `src/cauterule/corpus/staleness.py`** — `build_staleness_corpus()` generates historical failures that no longer matter
- [ ] **Write test** `tests/corpus/test_staleness.py` — test staleness trajectories have timestamps in the past
- [ ] **Run** `pytest tests/corpus/test_staleness.py -v` — PASS

### Task 23.9: Public Synthetic Corpus

**Files:** Create `corpus/public/` directory and `corpus/public/__init__.py`

- [ ] **Create `corpus/public/README.md`** — documents corpus format and how to contribute
- [ ] **Create `corpus/public/__init__.py`** — `load_public_corpus()` loads from `corpus/public/` directory
- [ ] **Write test** `tests/corpus/test_public.py` — test loading from public directory
- [ ] **Run** `pytest tests/corpus/test_public.py -v` — PASS

### Task 23.10: Private Local Corpus Mode

**Files:** Create `src/cauterule/corpus/private.py`

- [ ] **Create `src/cauterule/corpus/private.py`** — `PrivateCorpus` class wrapping local trace directory without uploading
- [ ] **Write test** `tests/corpus/test_private.py` — test private mode reads local dir
- [ ] **Run** `pytest tests/corpus/test_private.py -v` — PASS

### Task 23.11: Corpus Contribution Guide

**Files:** Modify `CONTRIBUTING.md`

- [ ] **Add section to `CONTRIBUTING.md`** — "Contributing Trajectories" section with format spec, submission process, naming conventions
- [ ] **Verify** — file parses as markdown, section is present

---

## Milestone M24: Benchmarks (12 tasks)

**Directory:** `tests/benchmark/`

### Task 24.1: Replay Determinism Test

**Files:** Create `tests/benchmark/__init__.py`, `tests/benchmark/test_determinism.py`

- [ ] **Create `tests/benchmark/__init__.py`** — empty init
- [ ] **Create `tests/benchmark/test_determinism.py`** — test same candidate + same corpus = same replay report
- [ ] **Run** `pytest tests/benchmark/test_determinism.py -v` — PASS

### Task 24.2: Gold-Family Acceptance Rate

**Files:** Create `tests/benchmark/test_gold_family.py`

- [ ] **Create `tests/benchmark/test_gold_family.py`** — test >=85% of candidates in acceptable families
- [ ] **Run** `pytest tests/benchmark/test_gold_family.py -v` — PASS

### Task 24.3: Counterexample Rejection Rate

**Files:** Create `tests/benchmark/test_counterexample.py`

- [ ] **Create `tests/benchmark/test_counterexample.py`** — test >=90% of bad rules correctly rejected
- [ ] **Run** `pytest tests/benchmark/test_counterexample.py -v` — PASS

### Task 24.4: Near-Miss Precision

**Files:** Create `tests/benchmark/test_nearmiss.py`

- [ ] **Create `tests/benchmark/test_nearmiss.py`** — test >=90% near-miss scenarios do not trigger
- [ ] **Run** `pytest tests/benchmark/test_nearmiss.py -v` — PASS

### Task 24.5: Success-Regression Catch Rate

**Files:** Create `tests/benchmark/test_regression.py`

- [ ] **Create `tests/benchmark/test_regression.py`** — test >=95% of success-breaking rules caught
- [ ] **Run** `pytest tests/benchmark/test_regression.py -v` — PASS

### Task 24.6: Model Bake-off Harness

**Files:** Create `src/cauterule/benchmark/__init__.py`, `src/cauterule/benchmark/bakeoff.py`

- [ ] **Create `src/cauterule/benchmark/__init__.py`** — empty init
- [ ] **Create `src/cauterule/benchmark/bakeoff.py`** — `BakeoffHarness` class comparing GPT, Claude, local models on same corpus
- [ ] **Write test** `tests/benchmark/test_bakeoff.py` — test harness records results (mock LLM)
- [ ] **Run** `pytest tests/benchmark/test_bakeoff.py -v` — PASS

### Task 24.7: Prompt Bake-off Harness

**Files:** Create `src/cauterule/benchmark/prompts.py`

- [ ] **Create `src/cauterule/benchmark/prompts.py`** — `PromptBakeoffHarness` compares extractor prompt variants by replay pass rate
- [ ] **Write test** `tests/benchmark/test_prompts.py` — test harness records prompt comparisons
- [ ] **Run** `pytest tests/benchmark/test_prompts.py -v` — PASS

### Task 24.8: Rule Mutation Testing

**Files:** Create `tests/benchmark/test_mutation.py`

- [ ] **Create `tests/benchmark/test_mutation.py`** — perturb good rules, verify replay catches degradation
- [ ] **Run** `pytest tests/benchmark/test_mutation.py -v` — PASS

### Task 24.9: Confidence Calibration Test

**Files:** Create `tests/benchmark/test_calibration.py`

- [ ] **Create `tests/benchmark/test_calibration.py`** — confidence scores correlate with replay outcomes
- [ ] **Run** `pytest tests/benchmark/test_calibration.py -v` — PASS

### Task 24.10: Ablation Studies

**Files:** Create `tests/benchmark/test_ablation.py`

- [ ] **Create `tests/benchmark/test_ablation.py`** — compare no clustering vs clustering, single-pass vs multi-pass, tags vs no tags
- [ ] **Run** `pytest tests/benchmark/test_ablation.py -v` — PASS

### Task 24.11: Human vs LLM Lesson Comparison

**Files:** Create `tests/benchmark/test_human_vs_llm.py`

- [ ] **Create `tests/benchmark/test_human_vs_llm.py`** — compare manually written rules to extracted rules on same failures
- [ ] **Run** `pytest tests/benchmark/test_human_vs_llm.py -v` — PASS

### Task 24.12: Calibration Feedback Loop

**Files:** Create `src/cauterule/benchmark/calibration_loop.py`

- [ ] **Create `src/cauterule/benchmark/calibration_loop.py`** — `feed_calibration_data(thresholds: dict) -> dict` feeds calibration data into promotion gate hybrid mode thresholds
- [ ] **Write test** `tests/benchmark/test_calibration_loop.py` — test threshold updates based on calibration
- [ ] **Run** `pytest tests/benchmark/test_calibration_loop.py -v` — PASS

---

## Milestone M25: Scale & Reliability (9 tasks)

**Directory:** `tests/scale/`

### Task 25.1: Replay Latency Benchmark

**Files:** Create `tests/scale/__init__.py`, `tests/scale/test_replay_latency.py`

- [ ] **Create `tests/scale/__init__.py`** — empty init
- [ ] **Create `tests/scale/test_replay_latency.py`** — benchmark: tiny<2s, small<10s, medium<60s per candidate
- [ ] **Run** `pytest tests/scale/test_replay_latency.py -v` — PASS

### Task 25.2: Injection Latency Benchmark

**Files:** Create `tests/scale/test_injection_latency.py`

- [ ] **Create `tests/scale/test_injection_latency.py`** — benchmark: p50<100ms, p95<500ms on small corpus
- [ ] **Run** `pytest tests/scale/test_injection_latency.py -v` — PASS

### Task 25.3: Conflict Detection at Scale

**Files:** Create `tests/scale/test_conflict_scale.py`

- [ ] **Create `tests/scale/test_conflict_scale.py`** — benchmark: 100/1k/10k rules, <5s at 1k
- [ ] **Run** `pytest tests/scale/test_conflict_scale.py -v` — PASS

### Task 25.4: Storage Churn Benchmark

**Files:** Create `tests/scale/test_storage.py`

- [ ] **Create `tests/scale/test_storage.py`** — YAML + git manageable after frequent promote/retire
- [ ] **Run** `pytest tests/scale/test_storage.py -v` — PASS

### Task 25.5: Concurrent Ingestion Test

**Files:** Create `tests/scale/test_concurrent.py`

- [ ] **Create `tests/scale/test_concurrent.py`** — multiple failures at once: queue, dedup, consistent promotion
- [ ] **Run** `pytest tests/scale/test_concurrent.py -v` — PASS

### Task 25.6: LLM Cost Benchmark

**Files:** Create `tests/scale/test_cost.py`

- [ ] **Create `tests/scale/test_cost.py`** — cost per extracted candidate, per promoted rule, per prevented failure
- [ ] **Run** `pytest tests/scale/test_cost.py -v` — PASS

### Task 25.7: Memory Footprint Benchmark

**Files:** Create `tests/scale/test_memory.py`

- [ ] **Create `tests/scale/test_memory.py`** — <1GB RAM on small corpus
- [ ] **Run** `pytest tests/scale/test_memory.py -v` — PASS

### Task 25.8: Incremental Indexing Benchmark

**Files:** Create `tests/scale/test_indexing.py`

- [ ] **Create `tests/scale/test_indexing.py`** — <1s per new rule at 1k rules
- [ ] **Run** `pytest tests/scale/test_indexing.py -v` — PASS

### Task 25.9: Extractor Stability Test

**Files:** Create `tests/scale/test_extractor_stability.py`

- [ ] **Create `tests/scale/test_extractor_stability.py`** — repeat extraction on same trajectory, bounded variance
- [ ] **Run** `pytest tests/scale/test_extractor_stability.py -v` — PASS