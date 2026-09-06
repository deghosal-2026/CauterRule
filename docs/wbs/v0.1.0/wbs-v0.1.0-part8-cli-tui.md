# v0.1.0 — WBS Part 8: CLI, TUI & Observability

**Milestones:** M20-M22

## M20: CLI (Full Surface)

| # | Task | Files | Behavior | Status |
|---|------|-------|----------|--------|
| 20.1 | CLI framework | `src/cauterule/cli/app.py` | Click/Typer-based CLI entry point | ✅ |
| 20.2 | `cauterule init` | `src/cauterule/cli/init.py` | Scaffold: `cauterule.toml`, `rules/`, `.gitignore`, example agent, first rule | ✅ |
| 20.3 | `cauterule demo` | `src/cauterule/cli/demo.py` | Seeded failure history, full loop in <60s, narrated walkthrough | ✅ |
| 20.4 | `cauterule extract` | `src/cauterule/cli/extract.py` | Extract candidate from trajectory; `--dry-run` flag | ✅ |
| 20.5 | `cauterule test` | `src/cauterule/cli/test.py` | Replay-test candidate; `--ci` flag for JUnit XML | ✅ |
| 20.6 | `cauterule promote` | `src/cauterule/cli/promote.py` | Promote tested rule to store (git commit) | ✅ |
| 20.7 | `cauterule inject` | `src/cauterule/cli/inject.py` | Show which rules would fire; `--preflight` flag | ✅ |
| 20.8 | `cauterule list` | `src/cauterule/cli/list.py` | Table: id, trigger, status, hits, tags | ✅ |
| 20.9 | `cauterule show` | `src/cauterule/cli/show.py` | Full provenance view | ✅ |
| 20.10 | `cauterule search` | `src/cauterule/cli/search.py` | Full-text search across rules | ✅ |
| 20.11 | `cauterule audit` | `src/cauterule/cli/audit.py` | Full provenance trail (git log + replay + hits) | ✅ |
| 20.12 | `cauterule diff` | `src/cauterule/cli/diff.py` | Show changes between two versions of a rule | ✅ |
| 20.13 | `cauterule retire` | `src/cauterule/cli/retire.py` | Retire rule with reason (git commit) | ✅ |
| 20.14 | `cauterule history` | `src/cauterule/cli/history.py` | Timeline of promotions and retirements | ✅ |
| 20.15 | `cauterule conflicts` | `src/cauterule/cli/conflicts.py` | List detected conflicts | ✅ |
| 20.16 | `cauterule validate` | `src/cauterule/cli/validate.py` | Check rule store integrity | ✅ |
| 20.17 | `cauterule health` | `src/cauterule/cli/health.py` | Rule store health report | ✅ |
| 20.18 | `cauterule counterfactual` | `src/cauterule/cli/counterfactual.py` | "If you had these rules N days ago, you'd have avoided X failures" | ✅ |
| 20.19 | `cauterule story` | `src/cauterule/cli/story.py` | Generate narrative blog post of learning journey | ✅ |
| 20.20 | `cauterule explain` | `src/cauterule/cli/explain.py` | LLM explains why a rule fires and when | ✅ |
| 20.21 | `cauterule config` | `src/cauterule/cli/config.py` | View/edit configuration | ✅ |
| 20.22 | `cauterule pack` | `src/cauterule/cli/pack.py` | `pack list`, `pack info <name>` | ✅ |
| 20.23 | `cauterule metrics` | `src/cauterule/cli/metrics.py` | CLI summary: rules, precision, repeat-failure rate, store size | ✅ |
| 20.24 | `cauterule report` | `src/cauterule/cli/report.py` | Generate markdown report for sharing | ✅ |

### M20 Exit Gate

- [x] Run all tests: `pytest` — all pass (509 passed)
- [x] Lint strict clean: `ruff check` + `mypy src/` — zero errors
- [x] Test coverage total > 95%: `pytest --cov=src/cauterule --cov-report=term-missing` — 95.44%
- [x] Update all docs affected by this milestone
- [x] Verify all issues in this milestone are done
- [x] Close all completed issues
- [x] Commit with message: `milestone: M20 complete` (in 024cf08)
- [x] Push to main

## M21: TUI Review

| # | Task | Files | Behavior | Status |
|---|------|-------|----------|--------|
| 21.1 | TUI framework | `src/cauterule/tui/app.py` | Textual/rich-based terminal UI | ➡️ v0.2.0 |
| 21.2 | `cauterule review` | `src/cauterule/tui/review.py` | Browse, approve, reject candidates | ➡️ v0.2.0 |
| 21.3 | Evidence summary cards | `src/cauterule/tui/cards.py` | "Prevented 3 failures, broke 0 successes" | ➡️ v0.2.0 |
| 21.4 | Rule confidence cards | `src/cauterule/tui/confidence.py` | Confidence, prevented, broken, last hit, tags | ➡️ v0.2.0 |
| 21.5 | Human annotation capture | `src/cauterule/tui/annotate.py` | Tag, comment, categorize failures | ➡️ v0.2.0 |
| 21.6 | Batch review mode | `src/cauterule/tui/batch.py` | Review 10 candidates in one session | ➡️ v0.2.0 |
| 21.7 | Filter by tag/status/confidence | `src/cauterule/tui/filter.py` | Narrow the review queue | ➡️ v0.2.0 |

### M21 Exit Gate

- [ ] Run all tests: `pytest` — all pass
- [ ] Lint strict clean: `ruff check` + `mypy src/` — zero errors
- [ ] Test coverage total > 95%: `pytest --cov=src/cauterule --cov-report=term-missing`
- [ ] Update all docs affected by this milestone
- [ ] Verify all issues in this milestone are done
- [ ] Close all completed issues
- [ ] Commit with message: `milestone: M21 complete`
- [ ] Push to main

> **Note:** M21 is deferred to v0.2.0. The CLI surface covers all core operations. TUI is a nice-to-have for human review, not a v0.1.0 blocker.

## M22: Observability

| # | Task | Files | Behavior | Status |
|---|------|-------|----------|--------|
| 22.1 | Per-rule hit counter | `src/cauterule/observe/hits.py` | Tracks match count per rule | ➡️ v0.2.0 |
| 22.2 | Last-match timestamp | `src/cauterule/observe/timestamps.py` | Updates `last_match` on each injection | ➡️ v0.2.0 |
| 22.3 | Failure pattern leaderboard | `src/cauterule/observe/leaderboard.py` | Most common failure classes, most prevented, top gaps | ➡️ v0.2.0 |
| 22.4 | Coverage gap detector | `src/cauterule/observe/coverage_gap.py` | Domains with repeated failures but no matching rules | ➡️ v0.2.0 |
| 22.5 | Rule coverage score | `src/cauterule/observe/coverage_score.py` | Weighted blend of coverage %, precision %, stale % | ➡️ v0.2.0 |
| 22.6 | Learning journal | `src/cauterule/observe/journal.py` | Auto-generate markdown log: failure → rule → replay → promotion | ➡️ v0.2.0 |
| 22.7 | Domain coverage score | `src/cauterule/observe/domain_coverage.py` | How well current rules cover failure classes across domains | ➡️ v0.2.0 |
| 22.8 | Failure-class coverage score | `src/cauterule/observe/class_coverage.py` | % of recurring failure classes with at least one validated rule | ➡️ v0.2.0 |
| 22.9 | Coverage frontier | `src/cauterule/observe/coverage_frontier.py` | Identify next most valuable domain/failure family to learn | ➡️ v0.2.0 |
| 22.10 | Monthly learning report | `src/cauterule/observe/monthly_report.py` | Auto-generate report: rules learned, failures reduced, coverage gaps found | ➡️ v0.2.0 |

### M22 Exit Gate

- [ ] Run all tests: `pytest` — all pass
- [ ] Lint strict clean: `ruff check` + `mypy src/` — zero errors
- [ ] Test coverage total > 95%: `pytest --cov=src/cauterule --cov-report=term-missing`
- [ ] Update all docs affected by this milestone
- [ ] Verify all issues in this milestone are done
- [ ] Close all completed issues
- [ ] Commit with message: `milestone: M22 complete`
- [ ] Push to main

> **Note:** M22 is deferred to v0.2.0. The CLI provides basic observability (`metrics`, `health`, `report`). The formal observability subsystem is not a v0.1.0 blocker.
