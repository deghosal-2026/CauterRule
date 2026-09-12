# CauterRule v0.3.0 Release Notes

**Release date:** _pending tag_

CauterRule v0.3.0 is the **Hardening & Ecosystem** release. It fixes critical
data-integrity bugs found by the v0.2.0 field test, ships first-class adapters,
adds rule lifecycle management, a pack ecosystem, corpus/benchmark
infrastructure, and proves it with a full field test.

> This document is finalized by #633 (release notes) and #630 (CHANGELOG).
> The Security section below is produced by #620.

---

## What's New

See [`CHANGELOG.md`](../../../CHANGELOG.md) for the full v0.3.0 entry (#630) and
[`README.md`](../../../README.md) for the feature tour. Highlights:

- **Adapters** — LangGraph, CrewAI, PydanticAI, generic `@watch`/`inject` GA
- **Rule lifecycle** — specificity scoring, outcome tracking, supersession, retirement, quarantine
- **Pack ecosystem** — install/create/publish/semver/deps/scaffold/share + certification
- **Reliability** — atomic store writes, path-traversal guards, duplicate/conflict detection
- **Infra** — Docker compose, remote MCP hardening, OTEL, corpus/bakeoff/benchmark CLIs
- **Field test** — latency, cost, human agreement, safety-adjusted ranking

## Security

Scan date: **2026-09-12**. Tooling: truffleHog 3.97.4, pip-audit 2.10.1,
OpenSSF Scorecard 5.5.0. CI: `.github/workflows/security-scan.yml`.

### truffleHog

- **0 verified secrets** across the repository filesystem.
- 7 unverified matches, all in test modules marked `SECURITY-FIXTURE` — intentional
  fake credentials used to verify redaction and leakage prevention. No fixture
  contains a real credential.
- Exclusions: virtualenvs, caches, build artifacts, and compiled bytecode via
  `.trufflehog-exclude-paths.txt`.

### Dependency audit (pip-audit)

- `pip-audit --strict .` on production dependencies (`click`, `pyyaml`,
  `textual`, `mcp`, `requests`, `litellm`, `opentelemetry-*`): **0 known
  vulnerabilities**.
- Awareness scan of the full dev virtualenv: 4 advisories confined to `pip`
  itself (the build tool). Non-blocking; resolved by upgrading pip.

### Custom secret regex scan

- `scripts/security/secret_scan.py` applies AWS/GitHub/Slack/Stripe/SSH/JWT/
  Google/generic patterns across source and fixtures.
- Fixture-marker aware: files declaring `SECURITY-FIXTURE` are exempt.
- Result: **0 unmarked matches**.

### OpenSSF Scorecard

- Aggregate: **3.8/10** (target ≥7/10). The gap is structural for a young,
  single-maintainer repository and is tracked with remediation rather than
  ignored.
- Passing checks: Binary-Artifacts (10), Dangerous-Workflow (10), License (10),
  Security-Policy (10), Vulnerabilities (10).
- Remediation: top-level token permissions added; dependabot (#615), SAST/CI
  hardening/fuzzing/action-pinning (#614), and branch-protection/review policy
  as the project matures. Details in [`SECURITY.md`](../../../SECURITY.md).

### Threat-model changes

SECURITY.md now documents v0.3.0 surfaces: remote MCP bearer auth, per-client
rate limiting, payload validation, adapter redaction-on-disk guarantees, pack
checksums/certification, and rule-lifecycle safety.

## Known Issues

See the issue tracker for open items. No security blockers at release.

## Upgrade Guide

See [`CHANGELOG.md`](../../../CHANGELOG.md) (#630). No breaking API changes;
version bumped from 0.2.0 to 0.3.0.
