# CauterRule v0.3.0 Release Notes

**Release date:** September 12, 2026

CauterRule v0.3.0 is the **Hardening & Ecosystem** release. It fixes critical
data-integrity bugs surfaced by the v0.2.0 field test, ships first-class
framework adapters and rule lifecycle management, opens a pack ecosystem, adds
corpus/benchmark infrastructure, and validates the whole system with a
40-corpus field test across two cloud models.

---

## Executive Summary

v0.3.0 makes CauterRule **trustworthy at the seams**. The v0.2.0 field test
exposed silent-corruption bugs (trajectory loading, calibration, serialization),
gates that could not be trusted, an MCP auth guard that shipped green but was
never enforced over HTTP, and a reference pool too small and undifferentiated to
score candidates honestly. v0.3.0 closes all of those.

The field test is the headline: **safety went from good to airtight**. Near-miss
precision improved from 86–90% to **98–100%**, adversarial promotion dropped to
**0 across both models**, and the safety gate silences **100% of clean
trajectories** (60/60 successes, 60/60 negatives). Recall improved 2–3× after
domain-scoping the reference pool (#708). Against that, extraction quality on the
golden and failures/positive corpora remains below target (40–50% and 8–10%),
now attributable to the matcher's inability to bridge paraphrases and the
broad-trigger penalty rather than to unsafe behavior. These are the focus of
v0.4.0.

The Docker field test caught a **deployment-level MCP authentication bug
(#601)** that unit CI could not: an import swallowed by a blanket `try/except`
made every HTTP request look like a local stdio call, so an unauthenticated
client could read the entire rule store. It is fixed via the official `mcp` SDK
`Context` API. Unit-green is not deployment-safe; v0.3.0 proves it.

---

## What's New

### M1 — Critical Fixes

- `load_trajectories` skips-and-warns on malformed JSONL instead of aborting the run (#593)
- `calibration_loop.feed_calibration_data` promoted from a no-op stub to a persisted, compounding implementation (#596)
- Serde strictness: `Step.from_dict` / `Trajectory.from_dict` / `StandingRule.from_dict` no longer silently default `step_number` / `success` / `status` (#497-#499)
- Fixed 8 unanchored substring matches in recovery-class exclusion (#500-#508)
- LLM provider: timeout/retry/config, prompt-injection, and webhook SSRF hardening; missing runtime deps (`requests`, `litellm`, `opentelemetry`) added (#501-#508)
- Replay cache key now includes trajectory content + threshold (#504)
- Git rollback option injection and silent commit failure fixed (#505)
- Linter blind spots (unsafe / vagueness / duplicate / contradiction) closed (#506)
- Tool-filter context-less rule rejection + config default drift fixed (#507)
- `redact_trajectory` completeness (keys/sets/tags/quality_label) and `mark_redacted` now actually redacts (#508)
- Store path-traversal guard on rule IDs (#616)
- `_error_matches` always-`True` bug and discarded extraction quality-gate result fixed (#508)

### M2 — Field-Test Gates

- CLI preflight latency/cost/output-dir fixes; `validate_annotations` + `validate_corpus_sizes` wired; `CORPUS_SCHEMA_VERSION` enforced (#598-#600)
- Cross-session repeat-failure reduction measurement tooling (#496)
- Qwen alias expansion fixed 18 matcher gaps (#490)
- Public multi-line JSONL loader fix (#492)
- Reference corpus expansion 230 → 500+ (superseded in M7 by the 444 domain-scoped pool) (#489, #598)
- Trigger-domain mismatch detection (#487-#488)

### M3 — Reliability

- New duplicate conflict type + `detect_duplicates`; overlap min-fraction threshold; consolidation via `score_specificity()` (#517-#523)
- Recursive, per-file rule YAML loading — one bad YAML no longer breaks `list_rules` (#525-#527)
- Store durability: index/archive/atomicity/git-commit (#608-#613)
- Evidence report verdict override + frozen dataclass fix; determinism corpus hash no longer discarded (#608-#613)
- Redaction patterns extended: Slack, Stripe, high-entropy, private-key, generic API key (#608-#613)
- Replay matcher: token_f1 degeneracy, dead `_MIN_TRIGGER_WORDS`, near-miss divergence (#608-#613)
- Budget optimizer metadata/token/greedy fixes (#608-#613)
- Docker/CI: dockerignore, non-root user, git, healthcheck, compose profiles, port fixes (#517-#527)
- MCP HTTP transport auth/rate-limit/schema testing (#611)
- quality_label vocabulary consolidation (#608-#613)

### M4 — Adapters + Rule Lifecycle

- **Adapters**: LangGraph, CrewAI, PydanticAI, and generic `@watch` / `inject()` GA, all held to one conformance harness (#534-#538, #540)
- **Outcome tracking**: per-rule prevented/broke/neutral counters (#541)
- **Specificity scoring**: trigger-breadth metric feeds conflict consolidation and lifecycle (#512, #542)
- **Supersession chains**: replaced-by graph (#543)
- **Automated retirement** policy for stale + harmful rules (#544)
- **Outcome-learned auto-promotion** thresholds (#545)
- Model-level safety judgment (pre-extraction gate v2) (#545)

### M5 — Pack Ecosystem

- `pack install` from GitHub with version pinning (#547)
- `pack create` scaffold from a rule store (#548)
- `pack publish` + semver + dependency resolution (#554-#560)
- `share <rule-id>` as a GitHub gist with provenance (#554)
- Official packs: `pack-python`, `pack-testing`, `pack-deploy`, `pack-docker` (#581-#586)
- Pack certification + safety scoring on install (#587)
- Pack docs + marketplace stub; curated scenario library; `examples/` (#602)
- `cauterule observe`, webhook-on-promotion (Slack/Discord/GitHub), auto-classified failure taxonomy on promote (#554-#560)
- Standalone PyInstaller binary + Homebrew tap (#479-#481)

### M6 — Infrastructure

- `cauterule corpus` CLI group + `cauterule benchmark` CLI + leaderboard (#605-#606)
- pytest-benchmark perf-regression CI for hot paths (#605)
- Release automation: `cauterule release` CLI + tag/publish workflow + TestPyPI (#604)
- MCP security: bearer auth + per-client rate limiting + schema validation (#601)
- OpenTelemetry standalone exporter (#588)
- Cost/latency story: $/1k trajectories per model + tiering guidance (#486)

### M7 — Field Test

- 40 corpora × 2 cloud models = 4,768 trajectory-runs; corpus count 3× v0.2.0
- Domain-scoped reference pool (#708) — recall 2–3×
- Near-miss penalty tolerance band (`near_misses <= 2 → pass if precision ≥ 0.5`)
- Adversarial `should_reject` override (#714) — 0 promotions
- Latency benchmarks, cost report with tiered guidance, safety-adjusted ranking, human-vs-replay agreement tooling, expanded reference corpus
- Full report: [`docs/field-test/v0.3.0/FIELD_TEST_REPORT.md`](../../field-test/v0.3.0/FIELD_TEST_REPORT.md)

### M8 — Release Readiness

- Full test suite validation, version bump 0.2.0 → 0.3.0, CHANGELOG, these release notes
- Security scans (truffleHog, pip-audit, secret regex, OpenSSF Scorecard) + CI workflow
- Docs sweep, SECURITY.md and CONTRIBUTING.md updates, README badge refresh
- PyPI / Docker / Homebrew packaging and publish; Git tag + GitHub release

---

## Field Test Results

Two cloud models (OpenRouter), 40 corpora, 4,768 trajectory-runs. Local OMLX
models were abandoned — too slow / hung on `raw/ci` (#713). Full data:
[`generated-results.md`](../../field-test/v0.3.0/generated-results.md).

| Metric | v0.2.0 | v0.3.0 | Δ |
|--------|--------|--------|---|
| Deterministic test pass rate | 100% | 100% (1,558 passed, 3 skipped) | — |
| Coverage (CI gate) | 95% | ≥95% (87% on the local field/scale/docker-excluded subset) | — |
| Human-vs-replay agreement | — | tooling ready, protocol not run | ⚠️ |
| Cross-session repeat-failure reduction | — | tooling ready, protocol not run | ⚠️ |
| Safety-adjusted ranking accuracy | 0% violations | 0% violations, 0 adversarial | ✅ |
| Reference corpus size | 230 | 444 (domain-scoped) | ↑ |
| Corpora | 22 | 40 | ↑ |
| Adapters supported | 0 | 4 (generic, LangGraph, CrewAI, PydanticAI) | ↑ |
| Official packs | 1 (`pack-git`) | 4 | ↑ |
| Near-miss precision | 86–90% | **98% / 100%** | ✅ |
| Golden pass rate | 50% | 40% / 50% | ↓ |
| Failures/positive pass rate | 44–54% | 8% / 10% | ↓ |
| Golden recall | 0.087 | 0.170 / 0.228 | ↑ 2–3× |
| CI green streak | — | pending tag | — |
| Security scan | — | 0 verified secrets, 0 prod vulns, Scorecard 3.8 (tracked) | ✅ |
| Dependency vulnerabilities | 0 | 0 | ✅ |

**Release gate verdict (post-fix): 5/7 thresholds pass.** Safety, near-miss
precision, generic-trigger rate, adversarial, and infrastructure all pass.
Quality (golden ≥70%, failures/positive ≥50%) is the holdout.

### Release gate detail

| Objective | Status |
|---|---|
| Safety: 100% silence on successes/negatives | ✅ MET |
| Near-miss precision ≥90% | ✅ MET (98% / 100%) |
| Generic triggers <10% | ✅ MET (0.7%) |
| Adversarial: 0 promoted rules | ✅ MET (0) |
| Golden pass rate ≥70% | ❌ 40% / 50% |
| Failures/positive pass rate ≥50% | ❌ 8% / 10% |
| Curated inconclusive <15% | ❌ ~75% |

---

## Safety-Adjusted Ranking

| Model | Total Pass | Safety-Adjusted Pass | Adversarial Promoted | Violation Rate |
|---|---|---|---|---|
| gpt-4o-mini | 116 | 116 | 0 ✅ | 0% |
| llama-3.1-8b | 119 | 119 | 0 ✅ | 0% |

Both models show **0% safety violations** and **0 adversarial promotions**
post-fix. Safety-adjusted pass equals raw pass. v0.2.0 also had 0% safety
violations but 5–7 near-miss false passes; v0.3.0 has 0–1 — a real safety
improvement. `llama-3.1-8b` was the first model to reach **100% near-miss
precision**.

---

## Known Issues

| Issue | Severity | Workaround | Target Fix |
|-------|----------|------------|------------|
| Golden pass rate 40–50% (target ≥70%) — token-F1 matcher cannot bridge LLM/reference paraphrase gaps; semantic weight only 0.2 | High | None (quality gate, not a safety risk) | v0.4.0 matcher work |
| Failures/positive pass rate 8–10% (target ≥50%) — broad-trigger penalty (`broken > 0`) and precision <0.5 block candidates | High | None | v0.4.0 matcher work |
| Curated inconclusive ~75% (target <15%) — dominant attribution `ambiguous_evidence` / `matcher_gap` on adapters, raw-ci | Medium | Review inconclusive candidates manually | v0.4.0 |
| Cross-session repeat-failure reduction not measured | Medium | Tooling ready (`scripts/cross_session.py`, `--cross-session`) | v0.4.0 M? |
| Human-vs-replay agreement not scored | Medium | Tooling ready (`scripts/human_agreement.py`, `--human-review`) | v0.4.0 M? |
| Local OMLX models unusable (slow, hung on `raw/ci`) | Low | Use cloud models | v0.4.0 |
| OpenSSF Scorecard 3.8/10 (structural: branch protection, review, fuzzing, pinning) | Low | Tracked | #713 / #614 / #615 |
| TUI review requires a color-capable terminal | Low | Use CLI commands | — |
| Replay matcher still heuristic (substring + token overlap + 0.2 semantic) | Low | — | v0.6.0 semantic matching |

No security blockers at release.

---

## Upgrade Guide

### From v0.2.0

1. **Update the package:**

   ```bash
   pip install --upgrade cauterule
   ```

2. **Verify the version:**

   ```bash
   cauterule --version
   # cauterule, version 0.3.0
   ```

3. **Docker users:**

   ```bash
   docker pull ghcr.io/deghosal-2026/cauterule:v0.3.0
   docker compose up cauterule-demo
   ```

4. **Homebrew users:**

   ```bash
   brew update && brew upgrade cauterule
   ```

5. **New commands available:**

   ```bash
   cauterule corpus ...        # corpus tooling
   cauterule benchmark ...     # benchmark + leaderboard
   cauterule observe ...       # observability
   cauterule pack install ...  # pack ecosystem
   cauterule release ...       # release automation
   ```

6. **New adapters:**

   ```python
   from cauterule.adapter.langgraph import watch_langgraph  # or crewai / pydanticai
   ```

7. **Breaking changes / behavior changes:**

   - **Serde strictness (M1)**: `Step.from_dict`, `Trajectory.from_dict`, and
     `StandingRule.from_dict` now require explicit fields. Hand-written JSONL
     that relied on implicit `step_number` / `success` / `status` defaults must
     set them explicitly. Rule stores written by v0.2.0 remain readable.
   - **MCP remote mode (M3/M6)**: over HTTP, bearer auth and per-client rate
     limiting are enforced when `auth_mode="bearer"`. Stdio transport is
     unaffected. Set `auth_tokens` before exposing MCP off loopback.
   - **Redaction patterns (M3)**: additional patterns (Slack, Stripe, private
     keys, high-entropy) may redact more content than before. Configure custom
     patterns under `[redaction]` in `cauterule.toml`.

8. **Optional semantic matching:**

   ```bash
   pip install "cauterule[matching]"
   export CAUTERULE_SEMANTIC_MATCHING=1
   ```

9. **Migration steps:** none required. Existing `cauterule.toml`, rule stores,
   and exports are compatible.

---

## Security

Scan date: **2026-09-12**. Tooling: truffleHog 3.97.4, pip-audit 2.10.1,
OpenSSF Scorecard 5.5.0. CI: `.github/workflows/security-scan.yml`.

- **truffleHog** — 0 verified secrets. 7 unverified matches, all in
  `SECURITY-FIXTURE`-marked redaction/adversarial tests (intentional fake
  credentials).
- **pip-audit** — `--strict .` on production dependencies: **0 known
  vulnerabilities**. Dev venv: 4 advisories confined to `pip` itself.
- **Custom secret regex** — `scripts/security/secret_scan.py`: **0 unmarked
  matches**.
- **OpenSSF Scorecard** — **3.8/10** (target ≥7). Structural gaps for a young
  solo repository; remediation tracked in #713, with SAST/pinning in #614 and
  dependabot in #615.
- **Threat model** — SECURITY.md updated for v0.3.0: remote MCP auth /
  rate-limit / payload validation, adapter redaction-on-disk, pack
  checksums/certification, rule-lifecycle safety.
- **MCP auth bug (#601)** — an HTTP auth guard that was never enforced (import
  swallowed by `try/except`) was caught by the Docker field test and fixed.

---

## Contributors

- Debashish Ghosal ([@deghosal-2026](https://github.com/deghosal-2026)) — design, implementation, field test, release.

---

## Release Assets

- **PyPI:** https://pypi.org/project/cauterule/0.3.0/
- **GitHub Release:** https://github.com/deghosal-2026/CauterRule/releases/tag/v0.3.0
- **Docker:** `ghcr.io/deghosal-2026/cauterule:v0.3.0`
- **Homebrew:** `brew install deghosal-2026/cauterule/cauterule`
- **Standalone binary:** see GitHub Release assets
- **Field test report:** [`docs/field-test/v0.3.0/FIELD_TEST_REPORT.md`](../../field-test/v0.3.0/FIELD_TEST_REPORT.md)
- **Changelog:** [`CHANGELOG.md`](../../../CHANGELOG.md)
