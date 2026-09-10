# v0.4.0 — WBS Part 3: Phase 3 — Field Test

**Milestone:** M5 ([v0.4.0-M5: Field Test](https://github.com/deghosal-2026/CauterRule/milestone/64))

**Theme:** Prove semantic matching + fleet work on real models, with new trajectories for integrations/matching/fleet and embedding cost tracking.

---

## M5: Field Test (12 issues)

**Goal:** Run the v0.4.0 field test across 2 OMLX local LLMs + cloud LLMs, with updated runner scripts, new corpus trajectories, Docker + dashboard + fleet-cluster validation, and a published report with semantic + fleet results.

**Execution order:** plan (#619) → runner scripts (#624) → corpus (#628) → Docker plan/run (#631, #636) → model runs (#638, #643) → measurements (#647, #652) → report (#656) → known issues (#659) → exit gate (#664)

**Dependencies:** M1-M4 (all integrations, matching, and fleet features under test)

| # | Task | Issue |
|---|------|-------|
| 5.1 | Create field test plan — methodology, corpus plan, thresholds, scoring | [#619](https://github.com/deghosal-2026/CauterRule/issues/619) |
| 5.2 | Update field test runner scripts for v0.4.0 changes | [#624](https://github.com/deghosal-2026/CauterRule/issues/624) |
| 5.3 | Update corpus for v0.4.0 field test — integrations/matching/fleet | [#628](https://github.com/deghosal-2026/CauterRule/issues/628) |
| 5.4 | Docker test plan — multi-service compose, integration services, dashboard container | [#631](https://github.com/deghosal-2026/CauterRule/issues/631) |
| 5.5 | Create and run Docker tests — integration suites, dashboard smoke, fleet cluster | [#636](https://github.com/deghosal-2026/CauterRule/issues/636) |
| 5.6 | Run field test against 2 OMLX local LLMs — integration + matching + fleet | [#638](https://github.com/deghosal-2026/CauterRule/issues/638) |
| 5.7 | Run field test against cloud LLMs — gpt-4o-mini + llama-3.1-8b-instruct | [#643](https://github.com/deghosal-2026/CauterRule/issues/643) |
| 5.8 | Cost measurement — LLM + embedding cost per candidate, per promoted rule | [#647](https://github.com/deghosal-2026/CauterRule/issues/647) |
| 5.9 | Multi-environment validation — macOS, Linux, Docker end-to-end | [#652](https://github.com/deghosal-2026/CauterRule/issues/652) |
| 5.10 | Generate field test report — semantic + fleet results | [#656](https://github.com/deghosal-2026/CauterRule/issues/656) |
| 5.11 | Document known issues — per-feature severity, workaround, assignee | [#659](https://github.com/deghosal-2026/CauterRule/issues/659) |
| 5.12 | M5 exit gate — code review, lint strict, coverage, docs updated, all issues resolved | [#664](https://github.com/deghosal-2026/CauterRule/issues/664) |

### M5 Exit Gate

- [ ] All tests run clear: `pytest` — all pass
- [ ] Total code coverage > 92%: `pytest --cov=src/cauterule --cov-report=term-missing`
- [ ] Lint strict clean: `ruff check .` + `mypy src/ tests/` — zero errors
- [ ] All necessary and affected docs are updated
- [ ] Field test report published with semantic + fleet results
- [ ] Known issues documented with severity/workaround/assignee
- [ ] Verify all issues in this milestone are done
- [ ] Close all completed issues
- [ ] Code committed and pushed to branch (v0.4.0 branch — TBD, confirm before Phase 1)
