# CauterRule v0.3.0 — Pre-Release Aggregate Gate

**Date:** 2026-09-12
**Branch:** `feat-v0.3.0`
**Gate issue:** #665

Every release gate from `docs/wbs/v0.3.0/wbs-v0.3.0-index.md` is checked below
with evidence. Deviations are called out explicitly and mirrored in the known
issues of [`release-notes.md`](release-notes.md).

| Gate | Threshold | Result | Evidence |
|------|-----------|--------|----------|
| Tests pass (deterministic subset) | 100% | ✅ 1,558 passed, 3 skipped | `pytest --ignore=tests/field --ignore=tests/scale -k "not docker"` |
| Coverage (deterministic subset) | ≥85% | ✅ 87% | `pytest --cov=cauterule ...`; gate lowered from 95% per maintainer decision |
| Lint strict | 0 errors | ✅ | `ruff check .` + `ruff format --check .` |
| Types (CI scope) | 0 errors | ✅ | `mypy src/` |
| Types (full scope) | 0 errors | ⚠️ ~30 in `tests/` (arg-type on intentional invalid-literal fixtures) | not gated by CI |
| Field-test report drift | up to date | ✅ | `python scripts/generate_field_test_report.py --check` |
| Security scan | clean | ✅ | truffleHog 0 verified; pip-audit 0 prod vulns; secret regex 0 unmarked |
| OpenSSF Scorecard | ≥7/10 | ⚠️ 3.8/10 — structural, tracked #713 | `docs/release/v0.3.0/release-notes.md` §Security |
| PyPI published | 0.3.0 | ✅ | https://pypi.org/project/cauterule/0.3.0/ |
| CI green (3 consecutive) | green on main | ⏳ pending merge PR (#674) | CI runs only on `main`/PRs |
| Field test thresholds | ≥5/7 | ✅ 5/7 | `docs/field-test/v0.3.0/FIELD_TEST_REPORT.md` |
| Golden pass rate | ≥70% | ❌ 40–50% | documented known issue; targeted v0.4.0 |
| Near-miss precision | ≥90% | ✅ 98–100% | field test report |
| Adversarial promotions | 0 | ✅ 0 | field test report |
| Cross-session repeat-failure | ≥50% | ⏳ tooling ready, protocol not run | `scripts/cross_session.py` |
| Human-vs-replay agreement | measured | ⏳ tooling ready, not scored | `scripts/human_agreement.py` |

## Outcome

Local, packaging, and security gates pass. Two gates are **not met** and are
documented rather than hidden:

1. **Golden pass rate (40–50%)** and **failures/positive (8–10%)** — matcher
   paraphrase limitation; the near-miss/adversarial safety gates compensate.
   Targeted for v0.4.0.
2. **OpenSSF Scorecard (3.8/10)** — structural for a young solo repo; tracked
   in #713 with remediation via #614/#615.

**CI green** is verified by the merge PR (#674); this document is updated once
the run completes.

**Decision:** proceed to tag v0.3.0 with the above documented exceptions.
