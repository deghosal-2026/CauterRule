# v0.4.0 — WBS Part 1: Phase 1 — Deep Integrations & Observability

**Milestones:** M1-M2 ([M1](https://github.com/deghosal-2026/CauterRule/milestone/58) · [M2](https://github.com/deghosal-2026/CauterRule/milestone/59))

**Theme:** Connect CauterRule to the agent ecosystem (observability platforms, eval forges, CI) and make learning visible (dashboard, digests, trends). Outcome tracking first — metrics depend on it (#561).

---

## M1: Deep Integrations (9 issues)

**Goal:** Production failures and synthetic scenarios flow into extraction; rule testing runs in CI with PR annotations.

**Dependencies:** None (foundation for v0.4.0; builds on v0.3.0 adapters)

| # | Task | Issue |
|---|------|-------|
| 1.1 | LangSmith/Phoenix rule-event export | [#539](https://github.com/deghosal-2026/CauterRule/issues/539) |
| 1.2 | DecisionJournal integration — decision log becomes historical scenarios | [#535](https://github.com/deghosal-2026/CauterRule/issues/535) |
| 1.3 | AgentObservatory integration — prod failures flow into extraction | [#533](https://github.com/deghosal-2026/CauterRule/issues/533) |
| 1.4 | Rule testing in CI: GitHub Action with PR annotations (GA) | [#530](https://github.com/deghosal-2026/CauterRule/issues/530) |
| 1.5 | Integration docs + example repo (all platforms e2e) | [#528](https://github.com/deghosal-2026/CauterRule/issues/528) |
| 1.6 | AgentEvalForge integration — synthetic scenarios feed replay | [#529](https://github.com/deghosal-2026/CauterRule/issues/529) |
| 1.7 | Real-agent + chaos + long-running integration tests | [#485](https://github.com/deghosal-2026/CauterRule/issues/485) |
| 1.8 | Deep integrations epic: AgentObservatory + AgentEvalForge + LangSmith/Phoenix | [#484](https://github.com/deghosal-2026/CauterRule/issues/484) |
| 1.9 | CI rule testing: test --ci as GitHub Action with PR annotations | [#483](https://github.com/deghosal-2026/CauterRule/issues/483) |

### M1 Exit Gate

- [ ] All tests run clear: `pytest` — all pass
- [ ] Total code coverage > 92%: `pytest --cov=src/cauterule --cov-report=term-missing`
- [ ] Lint strict clean: `ruff check .` + `mypy src/ tests/` — zero errors
- [ ] All necessary and affected docs are updated
- [ ] Verify all issues in this milestone are done
- [ ] Close all completed issues
- [ ] Code committed and pushed to branch (v0.4.0 branch — TBD, confirm before Phase 1)

---

## M2: Observability & Analytics (9 issues)

**Goal:** A dashboard that shows store growth, precision/recall, and replay evidence — plus weekly digests, trend lines, and accessibility/i18n foundations.

**Dependencies:** M1 (integration event streams) + outcome tracking prerequisite (#561 → #589, #562)

| # | Task | Issue |
|---|------|-------|
| 2.1 | TUI accessibility mode + CLI --no-color guarantee + i18n infrastructure | [#590](https://github.com/deghosal-2026/CauterRule/issues/590) |
| 2.2 | OSS traction metrics tracking + derived scores (Learning Efficiency / Trust / DX) | [#589](https://github.com/deghosal-2026/CauterRule/issues/589) |
| 2.3 | Weekly digest + stakeholder report (email/markdown) | [#569](https://github.com/deghosal-2026/CauterRule/issues/569) |
| 2.4 | Dashboard frontend — store growth, precision/recall, hit-rate heatmap | [#568](https://github.com/deghosal-2026/CauterRule/issues/568) |
| 2.5 | Dashboard backend — cauterule dashboard API (FastAPI) | [#567](https://github.com/deghosal-2026/CauterRule/issues/567) |
| 2.6 | Metrics dependency: outcome tracking must land first (v0.2.1) | [#561](https://github.com/deghosal-2026/CauterRule/issues/561) |
| 2.7 | Replay visualization in dashboard (evidence explorer) | [#566](https://github.com/deghosal-2026/CauterRule/issues/566) |
| 2.8 | Trend lines + failure-recurrence tracking | [#562](https://github.com/deghosal-2026/CauterRule/issues/562) |
| 2.9 | Web dashboard + weekly digest (v0.5.0 observability epic) | [#482](https://github.com/deghosal-2026/CauterRule/issues/482) |

### M2 Exit Gate

- [ ] All tests run clear: `pytest` — all pass
- [ ] Total code coverage > 92%: `pytest --cov=src/cauterule --cov-report=term-missing`
- [ ] Lint strict clean: `ruff check .` + `mypy src/ tests/` — zero errors
- [ ] All necessary and affected docs are updated
- [ ] Verify all issues in this milestone are done
- [ ] Close all completed issues
- [ ] Code committed and pushed to branch (v0.4.0 branch — TBD, confirm before Phase 1)
