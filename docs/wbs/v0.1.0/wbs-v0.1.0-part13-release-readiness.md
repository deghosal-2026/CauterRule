# v0.1.0 — WBS Part 13: Release Readiness

**Milestones:** M32

## M32: Release Readiness

> **Goal:** Final release readiness gate for v0.1.0. All issues are strictly sequential — each depends on the previous one completing successfully. No issue in M32 can close until the aggregate pre-release gate passes.

**Execution order:** M32.1 → M32.2 → M32.3 → M32.4 → M32.5 → M32.6

| Issue | Title | Area | Complexity |
|-------|-------|------|------------|
| M32.1 | Security scan — truffleHog, dependency audit, secret detection | security | low |
| M32.2 | All tests passing — full deterministic suite + field test confirmed green | testing | medium |
| M32.3 | Field test report finalized — results document, scorecards, verdict deltas | docs/field-test | medium |
| M32.4 | Docs sweep — README, CHANGELOG, release notes, all docs | docs | medium |
| M32.5 | Packaging & PyPI release — build, dist, Dockerfile pin, upload | release | medium |
| M32.6 | Release tags and milestone closure — git tag, GitHub release, close all v0.1.0 milestones | release | low |

---

### M32.1 — Security scan — truffleHog, dependency audit, secret detection

**Problem:** Before shipping v0.1.0, the release must pass a security scan. Any leaked secrets, vulnerable dependencies, or security regressions must be caught before the tag is created.

**Scope:**
- Run truffleHog across the entire repo to detect any committed secrets
- Run `pip-audit` or equivalent dependency vulnerability scanner
- Verify SECURITY.md is current and accurate
- Confirm no new secrets or credentials are committed in M1-M31 changes
- Run OpenSSF scorecard check (if applicable)

**Completion checklist:**
- [ ] truffleHog scan completes with zero findings (or documented false positives)
- [ ] Dependency audit shows zero known vulnerabilities in production dependencies
- [ ] SECURITY.md reviewed and updated if needed
- [ ] Any secrets found are removed and the commit history is cleaned
- [ ] Scan results published in the release notes
- [ ] OpenSSF badge passing (or regression filed with mitigation)

---

### M32.2 — All tests passing — full deterministic suite + field test confirmed green

**Problem:** All code merged in M1-M31 must pass the full test suite. This includes the deterministic tests, the field test sweep, and the Docker integration test. No test failures are acceptable at release time.

**Scope:**
- Run full deterministic test suite: `pytest tests/ --cov=src/`
- Confirm all 235+ deterministic tests pass
- Confirm field test results from M31 show 0 true failures
- Confirm Docker integration test passes
- Verify no flaky tests are polluting results
- Run tests in CI (GitHub Actions) and confirm hermetic pass

**Completion checklist:**
- [ ] Deterministic suite: 100% pass (all tests, 0 failures)
- [ ] Field test: 0 true failures, all 34 goals complete
- [ ] Docker integration: full pipeline passes inside container
- [ ] CI run: hermetic pass on GitHub Actions
- [ ] Test count: documented and matches CI output
- [ ] Coverage: >95% on all modules

---

### M32.3 — Field test report finalized — results document, scorecards, verdict deltas

**Problem:** The M31 field test produces raw results. These must be compiled into a finalized field test report document with scorecards, verdict delta analysis, and operational benchmark results.

**Scope:**
- Create `field-test/v0.1.0/FIELD_TEST_REPORT.md`
- Include Scorecard A (release gate) and Scorecard B (detailed results)
- Document all verdict deltas vs baseline
- Include operational benchmark results
- Include cost-per-iteration breakdown
- Include multi-environment test results

**Completion checklist:**
- [ ] Field test results document published at `field-test/v0.1.0/FIELD_TEST_REPORT.md`
- [ ] Scorecard A: PASS
- [ ] All verdict deltas attributable
- [ ] Operational benchmark metrics reported
- [ ] Multi-environment metrics reported

---

### M32.4 — Docs sweep — README, CHANGELOG, release notes, all docs

**Problem:** All documentation must be current for the v0.1.0 release. This includes the README, CHANGELOG, release notes, and all design docs.

**Scope:**
- README: update version, add summary of v0.1.0 features
- CHANGELOG: add v0.1.0 entry with all M1-M31 changes
- Release notes: create `docs/release/v0.1.0/release-notes.md`
- Design docs: confirm all PRD, design, and WBS docs are current
- Field test results document: finalized (see M32.3)
- Confirm no stale-doc contradictions

**Version bump locations:**

| Location | Change |
|----------|--------|
| `pyproject.toml` | `version = "0.0.1"` → `"0.1.0"` |
| `src/cauterule/__init__.py` | `__version__ = "0.0.1"` → `"0.1.0"` |
| `Dockerfile` | pinned version |
| `README.md` | PyPI badge + status line |
| `CHANGELOG.md` | new `## v0.1.0` entry |
| `docs/release/v0.1.0/release-notes.md` | new file |

**Completion checklist:**
- [ ] README points to v0.1.0
- [ ] CHANGELOG has complete v0.1.0 entry
- [ ] Release notes published and reviewed
- [ ] API reference matches current code
- [ ] All design docs are current
- [ ] Version bumped at all 6 locations
- [ ] No stale-doc contradictions (grep sweep for "0.0.1-only" claims)

---

### M32.5 — Packaging & PyPI release — build, dist, Dockerfile pin, upload

**Problem:** The v0.1.0 release must be packaged and published to PyPI. This includes building distribution artifacts, pinning the Dockerfile, and uploading to PyPI.

**Scope:**
- Build distribution artifacts: `python -m build`
- Verify dist artifacts are correct (check sdist and wheel)
- Update Dockerfile to pin v0.1.0
- Build and test Docker image locally
- Upload to PyPI: `twine upload dist/*`
- Verify PyPI package installs correctly: `pip install cauterule==0.1.0`

**Completion checklist:**
- [ ] Version bumped at all 6 locations
- [ ] Distribution artifacts build cleanly (sdist + wheel)
- [ ] Dockerfile pinned to v0.1.0
- [ ] Docker image builds and runs correctly
- [ ] Package uploaded to PyPI
- [ ] Fresh install from PyPI works: `pip install cauterule==0.1.0 && cauterule demo`

---

### M32.6 — Release tags and milestone closure — git tag, GitHub release, close all v0.1.0 milestones

**Problem:** The final step of the release process: create the git tag, publish the GitHub release, and close all v0.1.0 milestones (M1-M31).

**Prerequisites (all must be green before this issue starts):**
- [ ] M32.1 Security scan clean
- [ ] M32.2 All tests passing
- [ ] M32.3 Field test report finalized
- [ ] M32.4 Docs sweep complete
- [ ] M32.5 PyPI release published

**Completion checklist:**
- [ ] Git tag v0.1.0 created and pushed
- [ ] GitHub release published with release notes
- [ ] All v0.1.0 milestones closed (M1-M32)
- [ ] No open issues remain in v0.1.0 scope
- [ ] Deferred issues (v0.1.1+) remain open with documented rationale
- [ ] Announcement ready (dev.to article or crosslinks)

---

### M32 Closure Gate

Before M32 closes, the following must be true:

#### Standard milestone exit gate
- [ ] Run all tests: `pytest` — all pass
- [ ] Lint strict clean: `ruff check` + `mypy src/` — zero errors
- [ ] Test coverage total > 95%: `pytest --cov=src/cauterule --cov-report=term-missing`
- [ ] Update all docs affected by this milestone
- [ ] Verify all issues in this milestone are done
- [ ] Close all completed issues
- [ ] Commit with message: `milestone: M32 complete`
- [ ] Push to main

#### Pre-Release Aggregate Gate (M32-specific)

All of the following must be green before M32.6 tags:

- [ ] Code review: clean on the full release diff
- [ ] All testcases green: full suite, zero unexplained skips
- [ ] Lint clean: `ruff check` + `ruff format --check` 0 errors
- [ ] Type check: `mypy --strict src/ tests/` 0 errors
- [ ] Test coverage: >95% on all modules (including all new modules)
- [ ] Security scans: truffleHog clean, dependency audit clean
- [ ] Field test: 34/34 goals, Scorecard A PASS, intended-deltas-only regression
- [ ] Docker tests: green against the rebuilt 0.1.0 image
- [ ] Docs: complete and consistent, no stale-doc contradictions
- [ ] PyPI: v0.1.0 published with release-notes link

#### Post-Release Checklist

- [ ] GitHub release published with release notes link
- [ ] PyPI page shows v0.1.0
- [ ] All v0.1.0 milestones closed (M1-M32)
- [ ] v0.1.1+ deferred issues remain open with documented rationale
- [ ] `main` branch is up to date
- [ ] Announcement published (dev.to, social, or internal)