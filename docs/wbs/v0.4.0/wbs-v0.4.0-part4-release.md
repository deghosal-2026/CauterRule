# v0.4.0 — WBS Part 4: Phase 4 — Release Readiness & Distribution

**Milestone:** M6 ([v0.4.0-M6: Release Readiness](https://github.com/deghosal-2026/CauterRule/milestone/65))

**Theme:** Docs, release readiness, and release. Version bump → validation → packaging (PyPI via TestPyPI, multi-arch Docker, Homebrew) → docs/notes → announcements → merge.

---

## M6: Release Readiness & Distribution (17 issues)

**Goal:** Final release gate for v0.4.0. Strictly sequential — no issue closes until the aggregate pre-release gate passes.

**Execution order:** bump (#621) → validation (#618) → security (#617) → packaging (#644, #646, #651) → docs (#639, #634, #632, #627, #623) → badges (#666) → pre-release gate (#660) → tag (#655) → announcements (#672) → post-release (#662) → merge (#669)

**Dependencies:** M5 (field test results feed release notes and report)

| # | Task | Issue |
|---|------|-------|
| 6.1 | Version bump — pyproject.toml, __init__.py, Dockerfile, README v0.3.0 → v0.4.0 | [#621](https://github.com/deghosal-2026/CauterRule/issues/621) |
| 6.2 | Full test suite validation — all deterministic tests pass, coverage >95%, CI green | [#618](https://github.com/deghosal-2026/CauterRule/issues/618) |
| 6.3 | Security scan — truffleHog, dependency audit, secret detection, OpenSSF scorecard | [#617](https://github.com/deghosal-2026/CauterRule/issues/617) |
| 6.4 | PyPI packaging and publish — build, upload to TestPyPI then PyPI, verify install | [#644](https://github.com/deghosal-2026/CauterRule/issues/644) |
| 6.5 | Docker publish — multi-arch build + push with v0.4.0 tag + latest | [#646](https://github.com/deghosal-2026/CauterRule/issues/646) |
| 6.6 | Homebrew bump — update formula for v0.4.0 release | [#651](https://github.com/deghosal-2026/CauterRule/issues/651) |
| 6.7 | Update CONTRIBUTING.md — integration adapter spec, dashboard theming | [#639](https://github.com/deghosal-2026/CauterRule/issues/639) |
| 6.8 | Update SECURITY.md — new integration footprint, fleet security model | [#634](https://github.com/deghosal-2026/CauterRule/issues/634) |
| 6.9 | Docs sweep — README, user guide, architecture, design docs, API reference | [#632](https://github.com/deghosal-2026/CauterRule/issues/632) |
| 6.10 | Release notes — what's new, field test results, known issues, upgrade guide | [#627](https://github.com/deghosal-2026/CauterRule/issues/627) |
| 6.11 | CHANGELOG — create v0.4.0 entry with all M1-M6 changes | [#623](https://github.com/deghosal-2026/CauterRule/issues/623) |
| 6.12 | Update README badges — fresh v0.4.0 badges | [#666](https://github.com/deghosal-2026/CauterRule/issues/666) |
| 6.13 | Pre-release aggregate gate — verify all gates pass before tagging | [#660](https://github.com/deghosal-2026/CauterRule/issues/660) |
| 6.14 | Git tag, GitHub release, milestone closure — create v0.4.0 tag and close all milestones | [#655](https://github.com/deghosal-2026/CauterRule/issues/655) |
| 6.15 | Article ideas and announcements — dev.to articles, blog posts, social content | [#672](https://github.com/deghosal-2026/CauterRule/issues/672) |
| 6.16 | Post-release checklist — verify PyPI, GitHub, Docker, milestones, announcements | [#662](https://github.com/deghosal-2026/CauterRule/issues/662) |
| 6.17 | Merge all changes to main — final PR, code review, merge, verify CI | [#669](https://github.com/deghosal-2026/CauterRule/issues/669) |

### M6 Exit Gate (Final Release Gate)

- [ ] All 6 milestones complete and exit gates passed
- [ ] M5 field test complete and report published (semantic + fleet results)
- [ ] Pre-release aggregate gate passes (#660)
- [ ] Security scan clean (#617) with new integration footprint
- [ ] All tests run clear: `pytest` — all pass
- [ ] Total code coverage > 92%: `pytest --cov=src/cauterule --cov-report=term-missing`
- [ ] Lint strict clean: `ruff check .` + `mypy src/ tests/` — zero errors
- [ ] All necessary and affected docs are updated (field test report, release notes, CHANGELOG)
- [ ] All distribution channels verified (PyPI incl. TestPyPI, Docker multi-arch, Homebrew)
- [ ] Tag v0.4.0 created, GitHub release published, milestones closed
- [ ] Code committed and pushed to branch (v0.4.0 branch — TBD, confirm before Phase 1)
