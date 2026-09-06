# M21-M25: TUI Review, Observability, Corpus, Benchmarks & Scale

**Date:** 2026-09-05
**Related WBS:** Part 8 (M21-M22), Part 9 (M23-M25)
**Status:** Approved

## Overview

Five milestones completing the remaining infrastructure before field tests and release:

| Milestone | Module | Tasks | Description |
|-----------|--------|-------|-------------|
| M21 | `src/cauterule/tui/` | 7 | Textual-based terminal UI for `cauterule review` |
| M22 | `src/cauterule/observe/` | 10 | Hit counters, coverage scores, reports, learning journal |
| M23 | `src/cauterule/corpus/` | 11 | Tiered corpora, domain corpora, gold/counterexample/near-miss |
| M24 | `tests/benchmark/` | 12 | 5 core benchmarks + bake-offs + mutation + calibration |
| M25 | `tests/scale/` | 9 | 9 latency/scaling benchmarks |

## Dependencies

M21 (TUI) depends on M20 (CLI) — done. M22 (observe) depends on M15 (store), M17 (injection), M10 (replay coverage) — all done. M23 (corpus) depends on M4 (capture), M10 (replay) — done. M24 (benchmarks) depends on M23 (corpus) — but corpus stubs can satisfy benchmark imports. M25 (scale) depends on M23-M24 — same, stubs acceptable.

**Strategy:** All 5 milestones built in parallel. Test suites may be limited to unit tests until sibling milestones complete. Integration tests come at the end.

## M21: TUI Review

- **New dependency:** `textual>=1.0` (core dependency — TUI is a primary UX surface)
- **Module:** `src/cauterule/tui/`
- **Entry:** `cauterule review` command registers in `cli/app.py`
- **Components:**
  - `tui/app.py` — Textual App, screens, keybindings
  - `tui/review.py` — Browse/pending-queue, approve/reject candidates
  - `tui/cards.py` — Evidence summary cards ("Prevented 3 failures, broke 0 successes")
  - `tui/confidence.py` — Confidence, prevented, broken, last hit, tags
  - `tui/annotate.py` — Human annotation: tag, comment, categorize
  - `tui/batch.py` — Batch review (10 candidates per session)
  - `tui/filter.py` — Filter by tag/status/confidence

## M22: Observability

- **Module:** `src/cauterule/observe/`
- **Data sources:** Store reads (hit counts, timestamps, tags), injection logs (match data), replay results (precision/recall)
- **Components:**
  - `observe/hits.py` — Per-rule hit counter (reads `rule.metadata.match_count`)
  - `observe/timestamps.py` — Updates `last_match` on each injection
  - `observe/leaderboard.py` — Most prevented, most broken, top gaps
  - `observe/coverage_gap.py` — Domains with repeated failures but no matching rules
  - `observe/coverage_score.py` — Blended score of coverage%, precision%, stale%
  - `observe/journal.py` — Auto-generate markdown log
  - `observe/domain_coverage.py` — Coverage by domain
  - `observe/class_coverage.py` — Coverage by failure class
  - `observe/coverage_frontier.py` — Next most valuable domain to learn
  - `observe/monthly_report.py` — Auto-generated monthly report

## M23: Corpus

- **Module:** `src/cauterule/corpus/`
- **Directory:** `corpus/public/` for shareable synthetic data
- **Components:**
  - `corpus/format.py` — JSONL schema with metadata
  - `corpus/tiers.py` — tiny(25), small(100), medium(1k), large(10k+)
  - `corpus/domains/` — coding, DevOps, research, support, browser_automation
  - `corpus/labels.py` — Quality labels: clear, ambiguous, multi_causal, misleading, operator_induced
  - `corpus/gold.py` — Multiple acceptable abstractions per scenario
  - `corpus/counterexample.py` — Trajectories where plausible rules should be rejected
  - `corpus/nearmiss.py` — Similar-looking scenarios that should not trigger
  - `corpus/staleness.py` — Historical failures that no longer matter
  - `corpus/private.py` — Local-traces-only mode

## M24: Benchmarks

- **Tests:** `tests/benchmark/` (pytest-based, hermetic, no LLM calls)
- **Benchmarks:**
  - `determinism.py` — Same candidate + same corpus = same report
  - `gold_family.py` — >=85% acceptance rate on gold families
  - `counterexample.py` — >=90% rejection rate on bad rules
  - `nearmiss.py` — >=90% near-miss avoidance
  - `regression.py` — >=95% success-breaking rules caught
  - `bakeoff.py` — Model comparison harness
  - `prompts.py` — Prompt variant comparison harness
  - `mutation.py` — Perturb good rules, verify degradation caught
  - `calibration.py` — Confidence correlates with replay outcomes
  - `ablation.py` — Compare clustering vs none, single-pass vs multi-pass
  - `human_vs_llm.py` — Compare manual vs extracted rules
  - `calibration_loop.py` — Feed calibration data to promotion thresholds

## M25: Scale & Reliability

- **Tests:** `tests/scale/` (pytest-based benchmarks)
- **Benchmarks:**
  - `replay_latency.py` — tiny<2s, small<10s, medium<60s per candidate
  - `injection_latency.py` — p50<100ms, p95<500ms on small corpus
  - `conflict_scale.py` — 100/1k/10k rules, <5s at 1k
  - `storage.py` — YAML+git manageable after frequent promote/retire
  - `concurrent.py` — Multiple failures at once: queue, dedup, consistent promotion
  - `cost.py` — Cost per extracted candidate, per promoted rule
  - `memory.py` — <1GB RAM on small corpus
  - `indexing.py` — <1s per new rule at 1k rules
  - `extractor_stability.py` — Repeat extraction on same trajectory, bounded variance

## Exit Gate (all milestones)

- `pytest` all pass
- `ruff check .` + `mypy src/ tests/` clean
- `pytest --cov=src/cauterule --cov-report=term-missing` >95%
- Update docs, close issues, commit `milestone: M# complete`, push