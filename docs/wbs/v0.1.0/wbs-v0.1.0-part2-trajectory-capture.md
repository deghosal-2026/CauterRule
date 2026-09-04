# v0.1.0 — WBS Part 2: Trajectory Capture & Redaction

**Milestones:** M4-M5

## M4: Trajectory Capture

| # | Task | Files | Behavior | Status |
|---|------|-------|----------|--------|
| 4.1 | `@cauterule.watch` decorator | `src/cauterule/adapter/decorator.py` | Wraps any agent function; captures trajectory on failure | ⬜ |
| 4.2 | `cauterule.inject()` context manager | `src/cauterule/adapter/inject.py` | Preps context with matching rules before task execution | ⬜ |
| 4.3 | Trajectory writer | `src/cauterule/capture/writer.py` | Writes JSONL to `trajectories/YYYY-MM-DD/failure-T-{NNN}.jsonl` or `success-T-{NNN}.jsonl` | ⬜ |
| 4.4 | Step capture | `src/cauterule/capture/step.py` | Captures tool name, input, output, error, state per step | ⬜ |
| 4.5 | Failure point detection | `src/cauterule/capture/failure.py` | Identifies which step failed and classifies failure class | ⬜ |
| 4.6 | Auto-classified failure taxonomy | `src/cauterule/capture/taxonomy.py` | Labels trajectories with `git/push`, `python/import`, `docker/network`, etc. | ⬜ |
| 4.7 | Trajectory metadata enrichment | `src/cauterule/capture/metadata.py` | Adds quality_label, domain, severity, tags, environment | ⬜ |

### M4 Exit Gate

- [ ] Run all tests: `pytest` — all pass
- [ ] Lint strict clean: `ruff check` + `mypy src/` — zero errors
- [ ] Test coverage total > 95%: `pytest --cov=src/cauterule --cov-report=term-missing`
- [ ] Update all docs affected by this milestone
- [ ] Verify all issues in this milestone are done
- [ ] Close all completed issues
- [ ] Commit with message: `milestone: M4 complete`
- [ ] Push to main

## M5: Redaction

| # | Task | Files | Behavior | Status |
|---|------|-------|----------|--------|
| 5.1 | Redaction engine | `src/cauterule/redaction/engine.py` | Strips secrets from trajectory before LLM extraction | ⬜ |
| 5.2 | Built-in secret patterns | `src/cauterule/redaction/patterns.py` | AWS keys, GitHub tokens, JWTs, generic API keys, passwords | ⬜ |
| 5.3 | Custom pattern config | `src/cauterule/redaction/config.py` | User-defined patterns via `cauterule.toml` | ⬜ |
| 5.4 | Redaction flag on trajectory | `src/cauterule/redaction/flag.py` | Sets `redacted: true` on trajectory metadata | ⬜ |
| 5.5 | Redaction corpus test | `tests/redaction/test_corpus.py` | 100% success on redaction corpus | ⬜ |

### M5 Exit Gate

- [ ] Run all tests: `pytest` — all pass
- [ ] Lint strict clean: `ruff check` + `mypy src/` — zero errors
- [ ] Test coverage total > 95%: `pytest --cov=src/cauterule --cov-report=term-missing`
- [ ] Update all docs affected by this milestone
- [ ] Verify all issues in this milestone are done
- [ ] Close all completed issues
- [ ] Commit with message: `milestone: M5 complete`
- [ ] Push to main
