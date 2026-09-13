# CauterRule v0.3.1 — Post-Release Verification

**Date:** 2026-09-13
**Release:** v0.3.1 — Accuracy & Trust
**Tag:** `v0.3.1` (`6363e19`)

Verification that every distribution channel resolves after the release.

## Channels

| Channel | Check | Result |
|---|---|---|
| PyPI | `https://pypi.org/pypi/cauterule/0.3.1/json` | ✅ HTTP 200 |
| PyPI (latest) | `https://pypi.org/pypi/cauterule/json` | ✅ HTTP 200 |
| Fresh install | `python -m venv` + `pip install cauterule==0.3.1` → `cauterule --version` | ✅ `0.3.1` |
| GitHub Release | `gh release view v0.3.1` | ✅ published, not draft; assets: `cauterule-0.3.1.tar.gz`, `cauterule-0.3.1-py3-none-any.whl` |
| Git tag | `git tag` | ✅ `v0.3.1` |
| README | version/status/badges reference v0.3.1 | ✅ |
| Release notes | `docs/release/v0.3.1/release-notes.md` on tag | ✅ HTTP 200 |
| Docs index | `docs/README.md` current release v0.3.1 | ✅ |
| Field-test report | `docs/field-test/v0.3.1/FIELD_TEST_REPORT.md` | ✅ committed |
| Changelog | `CHANGELOG.md` dated `[0.3.1] - 2026-09-13` | ✅ |
| Security | truffleHog 0/0, pip-audit 0 prod vulns, secret regex clean, Scorecard 5.1/10 | ✅ |
| Docker (GHCR) | `ghcr.io/deghosal-2026/cauterule:v0.3.1` | ⏭️ deferred by request (not published) |
| Homebrew | `deghosal-2026/cauterule` formula | ⏭️ deferred by request (not published) |

## Milestones

| Milestone | State |
|---|---|
| v0.3.1-M1 (66) | ✅ 0 open issues |
| v0.3.1-M2 (67) | ✅ 0 open issues |
| v0.3.1-M3 (68) | closes with #759-#761 |

## Notes

Docker and Homebrew were explicitly deferred for this patch per maintainer
request; the README/docs list them as release channels, and this document
records that they were not published for v0.3.1. All other channels verified by
a fresh install / release lookup.