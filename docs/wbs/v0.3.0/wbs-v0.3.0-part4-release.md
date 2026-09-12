# v0.3.0 — WBS Part 4: Phase 4 — Release Readiness & Distribution

**Milestone:** M8 ([v0.3.0-M8: Release Readiness](https://github.com/deghosal-2026/CauterRule/milestone/63))

**Theme:** Docs, release readiness, and release. Version bump → validation → packaging (PyPI/Docker/Homebrew) → docs/notes → announcements → merge.

---

## M8: Release Readiness & Distribution (17 issues)

**Goal:** Final release gate for v0.3.0. Strictly sequential — no issue closes until the aggregate pre-release gate passes.

**Execution order:** bump (#626) → validation (#622) → security (#620) → packaging (#649, #654, #657) → docs (#645, #640, #637, #633, #630) → badges (#670) → pre-release gate (#665) → tag (#661) → announcements (#675) → post-release (#668) → merge (#674)

**Dependencies:** M7 (field test results feed release notes and report)

| # | Task | Issue |
|---|------|-------|
| 8.1 | Version bump — pyproject.toml, __init__.py, Dockerfile, README, all version refs | [#626](https://github.com/deghosal-2026/CauterRule/issues/626) ✓ |
| 8.2 | Full test suite validation — all deterministic tests pass, coverage ≥85%, CI green | [#622](https://github.com/deghosal-2026/CauterRule/issues/622) ✓ |
| 8.3 | Security scan — truffleHog, dependency audit, secret detection, OpenSSF scorecard | [#620](https://github.com/deghosal-2026/CauterRule/issues/620) ✓ |
| 8.4 | PyPI packaging and publish — build dist artifacts, upload, verify install | [#649](https://github.com/deghosal-2026/CauterRule/issues/649) ✓ |
| 8.5 | Docker publish — build + push to GHCR with v0.3.0 tag | [#654](https://github.com/deghosal-2026/CauterRule/issues/654) |
| 8.6 | Homebrew bump — update formula for v0.3.0 release | [#657](https://github.com/deghosal-2026/CauterRule/issues/657) |
| 8.7 | Update CONTRIBUTING.md — pack format, adapter spec, corpus guide for v0.3.0 | [#645](https://github.com/deghosal-2026/CauterRule/issues/645) ✓ |
| 8.8 | Update SECURITY.md — security policy, threat model, adversarial coverage | [#640](https://github.com/deghosal-2026/CauterRule/issues/640) ✓ |
| 8.9 | Docs sweep — README, user guide, architecture, design docs, API reference | [#637](https://github.com/deghosal-2026/CauterRule/issues/637) ✓ |
| 8.10 | Release notes — what's new, field test results, known issues, upgrade guide | [#633](https://github.com/deghosal-2026/CauterRule/issues/633) ✓ |
| 8.11 | CHANGELOG — create v0.3.0 entry with all M1-M8 changes | [#630](https://github.com/deghosal-2026/CauterRule/issues/630) ✓ |
| 8.12 | Update README badges — fresh coverage, field test, license, version badges | [#670](https://github.com/deghosal-2026/CauterRule/issues/670) |
| 8.13 | Pre-release aggregate gate — verify all release gates pass before tagging | [#665](https://github.com/deghosal-2026/CauterRule/issues/665) ✓ |
| 8.14 | Git tag, GitHub release, milestone closure — create v0.3.0 tag | [#661](https://github.com/deghosal-2026/CauterRule/issues/661) |
| 8.15 | Article ideas and announcements — dev.to articles, blog posts, social content | [#675](https://github.com/deghosal-2026/CauterRule/issues/675) |
| 8.16 | Post-release checklist — verify PyPI, GitHub release, milestones, announcements | [#668](https://github.com/deghosal-2026/CauterRule/issues/668) |
| 8.17 | Merge all changes to main — final PR with all v0.3.0 changes | [#674](https://github.com/deghosal-2026/CauterRule/issues/674) |

### M8 Exit Gate (Final Release Gate)

- [ ] All 8 milestones complete and exit gates passed
- [ ] M7 field test complete and report published
- [ ] Pre-release aggregate gate passes (#665)
- [ ] Security scan clean (#620)
- [ ] All tests run clear: `pytest` — all pass
- [ ] Total code coverage > 85% (deterministic subset): `pytest --cov=src/cauterule --cov-report=term-missing --ignore=tests/field --ignore=tests/scale -k "not docker"`
- [ ] Lint strict clean: `ruff check .` + `mypy src/ tests/` — zero errors
- [ ] All necessary and affected docs are updated (field test report, release notes, CHANGELOG)
- [ ] All distribution channels verified (PyPI, Homebrew, Docker)
- [ ] Tag v0.3.0 created, GitHub release published, milestones closed
- [ ] Code committed and pushed to branch (`feat-v0.3.0`), then merge feat-v0.3.0 → main (#674)
