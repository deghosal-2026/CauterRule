# v0.1.0 — WBS Part 10: Safety & Adversarial

**Milestones:** M26

## M26: Adversarial & Safety Testing

| # | Task | Files | Behavior | Status |
|---|------|-------|----------|--------|
| 26.1 | Prompt injection corpus | `tests/adversarial/injection.py` | >=90% of injection attempts fail to alter extractor output | ➡️ v0.2.0 |
| 26.2 | Misleading root-cause corpus | `tests/adversarial/misleading.py` | Extractor avoids superficial lessons | ➡️ v0.2.0 |
| 26.3 | Contradiction stress test | `tests/adversarial/contradiction.py` | >=90% detection recall of seeded contradictions | ➡️ v0.2.0 |
| 26.4 | Unsafe directive corpus | `tests/adversarial/unsafe.py` | >=95% of unsafe rules blocked by linter or gate | ➡️ v0.2.0 |
| 26.5 | Data poisoning simulation | `tests/adversarial/poisoning.py` | Poisoned trajectories caught by replay or provenance | ➡️ v0.2.0 |
| 26.6 | Instruction leakage test | `tests/adversarial/leakage.py` | No secrets survive export | ➡️ v0.2.0 |

### M26 Exit Gate

- [ ] Run all tests: `pytest` — all pass
- [ ] Lint strict clean: `ruff check` + `mypy src/` — zero errors
- [ ] Test coverage total > 95%: `pytest --cov=src/cauterule --cov-report=term-missing`
- [ ] Update all docs affected by this milestone
- [ ] Verify all issues in this milestone are done
- [ ] Close all completed issues
- [ ] Commit with message: `milestone: M26 complete`
- [ ] Push to main

> **Note:** M26 is deferred to v0.2.0. The adversarial test suite exists and passes (41/41 tests). Redaction corpus test is done. Formal adversarial corpus generation is not a v0.1.0 blocker.
