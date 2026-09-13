# CauterRule v0.3.1 Release Notes

**Release date:** September 13, 2026

CauterRule v0.3.1 is the **Accuracy & Trust** patch. It fixes the correctness
defects found by the v0.3.0 code review, makes the replay verdict trustworthy,
measures extraction quality directly for the first time, moves the adversarial
source-trust gate into production promotion, and re-validates the whole system
with a full 40-corpus × 2-model field-test sweep.

---

## Executive Summary

v0.3.0 proved the loop end-to-end. v0.3.1 makes the *verdict* trustworthy.

The v0.3.0 field test passed the safety gates but failed the quality gates:
golden 40–50% (target ≥70%) and failures/positive 8–10% (target ≥50%). The
v0.3.0 code review then found a matcher/scorer defect class — an unreachable
semantic floor, a failure-signature diluted by `failure_class`, spurious
`broken` successes, and scorer ordering that discarded net-positive rules — plus
43 further defects across the codebase.

v0.3.1 closes all of them. The headline: **the first release to clear every hard
quality and safety gate on both models** — golden **82–83%** (n=60),
failures/positive **50–52%**, adapters **60/60**, nearmiss **0 false accepts**,
adversarial **0 promotions**, generic triggers **0.4–0.7%**. Total pass volume
grew ~5× (116–119 → 601–626) while safety held flat.

Two structural gains underpin that:

- **Extraction quality is now measured directly** (`extraction_f1`,
  trigger-only `extraction_agreement`). Agreement is 0.74–0.92 while token-F1
  stays 0.42–0.65 — confirming v0.3.0's quality gap was the *matcher proxy*, not
  the model.
- **The adversarial source-trust gate is now in production**, not just the test
  harness. `auto_promote` hard-rejects candidates mined from
  prompt-injection-tainted trajectories, independent of linter/replay/safety/
  confidence, and `force` cannot override it (#727).

---

## What's Fixed

### M1 — Critical Code Fixes

- **Matcher/scorer correctness** (#721–#724): semantic floor lowered to 0.62
  against a class-free failure-signature view; `broken` domain-gated with a
  match-strength margin; scorer reordered so net-positive rules pass and the
  near-miss band is bounded.
- **Spurious `broken` successes** no longer block correct rules (#723).
- **Production source-trust gate** (#727): injection-tainted trajectory sources
  are flagged at capture and hard-blocked from auto-promotion — the v0.3.0
  "test-only" adversarial protection gap is closed.

### M2 — Evaluation, Code Review & Field Test

- **43 code-review fixes** (`#762`–`#804`, 11 Critical + 32 Important):
  signature-aware cache, threshold-aware near-miss handling, source-trust
  plumbing, MCP fail-closed auth, pack/export security hardening, token/cost
  plumbing, and input-validation gaps.
- **Extraction-accuracy metric** added to every field-test `summary.json`
  (#730); agreement redefined to the trigger-only semantic match (J6), with the
  directive reported as `directive_f1`.
- **Corpus/reference work**: reference pool 444 → **588** trajectories; golden
  expanded to **n=60** with `expected_rule` backfill (#735); adapter and CI
  sibling references added (#726); raw/ci corpus repaired 110 → 48 (J11).
- **Threshold recalibration** after the matcher/scorer changes (#736).
- **Safety-correctness fixes** (J1/J2/J10/J13): nearmiss/adversarial scored as
  rejection corpora; harness health uses the `attempted` denominator; extraction
  metrics emit `null` (not `0.0`) with no ground truth; correct safety-rate
  labels.

---

## Field Test Results

Full sweep: 2 cloud models (gpt-4o-mini, llama-3.1-8b) × 40 corpora = **4,742
trajectory-runs**, 588-trajectory domain-scoped reference pool. Full data:
[`FIELD_TEST_REPORT.md`](../../field-test/v0.3.1/FIELD_TEST_REPORT.md).

| Metric | v0.3.0 | v0.3.1 | Δ |
|--------|--------|--------|---|
| Golden pass rate (n) | 30–50% (10) | **82% / 83%** (60) | ✅ |
| Failures/positive pass rate | 8% / 10% | **50% / 52%** | ✅ |
| Adapters | 0/60 | **60/60** | ✅ |
| raw/ci | 0/110 | **21/47 / 26/47** | ✅ |
| reference-expansion | 19/303 | **201/303 / 198/303** | ✅ ~10× |
| Golden recall | 0.170 / 0.228 | **0.377 / 0.427** | ✅ ~2× |
| Near-miss false accepts | 0–1 | **0 / 0** | ✅ held |
| Adversarial promotions | 0 | **0 (all 9 corpora)** | ✅ held |
| Generic triggers | 0.7% | **0.4% / 0.7%** | ✅ held |
| Extraction agreement | not measured | **0.74–0.92** | ✅ new |
| Total pass (full sweep) | 116–119 | **601 / 626** | ✅ ~5× |
| Cost / 1k trajectories | — | **$0.20 (gpt) / $0.05 (llama)** | ✅ |

### Release gate verdict (full sweep)

| Objective | Status |
|---|---|
| Safety: 100% silence on successes/negatives | ✅ MET |
| Near-miss precision (0 accepts) | ✅ MET |
| Adversarial: 0 promoted rules (all 9 corpora) | ✅ MET |
| Generic triggers <10% (0.4% / 0.7%) | ✅ MET |
| Golden pass rate ≥70% (n≥60) | ✅ MET (82% / 83%) |
| Failures/positive pass rate ≥50% | ✅ MET (50% / 52%) |
| Curated inconclusive <15% | ⚠️ PARTIAL (golden 17–18%, within CIs) |
| Infrastructure | ✅ MET (Docker 180/180, preflight, cost corpus) |

---

## Known Issues

| Issue | Severity | Workaround / next |
|-------|----------|-------------------|
| 0-accepted corpora: `public/staleness`, `public/synthetic`, `lifecycle`, `mcp`, gpt `public/domains` | Major | Reference-coverage/matcher gaps carried from v0.3.0 (J18); root-cause via `diagnose_corpus.py`, add same-domain references |
| Cross-session repeat-failure reduction not measured (#741) | Medium | Tooling ready (`scripts/cross_session.py`); run the 5-session protocol |
| Human-vs-replay agreement not measured (#742) | Medium | Tooling ready (`scripts/human_agreement.py`); sample + score reviews |
| llama `no_candidates` on adversarial corpora (J16) | Medium | Extraction variance on the 8B; consider a retry/parse pass |
| Harness-health false-FAIL on gate-dropped / no-candidate corpora (J17) | Medium | Make the check `n/a` when `attempted == 0` |
| Golden inconclusive 17–18% (target <15%) | Low | Replay/matcher residual, within CIs |

No security blockers at release.

---

## Upgrade Guide

### From v0.3.0

1. **Update the package:**

   ```bash
   pip install --upgrade cauterule
   ```

2. **Verify the version:**

   ```bash
   cauterule --version
   # cauterule, version 0.3.1
   ```

3. **Behavior changes to review:**

   - **Replay/scorer** — thresholds and verdict ordering changed (semantic floor
     0.62, `broken` domain-gated + margin, scorer reordered). Rules that were
     inconclusive under v0.3.0 may now pass; broad/near-miss rules remain
     bounded. Re-run `cauterule test` if you rely on prior verdicts.
   - **Auto-promotion** — candidates mined from a prompt-injection-tainted
     source are now hard-rejected even with clean linter / `pass` evidence /
     high confidence. `force` does not override this; route to human review.
   - **Field-test metrics** — `summary.json` now carries `extraction_f1` /
     `extraction_agreement` / `directive_f1`; extraction metrics are `null`
     (not `0.0`) when no ground truth exists.

4. **Docker users:**

   ```bash
   docker pull ghcr.io/deghosal-2026/cauterule:v0.3.1
   docker compose up cauterule-demo
   ```

5. **Homebrew users:**

   ```bash
   brew update && brew upgrade cauterule
   ```

6. **Migration steps:** none required. Existing `cauterule.toml`, rule stores,
   and exports are compatible.

---

## Security

Scan date: **2026-09-13**. Tooling: truffleHog 3.97.4, pip-audit 2.10.1,
OpenSSF Scorecard v5.1.1. CI: `.github/workflows/security-scan.yml`.

- **truffleHog** — 0 verified and 0 unverified secrets.
- **pip-audit** — `--strict .` on production dependencies: 0 known
  vulnerabilities. Dev venv advisories confined to `pypdf`/`torch` (not shipped).
- **Custom secret regex** — `scripts/security/secret_scan.py`: 0 unmarked matches.
- **OpenSSF Scorecard** — **5.1/10** (up from 3.8). Structural gaps tracked;
  dependabot now detected.
- **Threat model** — SECURITY.md updated for v0.3.1: the adversarial
  source-trust gate (#727) is documented and enforced in production promotion.

---

## Contributors

- Debashish Ghosal ([@deghosal-2026](https://github.com/deghosal-2026)) — design, implementation, field test, release.

---

## Release Assets

- **PyPI:** https://pypi.org/project/cauterule/0.3.1/
- **GitHub Release:** https://github.com/deghosal-2026/CauterRule/releases/tag/v0.3.1
- **Docker:** `ghcr.io/deghosal-2026/cauterule:v0.3.1`
- **Homebrew:** `brew install deghosal-2026/cauterule/cauterule`
- **Standalone binary:** see GitHub Release assets
- **Field test report:** [`docs/field-test/v0.3.1/FIELD_TEST_REPORT.md`](../../field-test/v0.3.1/FIELD_TEST_REPORT.md)
- **Changelog:** [`CHANGELOG.md`](../../../CHANGELOG.md)