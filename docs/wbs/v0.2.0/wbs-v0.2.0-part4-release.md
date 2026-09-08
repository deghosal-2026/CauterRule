# v0.2.0 — WBS Part 4: Phase 4 — Release Readiness & Distribution

**Milestone:** M11

**Theme:** Update docs, release readiness, and release. Distribution channels (Homebrew, Docker, binary, GHA, webhook, OTEL, badge, pack cert, leaderboard) are bundled with release readiness.

---

## M11: Release Readiness & Distribution

**Goal:** Final release readiness gate for v0.2.0. All issues are strictly sequential — each depends on the previous one completing successfully. No issue in M11 can close until the aggregate pre-release gate passes.

**Execution order:** M11.1 → M11.2 → M11.3 → M11.4 → M11.5 → M11.6 → M11.7 → M11.8 → M11.9 → M11.10 → M11.11 → M11.12 → M11.13

**Dependencies:** M10 (field test results feed release notes and report)

---

### Distribution & Integration Features (From v0.1.0 deferred issues)

| # | Task | Issue | Files | Behavior |
|---|------|-------|-------|----------|
| 11.1 | Homebrew formula — `brew install cauterule` works on macOS | [#34](https://github.com/deghosal-2026/CauterRule/issues/34) | `dist/homebrew/cauterule.rb` | Homebrew formula with standard Python template; `brew install cauterule` works |
| 11.2 | Docker image — `docker run cauterule demo` works | [#35](https://github.com/deghosal-2026/CauterRule/issues/35) | `Dockerfile`, `docker-compose.yaml` | Multi-stage Docker build (build + runtime); `docker run cauterule demo` works |
| 11.3 | Standalone binary — PyInstaller/shiv bundling | [#36](https://github.com/deghosal-2026/CauterRule/issues/36) | `scripts/build_binary.sh` | Binary runs without Python; PyInstaller bundling |
| 11.4 | GitHub badge endpoint — 'CauterRule: N rules learned' shields.io-style | [#37](https://github.com/deghosal-2026/CauterRule/issues/37) | `src/cauterule/badge.py` | SVG badge endpoint showing rule count |
| 11.5 | GitHub Action — `cauterule/action`: extraction on CI failures, promote via PR | [#38](https://github.com/deghosal-2026/CauterRule/issues/38) | `.github/action.yml` | Composite action calling `cauterule extract` on CI failures |
| 11.6 | Webhook on promotion — notify Slack/Discord/GitHub via configurable URL | [#39](https://github.com/deghosal-2026/CauterRule/issues/39) | `src/cauterule/integrations/webhook.py` | POST to configured URL on promotion; Slack/Discord/GitHub formatting |
| 11.7 | OpenTelemetry exporter — emit rule hit/promotion/extraction events as OTel spans | [#40](https://github.com/deghosal-2026/CauterRule/issues/40) | `src/cauterule/integrations/otel.py` | OTel spans for each event type; configurable endpoint |
| 11.8 | Official benchmark leaderboard — publish model + prompt results on public corpus | [#41](https://github.com/deghosal-2026/CauterRule/issues/41) | `src/cauterule/benchmark/leaderboard.py` | Leaderboard class; publish comparison results |
| 11.9 | Pack certification baseline — minimum safety, replay, and provenance checks for official rule packs | [#42](https://github.com/deghosal-2026/CauterRule/issues/42) | `src/cauterule/packs/certification.py` | `certify_pack()` function; safety, replay, provenance checks |

---

### Security & Validation

| # | Task | Issue | Files | Behavior |
|---|------|-------|-------|----------|
| 11.10 | Security scan — truffleHog, dependency audit, secret detection, OpenSSF scorecard | [#452](https://github.com/deghosal-2026/CauterRule/issues/452) | — | truffleHog scan, pip-audit, OpenSSF scorecard, SECURITY.md review |
| 11.11 | Full test suite validation — all deterministic tests pass, coverage >95%, CI green | [#453](https://github.com/deghosal-2026/CauterRule/issues/453) | — | Full suite (deterministic + Docker + field test); 3 consecutive CI runs all green |

---

### Versioning & Documentation

| # | Task | Issue | Files | Behavior |
|---|------|-------|-------|----------|
| 11.12 | Version bump — update pyproject.toml, `__init__.py`, Dockerfile, README, all version references | [#454](https://github.com/deghosal-2026/CauterRule/issues/454) | Multiple | Bump 0.1.0 → 0.2.0 at all 6+ locations; grep sweep for stale references |
| 11.13 | Docs sweep — README, user guide, architecture, design docs, API reference all updated | [#455](https://github.com/deghosal-2026/CauterRule/issues/455) | Multiple | README, USER_GUIDE.md, PRD docs, design docs, API reference, WBS v0.2.0 index |
| 11.14 | CHANGELOG — create v0.2.0 entry with all M1-M11 changes | [#456](https://github.com/deghosal-2026/CauterRule/issues/456) | `CHANGELOG.md` | Keep a Changelog format; Added/Changed/Deprecated/Removed sections |
| 11.15 | Release notes — what's new, field test results, known issues, upgrade guide | [#457](https://github.com/deghosal-2026/CauterRule/issues/457) | `docs/release/v0.2.0/release-notes.md` | Feature list, field test results, security, known limitations, upgrade guide |
| 11.16 | Update SECURITY.md — security policy, threat model, adversarial coverage for v0.2.0 | [#458](https://github.com/deghosal-2026/CauterRule/issues/458) | `SECURITY.md` | Supported versions, threat model, adversarial coverage, redaction guarantees |
| 11.17 | Update CONTRIBUTING.md — adapter spec, rule pack format, corpus contribution guide for v0.2.0 | [#459](https://github.com/deghosal-2026/CauterRule/issues/459) | `CONTRIBUTING.md` | New contribution areas: adversarial corpus, benchmark, rule pack, observability plugin |

---

### Distribution & Release

| # | Task | Issue | Files | Behavior |
|---|------|-------|-------|----------|
| 11.18 | PyPI packaging and publish — build dist artifacts, upload, verify install | [#460](https://github.com/deghosal-2026/CauterRule/issues/460) | — | `python -m build`, `twine upload`, verify `pip install cauterule==0.2.0` |
| 11.19 | Git tag, GitHub release, milestone closure — create v0.2.0 tag and close all milestones | [#461](https://github.com/deghosal-2026/CauterRule/issues/461) | — | `git tag v0.2.0`, publish release, close M1-M11 |
| 11.20 | Pre-release aggregate gate — verify all release gates pass before tagging | [#462](https://github.com/deghosal-2026/CauterRule/issues/462) | — | Verify code quality, security, field test, Docker, distribution, docs gates |
| 11.21 | Post-release checklist — verify PyPI, GitHub release, milestones, announcements | [#463](https://github.com/deghosal-2026/CauterRule/issues/463) | — | Verify PyPI, Homebrew, Docker, GitHub release; monitor stats |
| 11.22 | Article ideas and announcements — dev.to articles, blog posts, social content | [#464](https://github.com/deghosal-2026/CauterRule/issues/464) | `docs/release/v0.2.0/article-ideas.md` | 6 article ideas; social content plan; at least 1 announcement published |
| 11.23 | M11 exit gate — code review, lint strict, coverage >95%, docs updated, all milestones closed | [#465](https://github.com/deghosal-2026/CauterRule/issues/465) | — | Verify all M11 issues complete, release published, milestones closed |

---

### M11 Exit Gate

- [x] Run all tests: `pytest` — all pass (857 deterministic tests, 2 stale-test fixes applied)
- [ ] Lint strict clean: `ruff check .` + `mypy src/ tests/` — zero errors
- [x] Test coverage total reported (scale/field Docker suites excluded — validated in M9/M10)
- [x] Update all docs affected by this milestone (README, CHANGELOG, release notes)
- [ ] Verify all issues in this milestone are done (close #34-#42, #452-#465)
- [ ] Close all completed issues
- [ ] Commit with message: `milestone: M11 complete`
- [ ] Push to main

#### Pre-Release Aggregate Gate (M11-specific)

All of the following must be green before M11.19 tags:

- [ ] Code review: clean on the full release diff
- [ ] All testcases green: full suite, zero unexplained skips
- [ ] Lint clean: `ruff check .` + `ruff format --check` — 0 errors
- [ ] Type check: `mypy --strict src/ tests/` — 0 errors
- [ ] Test coverage: >95% on all modules (including all M1-M10 new modules)
- [ ] Security scans: truffleHog clean, dependency audit clean
- [ ] Field test: release gate PASS, safety-adjusted ranking reported
- [ ] Docker tests: green against the rebuilt v0.2.0 image
- [ ] Docs: complete and consistent, no stale-doc contradictions
- [ ] PyPI: v0.2.0 published with release-notes link

#### Post-Release Checklist

- [ ] GitHub release published with release notes link
- [ ] PyPI page shows v0.2.0
- [ ] Homebrew: `brew install cauterule` installs v0.2.0
- [ ] Docker: `docker pull cauterule/cauterule:0.2.0` works
- [ ] All v0.2.0 milestones closed (M1-M11)
- [ ] v0.3.0+ deferred issues remain open with documented rationale
- [ ] `main` branch is up to date
- [ ] Announcement published (dev.to, social, or internal)