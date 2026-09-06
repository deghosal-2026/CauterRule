# v0.1.0 — WBS Part 13: Release Readiness

**Milestones:** M31

## M31: Release Readiness

> **Goal:** Final release readiness gate for v0.1.0. All issues are strictly sequential — each depends on the previous one completing successfully. No issue in M31 can close until the aggregate pre-release gate passes.
> 
> **Note:** M31 also includes all Distribution tasks (formerly M28): PyPI config, Homebrew formula, Docker image, standalone binary, GitHub badge, GitHub Action, webhook, OpenTelemetry exporter, benchmark leaderboard, and pack certification. These are listed as M31.2.x sub-tasks.

**Execution order:** M31.1 → M31.2 → M31.3 → M31.4 → M31.5 → M31.6 → M31.7

| Issue | Title | Area | Status |
|-------|-------|------|--------|
| M31.1 | Security scan — truffleHog, dependency audit, secret detection | security | ✅ |
| M31.2 | All tests passing — full deterministic suite + field test confirmed green | testing | ✅ |
| M31.2.1 | PyPI publish config | release | ✅ |
| M31.3 | Field test report finalized — results document, scorecards, verdict deltas | docs/field-test | ✅ |
| M31.4 | Docs sweep — README, CHANGELOG, release notes, all docs | docs | ✅ |
| M31.5 | Packaging & PyPI release — build, dist, Dockerfile pin, upload | release | ⬜ |
| M31.6 | Release tags and milestone closure — git tag, GitHub release, close all v0.1.0 milestones | release | ⬜ |

---

### M31.1 — Security scan — truffleHog, dependency audit, secret detection

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

### M31.2 — All tests passing — full deterministic suite + field test confirmed green

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

### M31.2.1 — PyPI publish config

**Status:** ✅ Complete

**Problem:** `pip install cauterule` must work before packaging.

**Scope:**
- Verify `pyproject.toml` has all required metadata (license, classifiers, long_description_content_type)
- Create `scripts/build.sh` for `python -m build` + `twine upload dist/*`
- Add `build` and `twine` to dev dependencies

**Completion checklist:**
- [x] `pyproject.toml` has all required fields
- [x] `scripts/build.sh` exists and is executable
- [x] Build + twine deps in pyproject.toml

---

### M31.2.2 — Homebrew formula

**Status:** ➡️ Deferred to v0.2.0

**Status:** ➡️ Deferred to v0.2.0

**Problem:** `brew install cauterule` must work on macOS.

**Scope:**
- Create `dist/homebrew/cauterule.rb` with standard Python formula template

**Completion checklist:**
- [ ] `dist/homebrew/cauterule.rb` created

---

### M31.2.3 — Docker image

**Status:** ➡️ Deferred to v0.2.0

**Problem:** `docker run cauterule demo` must work.

**Scope:**
- Create `Dockerfile` (multi-stage: build + runtime)
- Create `docker-compose.yaml` with demo service

**Completion checklist:**
- [ ] `Dockerfile` created and builds
- [ ] `docker-compose.yaml` created

---

### M31.2.4 — Standalone binary

**Status:** ➡️ Deferred to v0.2.0

**Problem:** Users should be able to run cauterule without Python installed.

**Scope:**
- Create `scripts/build_binary.sh` using PyInstaller
- Add `pyinstaller` to optional deps

**Completion checklist:**
- [ ] `scripts/build_binary.sh` exists
- [ ] pyinstaller in optional deps

---

### M31.2.5 — GitHub badge endpoint

**Status:** ➡️ Deferred to v0.2.0

**Problem:** A shields.io-style badge showing "N rules learned" for README.

**Scope:**
- Create `src/cauterule/badge.py` serving an SVG badge template

**Completion checklist:**
- [ ] `src/cauterule/badge.py` created with SVG template

---

### M31.2.6 — GitHub Action

**Status:** ➡️ Deferred to v0.2.0

**Problem:** CI integration — run extraction on CI failures.

**Scope:**
- Create `.github/action.yml` composite action calling `cauterule extract`

**Completion checklist:**
- [ ] `.github/action.yml` created

---

### M31.2.7 — Webhook on promotion

**Status:** ➡️ Deferred to v0.2.0

**Problem:** Notify Slack/Discord/GitHub when a rule is promoted.

**Scope:**
- Create `src/cauterule/integrations/__init__.py` and `src/cauterule/integrations/webhook.py`
- `WebhookNotifier` class sends POST to configured URL on promotion

**Completion checklist:**
- [ ] `src/cauterule/integrations/webhook.py` created
- [ ] Tests pass

---

### M31.2.8 — OpenTelemetry exporter

**Status:** ➡️ Deferred to v0.2.0

**Problem:** Emit rule hit/promotion/extraction events as OTel spans.

**Scope:**
- Create `src/cauterule/integrations/otel.py` — `OtelExporter` class

**Completion checklist:**
- [ ] `src/cauterule/integrations/otel.py` created

---

### M31.2.9 — Official benchmark leaderboard

**Status:** ➡️ Deferred to v0.2.0

**Problem:** Publish model + prompt results on public corpus.

**Scope:**
- Create `src/cauterule/benchmark/leaderboard.py` — `Leaderboard` class
- Test in `tests/benchmark/test_leaderboard.py`

**Completion checklist:**
- [ ] `src/cauterule/benchmark/leaderboard.py` created
- [ ] Tests pass

---

### M31.2.10 — Pack certification baseline

**Problem:** Minimum safety, replay, and provenance checks for official rule packs.

**Scope:**
- Create `src/cauterule/packs/certification.py` — `certify_pack()` function
- Test in `tests/packs/test_certification.py`

**Completion checklist:**
- [ ] `src/cauterule/packs/certification.py` created
- [ ] Tests pass

---

### M31.3 — Field test report finalized — results document, scorecards, verdict deltas

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

### M31.4 — Docs sweep — README, CHANGELOG, release notes, all docs

**Problem:** All documentation must be current for the v0.1.0 release. This includes the README, CHANGELOG, release notes, and all design docs.

**Scope:**
- README: update version, add summary of v0.1.0 features
- CHANGELOG: add v0.1.0 entry with all M1-M31 changes
- Release notes: create `docs/release/v0.1.0/release-notes.md`
- Design docs: confirm all PRD, design, and WBS docs are current
- Field test results document: finalized (see M31.3)
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

### M31.5 — Packaging & PyPI release — build, dist, Dockerfile pin, upload

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

### M31.6 — Release tags and milestone closure — git tag, GitHub release, close all v0.1.0 milestones

**Problem:** The final step of the release process: create the git tag, publish the GitHub release, and close all v0.1.0 milestones (M1-M31).

**Prerequisites (all must be green before this issue starts):**
- [ ] M31.1 Security scan clean
- [ ] M31.2 All tests passing
- [ ] M31.3 Field test report finalized
- [ ] M31.4 Docs sweep complete
- [ ] M31.5 PyPI release published

**Completion checklist:**
- [ ] Git tag v0.1.0 created and pushed
- [ ] GitHub release published with release notes
- [ ] All v0.1.0 milestones closed (M1-M31)
- [ ] No open issues remain in v0.1.0 scope
- [ ] Deferred issues (v0.1.1+) remain open with documented rationale
- [ ] Announcement ready (dev.to article or crosslinks)

---

### M31 Closure Gate

Before M31 closes, the following must be true:

#### Standard milestone exit gate
- [ ] Run all tests: `pytest` — all pass
- [ ] Lint strict clean: `ruff check` + `mypy src/` — zero errors
- [ ] Test coverage total > 95%: `pytest --cov=src/cauterule --cov-report=term-missing`
- [ ] Update all docs affected by this milestone
- [ ] Verify all issues in this milestone are done
- [ ] Close all completed issues
- [ ] Commit with message: `milestone: M31 complete`
- [ ] Push to main

#### Pre-Release Aggregate Gate (M31-specific)

All of the following must be green before M31.6 tags:

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
- [ ] All v0.1.0 milestones closed (M1-M31)
- [ ] v0.1.1+ deferred issues remain open with documented rationale
- [ ] `main` branch is up to date
- [ ] Announcement published (dev.to, social, or internal)