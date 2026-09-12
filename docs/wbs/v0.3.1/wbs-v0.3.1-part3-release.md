# v0.3.1 — WBS Part 3: Phase 3 — Release Readiness & Launch

**Milestone:** M3 ([v0.3.1-M3: Release Readiness & Launch](https://github.com/deghosal-2026/CauterRule/milestone/68))

**Theme:** Version bump → validation → security → packaging (PyPI/Docker/Homebrew) → docs/notes/CHANGELOG → badges → pre-release gate → tag → launch → post-release → merge.

---

## M3: Release Readiness & Launch (16 issues)

**Goal:** Ship and announce v0.3.1. Strictly sequential — no release artifact publishes until the aggregate pre-release gate passes.

**Execution order:** bump (#746) → validation (#747) → security (#748) → packaging (#749, #750, #751) → docs (#752, #755, #753, #754) → badges (#756) → pre-release gate (#757) → tag (#758) → launch (#759) → post-release (#760) → merge (#761).

**Dependencies:** M2 (field test results feed the report, release notes, and known issues).

| # | Task | Issue |
|---|------|-------|
| 3.1 | Version bump 0.3.0 → 0.3.1 — pyproject, `__init__`, Dockerfile, README, all refs | [#746](https://github.com/deghosal-2026/CauterRule/issues/746) |
| 3.2 | Full test suite validation — tests, coverage ≥92%, ruff/mypy strict, CI | [#747](https://github.com/deghosal-2026/CauterRule/issues/747) |
| 3.3 | Security scan — truffleHog, pip-audit, OpenSSF, secret detection | [#748](https://github.com/deghosal-2026/CauterRule/issues/748) |
| 3.4 | PyPI packaging and publish 0.3.1 — build, TestPyPI, PyPI, verify install | [#749](https://github.com/deghosal-2026/CauterRule/issues/749) |
| 3.5 | Docker publish — multi-arch build + push `v0.3.1` + `latest` | [#750](https://github.com/deghosal-2026/CauterRule/issues/750) |
| 3.6 | Homebrew bump to 0.3.1 | [#751](https://github.com/deghosal-2026/CauterRule/issues/751) |
| 3.7 | Docs sweep — README, user guide, architecture, adapters | [#752](https://github.com/deghosal-2026/CauterRule/issues/752) |
| 3.8 | CHANGELOG — v0.3.1 entry (Keep a Changelog) | [#753](https://github.com/deghosal-2026/CauterRule/issues/753) |
| 3.9 | Release notes — v0.3.1 (fixes, results, known issues, upgrade guide) | [#754](https://github.com/deghosal-2026/CauterRule/issues/754) |
| 3.10 | Update SECURITY.md and CONTRIBUTING.md | [#755](https://github.com/deghosal-2026/CauterRule/issues/755) |
| 3.11 | Refresh badges (version, coverage, field test) | [#756](https://github.com/deghosal-2026/CauterRule/issues/756) |
| 3.12 | Pre-release aggregate gate — verify all gates pass before tagging | [#757](https://github.com/deghosal-2026/CauterRule/issues/757) |
| 3.13 | Tag `v0.3.1`, GitHub release, close milestones | [#758](https://github.com/deghosal-2026/CauterRule/issues/758) |
| 3.14 | Launch — announcements + dev.to articles | [#759](https://github.com/deghosal-2026/CauterRule/issues/759) |
| 3.15 | Post-release verification checklist | [#760](https://github.com/deghosal-2026/CauterRule/issues/760) |
| 3.16 | Merge all changes to main | [#761](https://github.com/deghosal-2026/CauterRule/issues/761) |

### Launch scope (#759)

- Publish v0.3.1 dev.to articles, including the extraction-vs-replay piece and any new ones.
- Blog post / GitHub discussion / social posts; update README "Field Test Results".
- Cross-link the field test report and release notes.

### M3 Exit Gate (Final Release Gate)

- [ ] **All tests pass:** `pytest` — all pass
- [ ] **Lint strict clean:** `ruff check .` — zero errors
- [ ] **Types strict clean:** `mypy src/ tests/` (strict) — zero errors
- [ ] **Test coverage > 92%** (deterministic subset)
- [ ] **All necessary and affected docs updated** (README, user guide, release notes, CHANGELOG, SECURITY, WBS)
- [ ] **Code committed and pushed** to `feat-v0.3.1`, then merged to `main` (#761)
- [ ] **WBS updated** (`docs/wbs/v0.3.1/`)
- [ ] **All 16 M3 issues closed** and milestones M1-M3 closed
- [ ] Pre-release aggregate gate passed (#757)
- [ ] PyPI + Docker + Homebrew 0.3.1 verified by a fresh install/pull
- [ ] Tag `v0.3.1` + GitHub release published
- [ ] Launch announcement published

### See also

- [Part 2 — Evaluation & Field Test](wbs-v0.3.1-part2-field-test.md)
- [v0.3.0 WBS Part 4](../v0.3.0/wbs-v0.3.0-part4-release.md) (the template)
