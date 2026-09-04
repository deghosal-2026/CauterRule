# v0.1.0 — WBS Part 10: Safety, Adversarial & Field Tests

**Milestones:** M26-M27

## M26: Adversarial & Safety Testing

| # | Task | Files | Behavior | Status |
|---|------|-------|----------|--------|
| 26.1 | Prompt injection corpus | `tests/adversarial/injection.py` | >=90% of injection attempts fail to alter extractor output | ⬜ |
| 26.2 | Misleading root-cause corpus | `tests/adversarial/misleading.py` | Extractor avoids superficial lessons | ⬜ |
| 26.3 | Contradiction stress test | `tests/adversarial/contradiction.py` | >=90% detection recall of seeded contradictions | ⬜ |
| 26.4 | Unsafe directive corpus | `tests/adversarial/unsafe.py` | >=95% of unsafe rules blocked by linter or gate | ⬜ |
| 26.5 | Data poisoning simulation | `tests/adversarial/poisoning.py` | Poisoned trajectories caught by replay or provenance | ⬜ |
| 26.6 | Instruction leakage test | `tests/adversarial/leakage.py` | No secrets survive export | ⬜ |

### M26 Exit Gate

- [ ] Run all tests: `pytest` — all pass
- [ ] Lint strict clean: `ruff check` + `mypy src/` — zero errors
- [ ] Test coverage total > 95%: `pytest --cov=src/cauterule --cov-report=term-missing`
- [ ] Update all docs affected by this milestone
- [ ] Verify all issues in this milestone are done
- [ ] Close all completed issues
- [ ] Commit with message: `milestone: M26 complete`
- [ ] Push to main

## M27: Field Tests

| # | Task | Files | Behavior | Status |
|---|------|-------|----------|--------|
| 27.1 | Single-agent coding field test | `field-test/v0.1.0/coding.md` | Coding agent on real repo tasks; measure repeat-failure reduction | ⬜ |
| 27.2 | Long-horizon task field test | `field-test/v0.1.0/long-horizon.md` | 20-50 step tasks; rules help when failures occur late | ⬜ |
| 27.3 | Noisy trajectory field test | `field-test/v0.1.0/noisy.md` | Inject retries/irrelevant calls; extractor still finds lesson | ⬜ |
| 27.4 | Human-in-the-loop field test | `field-test/v0.1.0/human-review.md` | Auto vs human promotion: precision, trust, operator load | ⬜ |
| 27.5 | Cold-start field test | `field-test/v0.1.0/cold-start.md` | Zero rules → time to first useful rule + first prevented failure | ⬜ |
| 27.6 | Cross-session memory field test | `field-test/v0.1.0/cross-session.md` | Fail day 1, retry day 3 in fresh session; rule still applies | ⬜ |
| 27.7 | Regression field test | `field-test/v0.1.0/regression.md` | Old promoted rules still pass after prompt/model changes | ⬜ |
| 27.8 | Multi-environment field test | `field-test/v0.1.0/multi-env.md` | macOS, Linux, CI container; environment-specific lessons | ⬜ |

### M27 Exit Gate

- [ ] Run all tests: `pytest` — all pass
- [ ] Lint strict clean: `ruff check` + `mypy src/` — zero errors
- [ ] Test coverage total > 95%: `pytest --cov=src/cauterule --cov-report=term-missing`
- [ ] Update all docs affected by this milestone
- [ ] Verify all issues in this milestone are done
- [ ] Close all completed issues
- [ ] Commit with message: `milestone: M27 complete`
- [ ] Push to main
