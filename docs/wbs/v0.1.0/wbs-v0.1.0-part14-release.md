# v0.1.0 — WBS Part 14: Release

**Milestones:** M32

## M32: Release

> **Goal:** Final packaging, documentation, and release of v0.1.0. Tag the release, publish to PyPI, and close all remaining milestones.

| # | Task | Files | Behavior | Status |
|---|------|-------|----------|--------|
| 32.1 | CONTRIBUTING.md | `CONTRIBUTING.md` | How to contribute, adapter spec, rule pack format, corpus guide | ⬜ |
| 32.2 | CHANGELOG.md | `CHANGELOG.md` | Conventional commits, Keep a Changelog format | ⬜ |
| 32.3 | SECURITY.md | `SECURITY.md` | Security policy, threat model summary, adversarial coverage | ⬜ |
| 32.4 | README.md | `README.md` | Updated with full v0.1.0 feature list, quick start, architecture | ⬜ |
| 32.5 | Release notes | `docs/release/v0.1.0/release-notes.md` | What's new, field test results, known issues, upgrade guide | ⬜ |
| 32.6 | Release gate check | `scripts/release_check.sh` | Verify all release gates pass (demo, precision, counterexample, redaction, validate, install) | ⬜ |
| 32.7 | Build & publish to PyPI | `pyproject.toml`, `Dockerfile` | Build sdist + wheel, upload to PyPI | ⬜ |
| 32.8 | Git tag & GitHub release | — | Tag v0.1.0, publish GitHub release, close all milestones | ⬜ |

### M32 Exit Gate

- [ ] Run all tests: `pytest` — all pass
- [ ] Lint strict clean: `ruff check` + `mypy src/` — zero errors
- [ ] Test coverage total > 95%: `pytest --cov=src/cauterule --cov-report=term-missing`
- [ ] Update all docs affected by this milestone
- [ ] Verify all issues in this milestone are done
- [ ] Close all completed issues
- [ ] Commit with message: `milestone: M32 complete`
- [ ] Push to main