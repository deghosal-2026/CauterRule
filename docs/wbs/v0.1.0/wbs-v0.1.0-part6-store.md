# v0.1.0 — WBS Part 6: Rule Store, Packs & Injection

**Milestones:** M15-M17

## M15: Rule Store

| # | Task | Files | Behavior | Status |
|---|------|-------|----------|--------|
| 15.1 | Rule store manager | `src/cauterule/store/manager.py` | CRUD: add, get, list, retire, supersede rules | ✅ |
| 15.2 | Index file manager | `src/cauterule/store/index.py` | Maintains `rules/index.yaml` with all rules, statuses, tags, taxonomy | ✅ |
| 15.3 | Archive manager | `src/cauterule/store/archive.py` | Moves retired rules to `rules/archived/` | ✅ |
| 15.4 | Git operations | `src/cauterule/store/git.py` | Commit promotion/retirement/consolidation with conventional messages | ✅ |
| 15.5 | Rollback support | `src/cauterule/store/rollback.py` | `git revert` any promotion; store stays consistent | ✅ |
| 15.6 | Store validator | `src/cauterule/store/validator.py` | `cauterule validate`: no orphaned refs, missing provenance, broken links, duplicate IDs | ✅ |
| 15.7 | Store health report | `src/cauterule/store/health.py` | `cauterule health`: coverage, stale rules, conflicts, avg effectiveness, coverage gaps | ✅ |

### M15 Exit Gate

- [x] Run all tests: `pytest` — all pass (509 passed)
- [x] Lint strict clean: `ruff check` + `mypy src/` — zero errors
- [x] Test coverage total > 95%: `pytest --cov=src/cauterule --cov-report=term-missing` — 95.44%
- [x] Update all docs affected by this milestone
- [x] Verify all issues in this milestone are done
- [x] Close all completed issues
- [x] Commit with message: `milestone: M15 complete` (in 024cf08)
- [x] Push to main

## M16: Rule Packs

| # | Task | Files | Behavior | Status |
|---|------|-------|----------|--------|
| 16.1 | Pack format spec | `src/cauterule/packs/format.py` | Manifest with name, version, description, author, rule list | ✅ |
| 16.2 | Pack loader | `src/cauterule/packs/loader.py` | Loads pack rules from `rules/packs/<name>/` | ✅ |
| 16.3 | Pack manager | `src/cauterule/packs/manager.py` | `cauterule pack list`, `cauterule pack info <name>` | ✅ |
| 16.4 | Bundled `pack-git` | `packs/pack-git/manifest.yaml`, `R-101.yaml`...`R-115.yaml` | 10-15 pre-built git rules (push, merge, rebase, conflicts, hooks) | ✅ |
| 16.5 | Pack rule read-only enforcement | `src/cauterule/packs/readonly.py` | Pack rules cannot be retired or modified locally | ✅ |

### M16 Exit Gate

- [x] Run all tests: `pytest` — all pass (509 passed)
- [x] Lint strict clean: `ruff check` + `mypy src/` — zero errors
- [x] Test coverage total > 95%: `pytest --cov=src/cauterule --cov-report=term-missing` — 95.44%
- [x] Update all docs affected by this milestone
- [x] Verify all issues in this milestone are done
- [x] Close all completed issues
- [x] Commit with message: `milestone: M16 complete` (in 024cf08)
- [x] Push to main

## M17: Rule Injection & Loop Orchestration

| # | Task | Files | Behavior | Status |
|---|------|-------|----------|--------|
| 17.1 | Structured matcher | `src/cauterule/injection/matcher.py` | Match by trigger, tool, error type, context, tags, taxonomy | ✅ |
| 17.2 | Specificity ordering | `src/cauterule/injection/ordering.py` | More specific rules first | ✅ |
| 17.3 | Injection formatter | `src/cauterule/injection/formatter.py` | Produces clean markdown block for agent context | ✅ |
| 17.4 | Rule explanations | `src/cauterule/injection/explainer.py` | LLM generates human-readable explanation of why rule fires | ✅ |
| 17.5 | Rule templates | `src/cauterule/injection/templates.py` | retry, verify-then-act, check-preconditions | ✅ |
| 17.6 | Context budget optimizer | `src/cauterule/injection/budget.py` | Rank rules, compress, fit token budget | ✅ |
| 17.7 | Preflight mode | `src/cauterule/injection/preflight.py` | Predict likely failures and recommend rules before task | ✅ |
| 17.8 | No-match graceful degradation | `src/cauterule/injection/fallback.py` | Empty set if no rules match | ✅ |
| 17.9 | Lesson portfolio optimizer | `src/cauterule/injection/portfolio.py` | If only N rules can be injected, choose the set that maximizes expected failure prevention | ✅ |
| 17.10 | Loop orchestrator | `src/cauterule/loop/orchestrator.py` | Wires capture → redact → cluster → extract → lint → replay → tournament → conflict → promote → inject into one triggered pipeline with error-handling policy | ✅ |
| 17.11 | Loop error handling | `src/cauterule/loop/errors.py` | Extraction retry, replay failure hold, linter block, git push retry, async conflict retry, redaction block | ✅ |

### M17 Exit Gate

- [x] Run all tests: `pytest` — all pass (509 passed)
- [x] Lint strict clean: `ruff check` + `mypy src/` — zero errors
- [x] Test coverage total > 95%: `pytest --cov=src/cauterule --cov-report=term-missing` — 95.44%
- [x] Update all docs affected by this milestone
- [x] Verify all issues in this milestone are done
- [x] Close all completed issues
- [x] Commit with message: `milestone: M17 complete` (in 024cf08)
- [x] Push to main
