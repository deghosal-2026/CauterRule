# v0.1.0 — WBS Part 9: Corpus, Benchmarks & Scale

**Milestones:** M23-M25

## M23: Corpus

| # | Task | Files | Behavior | Status |
|---|------|-------|----------|--------|
| 23.1 | Corpus format spec | `src/cauterule/corpus/format.py` | JSONL with metadata schema | ⬜ |
| 23.2 | Tiered corpus builder | `src/cauterule/corpus/tiers.py` | tiny (25), small (100), medium (1k), large (10k+) | ⬜ |
| 23.3 | Domain-specific corpora | `src/cauterule/corpus/domains/` | coding, DevOps, research, support, browser automation | ⬜ |
| 23.4 | Trajectory quality labels | `src/cauterule/corpus/labels.py` | clear, ambiguous, multi-causal, misleading, operator-induced | ⬜ |
| 23.5 | Gold rule families | `src/cauterule/corpus/gold.py` | Multiple acceptable abstractions per benchmark scenario | ⬜ |
| 23.6 | Counterexample corpus | `src/cauterule/corpus/counterexample.py` | Trajectories where plausible rules should be rejected | ⬜ |
| 23.7 | Near-miss corpus | `src/cauterule/corpus/nearmiss.py` | Scenarios that look similar but should not trigger | ⬜ |
| 23.8 | Staleness corpus | `src/cauterule/corpus/staleness.py` | Historical failures that no longer matter | ⬜ |
| 23.9 | Public synthetic corpus | `corpus/public/` | Shareable, no secrets | ⬜ |
| 23.10 | Private local corpus mode | `src/cauterule/corpus/private.py` | Point CauterRule at local traces without uploading | ⬜ |
| 23.11 | Corpus contribution guide | `CONTRIBUTING.md` section | How contributors submit trajectories | ⬜ |

### M23 Exit Gate

- [ ] Run all tests: `pytest` — all pass
- [ ] Lint strict clean: `ruff check` + `mypy src/` — zero errors
- [ ] Test coverage total > 95%: `pytest --cov=src/cauterule --cov-report=term-missing`
- [ ] Update all docs affected by this milestone
- [ ] Verify all issues in this milestone are done
- [ ] Close all completed issues
- [ ] Commit with message: `milestone: M23 complete`
- [ ] Push to main

## M24: Benchmarks

| # | Task | Files | Behavior | Status |
|---|------|-------|----------|--------|
| 24.1 | Replay determinism test | `tests/benchmark/determinism.py` | Same candidate + same corpus = same report | ⬜ |
| 24.2 | Gold-family acceptance rate | `tests/benchmark/gold_family.py` | >=85% of benchmark candidates in acceptable families | ⬜ |
| 24.3 | Counterexample rejection rate | `tests/benchmark/counterexample.py` | >=90% of bad rules correctly rejected | ⬜ |
| 24.4 | Near-miss precision | `tests/benchmark/nearmiss.py` | >=90% of near-miss scenarios do not trigger | ⬜ |
| 24.5 | Success-regression catch rate | `tests/benchmark/regression.py` | >=95% of success-breaking rules caught | ⬜ |
| 24.6 | Model bake-off harness | `src/cauterule/benchmark/bakeoff.py` | Compare GPT, Claude, local models on same corpus | ⬜ |
| 24.7 | Prompt bake-off harness | `src/cauterule/benchmark/prompts.py` | Compare extractor prompt variants by replay pass rate | ⬜ |
| 24.8 | Rule mutation testing | `tests/benchmark/mutation.py` | Perturb good rule, verify replay catches degradation | ⬜ |
| 24.9 | Confidence calibration test | `tests/benchmark/calibration.py` | Confidence scores correlate with replay outcomes | ⬜ |

### M24 Exit Gate

- [ ] Run all tests: `pytest` — all pass
- [ ] Lint strict clean: `ruff check` + `mypy src/` — zero errors
- [ ] Test coverage total > 95%: `pytest --cov=src/cauterule --cov-report=term-missing`
- [ ] Update all docs affected by this milestone
- [ ] Verify all issues in this milestone are done
- [ ] Close all completed issues
- [ ] Commit with message: `milestone: M24 complete`
- [ ] Push to main

## M25: Scale & Reliability

| # | Task | Files | Behavior | Status |
|---|------|-------|----------|--------|
| 25.1 | Replay latency benchmark | `tests/scale/replay_latency.py` | tiny <2s, small <10s, medium <60s per candidate | ⬜ |
| 25.2 | Injection latency benchmark | `tests/scale/injection_latency.py` | p50 <100ms, p95 <500ms on `small` corpus | ⬜ |
| 25.3 | Conflict detection at scale | `tests/scale/conflict_scale.py` | 100/1k/10k rules, <5s at 1k | ⬜ |
| 25.4 | Storage churn benchmark | `tests/scale/storage.py` | YAML + git manageable after frequent promote/retire | ⬜ |
| 25.5 | Concurrent ingestion test | `tests/scale/concurrent.py` | Multiple failures at once: queue, dedup, consistent promotion | ⬜ |
| 25.6 | LLM cost benchmark | `tests/scale/cost.py` | Cost per extracted candidate, per promoted rule, per prevented failure | ⬜ |
| 25.7 | Memory footprint benchmark | `tests/scale/memory.py` | <1GB RAM on `small` corpus | ⬜ |
| 25.8 | Incremental indexing benchmark | `tests/scale/indexing.py` | <1s per new rule at 1k rules | ⬜ |
| 25.9 | Extractor stability test | `tests/scale/extractor_stability.py` | Repeat extraction on same trajectory, bounded variance | ⬜ |

### M25 Exit Gate

- [ ] Run all tests: `pytest` — all pass
- [ ] Lint strict clean: `ruff check` + `mypy src/` — zero errors
- [ ] Test coverage total > 95%: `pytest --cov=src/cauterule --cov-report=term-missing`
- [ ] Update all docs affected by this milestone
- [ ] Verify all issues in this milestone are done
- [ ] Close all completed issues
- [ ] Commit with message: `milestone: M25 complete`
- [ ] Push to main
