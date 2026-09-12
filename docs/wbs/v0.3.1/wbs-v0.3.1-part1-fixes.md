# v0.3.1 — WBS Part 1: Phase 1 — Critical Code Fixes

**Milestone:** M1 ([v0.3.1-M1: Critical Code Fixes](https://github.com/deghosal-2026/CauterRule/milestone/66))

**Theme:** Fix the correctness defects in the replay matcher, simulator, scorer, candidate selection, extraction, and promotion trust that block promotion quality. Found by the v0.3.0 code review.

---

## M1: Critical Code Fixes (10 issues)

**Goal:** Make the replay verdict trustworthy. Today the "evidence" that gates promotion is a text-similarity proxy (0.2-weight semantic term with an unreachable 0.80 floor), successes are counted as `broken` without a domain gate or match margin, the scorer lets `broken>0` short-circuit the precision ladder, extraction quality is unmeasured, candidate selection favors low-recall rules, 2-pass candidates are never deduped, and the adversarial defense exists only in the field-test runner.

**Execution order:** #720 (umbrella) → #721, #722 (matcher) → #723 (simulator) → #724 (scorer) → #731, #732 (selection) → #725 (extraction) → #727 (trust) → #681 (coverage).

**Dependencies:** none (fixes first). #723/#724 build on #721/#722; #732 should land before #731 is re-measured.

| # | Task | Severity | Issue |
|---|------|----------|-------|
| 1.1 | Replay is a text-similarity proxy, not behavioral validation (architecture umbrella) | Critical | [#720](https://github.com/deghosal-2026/CauterRule/issues/720) |
| 1.2 | Matcher: semantic similarity cannot carry a match below cosine 0.80 | High | [#721](https://github.com/deghosal-2026/CauterRule/issues/721) |
| 1.3 | Matcher: score against the failure signature, not the full haystack | High | [#722](https://github.com/deghosal-2026/CauterRule/issues/722) |
| 1.4 | Simulator: stop counting spurious 'broken' successes (domain gate + margin + recovery) | Critical | [#723](https://github.com/deghosal-2026/CauterRule/issues/723) |
| 1.5 | Scorer: pass net-positive rules (fix `broken>0` ordering + broaden near-miss band) | Critical | [#724](https://github.com/deghosal-2026/CauterRule/issues/724) |
| 1.6 | Candidate ranking: prefer recall over precision; align runner and production | Medium | [#731](https://github.com/deghosal-2026/CauterRule/issues/731) |
| 1.7 | Deduplicate 2-pass candidates (`deduplicate()` is defined but uncalled) | Medium | [#732](https://github.com/deghosal-2026/CauterRule/issues/732) |
| 1.8 | Extraction: add a structured `error_signature` field | High | [#725](https://github.com/deghosal-2026/CauterRule/issues/725) |
| 1.9 | Enforce adversarial source-trust in production promotion (not just the runner) | Critical | [#727](https://github.com/deghosal-2026/CauterRule/issues/727) |
| 1.10 | Coverage 86% → 95% (#494) — TUI/observe/review/release/adversarial CLI + integrations | Medium | [#681](https://github.com/deghosal-2026/CauterRule/issues/681) |

### Context (from the v0.3.0 field test)

- `F-001` (git non-fast-forward) extracts a near-verbatim correct rule but replays as **inconclusive** (`precision 0.625`, `broken=3`, `near_misses=1`) — the three "broken" successes include a successful `git status` sharing only the token `git` (#723).
- `failures/positive` committed `inconclusive_breakdown = { broad_trigger: 0, matcher_gap: 22, ambiguous_evidence: 56 }`; the real blockers are the `precision<0.5` bar and spurious `broken` (#723, #724).
- The semantic term is capped at 0.2 of the blend and only floors at cosine ≥ 0.80, so a true paraphrase with zero shared tokens scores ~0.2 (#721, #722).
- `adversarial_unsafe` (llama) shows `unsafe-004` (`should_reject`) passing at precision 1.0 in committed artifacts — production auto-promote has no equivalent control (#727).
- `expected_rule` ground truth exists in `failures_positive` (23/50) and `reference-expansion` (288) but is never parsed or scored (#730, delivered in M2).

### M1 Exit Gate — closed 2026-09-12

- [x] **All tests pass:** `pytest` — deterministic suite green
- [x] **Lint strict clean:** `ruff check .` — zero errors
- [x] **Types strict clean:** `mypy src/ tests/` (strict) — zero errors (528 files)
- [ ] **Test coverage > 92%** — **88.5%**; remaining coverage folded into M4 (#747, release validation)
- [x] **Docs updated** (this WBS; report/calibration updates land with M2/M3)
- [x] **Code committed and pushed** to `feat-v0.3.1` @ `2b94b19`
- [x] **WBS updated** (`docs/wbs/v0.3.1/`)
- [x] **M1 issues closed** — 9 code issues done; #681 deferred to #747
- [x] Regression covered by unit tests (field-test validation is M3)

**Delivered (commit `2b94b19`):** failure-signature matching + semantic floor (#722, #721), structured `error_signature` (#725), spurious-`broken` fix (#723), net-positive scorer + `verdict_reason` (#724), recall-weighted ranking (#731), 2-pass dedup (#732), adversarial source-trust gate (#727), grounded outcome signal + `outcome_precision` (#720). Deep-review fixes: SHA false-positive, generic-signature floor, single `match_score`.

### See also

- [Part 2 — Evaluation & Field Test](wbs-v0.3.1-part2-field-test.md)
- [v0.3.0 field test report §1, §4, §9](../../field-test/v0.3.0/FIELD_TEST_REPORT.md)
