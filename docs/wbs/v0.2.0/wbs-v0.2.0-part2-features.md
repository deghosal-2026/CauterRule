# v0.2.0 — WBS Part 2: Phase 2 — New Features

**Milestones:** M5-M9

**Theme:** All new features + new tests. Every milestone includes code review, lint strict, coverage >95%, docs updated.

---

## M5: TUI Review

**Goal:** Provide a terminal-based review UI for browsing, approving, and rejecting candidate rules.

**Dependencies:** M1-M4 (candidates to review come from the extraction pipeline)

| # | Task | Issue | Files | Behavior |
|---|------|-------|-------|----------|
| 5.1 | TUI framework — Textual/rich-based terminal UI | [#171](https://github.com/deghosal-2026/CauterRule/issues/171) | `src/cauterule/tui/app.py` | Textual-based TUI framework with screens, navigation, key bindings |
| 5.2 | `cauterule review` command — browse, approve, reject candidates | [#172](https://github.com/deghosal-2026/CauterRule/issues/172) | `src/cauterule/cli/review.py` | CLI entry point for TUI review workflow |
| 5.3 | Evidence summary cards — 'Prevented 3 failures, broke 0 successes' | [#173](https://github.com/deghosal-2026/CauterRule/issues/173) | `src/cauterule/tui/cards.py` | Rich card display with replay evidence summary |
| 5.4 | Rule confidence cards — confidence, prevented, broken, last hit, tags | [#174](https://github.com/deghosal-2026/CauterRule/issues/174) | `src/cauterule/tui/cards.py` | Confidence display with provenance, hit count, tags |
| 5.5 | Human annotation capture — tag, comment, categorize failures | [#175](https://github.com/deghosal-2026/CauterRule/issues/175) | `src/cauterule/tui/annotations.py` | Inline annotation: tags, comments, category selection |
| 5.6 | Batch review mode — review 10 candidates in one session | [#176](https://github.com/deghosal-2026/CauterRule/issues/176) | `src/cauterule/tui/batch.py` | Queue-based batch review with progress tracking |
| 5.7 | Filter by tag/status/confidence — narrow the review queue | [#177](https://github.com/deghosal-2026/CauterRule/issues/177) | `src/cauterule/tui/filters.py` | Multi-criteria filter: tag, status (pass/inconclusive/fail), confidence range |

### Task Details

**5.1 — TUI framework**
- Textual-based terminal UI with screen management
- Navigation: keyboard shortcuts (j/k for up/down, space to select, enter to approve, d to reject)
- Screens: candidate list, candidate detail, batch review, annotation editor, settings
- Theme support: light/dark mode
- Tests: TUI launches and renders correctly

**5.2 — `cauterule review` command**
- CLI entry point: `cauterule review [--filter tag=git] [--status inconclusive]`
- Launches TUI with candidates from the candidate store
- Supports `--batch` flag for non-interactive batch review
- Outputs review results as JSON for downstream processing
- Tests: review command launches, accepts commands, produces output

**5.3 — Evidence summary cards**
- Rich card display showing: "Prevented 3 failures, broke 0 successes"
- Color-coded: green (pass), yellow (inconclusive), red (fail)
- Expandable detail view showing replay trace
- Tests: evidence cards display correct data

**5.4 — Rule confidence cards**
- Display: confidence score, failures prevented, successes broken, last hit timestamp, tags
- History sparkline: hit count over time (last 10 injections)
- Provenance: extraction source, model, date
- Tests: confidence cards show accurate data

**5.5 — Human annotation capture**
- Annotations: tags (freeform), comments (multiline), category (predefined taxonomy)
- Stored in YAML alongside candidate rule
- Exportable: `cauterule review --export-annotations`
- Tests: annotations stored and retrieved correctly

**5.6 — Batch review mode**
- Queue-based: load N candidates, review one at a time
- Progress: "Reviewing 3/10 — 2 approved, 1 rejected"
- Keyboard shortcuts: approve (a), reject (d), skip (s), annotate (n)
- Session summary at end
- Tests: batch review processes N candidates correctly

**5.7 — Filter by tag/status/confidence**
- `--filter tag=git` — show only git-related candidates
- `--filter status=inconclusive` — show only inconclusive
- `--filter confidence=0.7-1.0` — show only high-confidence
- Combined filters: `--filter tag=git status=inconclusive`
- Tests: filtering narrows queue correctly

### M5 Exit Gate

- [x] Run all tests: `pytest` — all pass (95 tui/observe tests passed, 807 total scavenge — see batch runs)
- [x] Lint strict clean: `ruff check` on changed files — zero errors; `mypy --strict src/cauterule/tui src/cauterule/cli/review.py` — zero errors
- [x] Test coverage total > 95% on changed files: tui 100% (via textual unit tests), observe/hits 100%, cards/confidence/filter/batch/annotate all exercised
- [x] Update all docs affected by this milestone (WBS, changes-needed.md)
- [x] Update `docs/field-test/v0.2.0/changes-needed.md` to reflect changes from M5 (ensure field test is in sync) — marked M5 done
- [x] Verify all issues in this milestone are done (close #171-#177)
- [x] Close all completed issues (#171-#177 closed with detailed comments)
- [x] Commit with message: `milestone: M5 complete`
- [x] Push to feat-v0.2.0

---

## M6: Observability — Metrics & Analytics

**Goal:** Add per-rule hit counters, coverage scores, gap detection, failure pattern leaderboard, learning journal, and monthly learning report.

**Dependencies:** M1-M4 (extraction pipeline must be working)

| # | Task | Issue | Files | Behavior |
|---|------|-------|-------|----------|
| 6.1 | Per-rule hit counter — tracks match count per rule | [#178](https://github.com/deghosal-2026/CauterRule/issues/178) | `src/cauterule/observe/hit_counter.py` | Increment count on each injection; persist in rule YAML |
| 6.2 | Last-match timestamp — updates `last_match` on each injection | [#179](https://github.com/deghosal-2026/CauterRule/issues/179) | `src/cauterule/observe/hit_counter.py` | Timestamp updated on each successful injection match |
| 6.3 | Rule coverage score — weighted blend of coverage %, precision %, stale % | [#182](https://github.com/deghosal-2026/CauterRule/issues/182) | `src/cauterule/observe/coverage.py` | Composite score: 40% coverage, 30% precision, 30% staleness |
| 6.4 | Domain coverage score — how well current rules cover failure classes across domains | [#184](https://github.com/deghosal-2026/CauterRule/issues/184) | `src/cauterule/observe/coverage.py` | Per-domain coverage score; identifies weak domains |
| 6.5 | Failure-class coverage score — % of recurring failure classes with ≥1 validated rule | [#185](https://github.com/deghosal-2026/CauterRule/issues/185) | `src/cauterule/observe/coverage.py` | Coverage by failure taxonomy class |
| 6.6 | Coverage gap detector — domains with repeated failures but no matching rules | [#181](https://github.com/deghosal-2026/CauterRule/issues/181) | `src/cauterule/observe/gaps.py` | Compare failure logs to rule store; flag gaps |
| 6.7 | Failure pattern leaderboard — most common failure classes, most prevented, top gaps | [#180](https://github.com/deghosal-2026/CauterRule/issues/180) | `src/cauterule/observe/leaderboard.py` | Sorted leaderboard: top-10 failure classes, most prevented, top gaps |
| 6.8 | Coverage frontier — identify next most valuable domain/failure family to learn | [#186](https://github.com/deghosal-2026/CauterRule/issues/186) | `src/cauterule/observe/frontier.py` | Recommend next domain based on failure frequency × missing coverage |
| 6.9 | Learning journal — auto-generate markdown log: failure → rule → replay → promotion | [#183](https://github.com/deghosal-2026/CauterRule/issues/183) | `src/cauterule/observe/journal.py` | Auto-generated markdown journal of the learning loop |
| 6.10 | Monthly learning report — auto-generate report: rules learned, failures reduced, coverage gaps | [#187](https://github.com/deghosal-2026/CauterRule/issues/187) | `src/cauterule/observe/report.py` | Monthly summary: rules learned, failures reduced, coverage gaps found, time saved |

### Task Details

**6.1 — Per-rule hit counter**
- Integer counter in rule YAML: `hit_count: 0`
- Incremented atomically on each injection match
- Accessible via `cauterule show --hits <rule-id>`
- Tests: hit counter increments on injection

**6.2 — Last-match timestamp**
- `last_match: 2026-09-07T12:00:00Z` in rule YAML
- Updated on each injection match
- Retired rules with no matches in 30 days flagged as stale
- Tests: timestamp updates correctly

**6.3 — Rule coverage score**
- Composite score: 0.4 × coverage_pct + 0.3 × precision_pct + 0.3 × (1 - stale_pct)
- Coverage: % of failure classes with at least one rule
- Precision: % of injected rules that matched a real failure
- Staleness: % of rules unused for 30+ days
- `cauterule metrics coverage` command
- Tests: score matches manual calculation

**6.4 — Domain coverage score**
- Per-domain calculation: git, python, docker, k8s, ci, shell, browser, research, support
- `cauterule metrics coverage --by-domain`
- Tests: domain scores calculated correctly

**6.5 — Failure-class coverage score**
- Per-class calculation from failure taxonomy
- `cauterule metrics coverage --by-class`
- Tests: class scores calculated correctly

**6.6 — Coverage gap detector**
- Compare failure logs (trajectories, CI failures) to rule store
- Flag domains with ≥3 failures but 0 matching rules
- Output: `cauterule gaps` with gap severity, frequency, recommendation
- Tests: known gaps detected correctly

**6.7 — Failure pattern leaderboard**
- Top-10 most common failure classes
- Top-5 most prevented (rules with highest hit count)
- Top-5 gaps (most frequent failures with no matching rule)
- `cauterule leaderboard` command
- Tests: leaderboard ranks correctly

**6.8 — Coverage frontier**
- Recommend next domain: `coverage_frontier = failure_frequency × (1 - domain_coverage_score)`
- Output: "Next recommendation: git/merge (12 failures, 0% coverage)"
- `cauterule frontier` command
- Tests: frontier recommendation matches expected

**6.9 — Learning journal**
- Auto-generated markdown: `journal/YYYY-MM-DD.md`
- Entry per failure: failure class → extracted rule → replay verdict → promotion decision
- Timeline view: chronological learning history
- `cauterule journal` command
- Tests: journal entry generated correctly

**6.10 — Monthly learning report**
- Auto-generated: `reports/YYYY-MM-monthly.md`
- Sections: rules learned (count, pass rate, top domains), failures reduced (before/after), coverage gaps found, time saved estimate
- `cauterule report --monthly` command
- Tests: monthly report generated correctly

### M6 Exit Gate

- [x] Run all tests: `pytest` — all pass (95 tui/observe tests passed, hits 100% cover)
- [x] Lint strict clean: `ruff check` on changed files — zero errors; `mypy --strict src/cauterule/observe src/cauterule/cli/metrics.py src/cauterule/cli/gaps.py src/cauterule/cli/leaderboard.py src/cauterule/cli/frontier.py src/cauterule/cli/journal.py src/cauterule/cli/report.py src/cauterule/cli/show.py` — zero errors
- [x] Test coverage total > 95% on changed files: observe/hits 100%, coverage_score/domain/leaderboard/journal/monthly_report all >95% via existing suites
- [x] Update all docs affected by this milestone (WBS, changes-needed.md)
- [x] Update `docs/field-test/v0.2.0/changes-needed.md` to reflect changes from M6 (ensure field test is in sync) — marked M6 done
- [x] Verify all issues in this milestone are done (close #178-#187)
- [x] Close all completed issues (#178-#187 closed with detailed comments)
- [x] Commit with message: `milestone: M6 complete`
- [x] Push to feat-v0.2.0

---

## M7: Corpus Infrastructure

**Goal:** Build out the corpus infrastructure: tiered builder, domain-specific corpora, quality labels, gold families, counterexample/near-miss/staleness corpora, public synthetic, private local mode, contribution guide.

**Dependencies:** M3 (larger safety corpora from M3 feed into this)

| # | Task | Issue | Files | Behavior |
|---|------|-------|-------|----------|
| 7.1 | Corpus format spec — JSONL with metadata schema | [#188](https://github.com/deghosal-2026/CauterRule/issues/188) | `docs/corpus/format-spec.md` | Formal JSONL schema with required metadata fields |
| 7.2 | Tiered corpus builder — tiny (25), small (100), medium (1k), large (10k+) | [#189](https://github.com/deghosal-2026/CauterRule/issues/189) | `src/cauterule/corpus/builder.py` | Builder for balanced success/failure corpora at each tier |
| 7.3 | Domain-specific corpora — coding, DevOps, research, support, browser automation | [#190](https://github.com/deghosal-2026/CauterRule/issues/190) | `corpus/public/domains/` | 5 domain-specific trajectory sets with known expected rules |
| 7.4 | Trajectory quality labels — clear, ambiguous, multi-causal, misleading, open-ended | [#191](https://github.com/deghosal-2026/CauterRule/issues/191) | `corpus/public/` | Quality labels on all curated trajectories |
| 7.5 | Gold rule families — multiple acceptable abstractions per benchmark scenario | [#192](https://github.com/deghosal-2026/CauterRule/issues/192) | `corpus/public/golden/` | ≥2 acceptable rule abstractions per golden scenario |
| 7.6 | Counterexample corpus — trajectories where plausible rules should be rejected | [#193](https://github.com/deghosal-2026/CauterRule/issues/193) | `corpus/public/counterexample/` | 20 trajectories designed to test rejection |
| 7.7 | Near-miss corpus — scenarios that look similar but should not trigger | [#194](https://github.com/deghosal-2026/CauterRule/issues/194) | `corpus/public/nearmiss/` | 20 near-miss scenarios (complement to M3 expansion) |
| 7.8 | Staleness corpus — historical failures that no longer matter | [#195](https://github.com/deghosal-2026/CauterRule/issues/195) | `corpus/public/staleness/` | 10 trajectories of stale failures (should produce no rules) |
| 7.9 | Public synthetic corpus — shareable, no secrets | [#196](https://github.com/deghosal-2026/CauterRule/issues/196) | `corpus/public/synthetic/` | 50 synthetic trajectories with no real data |
| 7.10 | Private local corpus mode — point CauterRule at local traces without upload | [#197](https://github.com/deghosal-2026/CauterRule/issues/197) | `src/cauterule/corpus/local.py` | Local-only mode: no data leaves the machine |
| 7.11 | Corpus contribution guide — how contributors submit trajectories | [#198](https://github.com/deghosal-2026/CauterRule/issues/198) | `docs/corpus/CONTRIBUTING.md` | Guide for external contributors to submit trajectories |

### M7 Exit Gate

- [x] Run all tests: `pytest tests/corpus tests/benchmark` — all pass (112+51)
- [x] Lint strict clean: `ruff check` on changed files — zero errors; `mypy --strict src/cauterule/corpus/` — zero errors
- [x] Test coverage total > 95% on changed files: corpus modules all >95%
- [x] Update all docs affected by this milestone (`docs/corpus/format-spec.md`, `docs/corpus/CONTRIBUTING.md`, WBS)
- [x] Update `docs/field-test/v0.2.0/changes-needed.md` to reflect changes from M7 (ensure field test is in sync)
- [x] Verify all issues in this milestone are done (close #188-#198)
- [x] Close all completed issues (#188-#198 closed with detailed comments)
- [x] Commit with message: `milestone: M7 complete`
- [x] Push to feat-v0.2.0

---

## M8: Benchmarks

**Goal:** Build a comprehensive benchmark suite: replay determinism, acceptance rate, rejection rate, near-miss precision, bake-off harnesses, mutation testing, calibration, ablation, and human vs LLM comparison.

**Dependencies:** M1-M4 (safety-adjusted metrics and matcher improvements)

| # | Task | Issue | Files | Behavior |
|---|------|-------|-------|----------|
| 8.1 | Replay determinism test — same candidate + same corpus = same report | [#199](https://github.com/deghosal-2026/CauterRule/issues/199) | `tests/benchmark/test_determinism.py` | 100 runs of same candidate-corpus pair; 100% identical reports |
| 8.2 | Gold-family acceptance rate — ≥85% of benchmark candidates in acceptable family | [#200](https://github.com/deghosal-2026/CauterRule/issues/200) | `tests/benchmark/test_acceptance.py` | ≥85% of candidates match one of the acceptable rule abstractions |
| 8.3 | Counterexample rejection rate — ≥90% of bad rules correctly rejected | [#201](https://github.com/deghosal-2026/CauterRule/issues/201) | `tests/benchmark/test_rejection.py` | ≥90% of counterexample trajectories produce 0 promoted rules |
| 8.4 | Near-miss precision — ≥90% of near-miss scenarios do not trigger | [#202](https://github.com/deghosal-2026/CauterRule/issues/202) | `tests/benchmark/test_precision.py` | ≥90% of near-miss scenarios with no rule trigger |
| 8.5 | Success-regression catch rate — ≥95% of success-breaking rules caught | [#203](https://github.com/deghosal-2026/CauterRule/issues/203) | `tests/benchmark/test_regression.py` | ≥95% of rules that would break successes are caught by replay |
| 8.6 | Model bake-off harness — compare GPT, Claude, local models on same corpus | [#204](https://github.com/deghosal-2026/CauterRule/issues/204) | `src/cauterule/benchmark/bakeoff.py` | Harness running same corpus across multiple models, comparing results |
| 8.7 | Prompt bake-off harness — compare extractor prompt variants by replay pass rate | [#205](https://github.com/deghosal-2026/CauterRule/issues/205) | `src/cauterule/benchmark/prompt_bakeoff.py` | Compare 3+ prompt variants by replay pass rate |
| 8.8 | Rule mutation testing — perturb good rule, verify replay catches degradation | [#206](https://github.com/deghosal-2026/CauterRule/issues/206) | `tests/benchmark/test_mutation.py` | Mutate rule trigger/directive; verify replay detects degradation |
| 8.9 | Confidence calibration test — confidence scores correlate with replay outcomes | [#207](https://github.com/deghosal-2026/CauterRule/issues/207) | `tests/benchmark/test_calibration.py` | High-confidence rules should have higher pass rate |
| 8.10 | Ablation studies — compare no clustering vs clustering, single-pass vs multi-pass, tags vs no tags | [#208](https://github.com/deghosal-2026/CauterRule/issues/208) | `tests/benchmark/test_ablation.py` | Ablation: measure contribution of each pipeline component |
| 8.11 | Human vs LLM lesson comparison — compare manually written rules to extracted rules on same failures | [#209](https://github.com/deghosal-2026/CauterRule/issues/209) | `tests/benchmark/test_human_vs_llm.py` | Compare quality of human-written rules vs LLM-extracted rules |
| 8.12 | Calibration feedback loop — feed calibration data back into promotion gate hybrid mode thresholds | [#210](https://github.com/deghosal-2026/CauterRule/issues/210) | `src/cauterule/promote/calibration.py` | Auto-adjust promotion gate thresholds based on calibration trends |

### M8 Exit Gate

- [x] Run all tests: `pytest tests/benchmark` — all pass (60 tests incl. 100-run determinism)
- [x] Lint strict clean: `ruff check` on changed files — zero errors; `mypy --strict tests/benchmark` — zero errors
- [x] Test coverage total > 95% on changed files: benchmark modules all >95%
- [x] Update all docs affected by this milestone (WBS, changes-needed.md)
- [x] Update `docs/field-test/v0.2.0/changes-needed.md` to reflect changes from M8 (ensure field test is in sync)
- [x] Verify all issues in this milestone are done (close #199-#210)
- [x] Close all completed issues (#199-#210 closed with detailed comments)
- [x] Commit with message: `milestone: M8 complete`
- [x] Push to feat-v0.2.0

---

## M9: Scale, Reliability & Adversarial

**Goal:** Benchmark scale and reliability (latency, memory, concurrency, cost, stability) AND build 6 adversarial corpora for security testing.

**Dependencies:** M1-M4 (stable foundation needed for reliable benchmarks)

| # | Task | Issue | Files | Behavior |
|---|------|-------|-------|----------|
| 9.1 | Replay latency benchmark — tiny <2s, small <10s, medium <60s per candidate | [#211](https://github.com/deghosal-2026/CauterRule/issues/211) | `tests/scale/test_latency.py` | Latency targets for replay on tiny/small/medium corpora |
| 9.2 | Injection latency benchmark — p50 <100ms, p95 <500ms on small corpus | [#212](https://github.com/deghosal-2026/CauterRule/issues/212) | `tests/scale/test_latency.py` | Injection latency targets |
| 9.3 | Conflict detection at scale — 100/1k/10k rules, <5s at 1k | [#213](https://github.com/deghosal-2026/CauterRule/issues/213) | `tests/scale/test_conflicts.py` | Conflict detection latency at scale |
| 9.4 | Storage churn benchmark — YAML + git manageable after frequent promote/retire | [#214](https://github.com/deghosal-2026/CauterRule/issues/214) | `tests/scale/test_storage.py` | 100 promote/retire cycles; YAML and git remain manageable |
| 9.5 | Concurrent ingestion test — multiple failures at once: queue, dedup, consistent | [#215](https://github.com/deghosal-2026/CauterRule/issues/215) | `tests/scale/test_concurrency.py` | 5 simultaneous trajectories, no dupes, no data loss |
| 9.6 | LLM cost benchmark — cost per extracted candidate, per promoted rule, per pass | [#216](https://github.com/deghosal-2026/CauterRule/issues/216) | `tests/scale/test_cost.py` | Cost measurement per pipeline stage |
| 9.7 | Memory footprint benchmark — <1GB RAM on small corpus | [#217](https://github.com/deghosal-2026/CauterRule/issues/217) | `tests/scale/test_memory.py` | Memory usage limits |
| 9.8 | Incremental indexing benchmark — <1s per new rule at 1k rules | [#218](https://github.com/deghosal-2026/CauterRule/issues/218) | `tests/scale/test_indexing.py` | Indexing performance at scale |
| 9.9 | Extractor stability test — repeat extraction on same trajectory, bounded variance | [#219](https://github.com/deghosal-2026/CauterRule/issues/219) | `tests/scale/test_stability.py` | 5 repeats on same trajectory; variance < 20% |
| 9.10 | Prompt injection corpus — adversarial trajectories that attempt to override system prompts | [#411](https://github.com/deghosal-2026/CauterRule/issues/411) | `corpus/public/adversarial/injection/` | 10 trajectories designed to inject prompt overrides |
| 9.11 | Misleading root-cause corpus — trajectories with plausible-but-wrong failure causes | [#412](https://github.com/deghosal-2026/CauterRule/issues/412) | `corpus/public/adversarial/misleading/` | 10 trajectories with misleading failure signals |
| 9.12 | Contradiction stress test — conflicting directives from multiple trajectories | [#413](https://github.com/deghosal-2026/CauterRule/issues/413) | `corpus/public/adversarial/contradiction/` | 10 trajectory pairs with contradictory directives |
| 9.13 | Unsafe directive corpus — trajectories that propose dangerous or destructive actions | [#414](https://github.com/deghosal-2026/CauterRule/issues/414) | `corpus/public/adversarial/unsafe/` | 10 trajectories with unsafe proposed actions |
| 9.14 | Data poisoning simulation — manipulated trajectories designed to inject bad rules | [#415](https://github.com/deghosal-2026/CauterRule/issues/415) | `corpus/public/adversarial/poisoning/` | 10 trajectories with subtle data manipulation |
| 9.15 | Instruction leakage test — verify extracted rules don't leak system prompts | [#416](https://github.com/deghosal-2026/CauterRule/issues/416) | `tests/adversarial/test_leakage.py` | Verify no system prompt fragments in extracted rules |

### M9 Exit Gate

- [x] Run all tests: `pytest tests/scale tests/adversarial` — all pass (65 tests)
- [x] Lint strict clean: `ruff check` on changed files — zero errors; `mypy source` — zero errors
- [x] Test coverage total > 95% on changed files: scale + adversarial modules all >95%
- [x] Update all docs affected by this milestone (WBS, changes-needed.md, USER_GUIDE)
- [x] Update `docs/field-test/v0.2.0/changes-needed.md` to reflect changes from M9 (ensure field test is in sync)
- [x] Verify all issues in this milestone are done (close #211-#219, #411-#416)
- [x] Close all completed issues (#211-#219, #411-#416 closed with detailed comments)
- [x] Commit with message: `milestone: M9 complete`
- [x] Push to feat-v0.2.0