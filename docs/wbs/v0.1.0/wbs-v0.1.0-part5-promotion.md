# v0.1.0 — WBS Part 5: Promotion Gate, Linter & Conflicts

**Milestones:** M12-M14

## M12: Rule Linter

| # | Task | Files | Behavior | Status |
|---|------|-------|----------|--------|
| 12.1 | Vagueness check | `src/cauterule/linter/vagueness.py` | Detects generic triggers/directives ("be careful") | ✅ |
| 12.2 | Tautology check | `src/cauterule/linter/tautology.py` | Detects "when failing, don't fail" | ✅ |
| 12.3 | Duplicate check | `src/cauterule/linter/duplicate.py` | Detects semantically identical existing rules | ✅ |
| 12.4 | Contradiction check | `src/cauterule/linter/contradiction.py` | Detects conflicting existing rules | ✅ |
| 12.5 | Untestable check | `src/cauterule/linter/untestable.py` | Detects directives that cannot be verified via replay | ✅ |
| 12.6 | Unsafe directive check | `src/cauterule/linter/unsafe.py` | Blocks dangerous actions (rm -rf, force push, etc.) | ✅ |
| 12.7 | Linter orchestrator | `src/cauterule/linter/orchestrator.py` | Runs all checks, produces `LinterResult` | ✅ |

### M12 Exit Gate

- [x] Run all tests: `pytest` — all pass (260 passed)
- [x] Lint strict clean: `ruff check` + `mypy src/` — zero errors
- [x] Test coverage total > 95%: `pytest --cov=src/cauterule --cov-report=term-missing` — 97.69%
- [x] Update all docs affected by this milestone
- [x] Verify all issues in this milestone are done
- [x] Close all completed issues
- [x] Commit with message: `milestone: M12 complete`
- [x] Push to main

## M13: Conflict Detection

| # | Task | Files | Behavior | Status |
|---|------|-------|----------|--------|
| 13.1 | Direct contradiction detector | `src/cauterule/conflict/contradiction.py` | Same trigger, different directives | ⬜ |
| 13.2 | Specificity scorer | `src/cauterule/conflict/specificity.py` | Scores: context count, trigger precision, taxonomy depth, hit-tested, replay precision | ⬜ |
| 13.3 | Overlap detector | `src/cauterule/conflict/overlap.py` | Non-contradictory overlapping triggers | ⬜ |
| 13.4 | Consolidation engine | `src/cauterule/conflict/consolidation.py` | Merge overlapping rules, archive losers with `superseded_by` | ⬜ |
| 13.5 | Conflict report builder | `src/cauterule/conflict/report.py` | Produces `ConflictReport` with type, rules, trigger, resolution | ⬜ |

### M13 Exit Gate

- [ ] Run all tests: `pytest` — all pass
- [ ] Lint strict clean: `ruff check` + `mypy src/` — zero errors
- [ ] Test coverage total > 95%: `pytest --cov=src/cauterule --cov-report=term-missing`
- [ ] Update all docs affected by this milestone
- [ ] Verify all issues in this milestone are done
- [ ] Close all completed issues
- [ ] Commit with message: `milestone: M13 complete`
- [ ] Push to main

## M14: Promotion Gate

| # | Task | Files | Behavior | Status |
|---|------|-------|----------|--------|
| 14.1 | Auto-promote mode | `src/cauterule/promotion/auto.py` | Pass + clean linter + no conflicts → promoted | ⬜ |
| 14.2 | Human-review mode | `src/cauterule/promotion/human.py` | All verdicts generate evidence summary; human approves | ⬜ |
| 14.3 | Hybrid mode | `src/cauterule/promotion/hybrid.py` | Auto for high-confidence (>=0.8), review for low | ⬜ |
| 14.4 | Threshold config | `src/cauterule/promotion/thresholds.py` | conservative/balanced/aggressive presets | ⬜ |
| 14.5 | Promotion executor | `src/cauterule/promotion/executor.py` | Writes rule YAML, updates index, git commit | ⬜ |

### M14 Exit Gate

- [ ] Run all tests: `pytest` — all pass
- [ ] Lint strict clean: `ruff check` + `mypy src/` — zero errors
- [ ] Test coverage total > 95%: `pytest --cov=src/cauterule --cov-report=term-missing`
- [ ] Update all docs affected by this milestone
- [ ] Verify all issues in this milestone are done
- [ ] Close all completed issues
- [ ] Commit with message: `milestone: M14 complete`
- [ ] Push to main
