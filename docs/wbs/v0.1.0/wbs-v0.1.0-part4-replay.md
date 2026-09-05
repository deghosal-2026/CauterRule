# v0.1.0 — WBS Part 4: Replay Engine & Visualization

**Milestones:** M9-M11

## M9: Replay Harness

| # | Task | Files | Behavior | Status |
|---|------|-------|----------|--------|
| 9.1 | Trajectory loader | `src/cauterule/replay/loader.py` | Loads historical trajectories from corpus/scenarios dir | ✅ |
| 9.2 | Rule matcher | `src/cauterule/replay/matcher.py` | Matches candidate `when` clause against each trajectory's conditions | ✅ |
| 9.3 | Outcome simulator | `src/cauterule/replay/simulator.py` | Simulates whether rule would prevent failure or break success | ✅ |
| 9.4 | Evidence scorer | `src/cauterule/replay/scorer.py` | Computes precision, recall, verdict | ✅ |
| 9.5 | Evidence report builder | `src/cauterule/replay/report.py` | Produces `EvidenceReport` with failures_prevented, successes_broken, near_misses | ✅ |
| 9.6 | Determinism guarantee | `src/cauterule/replay/determinism.py` | Same candidate + same corpus = same report (no randomness) | ✅ |
| 9.7 | Insufficient history detection | `src/cauterule/replay/history_check.py` | Returns "inconclusive" if <3 trajectories | ✅ |

### M9 Exit Gate

- [x] Run all tests: `pytest` — all pass (229 passed)
- [x] Lint strict clean: `ruff check` + `mypy src/` — zero errors
- [x] Test coverage total > 95%: `pytest --cov=src/cauterule --cov-report=term-missing` — 97.44%
- [x] Update all docs affected by this milestone
- [x] Verify all issues in this milestone are done
- [x] Close all completed issues
- [x] Commit with message: `milestone: M9 complete`
- [x] Push to main

## M10: Replay Visualization

| # | Task | Files | Behavior | Status |
|---|------|-------|----------|--------|
| 10.1 | Replay trace builder | `src/cauterule/replay/trace.py` | Step-by-step trace of how rule would change each trajectory | ⬜ |
| 10.2 | Replay diff | `src/cauterule/replay/diff.py` | Before/after comparison of agent behavior with and without rule | ⬜ |
| 10.3 | "What if?" mode | `src/cauterule/replay/whatif.py` | Apply hypothetical rule (user-written) to trajectory, simulate outcome | ⬜ |
| 10.4 | Failure Time Machine | `src/cauterule/replay/rewind.py` | `cauterule rewind <trajectory>` — step-by-step replay with rule overlay | ⬜ |
| 10.5 | Near-miss logger | `src/cauterule/replay/nearmiss.py` | Logs partial matches as near misses, not counted as prevented/broken | ⬜ |

### M10 Exit Gate

- [ ] Run all tests: `pytest` — all pass
- [ ] Lint strict clean: `ruff check` + `mypy src/` — zero errors
- [ ] Test coverage total > 95%: `pytest --cov=src/cauterule --cov-report=term-missing`
- [ ] Update all docs affected by this milestone
- [ ] Verify all issues in this milestone are done
- [ ] Close all completed issues
- [ ] Commit with message: `milestone: M10 complete`
- [ ] Push to main

## M11: Replay Performance

| # | Task | Files | Behavior | Status |
|---|------|-------|----------|--------|
| 11.1 | Replay caching | `src/cauterule/replay/cache.py` | Cache replay results for same candidate + corpus hash | ⬜ |
| 11.2 | Parallel replay | `src/cauterule/replay/parallel.py` | Run N candidates in parallel for draft tournament | ⬜ |
| 11.3 | Performance benchmark | `tests/replay/test_performance.py` | tiny <2s, small <10s, medium <60s per candidate | ⬜ |
| 11.4 | Throughput benchmark | `tests/replay/test_throughput.py` | >=6 candidates/minute on `small` corpus | ⬜ |

### M11 Exit Gate

- [ ] Run all tests: `pytest` — all pass
- [ ] Lint strict clean: `ruff check` + `mypy src/` — zero errors
- [ ] Test coverage total > 95%: `pytest --cov=src/cauterule --cov-report=term-missing`
- [ ] Update all docs affected by this milestone
- [ ] Verify all issues in this milestone are done
- [ ] Close all completed issues
- [ ] Commit with message: `milestone: M11 complete`
- [ ] Push to main
